"""Centralized HTTP client for the Sharktech Cloud (OpenStack) API.

Authentication is performed via **Keystone v3** — the client obtains an
``X-Subject-Token`` and discovers service endpoints from the token's
catalogue.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from shark_cli.core.exceptions import APIError, AuthenticationError


class SharkClient:
    """Authenticates against Keystone v3 and exposes helpers for Nova /
    Neutron / other OpenStack services."""

    def __init__(
        self,
        auth_url: str,
        username: str,
        password: str,
        domain_id: str,
        project_id: str,
        insecure: bool = False,
    ) -> None:
        self._auth_url = auth_url.rstrip("/")
        self._username = username
        self._password = password
        self._domain_id = domain_id
        self._project_id = project_id

        self._token: str | None = None
        self._catalog: list[dict] = []

        self._http = httpx.Client(timeout=30.0, verify=not insecure)

        # Authenticate immediately so errors surface early
        self._authenticate()

    # ── Keystone v3 authentication ────────────────────────────────────

    def _authenticate(self) -> None:
        """POST to Keystone ``/v3/auth/tokens`` and store the token +
        service catalogue."""
        url = f"{self._auth_url}/v3/auth/tokens"
        payload = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": self._username,
                            "domain": {"name": self._domain_id},
                            "password": self._password,
                        }
                    },
                },
                "scope": {
                    "project": {
                        "name": self._project_id,
                        "domain": {"name": self._domain_id},
                    }
                },
            }
        }
        resp = self._http.post(url, json=payload)
        if resp.status_code in (401, 403):
            raise AuthenticationError(
                "Keystone authentication failed — verify your credentials "
                "('shark setup')."
            )
        if not resp.is_success:
            raise APIError(resp.status_code, resp.text[:300])

        self._token = resp.headers.get("X-Subject-Token", resp.headers.get("x-subject-token"))
        if not self._token:
            raise AuthenticationError("No X-Subject-Token returned by Keystone.")

        body = resp.json()
        self._catalog = body.get("token", {}).get("catalog", [])

    # ── Service catalogue helpers ─────────────────────────────────────

    def _endpoint_for(self, service_type: str, interface: str = "public") -> str:
        """Resolve a public endpoint URL from the Keystone catalogue."""
        for svc in self._catalog:
            if svc.get("type") == service_type:
                for ep in svc.get("endpoints", []):
                    if ep.get("interface") == interface:
                        return ep["url"].rstrip("/")
        raise APIError(
            0,
            f"Service '{service_type}' ({interface}) not found in the catalogue. "
            "Check your Sharktech project configuration.",
        )

    @property
    def compute_url(self) -> str:
        """Nova (compute) public endpoint."""
        return self._endpoint_for("compute")

    @property
    def network_url(self) -> str:
        """Neutron (network) public endpoint."""
        return self._endpoint_for("network")

    @property
    def identity_url(self) -> str:
        """Keystone (identity) public endpoint."""
        return self._endpoint_for("identity")

    # ── Generic HTTP helpers ──────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Auth-Token": self._token or "",
            "Accept": "application/json",
        }

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code in (401, 403):
            raise AuthenticationError()
        if not response.is_success:
            detail = ""
            try:
                body = response.json()
                detail = body.get("message") or body.get("error") or str(body)
            except Exception:
                detail = response.text[:300]
            raise APIError(response.status_code, detail)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        resp = self._http.get(url, headers=self._headers(), params=params)
        return self._handle_response(resp)

    def post(self, url: str, json: Optional[Dict[str, Any]] = None) -> Any:
        resp = self._http.post(url, headers=self._headers(), json=json)
        return self._handle_response(resp)

    def put(self, url: str, json: Optional[Dict[str, Any]] = None) -> Any:
        resp = self._http.put(url, headers=self._headers(), json=json)
        return self._handle_response(resp)

    def delete(self, url: str) -> Any:
        resp = self._http.delete(url, headers=self._headers())
        return self._handle_response(resp)

    def close(self) -> None:
        self._http.close()
