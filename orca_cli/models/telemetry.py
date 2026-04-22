"""Typed views of Gnocchi (metric) and Aodh (alarm) resources."""

from __future__ import annotations

from typing import TypedDict

# ── Gnocchi (metric) ──────────────────────────────────────────────────

class GnocchiResource(TypedDict, total=False):
    id: str
    type: str
    project_id: str
    user_id: str
    original_resource_id: str
    started_at: str
    ended_at: str
    revision_start: str
    revision_end: str
    metrics: dict


class GnocchiMetric(TypedDict, total=False):
    id: str
    name: str
    unit: str
    archive_policy_name: str
    archive_policy: dict
    resource_id: str
    creator: str
    created_by_user_id: str
    created_by_project_id: str


class ArchivePolicy(TypedDict, total=False):
    name: str
    aggregation_methods: list
    back_window: int
    definition: list


class GnocchiResourceType(TypedDict, total=False):
    name: str
    state: str
    attributes: dict


# ── Aodh (alarm) ──────────────────────────────────────────────────────

class Alarm(TypedDict, total=False):
    alarm_id: str
    name: str
    type: str
    description: str
    state: str
    state_timestamp: str
    state_reason: str
    severity: str
    enabled: bool
    project_id: str
    user_id: str
    ok_actions: list
    alarm_actions: list
    insufficient_data_actions: list
    repeat_actions: bool
    timestamp: str
    time_constraints: list
    threshold_rule: dict
    gnocchi_resources_threshold_rule: dict
    gnocchi_aggregation_by_metrics_threshold_rule: dict
    gnocchi_aggregation_by_resources_threshold_rule: dict
    event_rule: dict
    composite_rule: dict


class AlarmHistoryEntry(TypedDict, total=False):
    event_id: str
    alarm_id: str
    type: str
    detail: str
    on_behalf_of: str
    project_id: str
    user_id: str
    timestamp: str
