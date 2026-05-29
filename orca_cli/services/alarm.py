"""High-level operations on Aodh (alarm) resources."""

from __future__ import annotations

from typing import Any

from orca_cli.core.client import OrcaClient
from orca_cli.models.telemetry import Alarm, AlarmHistoryEntry


class AlarmService:
    """Typed wrapper around Aodh ``/v2`` endpoints."""

    def __init__(self, client: OrcaClient) -> None:
        self._client = client
        self._base = f"{client.alarming_url}/v2"

    # ── alarms ─────────────────────────────────────────────────────────

    def find(self, *, params: dict[str, Any] | None = None) -> list[Alarm]:
        data = self._client.get(f"{self._base}/alarms", params=params)
        return data if isinstance(data, list) else data.get("alarms", [])

    def get(self, alarm_id: str) -> Alarm:
        return self._client.get(f"{self._base}/alarms/{alarm_id}")

    def create(self, body: dict[str, Any]) -> Alarm:
        data = self._client.post(f"{self._base}/alarms", json=body)
        return data if data else {}

    def update(self, alarm_id: str, body: dict[str, Any]) -> Alarm:
        data = self._client.put(f"{self._base}/alarms/{alarm_id}",
                                json=body)
        return data if data else {}

    def delete(self, alarm_id: str) -> None:
        self._client.delete(f"{self._base}/alarms/{alarm_id}")

    def get_state(self, alarm_id: str) -> str:
        return self._client.get(f"{self._base}/alarms/{alarm_id}/state")

    def set_state(self, alarm_id: str, state: str) -> None:
        # Aodh expects a raw JSON string body (e.g. "alarm"), not an object.
        self._client.put(f"{self._base}/alarms/{alarm_id}/state",
                         json=state)  # type: ignore[arg-type]

    def find_history(
        self, alarm_id: str, *,
        params: dict[str, Any] | None = None,
    ) -> list[AlarmHistoryEntry]:
        data = self._client.get(
            f"{self._base}/alarms/{alarm_id}/history", params=params,
        )
        return data if isinstance(data, list) else data.get("history", [])

    # ── capabilities / quotas ──────────────────────────────────────────

    def get_capabilities(self) -> dict:
        return self._client.get(f"{self._base}/capabilities")

    def get_quota(self, project_id: str | None = None) -> dict:
        """Aodh ``GET /v2/quotas[/{project}]``."""
        suffix = f"/{project_id}" if project_id else ""
        data = self._client.get(f"{self._base}/quotas{suffix}")
        return data if isinstance(data, dict) else {}

    def get_metrics(self) -> list[dict]:
        """Aodh ``GET /v2/metrics`` — evaluator metrics."""
        data = self._client.get(f"{self._base}/metrics")
        return data if isinstance(data, list) else []

    def update_quota(self, body: dict[str, Any]) -> None:
        self._client.post(f"{self._base}/quotas", json=body)
