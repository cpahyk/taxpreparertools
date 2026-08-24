from __future__ import annotations

from typing import Any, Optional

import requests


class APIError(Exception):
    """Raised when the TaxPreparerTools API returns an error."""


class APIClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 20,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:

        url = f"{self.base_url}{path}"

        try:
            response = requests.request(
                method,
                url,
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise APIError(
                f"Could not connect to license server: {exc}"
            ) from exc

        try:
            data = response.json()
        except ValueError:
            data = {}

        if not response.ok:
            detail = data.get("detail", response.text)

            raise APIError(
                f"API error ({response.status_code}): {detail}"
            )

        return data

    def activate(
        self,
        license_key: str,
        installation_id: str,
        machine_hash: Optional[str] = None,
        version: str = "unknown",
    ) -> dict[str, Any]:

        return self._request(
            "POST",
            "/v1/license/activate",
            {
                "license_key": license_key,
                "installation_id": installation_id,
                "machine_hash": machine_hash,
                "product": "pdf-qbo-converter",
                "version": version,
            },
        )

    def validate(
        self,
        license_key: str,
        installation_id: str,
    ) -> dict[str, Any]:

        return self._request(
            "POST",
            "/v1/license/validate",
            {
                "license_key": license_key,
                "installation_id": installation_id,
                "product": "pdf-qbo-converter",
            },
        )

    def deactivate(
        self,
        license_key: str,
        installation_id: str,
    ) -> dict[str, Any]:

        return self._request(
            "POST",
            "/v1/license/deactivate",
            {
                "license_key": license_key,
                "installation_id": installation_id,
            },
        )

    def health(self) -> dict[str, Any]:
        return self._request(
            "GET",
            "/health",
        )
