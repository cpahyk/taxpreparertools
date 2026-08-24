from __future__ import annotations

import hashlib
import json
import os
import platform
import uuid
from pathlib import Path
from typing import Any, Optional

from api_client import APIClient

APP_NAME = "pdf-qbo-converter"
APP_VERSION = "2.0"


class LicenseManager:
    """Manages activation state for the PDF -> QBO Converter."""

    def __init__(self, api_client: Optional[APIClient] = None, version: str = APP_VERSION):
        self.api = api_client or APIClient()
        self.version = version
        self.state_file = self._state_file()

    @staticmethod
    def _state_file() -> Path:
        if os.name == "nt":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif platform.system() == "Darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

        folder = base / APP_NAME
        folder.mkdir(parents=True, exist_ok=True)
        return folder / "license.json"

    def _read(self) -> dict[str, Any]:
        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _write(self, data: dict[str, Any]) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        temp = self.state_file.with_suffix(".tmp")
        with temp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp.replace(self.state_file)

    def get_license_key(self) -> Optional[str]:
        value = self._read().get("license_key")
        return str(value) if value else None

    def get_installation_id(self) -> str:
        data = self._read()
        value = data.get("installation_id")
        if value:
            return str(value)

        value = str(uuid.uuid4())
        data["installation_id"] = value
        self._write(data)
        return value

    def get_machine_hash(self) -> str:
        raw = "|".join((platform.system(), platform.release(), platform.machine()))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def activate(self, license_key: str) -> dict[str, Any]:
        license_key = license_key.strip()
        if not license_key:
            raise ValueError("Please enter a license key.")

        installation_id = self.get_installation_id()
        machine_hash = self.get_machine_hash()

        # APIClient raises APIError for non-2xx responses, so a returned
        # response means the server accepted the activation request.
        response = self.api.activate(
            license_key=license_key,
            installation_id=installation_id,
            machine_hash=machine_hash,
            version=self.version,
        )

        data = self._read()
        data.update(
            {
                "license_key": license_key,
                "installation_id": installation_id,
                "product": "pdf-qbo-converter",
                "version": self.version,
            }
        )
        self._write(data)
        return response

    def validate(self) -> dict[str, Any]:
        license_key = self.get_license_key()
        if not license_key:
            raise RuntimeError("No license is activated on this computer.")

        return self.api.validate(
            license_key=license_key,
            installation_id=self.get_installation_id(),
        )

    def deactivate(self) -> dict[str, Any]:
        license_key = self.get_license_key()
        if not license_key:
            return {"success": True, "message": "No license is activated."}

        response = self.api.deactivate(
            license_key=license_key,
            installation_id=self.get_installation_id(),
        )

        data = self._read()
        data.pop("license_key", None)
        self._write(data)
        return response

    def clear_local_license(self) -> None:
        data = self._read()
        data.pop("license_key", None)
        self._write(data)
