"""Typed views of CloudKitty rating resources (only the fields orca reads)."""

from __future__ import annotations

from typing import TypedDict


class RatingModule(TypedDict, total=False):
    module_id: str
    description: str
    enabled: bool
    priority: int
    hot_config: bool


class HashmapService(TypedDict, total=False):
    service_id: str
    name: str


class HashmapField(TypedDict, total=False):
    field_id: str
    name: str
    service_id: str


class HashmapMapping(TypedDict, total=False):
    mapping_id: str
    value: str
    type: str
    cost: str
    map_type: str
    service_id: str
    field_id: str
    group_id: str
    tenant_id: str


class HashmapThreshold(TypedDict, total=False):
    threshold_id: str
    level: str
    type: str
    cost: str
    map_type: str
    service_id: str
    field_id: str
    group_id: str
    tenant_id: str


class HashmapGroup(TypedDict, total=False):
    group_id: str
    name: str


class RatingSummary(TypedDict, total=False):
    begin: str
    end: str
    tenant_id: str
    res_type: str
    rate: str
    qty: str
