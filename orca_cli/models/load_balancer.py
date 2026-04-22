"""Typed views of Octavia load-balancing resources (only the fields orca reads)."""

from __future__ import annotations

from typing import TypedDict


class LoadBalancer(TypedDict, total=False):
    id: str
    name: str
    description: str
    provisioning_status: str
    operating_status: str
    vip_address: str
    vip_port_id: str
    vip_subnet_id: str
    vip_network_id: str
    vip_qos_policy_id: str
    admin_state_up: bool
    provider: str
    flavor_id: str
    availability_zone: str
    created_at: str
    updated_at: str
    project_id: str
    tenant_id: str
    tags: list
    listeners: list
    pools: list


class Listener(TypedDict, total=False):
    id: str
    name: str
    description: str
    protocol: str
    protocol_port: int
    connection_limit: int
    admin_state_up: bool
    default_pool_id: str
    default_tls_container_ref: str
    sni_container_refs: list
    loadbalancers: list
    l7policies: list
    timeout_client_data: int
    timeout_member_connect: int
    timeout_member_data: int
    timeout_tcp_inspect: int
    provisioning_status: str
    operating_status: str
    created_at: str
    updated_at: str
    tags: list


class Pool(TypedDict, total=False):
    id: str
    name: str
    description: str
    protocol: str
    lb_algorithm: str
    session_persistence: dict
    admin_state_up: bool
    loadbalancers: list
    listeners: list
    members: list
    healthmonitor_id: str
    provisioning_status: str
    operating_status: str
    created_at: str
    updated_at: str
    tags: list


class Member(TypedDict, total=False):
    id: str
    name: str
    address: str
    protocol_port: int
    weight: int
    admin_state_up: bool
    subnet_id: str
    monitor_address: str
    monitor_port: int
    backup: bool
    provisioning_status: str
    operating_status: str


class HealthMonitor(TypedDict, total=False):
    id: str
    name: str
    type: str
    delay: int
    timeout: int
    max_retries: int
    max_retries_down: int
    http_method: str
    url_path: str
    expected_codes: str
    admin_state_up: bool
    pools: list
    provisioning_status: str
    operating_status: str


class L7Policy(TypedDict, total=False):
    id: str
    name: str
    description: str
    action: str
    position: int
    redirect_url: str
    redirect_pool_id: str
    redirect_prefix: str
    redirect_http_code: int
    admin_state_up: bool
    listener_id: str
    rules: list
    provisioning_status: str
    operating_status: str


class L7Rule(TypedDict, total=False):
    id: str
    type: str
    compare_type: str
    key: str
    value: str
    invert: bool
    admin_state_up: bool
    provisioning_status: str
    operating_status: str


class Amphora(TypedDict, total=False):
    id: str
    loadbalancer_id: str
    compute_id: str
    lb_network_ip: str
    vrrp_ip: str
    ha_ip: str
    vrrp_interface: str
    vrrp_id: int
    vrrp_priority: int
    role: str
    status: str
    cert_expiration: str
    cert_busy: bool
    created_at: str
    updated_at: str
