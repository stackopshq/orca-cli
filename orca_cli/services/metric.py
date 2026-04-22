"""High-level operations on Gnocchi (metric) resources."""

from __future__ import annotations

from typing import Any

from orca_cli.core.client import OrcaClient
from orca_cli.models.telemetry import (
    ArchivePolicy,
    GnocchiMetric,
    GnocchiResource,
    GnocchiResourceType,
)


class MetricService:
    """Typed wrapper around Gnocchi ``/v1`` endpoints."""

    def __init__(self, client: OrcaClient) -> None:
        self._client = client
        self._base = f"{client.metric_url}/v1"

    # ── resource types ─────────────────────────────────────────────────

    def find_resource_types(self) -> list[GnocchiResourceType]:
        data = self._client.get(f"{self._base}/resource_type")
        return data if isinstance(data, list) else data.get("resource_types", [])

    def get_resource_type(self, name: str) -> GnocchiResourceType:
        return self._client.get(f"{self._base}/resource_type/{name}")

    def create_resource_type(self, body: dict[str, Any]) -> GnocchiResourceType:
        data = self._client.post(f"{self._base}/resource_type", json=body)
        return data if data else {}

    def delete_resource_type(self, name: str) -> None:
        self._client.delete(f"{self._base}/resource_type/{name}")

    # ── resources ──────────────────────────────────────────────────────

    def find_resources(
        self, resource_type: str, *,
        params: dict[str, Any] | None = None,
    ) -> list[GnocchiResource]:
        data = self._client.get(
            f"{self._base}/resource/{resource_type}", params=params,
        )
        return data if isinstance(data, list) else data.get("resources", [])

    def get_resource(self, resource_type: str,
                     resource_id: str) -> GnocchiResource:
        return self._client.get(
            f"{self._base}/resource/{resource_type}/{resource_id}"
        )

    # ── metrics ────────────────────────────────────────────────────────

    def find_metrics(self, *,
                     params: dict[str, Any] | None = None) -> list[GnocchiMetric]:
        data = self._client.get(f"{self._base}/metric", params=params)
        return data if isinstance(data, list) else data.get("metrics", [])

    def get_metric(self, metric_id: str) -> GnocchiMetric:
        return self._client.get(f"{self._base}/metric/{metric_id}")

    def create_metric(self, body: dict[str, Any]) -> GnocchiMetric:
        data = self._client.post(f"{self._base}/metric", json=body)
        return data if data else {}

    def delete_metric(self, metric_id: str) -> None:
        self._client.delete(f"{self._base}/metric/{metric_id}")

    def get_measures(self, metric_id: str, *,
                     params: dict[str, Any] | None = None) -> list:
        return self._client.get(
            f"{self._base}/metric/{metric_id}/measures", params=params,
        )

    def add_measures(self, metric_id: str, measures: list[dict]) -> None:
        self._client.post(
            f"{self._base}/metric/{metric_id}/measures", json=measures,
        )

    # ── archive policies ───────────────────────────────────────────────

    def find_archive_policies(self) -> list[ArchivePolicy]:
        data = self._client.get(f"{self._base}/archive_policy")
        return data if isinstance(data, list) else data.get("archive_policies", [])

    def get_archive_policy(self, name: str) -> ArchivePolicy:
        return self._client.get(f"{self._base}/archive_policy/{name}")

    def create_archive_policy(self, body: dict[str, Any]) -> ArchivePolicy:
        data = self._client.post(f"{self._base}/archive_policy", json=body)
        return data if data else {}

    def delete_archive_policy(self, name: str) -> None:
        self._client.delete(f"{self._base}/archive_policy/{name}")

    # ── status ─────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        return self._client.get(f"{self._base}/status")
