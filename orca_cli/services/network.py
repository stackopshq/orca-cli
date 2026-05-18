"""High-level operations on Neutron networking resources."""

from __future__ import annotations

from typing import Any

from orca_cli.core.client import OrcaClient
from orca_cli.models.network import (
    Agent,
    AutoAllocatedTopology,
    FloatingIp,
    Network,
    Port,
    QosPolicy,
    QosRule,
    RbacPolicy,
    Router,
    SecurityGroup,
    SecurityGroupRule,
    Segment,
    Subnet,
    SubnetPool,
    Trunk,
)


class NetworkService:
    """Typed wrapper around the Neutron ``/v2.0`` endpoints.

    Owns URL construction for networks, subnets, ports, routers,
    floating IPs, security groups + rules, subnet pools, trunks,
    QoS policies + rules, agents, RBAC policies, segments, and
    auto-allocated topology. Retry, auth, and pagination live in
    OrcaClient — the service is purely a translation layer between
    Neutron and the typed models.
    """

    def __init__(self, client: OrcaClient) -> None:
        self._client = client
        self._base = f"{client.network_url}/v2.0"

    # ── networks ───────────────────────────────────────────────────────

    def find(self, *, params: dict[str, Any] | None = None) -> list[Network]:
        data = self._client.get(f"{self._base}/networks", params=params)
        return data.get("networks", [])

    def find_all(self, page_size: int = 1000, *,
                 params: dict[str, Any] | None = None) -> list[Network]:
        return self._client.paginate(f"{self._base}/networks", "networks",
                                     page_size=page_size, params=params)

    def get(self, network_id: str) -> Network:
        data = self._client.get(f"{self._base}/networks/{network_id}")
        return data.get("network", data)

    def create(self, body: dict[str, Any]) -> Network:
        data = self._client.post(f"{self._base}/networks",
                                 json={"network": body})
        return data.get("network", data) if data else {}

    def update(self, network_id: str, body: dict[str, Any]) -> Network:
        data = self._client.put(f"{self._base}/networks/{network_id}",
                                json={"network": body})
        return data.get("network", data) if data else {}

    def delete(self, network_id: str) -> None:
        self._client.delete(f"{self._base}/networks/{network_id}")

    # ── subnets ────────────────────────────────────────────────────────

    def find_subnets(self, *,
                     params: dict[str, Any] | None = None) -> list[Subnet]:
        data = self._client.get(f"{self._base}/subnets", params=params)
        return data.get("subnets", [])

    def find_all_subnets(self, page_size: int = 1000, *,
                         params: dict[str, Any] | None = None) -> list[Subnet]:
        return self._client.paginate(f"{self._base}/subnets", "subnets",
                                     page_size=page_size, params=params)

    def get_subnet(self, subnet_id: str) -> Subnet:
        data = self._client.get(f"{self._base}/subnets/{subnet_id}")
        return data.get("subnet", data)

    def create_subnet(self, body: dict[str, Any]) -> Subnet:
        data = self._client.post(f"{self._base}/subnets",
                                 json={"subnet": body})
        return data.get("subnet", data) if data else {}

    def update_subnet(self, subnet_id: str, body: dict[str, Any]) -> Subnet:
        data = self._client.put(f"{self._base}/subnets/{subnet_id}",
                                json={"subnet": body})
        return data.get("subnet", data) if data else {}

    def delete_subnet(self, subnet_id: str) -> None:
        self._client.delete(f"{self._base}/subnets/{subnet_id}")

    # ── ports ──────────────────────────────────────────────────────────

    def find_ports(self, *,
                   params: dict[str, Any] | None = None) -> list[Port]:
        data = self._client.get(f"{self._base}/ports", params=params)
        return data.get("ports", [])

    def find_all_ports(self, page_size: int = 1000, *,
                       params: dict[str, Any] | None = None) -> list[Port]:
        return self._client.paginate(f"{self._base}/ports", "ports",
                                     page_size=page_size, params=params)

    def get_port(self, port_id: str) -> Port:
        data = self._client.get(f"{self._base}/ports/{port_id}")
        return data.get("port", data)

    def create_port(self, body: dict[str, Any]) -> Port:
        data = self._client.post(f"{self._base}/ports",
                                 json={"port": body})
        return data.get("port", data) if data else {}

    def update_port(self, port_id: str, body: dict[str, Any]) -> Port:
        data = self._client.put(f"{self._base}/ports/{port_id}",
                                json={"port": body})
        return data.get("port", data) if data else {}

    def delete_port(self, port_id: str) -> None:
        self._client.delete(f"{self._base}/ports/{port_id}")

    # ── routers ────────────────────────────────────────────────────────

    def find_routers(self, *,
                     params: dict[str, Any] | None = None) -> list[Router]:
        data = self._client.get(f"{self._base}/routers", params=params)
        return data.get("routers", [])

    def find_all_routers(self, page_size: int = 1000, *,
                         params: dict[str, Any] | None = None) -> list[Router]:
        return self._client.paginate(f"{self._base}/routers", "routers",
                                     page_size=page_size, params=params)

    def get_router(self, router_id: str) -> Router:
        data = self._client.get(f"{self._base}/routers/{router_id}")
        return data.get("router", data)

    def create_router(self, body: dict[str, Any]) -> Router:
        data = self._client.post(f"{self._base}/routers",
                                 json={"router": body})
        return data.get("router", data) if data else {}

    def update_router(self, router_id: str, body: dict[str, Any]) -> Router:
        data = self._client.put(f"{self._base}/routers/{router_id}",
                                json={"router": body})
        return data.get("router", data) if data else {}

    def delete_router(self, router_id: str) -> None:
        self._client.delete(f"{self._base}/routers/{router_id}")

    def add_router_interface(self, router_id: str,
                             body: dict[str, Any]) -> dict | None:
        return self._client.put(
            f"{self._base}/routers/{router_id}/add_router_interface",
            json=body,
        )

    def remove_router_interface(self, router_id: str,
                                body: dict[str, Any]) -> dict | None:
        return self._client.put(
            f"{self._base}/routers/{router_id}/remove_router_interface",
            json=body,
        )

    def add_router_routes(self, router_id: str,
                          routes: list[dict[str, Any]]) -> dict | None:
        return self._client.put(
            f"{self._base}/routers/{router_id}/add_extraroutes",
            json={"router": {"routes": routes}},
        )

    def remove_router_routes(self, router_id: str,
                             routes: list[dict[str, Any]]) -> dict | None:
        return self._client.put(
            f"{self._base}/routers/{router_id}/remove_extraroutes",
            json={"router": {"routes": routes}},
        )

    # ── floating IPs ───────────────────────────────────────────────────

    def find_floating_ips(self, *,
                          params: dict[str, Any] | None = None) -> list[FloatingIp]:
        data = self._client.get(f"{self._base}/floatingips", params=params)
        return data.get("floatingips", [])

    def find_all_floating_ips(
        self, page_size: int = 1000, *,
        params: dict[str, Any] | None = None,
    ) -> list[FloatingIp]:
        return self._client.paginate(f"{self._base}/floatingips", "floatingips",
                                     page_size=page_size, params=params)

    def get_floating_ip(self, fip_id: str) -> FloatingIp:
        data = self._client.get(f"{self._base}/floatingips/{fip_id}")
        return data.get("floatingip", data)

    def create_floating_ip(self, body: dict[str, Any]) -> FloatingIp:
        data = self._client.post(f"{self._base}/floatingips",
                                 json={"floatingip": body})
        return data.get("floatingip", data) if data else {}

    def update_floating_ip(self, fip_id: str,
                           body: dict[str, Any]) -> FloatingIp:
        data = self._client.put(f"{self._base}/floatingips/{fip_id}",
                                json={"floatingip": body})
        return data.get("floatingip", data) if data else {}

    def delete_floating_ip(self, fip_id: str) -> None:
        self._client.delete(f"{self._base}/floatingips/{fip_id}")

    # ── security groups ────────────────────────────────────────────────

    def find_security_groups(
        self, *, params: dict[str, Any] | None = None,
    ) -> list[SecurityGroup]:
        data = self._client.get(f"{self._base}/security-groups", params=params)
        return data.get("security_groups", [])

    def find_all_security_groups(
        self, page_size: int = 1000, *,
        params: dict[str, Any] | None = None,
    ) -> list[SecurityGroup]:
        return self._client.paginate(f"{self._base}/security-groups",
                                     "security_groups",
                                     page_size=page_size, params=params)

    def get_security_group(self, sg_id: str) -> SecurityGroup:
        data = self._client.get(f"{self._base}/security-groups/{sg_id}")
        return data.get("security_group", data)

    def create_security_group(self, body: dict[str, Any]) -> SecurityGroup:
        data = self._client.post(f"{self._base}/security-groups",
                                 json={"security_group": body})
        return data.get("security_group", data) if data else {}

    def update_security_group(self, sg_id: str,
                              body: dict[str, Any]) -> SecurityGroup:
        data = self._client.put(f"{self._base}/security-groups/{sg_id}",
                                json={"security_group": body})
        return data.get("security_group", data) if data else {}

    def delete_security_group(self, sg_id: str) -> None:
        self._client.delete(f"{self._base}/security-groups/{sg_id}")

    def create_security_group_rule(
        self, body: dict[str, Any],
    ) -> SecurityGroupRule:
        data = self._client.post(f"{self._base}/security-group-rules",
                                 json={"security_group_rule": body})
        return data.get("security_group_rule", data) if data else {}

    def delete_security_group_rule(self, rule_id: str) -> None:
        self._client.delete(f"{self._base}/security-group-rules/{rule_id}")

    def find_security_group_rules(self, *,
                                  params: dict[str, Any] | None = None,
                                  ) -> list[SecurityGroupRule]:
        """List standalone security-group rules (optionally filtered)."""
        data = self._client.get(f"{self._base}/security-group-rules",
                                params=params)
        return data.get("security_group_rules", [])

    def get_security_group_rule(self, rule_id: str) -> SecurityGroupRule:
        data = self._client.get(
            f"{self._base}/security-group-rules/{rule_id}"
        )
        return data.get("security_group_rule", data)

    # ── subnet pools ───────────────────────────────────────────────────

    def find_subnet_pools(
        self, *, params: dict[str, Any] | None = None,
    ) -> list[SubnetPool]:
        data = self._client.get(f"{self._base}/subnetpools", params=params)
        return data.get("subnetpools", [])

    def find_all_subnet_pools(
        self, page_size: int = 1000, *,
        params: dict[str, Any] | None = None,
    ) -> list[SubnetPool]:
        return self._client.paginate(f"{self._base}/subnetpools", "subnetpools",
                                     page_size=page_size, params=params)

    def get_subnet_pool(self, pool_id: str) -> SubnetPool:
        data = self._client.get(f"{self._base}/subnetpools/{pool_id}")
        return data.get("subnetpool", data)

    def create_subnet_pool(self, body: dict[str, Any]) -> SubnetPool:
        data = self._client.post(f"{self._base}/subnetpools",
                                 json={"subnetpool": body})
        return data.get("subnetpool", data) if data else {}

    def update_subnet_pool(self, pool_id: str,
                           body: dict[str, Any]) -> SubnetPool:
        data = self._client.put(f"{self._base}/subnetpools/{pool_id}",
                                json={"subnetpool": body})
        return data.get("subnetpool", data) if data else {}

    def delete_subnet_pool(self, pool_id: str) -> None:
        self._client.delete(f"{self._base}/subnetpools/{pool_id}")

    # ── trunks ─────────────────────────────────────────────────────────

    def find_trunks(self, *,
                    params: dict[str, Any] | None = None) -> list[Trunk]:
        data = self._client.get(f"{self._base}/trunks", params=params)
        return data.get("trunks", [])

    def find_all_trunks(self, page_size: int = 1000, *,
                        params: dict[str, Any] | None = None) -> list[Trunk]:
        return self._client.paginate(f"{self._base}/trunks", "trunks",
                                     page_size=page_size, params=params)

    def get_trunk(self, trunk_id: str) -> Trunk:
        data = self._client.get(f"{self._base}/trunks/{trunk_id}")
        return data.get("trunk", data)

    def create_trunk(self, body: dict[str, Any]) -> Trunk:
        data = self._client.post(f"{self._base}/trunks",
                                 json={"trunk": body})
        return data.get("trunk", data) if data else {}

    def update_trunk(self, trunk_id: str, body: dict[str, Any]) -> Trunk:
        data = self._client.put(f"{self._base}/trunks/{trunk_id}",
                                json={"trunk": body})
        return data.get("trunk", data) if data else {}

    def delete_trunk(self, trunk_id: str) -> None:
        self._client.delete(f"{self._base}/trunks/{trunk_id}")

    def get_trunk_subports(self, trunk_id: str) -> list[dict]:
        data = self._client.get(f"{self._base}/trunks/{trunk_id}/get_subports")
        return data.get("sub_ports", []) if data else []

    def add_trunk_subports(self, trunk_id: str,
                           sub_ports: list[dict[str, Any]]) -> dict | None:
        return self._client.put(
            f"{self._base}/trunks/{trunk_id}/add_subports",
            json={"sub_ports": sub_ports},
        )

    def remove_trunk_subports(self, trunk_id: str,
                              sub_ports: list[dict[str, Any]]) -> dict | None:
        return self._client.put(
            f"{self._base}/trunks/{trunk_id}/remove_subports",
            json={"sub_ports": sub_ports},
        )

    # ── QoS policies + rules ───────────────────────────────────────────

    def find_qos_policies(
        self, *, params: dict[str, Any] | None = None,
    ) -> list[QosPolicy]:
        data = self._client.get(f"{self._base}/qos/policies", params=params)
        return data.get("policies", [])

    def find_all_qos_policies(
        self, page_size: int = 1000, *,
        params: dict[str, Any] | None = None,
    ) -> list[QosPolicy]:
        return self._client.paginate(f"{self._base}/qos/policies", "policies",
                                     page_size=page_size, params=params)

    def get_qos_policy(self, policy_id: str) -> QosPolicy:
        data = self._client.get(f"{self._base}/qos/policies/{policy_id}")
        return data.get("policy", data)

    def create_qos_policy(self, body: dict[str, Any]) -> QosPolicy:
        data = self._client.post(f"{self._base}/qos/policies",
                                 json={"policy": body})
        return data.get("policy", data) if data else {}

    def update_qos_policy(self, policy_id: str,
                          body: dict[str, Any]) -> QosPolicy:
        data = self._client.put(f"{self._base}/qos/policies/{policy_id}",
                                json={"policy": body})
        return data.get("policy", data) if data else {}

    def delete_qos_policy(self, policy_id: str) -> None:
        self._client.delete(f"{self._base}/qos/policies/{policy_id}")

    def find_qos_rules(self, policy_id: str, rule_type: str) -> list[QosRule]:
        """``rule_type`` is the plural segment
        (``bandwidth_limit_rules``, ``dscp_marking_rules``,
        ``minimum_bandwidth_rules``, ``minimum_packet_rate_rules``)."""
        data = self._client.get(
            f"{self._base}/qos/policies/{policy_id}/{rule_type}"
        )
        return data.get(rule_type, [])

    def create_qos_rule(self, policy_id: str, rule_type: str,
                        body: dict[str, Any]) -> QosRule:
        singular = rule_type[:-1]  # strip plural "s"
        data = self._client.post(
            f"{self._base}/qos/policies/{policy_id}/{rule_type}",
            json={singular: body},
        )
        return data.get(singular, data) if data else {}

    def delete_qos_rule(self, policy_id: str, rule_type: str,
                        rule_id: str) -> None:
        self._client.delete(
            f"{self._base}/qos/policies/{policy_id}/{rule_type}/{rule_id}"
        )

    def get_qos_rule(self, policy_id: str, rule_type: str,
                     rule_id: str) -> QosRule:
        singular = rule_type[:-1]
        data = self._client.get(
            f"{self._base}/qos/policies/{policy_id}/{rule_type}/{rule_id}"
        )
        return data.get(singular, data)

    def update_qos_rule(self, policy_id: str, rule_type: str,
                        rule_id: str, body: dict[str, Any]) -> QosRule:
        singular = rule_type[:-1]
        data = self._client.put(
            f"{self._base}/qos/policies/{policy_id}/{rule_type}/{rule_id}",
            json={singular: body},
        )
        return data.get(singular, data) if data else {}

    # ── agents (admin) ─────────────────────────────────────────────────

    def find_agents(self, *,
                    params: dict[str, Any] | None = None) -> list[Agent]:
        data = self._client.get(f"{self._base}/agents", params=params)
        return data.get("agents", [])

    def get_agent(self, agent_id: str) -> Agent:
        data = self._client.get(f"{self._base}/agents/{agent_id}")
        return data.get("agent", data)

    def update_agent(self, agent_id: str, body: dict[str, Any]) -> Agent:
        data = self._client.put(f"{self._base}/agents/{agent_id}",
                                json={"agent": body})
        return data.get("agent", data) if data else {}

    def delete_agent(self, agent_id: str) -> None:
        self._client.delete(f"{self._base}/agents/{agent_id}")

    # ── RBAC policies ──────────────────────────────────────────────────

    def find_rbac_policies(
        self, *, params: dict[str, Any] | None = None,
    ) -> list[RbacPolicy]:
        data = self._client.get(f"{self._base}/rbac-policies", params=params)
        return data.get("rbac_policies", [])

    def get_rbac_policy(self, rbac_id: str) -> RbacPolicy:
        data = self._client.get(f"{self._base}/rbac-policies/{rbac_id}")
        return data.get("rbac_policy", data)

    def create_rbac_policy(self, body: dict[str, Any]) -> RbacPolicy:
        data = self._client.post(f"{self._base}/rbac-policies",
                                 json={"rbac_policy": body})
        return data.get("rbac_policy", data) if data else {}

    def update_rbac_policy(self, rbac_id: str,
                           body: dict[str, Any]) -> RbacPolicy:
        data = self._client.put(f"{self._base}/rbac-policies/{rbac_id}",
                                json={"rbac_policy": body})
        return data.get("rbac_policy", data) if data else {}

    def delete_rbac_policy(self, rbac_id: str) -> None:
        self._client.delete(f"{self._base}/rbac-policies/{rbac_id}")

    # ── segments ───────────────────────────────────────────────────────

    def find_segments(self, *,
                      params: dict[str, Any] | None = None) -> list[Segment]:
        data = self._client.get(f"{self._base}/segments", params=params)
        return data.get("segments", [])

    def get_segment(self, segment_id: str) -> Segment:
        data = self._client.get(f"{self._base}/segments/{segment_id}")
        return data.get("segment", data)

    def create_segment(self, body: dict[str, Any]) -> Segment:
        data = self._client.post(f"{self._base}/segments",
                                 json={"segment": body})
        return data.get("segment", data) if data else {}

    def update_segment(self, segment_id: str,
                       body: dict[str, Any]) -> Segment:
        data = self._client.put(f"{self._base}/segments/{segment_id}",
                                json={"segment": body})
        return data.get("segment", data) if data else {}

    def delete_segment(self, segment_id: str) -> None:
        self._client.delete(f"{self._base}/segments/{segment_id}")

    # ── auto-allocated topology ────────────────────────────────────────

    def get_auto_allocated_topology(
        self, scope: str, *, dry_run: bool = False,
    ) -> AutoAllocatedTopology:
        """``scope`` is a project UUID or ``"null"`` for the current project.
        With ``dry_run=True`` Neutron only validates, it does not create."""
        params: dict[str, Any] = {"fields": "dry-run"} if dry_run else {}
        data = self._client.get(
            f"{self._base}/auto-allocated-topology/{scope}",
            params=params or None,
        )
        return data.get("auto_allocated_topology", data)

    def delete_auto_allocated_topology(self, scope: str) -> None:
        self._client.delete(f"{self._base}/auto-allocated-topology/{scope}")

    # ── quotas ─────────────────────────────────────────────────────────

    def find_quotas(self) -> list[dict]:
        """All quota entries visible to the caller (admin)."""
        data = self._client.get(f"{self._base}/quotas")
        q = data.get("quotas", [])
        return q if isinstance(q, list) else []

    def get_quota(self, project_id: str) -> dict:
        data = self._client.get(f"{self._base}/quotas/{project_id}")
        return data.get("quota", data)

    def get_quota_details(self, project_id: str) -> dict:
        """Quota with ``used`` / ``reserved`` / ``limit`` per resource.

        Exposes the ``/quotas/{id}/details`` endpoint that ``find_quotas`` /
        ``get_quota`` do not — needed by ``orca doctor`` to report headroom.
        """
        data = self._client.get(f"{self._base}/quotas/{project_id}/details")
        return data.get("quota", data)

    # ══════════════════════════════════════════════════════════════════
    #  2026-04-28 audit catch-up (lots 2-12) — OSC-parity Neutron
    #  resources. Single CRUD pattern: list / show / create / update /
    #  delete plus a handful of action endpoints. All ressources below
    #  follow the "envelope is the singular noun" wrapping convention.
    # ══════════════════════════════════════════════════════════════════

    # ── address groups ────────────────────────────────────────────────

    def find_address_groups(self, *,
                            params: dict[str, Any] | None = None) -> list[dict]:
        data = self._client.get(f"{self._base}/address-groups", params=params)
        return data.get("address_groups", [])

    def get_address_group(self, ag_id: str) -> dict:
        data = self._client.get(f"{self._base}/address-groups/{ag_id}")
        return data.get("address_group", data)

    def create_address_group(self, body: dict[str, Any]) -> dict:
        data = self._client.post(f"{self._base}/address-groups",
                                 json={"address_group": body})
        return data.get("address_group", data) if data else {}

    def update_address_group(self, ag_id: str,
                             body: dict[str, Any]) -> dict:
        data = self._client.put(f"{self._base}/address-groups/{ag_id}",
                                json={"address_group": body})
        return data.get("address_group", data) if data else {}

    def delete_address_group(self, ag_id: str) -> None:
        self._client.delete(f"{self._base}/address-groups/{ag_id}")

    def add_addresses_to_group(self, ag_id: str, addresses: list[str]) -> dict:
        data = self._client.put(
            f"{self._base}/address-groups/{ag_id}/add_addresses",
            json={"addresses": addresses},
        )
        return data.get("address_group", data) if data else {}

    def remove_addresses_from_group(self, ag_id: str,
                                     addresses: list[str]) -> dict:
        data = self._client.put(
            f"{self._base}/address-groups/{ag_id}/remove_addresses",
            json={"addresses": addresses},
        )
        return data.get("address_group", data) if data else {}

    # ── address scopes ────────────────────────────────────────────────

    def find_address_scopes(self, *,
                            params: dict[str, Any] | None = None) -> list[dict]:
        data = self._client.get(f"{self._base}/address-scopes", params=params)
        return data.get("address_scopes", [])

    def get_address_scope(self, as_id: str) -> dict:
        data = self._client.get(f"{self._base}/address-scopes/{as_id}")
        return data.get("address_scope", data)

    def create_address_scope(self, body: dict[str, Any]) -> dict:
        data = self._client.post(f"{self._base}/address-scopes",
                                 json={"address_scope": body})
        return data.get("address_scope", data) if data else {}

    def update_address_scope(self, as_id: str,
                             body: dict[str, Any]) -> dict:
        data = self._client.put(f"{self._base}/address-scopes/{as_id}",
                                json={"address_scope": body})
        return data.get("address_scope", data) if data else {}

    def delete_address_scope(self, as_id: str) -> None:
        self._client.delete(f"{self._base}/address-scopes/{as_id}")

    # ── floating IP port forwarding ───────────────────────────────────

    def find_port_forwardings(self, fip_id: str, *,
                              params: dict[str, Any] | None = None,
                              ) -> list[dict]:
        data = self._client.get(
            f"{self._base}/floatingips/{fip_id}/port_forwardings",
            params=params,
        )
        return data.get("port_forwardings", [])

    def get_port_forwarding(self, fip_id: str, pf_id: str) -> dict:
        data = self._client.get(
            f"{self._base}/floatingips/{fip_id}/port_forwardings/{pf_id}"
        )
        return data.get("port_forwarding", data)

    def create_port_forwarding(self, fip_id: str,
                               body: dict[str, Any]) -> dict:
        data = self._client.post(
            f"{self._base}/floatingips/{fip_id}/port_forwardings",
            json={"port_forwarding": body},
        )
        return data.get("port_forwarding", data) if data else {}

    def update_port_forwarding(self, fip_id: str, pf_id: str,
                               body: dict[str, Any]) -> dict:
        data = self._client.put(
            f"{self._base}/floatingips/{fip_id}/port_forwardings/{pf_id}",
            json={"port_forwarding": body},
        )
        return data.get("port_forwarding", data) if data else {}

    def delete_port_forwarding(self, fip_id: str, pf_id: str) -> None:
        self._client.delete(
            f"{self._base}/floatingips/{fip_id}/port_forwardings/{pf_id}"
        )

    # ── metering labels + rules ───────────────────────────────────────

    def find_metering_labels(self, *,
                             params: dict[str, Any] | None = None,
                             ) -> list[dict]:
        data = self._client.get(f"{self._base}/metering/metering-labels",
                                params=params)
        return data.get("metering_labels", [])

    def get_metering_label(self, label_id: str) -> dict:
        data = self._client.get(
            f"{self._base}/metering/metering-labels/{label_id}"
        )
        return data.get("metering_label", data)

    def create_metering_label(self, body: dict[str, Any]) -> dict:
        data = self._client.post(
            f"{self._base}/metering/metering-labels",
            json={"metering_label": body},
        )
        return data.get("metering_label", data) if data else {}

    def delete_metering_label(self, label_id: str) -> None:
        self._client.delete(
            f"{self._base}/metering/metering-labels/{label_id}"
        )

    def find_metering_label_rules(self, *,
                                  params: dict[str, Any] | None = None,
                                  ) -> list[dict]:
        data = self._client.get(
            f"{self._base}/metering/metering-label-rules", params=params,
        )
        return data.get("metering_label_rules", [])

    def get_metering_label_rule(self, rule_id: str) -> dict:
        data = self._client.get(
            f"{self._base}/metering/metering-label-rules/{rule_id}"
        )
        return data.get("metering_label_rule", data)

    def create_metering_label_rule(self, body: dict[str, Any]) -> dict:
        data = self._client.post(
            f"{self._base}/metering/metering-label-rules",
            json={"metering_label_rule": body},
        )
        return data.get("metering_label_rule", data) if data else {}

    def delete_metering_label_rule(self, rule_id: str) -> None:
        self._client.delete(
            f"{self._base}/metering/metering-label-rules/{rule_id}"
        )

    # ── network flavor + service profile ──────────────────────────────

    def find_network_flavors(self, *,
                             params: dict[str, Any] | None = None,
                             ) -> list[dict]:
        data = self._client.get(f"{self._base}/flavors", params=params)
        return data.get("flavors", [])

    def get_network_flavor(self, flavor_id: str) -> dict:
        data = self._client.get(f"{self._base}/flavors/{flavor_id}")
        return data.get("flavor", data)

    def create_network_flavor(self, body: dict[str, Any]) -> dict:
        data = self._client.post(f"{self._base}/flavors",
                                 json={"flavor": body})
        return data.get("flavor", data) if data else {}

    def update_network_flavor(self, flavor_id: str,
                              body: dict[str, Any]) -> dict:
        data = self._client.put(f"{self._base}/flavors/{flavor_id}",
                                json={"flavor": body})
        return data.get("flavor", data) if data else {}

    def delete_network_flavor(self, flavor_id: str) -> None:
        self._client.delete(f"{self._base}/flavors/{flavor_id}")

    def add_flavor_profile(self, flavor_id: str,
                           service_profile_id: str) -> None:
        self._client.post(
            f"{self._base}/flavors/{flavor_id}/service_profiles",
            json={"service_profile": {"id": service_profile_id}},
        )

    def remove_flavor_profile(self, flavor_id: str,
                              service_profile_id: str) -> None:
        self._client.delete(
            f"{self._base}/flavors/{flavor_id}/service_profiles/{service_profile_id}"
        )

    def find_service_profiles(self) -> list[dict]:
        data = self._client.get(f"{self._base}/service_profiles")
        return data.get("service_profiles", [])

    def get_service_profile(self, sp_id: str) -> dict:
        data = self._client.get(f"{self._base}/service_profiles/{sp_id}")
        return data.get("service_profile", data)

    def create_service_profile(self, body: dict[str, Any]) -> dict:
        data = self._client.post(f"{self._base}/service_profiles",
                                 json={"service_profile": body})
        return data.get("service_profile", data) if data else {}

    def update_service_profile(self, sp_id: str,
                               body: dict[str, Any]) -> dict:
        data = self._client.put(f"{self._base}/service_profiles/{sp_id}",
                                json={"service_profile": body})
        return data.get("service_profile", data) if data else {}

    def delete_service_profile(self, sp_id: str) -> None:
        self._client.delete(f"{self._base}/service_profiles/{sp_id}")

    # ── network segment ranges (admin SDN) ────────────────────────────

    def find_segment_ranges(self, *,
                            params: dict[str, Any] | None = None,
                            ) -> list[dict]:
        data = self._client.get(f"{self._base}/network_segment_ranges",
                                params=params)
        return data.get("network_segment_ranges", [])

    def get_segment_range(self, sr_id: str) -> dict:
        data = self._client.get(
            f"{self._base}/network_segment_ranges/{sr_id}"
        )
        return data.get("network_segment_range", data)

    def create_segment_range(self, body: dict[str, Any]) -> dict:
        data = self._client.post(
            f"{self._base}/network_segment_ranges",
            json={"network_segment_range": body},
        )
        return data.get("network_segment_range", data) if data else {}

    def update_segment_range(self, sr_id: str,
                             body: dict[str, Any]) -> dict:
        data = self._client.put(
            f"{self._base}/network_segment_ranges/{sr_id}",
            json={"network_segment_range": body},
        )
        return data.get("network_segment_range", data) if data else {}

    def delete_segment_range(self, sr_id: str) -> None:
        self._client.delete(
            f"{self._base}/network_segment_ranges/{sr_id}"
        )

    # ── L3 conntrack helpers (per-router) ─────────────────────────────

    def find_conntrack_helpers(self, router_id: str) -> list[dict]:
        data = self._client.get(
            f"{self._base}/routers/{router_id}/conntrack_helpers"
        )
        return data.get("conntrack_helpers", [])

    def get_conntrack_helper(self, router_id: str, ch_id: str) -> dict:
        data = self._client.get(
            f"{self._base}/routers/{router_id}/conntrack_helpers/{ch_id}"
        )
        return data.get("conntrack_helper", data)

    def create_conntrack_helper(self, router_id: str,
                                body: dict[str, Any]) -> dict:
        data = self._client.post(
            f"{self._base}/routers/{router_id}/conntrack_helpers",
            json={"conntrack_helper": body},
        )
        return data.get("conntrack_helper", data) if data else {}

    def update_conntrack_helper(self, router_id: str, ch_id: str,
                                body: dict[str, Any]) -> dict:
        data = self._client.put(
            f"{self._base}/routers/{router_id}/conntrack_helpers/{ch_id}",
            json={"conntrack_helper": body},
        )
        return data.get("conntrack_helper", data) if data else {}

    def delete_conntrack_helper(self, router_id: str, ch_id: str) -> None:
        self._client.delete(
            f"{self._base}/routers/{router_id}/conntrack_helpers/{ch_id}"
        )

    # ── router NDP proxy (per-router) ─────────────────────────────────

    def find_ndp_proxies(self, *,
                         params: dict[str, Any] | None = None) -> list[dict]:
        data = self._client.get(f"{self._base}/ndp_proxies", params=params)
        return data.get("ndp_proxies", [])

    def get_ndp_proxy(self, ndp_id: str) -> dict:
        data = self._client.get(f"{self._base}/ndp_proxies/{ndp_id}")
        return data.get("ndp_proxy", data)

    def create_ndp_proxy(self, body: dict[str, Any]) -> dict:
        data = self._client.post(f"{self._base}/ndp_proxies",
                                 json={"ndp_proxy": body})
        return data.get("ndp_proxy", data) if data else {}

    def update_ndp_proxy(self, ndp_id: str, body: dict[str, Any]) -> dict:
        data = self._client.put(f"{self._base}/ndp_proxies/{ndp_id}",
                                json={"ndp_proxy": body})
        return data.get("ndp_proxy", data) if data else {}

    def delete_ndp_proxy(self, ndp_id: str) -> None:
        self._client.delete(f"{self._base}/ndp_proxies/{ndp_id}")

    # ── local IP + associations (Yoga+) ───────────────────────────────

    def find_local_ips(self, *,
                       params: dict[str, Any] | None = None) -> list[dict]:
        data = self._client.get(f"{self._base}/local_ips", params=params)
        return data.get("local_ips", [])

    def get_local_ip(self, lip_id: str) -> dict:
        data = self._client.get(f"{self._base}/local_ips/{lip_id}")
        return data.get("local_ip", data)

    def create_local_ip(self, body: dict[str, Any]) -> dict:
        data = self._client.post(f"{self._base}/local_ips",
                                 json={"local_ip": body})
        return data.get("local_ip", data) if data else {}

    def update_local_ip(self, lip_id: str, body: dict[str, Any]) -> dict:
        data = self._client.put(f"{self._base}/local_ips/{lip_id}",
                                json={"local_ip": body})
        return data.get("local_ip", data) if data else {}

    def delete_local_ip(self, lip_id: str) -> None:
        self._client.delete(f"{self._base}/local_ips/{lip_id}")

    def find_local_ip_associations(self, lip_id: str) -> list[dict]:
        data = self._client.get(
            f"{self._base}/local_ips/{lip_id}/port_associations"
        )
        return data.get("port_associations", [])

    def create_local_ip_association(self, lip_id: str,
                                     body: dict[str, Any]) -> dict:
        data = self._client.post(
            f"{self._base}/local_ips/{lip_id}/port_associations",
            json={"port_association": body},
        )
        return data.get("port_association", data) if data else {}

    def delete_local_ip_association(self, lip_id: str, port_id: str) -> None:
        self._client.delete(
            f"{self._base}/local_ips/{lip_id}/port_associations/{port_id}"
        )

    # ── IP availability (admin) ───────────────────────────────────────

    def find_ip_availabilities(self, *,
                               params: dict[str, Any] | None = None,
                               ) -> list[dict]:
        data = self._client.get(
            f"{self._base}/network-ip-availabilities", params=params,
        )
        return data.get("network_ip_availabilities", [])

    def get_ip_availability(self, network_id: str) -> dict:
        data = self._client.get(
            f"{self._base}/network-ip-availabilities/{network_id}"
        )
        return data.get("network_ip_availability", data)

    # ── agent network/router bindings ─────────────────────────────────

    def add_network_to_dhcp_agent(self, agent_id: str,
                                  network_id: str) -> None:
        self._client.post(
            f"{self._base}/agents/{agent_id}/dhcp-networks",
            json={"network_id": network_id},
        )

    def remove_network_from_dhcp_agent(self, agent_id: str,
                                       network_id: str) -> None:
        self._client.delete(
            f"{self._base}/agents/{agent_id}/dhcp-networks/{network_id}"
        )

    def add_router_to_l3_agent(self, agent_id: str, router_id: str) -> None:
        self._client.post(
            f"{self._base}/agents/{agent_id}/l3-routers",
            json={"router_id": router_id},
        )

    def remove_router_from_l3_agent(self, agent_id: str,
                                    router_id: str) -> None:
        self._client.delete(
            f"{self._base}/agents/{agent_id}/l3-routers/{router_id}"
        )

    # ── subnet pool & trunk metadata removal (lot 12) ─────────────────

    def remove_subnet_pool_prefixes(self, pool_id: str,
                                    prefixes: list[str]) -> dict:
        """Remove address prefixes from a subnet pool."""
        # Subnet pools don't expose a direct "remove" endpoint — Neutron
        # expects a PUT with the full new list. The caller computes the
        # difference; we just forward.
        data = self._client.put(
            f"{self._base}/subnetpools/{pool_id}",
            json={"subnetpool": {"prefixes": prefixes}},
        )
        return data.get("subnetpool", data) if data else {}
