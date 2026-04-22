"""High-level operations on CloudKitty rating resources."""

from __future__ import annotations

from typing import Any

from orca_cli.core.client import OrcaClient
from orca_cli.models.rating import (
    HashmapField,
    HashmapGroup,
    HashmapMapping,
    HashmapService,
    HashmapThreshold,
    RatingModule,
    RatingSummary,
)

_HM = "/v1/rating/module_config/hashmap"


class RatingService:
    """Typed wrapper around CloudKitty ``/v1`` and ``/v2`` endpoints."""

    def __init__(self, client: OrcaClient) -> None:
        self._client = client
        self._base = client.rating_url

    # ── info ───────────────────────────────────────────────────────────

    def get_config(self) -> dict:
        return self._client.get(f"{self._base}/v1/info/config")

    def find_metrics(self) -> list[dict]:
        data = self._client.get(f"{self._base}/v1/info/metrics")
        return data.get("metrics", [])

    def get_metric(self, metric_id: str) -> dict:
        return self._client.get(f"{self._base}/v1/info/metrics/{metric_id}")

    # ── summary / dataframes ───────────────────────────────────────────

    def get_summary(self, *,
                    params: dict[str, Any] | None = None) -> RatingSummary:
        return self._client.get(f"{self._base}/v2/summary", params=params)

    def find_dataframes(self, *, v2: bool = True,
                        params: dict[str, Any] | None = None) -> dict:
        url = (f"{self._base}/v2/dataframes" if v2
               else f"{self._base}/v1/storage/dataframes")
        return self._client.get(url, params=params)

    # ── quotes ─────────────────────────────────────────────────────────

    def create_quote(self, payload: dict[str, Any]) -> dict:
        return self._client.post(
            f"{self._base}/v1/rating/quote", json=payload,
        ) or {}

    # ── modules ────────────────────────────────────────────────────────

    def find_modules(self) -> list[RatingModule]:
        data = self._client.get(f"{self._base}/v1/rating/modules")
        return data.get("modules", [])

    def get_module(self, module_id: str) -> RatingModule:
        return self._client.get(
            f"{self._base}/v1/rating/modules/{module_id}",
        )

    def update_module(self, module_id: str,
                      body: dict[str, Any]) -> RatingModule:
        data = self._client.put(
            f"{self._base}/v1/rating/modules/{module_id}",
            json=body,
        )
        return data if data else {}

    # ── hashmap: services ──────────────────────────────────────────────

    def find_hashmap_services(self) -> list[HashmapService]:
        data = self._client.get(f"{self._base}{_HM}/services")
        return data.get("services", [])

    def create_hashmap_service(self, name: str) -> HashmapService:
        data = self._client.post(f"{self._base}{_HM}/services",
                                 json={"name": name})
        return data if data else {}

    def delete_hashmap_service(self, service_id: str) -> None:
        self._client.delete(f"{self._base}{_HM}/services/{service_id}")

    # ── hashmap: fields ────────────────────────────────────────────────

    def find_hashmap_fields(
        self, *, params: dict[str, Any] | None = None,
    ) -> list[HashmapField]:
        data = self._client.get(f"{self._base}{_HM}/fields", params=params)
        return data.get("fields", [])

    def create_hashmap_field(
        self, body: dict[str, Any],
    ) -> HashmapField:
        data = self._client.post(f"{self._base}{_HM}/fields", json=body)
        return data if data else {}

    def delete_hashmap_field(self, field_id: str) -> None:
        self._client.delete(f"{self._base}{_HM}/fields/{field_id}")

    # ── hashmap: mappings ──────────────────────────────────────────────

    def find_hashmap_mappings(
        self, *, params: dict[str, Any] | None = None,
    ) -> list[HashmapMapping]:
        data = self._client.get(f"{self._base}{_HM}/mappings", params=params)
        return data.get("mappings", [])

    def create_hashmap_mapping(
        self, body: dict[str, Any],
    ) -> HashmapMapping:
        data = self._client.post(f"{self._base}{_HM}/mappings", json=body)
        return data if data else {}

    def delete_hashmap_mapping(self, mapping_id: str) -> None:
        self._client.delete(f"{self._base}{_HM}/mappings/{mapping_id}")

    # ── hashmap: thresholds ────────────────────────────────────────────

    def find_hashmap_thresholds(
        self, *, params: dict[str, Any] | None = None,
    ) -> list[HashmapThreshold]:
        data = self._client.get(f"{self._base}{_HM}/thresholds",
                                params=params)
        return data.get("thresholds", [])

    def create_hashmap_threshold(
        self, body: dict[str, Any],
    ) -> HashmapThreshold:
        data = self._client.post(f"{self._base}{_HM}/thresholds", json=body)
        return data if data else {}

    def delete_hashmap_threshold(self, threshold_id: str) -> None:
        self._client.delete(f"{self._base}{_HM}/thresholds/{threshold_id}")

    # ── hashmap: groups ────────────────────────────────────────────────

    def find_hashmap_groups(self) -> list[HashmapGroup]:
        data = self._client.get(f"{self._base}{_HM}/groups")
        return data.get("groups", [])

    def create_hashmap_group(self, name: str) -> HashmapGroup:
        data = self._client.post(f"{self._base}{_HM}/groups",
                                 json={"name": name})
        return data if data else {}

    def delete_hashmap_group(self, group_id: str) -> None:
        self._client.delete(f"{self._base}{_HM}/groups/{group_id}")
