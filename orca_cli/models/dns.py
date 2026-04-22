"""Typed views of Designate DNS resources (only the fields orca reads)."""

from __future__ import annotations

from typing import TypedDict


class Zone(TypedDict, total=False):
    id: str
    name: str
    description: str
    email: str
    ttl: int
    type: str
    masters: list
    serial: int
    status: str
    action: str
    pool_id: str
    project_id: str
    created_at: str
    updated_at: str


class Recordset(TypedDict, total=False):
    id: str
    zone_id: str
    zone_name: str
    name: str
    type: str
    ttl: int
    records: list
    description: str
    status: str
    action: str
    version: int
    project_id: str
    created_at: str
    updated_at: str


class ZoneTransferRequest(TypedDict, total=False):
    id: str
    zone_id: str
    zone_name: str
    key: str
    project_id: str
    target_project_id: str
    description: str
    status: str
    created_at: str


class Tld(TypedDict, total=False):
    id: str
    name: str
    description: str
    created_at: str
