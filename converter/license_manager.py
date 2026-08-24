"""
License management for the PDF -> QBO converter.

Responsibilities:
- Activate a license through the FastAPI backend
- Validate an activated license
- Deactivate a license
- Persist the local activation information
- Fail safely when the API is unavailable
"""

from __future__ import annotations

import json
import os
import platform
import uuid
from pathlib import Path
from typing import Any, Optional

from .api_client import APIClient


APP_NAME = "PDF_to_QBO_Converter"


class LicenseManager:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api = api_client or APIClient()
        self.license_file = self._license_file()

    # ---------------------------------------------------------
    # Local storage
    # ---------------------------------------------------------

    def _license_file(self) -> Path:
        """
        Store activation data in the user's local application-data
        directory rather than beside the executable.
        """
        if os.name == "nt":
            base = Path(
                os.environ.get(
                    "APPDATA",
                    Path.home() / "AppData" / "Roaming",
                )
            )
        else:
            base = Path(
                os.environ.get(
                    "XDG_CONFIG_HOME",
                    Path.home() / ".config",
                )
            )

        directory = base / APP_NAME
        directory.mkdir(parents=True, exist_ok=True)

        return directory / "license.json"

    def _load(self) -> dict[str, Any]:
        if not self.license_file.exists():
            return {}

        try:
            with self.license_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            return data if isinstance(data, dict) else {}

        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, data: dict[str, Any]) -> None:
        self.license_file.parent.mkdir(parents=True, exist_ok=True)

        temp_file = self.license_file.with_suffix(".tmp")

        with temp_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        temp_file.replace(self.license_file)

    def clear_local_license(self) -> None:
        try:
            self.license_file.unlink(missing_ok=True)
        except OSError:
            pass

    # ---------------------------------------------------------
    # Installation identity
    # ---------------------------------------------------------

    def installation_id(self) -> str:
        """
        Generate a stable installation identifier.

        It is deliberately stored locally rather than using sensitive
        hardware identifiers.
        """
        data = self._load()

        installation_id = data.get("installation_id")

        if installation_id:
            return str(installation_id)

        installation_id = str(uuid.uuid4())

        data["installation_id"] = installation_id
        self._save(data)

        return installation_id

    def machine_hash(self) -> str:
        """
        Returns a non-secret application fingerprint.

        If your backend does not require machine_hash, this can be
        removed from the request.
        """
        raw = "|".join(
            [
                platform.system(),
                platform.machine(),
                platform.python_version(),
            ]
        )

        import hashlib

        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ---------------------------------------------------------
    # License state
    # ---------------------------------------------------------

    def get_license_key(self) -> Optional[str]:
        data = self._load()
        key = data.get("license_key")

        return str(key) if key else None

    def is_activated(self) -> bool:
        return bool(self.get_license_key())

    # ---------------------------------------------------------
    # API helpers
    # ---------------------------------------------------------

    def _call_api(self, method: str, *args, **kwargs):
        """
        Supports either a normal API client method or a requests-like
        client implementation.

        This keeps the manager easy to adapt to your existing
        api_client.py.
        """
        function = getattr(self.api, method, None)

        if not callable(function):
            raise AttributeError(
                f"APIClient does not provide '{method}()'. "
                f"Add that method to api_client.py."
            )

        return function(*args, **kwargs)

    # ---------------------------------------------------------
    # Activation
    # ---------------------------------------------------------

    def activate(self, license_key: str) -> dict[str, Any]:
        license_key = license_key.strip()

        if not license_key:
            raise ValueError("License key is required.")

        installation_id = self.installation_id()
        machine_hash = self.machine_hash()

        payload = {
            "license_key": license_key,
            "installation_id": installation_id,
            "machine_hash": machine_hash,
            "product": APP_NAME,
        }

        response = self._call_api(
            "activate_license",
            payload,
        )

        response_data = self._response_to_dict(response)

        if not self._activation_succeeded(response_data):
            raise RuntimeError(
                self._error_message(
                    response_data,
                    "License activation failed.",
                )
            )

        data = self._load()

        data.update(
            {
                "license_key": license_key,
                "installation_id": installation_id,
                "machine_hash": machine_hash,
                "product": APP_NAME,
            }
        )

        self._save(data)

        return response_data

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(self) -> dict[str, Any]:
        license_key = self.get_license_key()

        if not license_key:
            raise RuntimeError("No license has been activated.")

        payload = {
            "license_key": license_key,
            "installation_id": self.installation_id(),
            "machine_hash": self.machine_hash(),
            "product": APP_NAME,
        }

        response = self._call_api(
            "validate_license",
            payload,
        )

        response_data = self._response_to_dict(response)

        if not self._validation_succeeded(response_data):
            self.clear_local_license()

            raise RuntimeError(
                self._error_message(
                    response_data,
                    "License validation failed.",
                )
            )

        return response_data

    # ---------------------------------------------------------
    # Deactivation
    # ---------------------------------------------------------

    def deactivate(self) -> dict[str, Any]:
        license_key = self.get_license_key()

        if not license_key:
            return {
                "success": True,
                "message": "No local license is activated.",
            }

        payload = {
            "license_key": license_key,
            "installation_id": self.installation_id(),
            "machine_hash": self.machine_hash(),
            "product": APP_NAME,
        }

        response = self._call_api(
            "deactivate_license",
            payload,
        )

        response_data = self._response_to_dict(response)

        if not self._response_success(response_data):
            raise RuntimeError(
                self._error_message(
                    response_data,
                    "License deactivation failed.",
                )
            )

        self.clear_local_license()

        return response_data

    # ---------------------------------------------------------
    # Response handling
    # ---------------------------------------------------------

    @staticmethod
    def _response_to_dict(response: Any) -> dict[str, Any]:
        if isinstance(response, dict):
            return response

        if hasattr(response, "json"):
            try:
                data = response.json()
                return data if isinstance(data, dict) else {}
            except Exception:
                pass

        if hasattr(response, "data"):
            data = response.data
            return data if isinstance(data, dict) else {}

        return {}

    @staticmethod
    def _response_success(data: dict[str, Any]) -> bool:
        if data.get("success") is True:
            return True

        if data.get("valid") is True:
            return True

        if data.get("active") is True:
            return True

        status = str(data.get("status", "")).lower()

        return status in {
            "success",
            "active",
            "valid",
            "activated",
        }

    @classmethod
    def _activation_succeeded(cls, data: dict[str, Any]) -> bool:
        return cls._response_success(data)

    @classmethod
    def _validation_succeeded(cls, data: dict[str, Any]) -> bool:
        return cls._response_success(data)

    @staticmethod
    def _error_message(
        data: dict[str, Any],
        default: str,
    ) -> str:
        for key in ("detail", "message", "error"):
            value = data.get(key)

            if value:
                return str(value)

        return default