from __future__ import annotations

import hashlib
import json
import os
import platform
import uuid
from pathlib import Path
from typing import Any, Optional

from .api_client import APIClient, APIError


APP_NAME = "pdf-qbo-converter"
APP_VERSION = "1.0.0"


class LicenseManager:
    """
    Client-side license manager for the PDF -> QBO Converter.

    Uses the existing APIClient:
        POST /v1/license/activate
        POST /v1/license/validate
        POST /v1/license/deactivate

    Local state is stored in the user's application-data directory.
    """

    def __init__(
        self,
        api_client: Optional[APIClient] = None,
        version: str = APP_VERSION,
    ) -> None:
        self.api = api_client or APIClient()
        self.version = version
        self.state_file = self._get_state_file()

    # ------------------------------------------------------------------
    # Local state
    # ------------------------------------------------------------------

    @staticmethod
    def _get_state_file() -> Path:
        if os.name == "nt":
            base = Path(
                os.environ.get(
                    "APPDATA",
                    Path.home() / "AppData" / "Roaming",
                )
            )
        elif platform.system() == "Darwin":
            base = (
                Path.home()
                / "Library"
                / "Application Support"
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

    def _read_state(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {}

        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_state(self, data: dict[str, Any]) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        tmp = self.state_file.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        tmp.replace(self.state_file)

    def clear(self) -> None:
        try:
            self.state_file.unlink(missing_ok=True)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Installation identity
    # ------------------------------------------------------------------

    def get_installation_id(self) -> str:
        state = self._read_state()
        installation_id = state.get("installation_id")

        if installation_id:
            return str(installation_id)

        installation_id = str(uuid.uuid4())
        state["installation_id"] = installation_id
        self._write_state(state)

        return installation_id

    def get_machine_hash(self) -> str:
        """
        Creates a stable application fingerprint from non-secret platform
        characteristics. It is only sent when activating the license.
        """
        raw = "|".join(
            (
                platform.system(),
                platform.release(),
                platform.machine(),
            )
        )

        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # License information
    # ------------------------------------------------------------------

    def get_license_key(self) -> Optional[str]:
        value = self._read_state().get("license_key")
        return str(value) if value else None

    def is_activated(self) -> bool:
        return bool(self.get_license_key())

    # ------------------------------------------------------------------
    # API operations
    # ------------------------------------------------------------------

    def activate(self, license_key: str) -> dict[str, Any]:
        """
        Activate the license on this installation.

        Matches the existing APIClient.activate() signature.
        """
        license_key = license_key.strip()

        if not license_key:
            raise ValueError("Please enter a license key.")

        installation_id = self.get_installation_id()
        machine_hash = self.get_machine_hash()

        response = self.api.activate(
            license_key=license_key,
            installation_id=installation_id,
            machine_hash=machine_hash,
            version=self.version,
        )

        if not self._looks_successful(response):
            raise APIError(
                self._message(response, "License activation failed.")
            )

        state = self._read_state()
        state.update(
            {
                "license_key": license_key,
                "installation_id": installation_id,
                "product": APP_NAME,
                "version": self.version,
            }
        )
        self._write_state(state)

        return response

    def validate(self) -> dict[str, Any]:
        """
        Validate the currently stored license against the server.

        A server-side failure is raised rather than silently treating an
        unreachable server as a valid license.
        """
        license_key = self.get_license_key()

        if not license_key:
            raise APIError("No license is activated on this computer.")

        response = self.api.validate(
            license_key=license_key,
            installation_id=self.get_installation_id(),
        )

        if not self._looks_successful(response):
            raise APIError(
                self._message(response, "License validation failed.")
            )

        return response

    def deactivate(self) -> dict[str, Any]:
        license_key = self.get_license_key()

        if not license_key:
            return {
                "success": True,
                "message": "No license is currently activated.",
            }

        response = self.api.deactivate(
            license_key=license_key,
            installation_id=self.get_installation_id(),
        )

        if not self._looks_successful(response):
            raise APIError(
                self._message(response, "License deactivation failed.")
            )

        state = self._read_state()
        state.pop("license_key", None)
        self._write_state(state)

        return response

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _looks_successful(data: Any) -> bool:
        if not isinstance(data, dict):
            return False

        # Common API response forms.
        for key in ("success", "valid", "active", "activated"):
            if data.get(key) is True:
                return True

        status = str(data.get("status", "")).strip().lower()
        if status in {
            "ok",
            "success",
            "valid",
            "active",
            "activated",
        }:
            return True

        # Some APIs return a license object without a boolean.
        # Only accept this if an explicit license key/status is present.
        license_status = str(
            data.get("license_status", "")
        ).strip().lower()

        return license_status in {
            "active",
            "valid",
            "activated",
        }

    @staticmethod
    def _message(
        data: Any,
        default: str,
    ) -> str:
        if isinstance(data, dict):
            for key in ("detail", "message", "error"):
                value = data.get(key)
                if value:
                    return str(value)

        return default


# Convenience factory for the converter application.
def create_license_manager(
    base_url: str = "http://localhost:8000",
) -> LicenseManager:
    return LicenseManager(
        api_client=APIClient(base_url=base_url),
    )
