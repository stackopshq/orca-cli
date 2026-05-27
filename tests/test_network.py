"""Tests for ``orca network`` commands."""

from __future__ import annotations

from orca_cli.core.config import save_profile, set_active_profile

# ── Helpers ────────────────────────────────────────────────────────────────

NET_ID = "11112222-3333-4444-5555-666677778888"
SUB_ID = "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
PORT_ID = "22223333-4444-5555-6666-777788889999"
RTR_ID = "33334444-5555-6666-7777-888899990000"


def _net(net_id=NET_ID, name="my-net", status="ACTIVE"):
    return {
        "id": net_id, "name": name, "status": status,
        "subnets": [SUB_ID], "router:external": False, "shared": False,
        "admin_state_up": True, "mtu": 1500,
        "availability_zones": ["az1"],
        "created_at": "2025-01-01", "updated_at": "2025-01-02",
    }


def _subnet(sub_id=SUB_ID, name="my-sub", cidr="10.0.0.0/24"):
    return {
        "id": sub_id, "name": name, "cidr": cidr,
        "ip_version": 4, "gateway_ip": "10.0.0.1",
        "enable_dhcp": True, "dns_nameservers": ["8.8.8.8"],
        "allocation_pools": [{"start": "10.0.0.10", "end": "10.0.0.200"}],
        "network_id": NET_ID, "created_at": "2025-01-01",
    }


def _port(port_id=PORT_ID, name="my-port", status="ACTIVE"):
    return {
        "id": port_id, "name": name, "status": status,
        "mac_address": "fa:16:3e:aa:bb:cc",
        "fixed_ips": [{"ip_address": "10.0.0.5", "subnet_id": SUB_ID}],
        "device_owner": "compute:nova", "device_id": "srv-1",
        "admin_state_up": True, "network_id": NET_ID,
        "security_groups": ["sg-1"], "created_at": "2025-01-01",
    }


def _router(rtr_id=RTR_ID, name="my-rtr", status="ACTIVE"):
    return {
        "id": rtr_id, "name": name, "status": status,
        "admin_state_up": True,
        "external_gateway_info": {"network_id": NET_ID},
        "routes": [], "created_at": "2025-01-01",
    }


def _setup_mock(mock_client):
    mock_client.network_url = "https://neutron.example.com"
    mock_client.compute_url = "https://nova.example.com/v2.1"

    posted = {}
    put_data = {}
    deleted = []

    def _get(url, **kwargs):
        # Network detail
        if f"networks/{NET_ID}" in url:
            return {"network": _net()}
        if "/networks" in url:
            return {"networks": [_net()]}
        # Subnet detail
        if f"subnets/{SUB_ID}" in url:
            return {"subnet": _subnet()}
        if "/subnets" in url:
            return {"subnets": [_subnet()]}
        # Port detail
        if f"ports/{PORT_ID}" in url:
            return {"port": _port()}
        if "/ports" in url:
            return {"ports": [_port()]}
        # Router detail
        if f"routers/{RTR_ID}" in url:
            return {"router": _router()}
        if "/routers" in url:
            return {"routers": [_router()]}
        # Servers (for topology)
        if "servers/detail" in url:
            return {"servers": [{"id": "srv-1", "name": "web-1"}]}
        return {}

    def _post(url, **kwargs):
        body = kwargs.get("json", {})
        posted.update(body)
        if "/networks" in url:
            return {"network": {"id": "new-net", "name": "new"}}
        if "/subnets" in url:
            return {"subnet": {"id": "new-sub", "name": "new"}}
        if "/ports" in url:
            return {"port": {"id": "new-port", "fixed_ips": [{"ip_address": "10.0.0.99"}]}}
        if "/routers" in url:
            return {"router": {"id": "new-rtr", "name": "new"}}
        return {}

    def _put(url, **kwargs):
        body = kwargs.get("json", {})
        put_data["url"] = url
        put_data.update(body)

    def _delete(url, **kwargs):
        deleted.append(url)

    mock_client.get = _get
    mock_client.post = _post
    mock_client.put = _put
    mock_client.delete = _delete

    return {"posted": posted, "put_data": put_data, "deleted": deleted}


# ══════════════════════════════════════════════════════════════════════════
#  Networks
# ══════════════════════════════════════════════════════════════════════════


class TestNetworks:

    def test_list(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "list"])
        assert result.exit_code == 0
        assert "my-n" in result.output

    def test_list_empty(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.network_url = "https://neutron.example.com"
        mock_client.get = lambda url, **kw: {"networks": []}

        result = invoke(["network", "list"])
        assert result.exit_code == 0
        assert "No networks found" in result.output

    def test_show(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "show", NET_ID])
        assert result.exit_code == 0
        assert "my-net" in result.output

    def test_create(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)

        result = invoke(["network", "create", "new-net"])
        assert result.exit_code == 0
        assert "created" in result.output.lower()
        assert state["posted"]["network"]["name"] == "new-net"

    def test_update(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "update", NET_ID, "--name", "renamed"])
        assert result.exit_code == 0
        assert "updated" in result.output.lower()

    def test_update_nothing(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "update", NET_ID])
        assert result.exit_code == 0
        assert "Nothing" in result.output

    def test_delete(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "delete", NET_ID, "-y"])
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()


# ══════════════════════════════════════════════════════════════════════════
#  Subnets
# ══════════════════════════════════════════════════════════════════════════


class TestSubnets:

    def test_subnet_list(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "subnet-list"])
        assert result.exit_code == 0
        assert "10.0" in result.output

    def test_subnet_show(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "subnet-show", SUB_ID])
        assert result.exit_code == 0
        assert "10.0.0.0/24" in result.output

    def test_subnet_create(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "subnet-create", "new-sub",
                         "--network-id", NET_ID, "--cidr", "10.0.1.0/24"])
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_subnet_create_with_options(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)

        result = invoke(["network", "subnet-create", "v6-sub",
                         "--network-id", NET_ID, "--cidr", "fd00::/64",
                         "--ip-version", "6", "--gateway", "fd00::1",
                         "--dns", "8.8.8.8", "--dns", "8.8.4.4"])
        assert result.exit_code == 0
        sub = state["posted"]["subnet"]
        assert sub["ip_version"] == 6
        assert sub["dns_nameservers"] == ["8.8.8.8", "8.8.4.4"]

    def test_subnet_delete(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "subnet-delete", SUB_ID, "-y"])
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()


class TestSubnetInspect:
    """``orca network subnet inspect`` — cross-references subnet + IP
    availability + ports + server names."""

    SUB = "11111111-1111-1111-1111-111111111111"
    NET = "22222222-2222-2222-2222-222222222222"
    SRV = "33333333-3333-3333-3333-333333333333"
    PORT = "44444444-4444-4444-4444-444444444444"
    DHCP_PORT = "55555555-5555-5555-5555-555555555555"

    def _wire(self, mock_client):
        mock_client.network_url = "https://neutron.example.com"
        mock_client.compute_url = "https://nova.example.com/v2.1"

        def _get(url, **kw):
            if f"/subnets/{self.SUB}" in url:
                return {"subnet": {
                    "id": self.SUB, "name": "audit-sub",
                    "cidr": "10.0.0.0/24", "gateway_ip": "10.0.0.1",
                    "ip_version": 4, "enable_dhcp": True,
                    "dns_nameservers": ["8.8.8.8"],
                    "allocation_pools": [{"start": "10.0.0.2", "end": "10.0.0.254"}],
                    "network_id": self.NET,
                }}
            if "/network-ip-availabilities/" in url:
                return {"network_ip_availability": {
                    "network_id": self.NET,
                    "subnet_ip_availability": [{
                        "subnet_id": self.SUB, "used_ips": 2, "total_ips": 253,
                        "cidr": "10.0.0.0/24",
                    }],
                }}
            if "/ports" in url and "subnet_id" in str(kw.get("params", {})):
                return {"ports": [
                    {"id": self.DHCP_PORT, "status": "ACTIVE",
                     "mac_address": "fa:16:3e:00:00:01",
                     "device_owner": "network:distributed",
                     "device_id": "ovnmeta-1",
                     "fixed_ips": [{"ip_address": "10.0.0.2", "subnet_id": self.SUB}]},
                    {"id": self.PORT, "status": "ACTIVE",
                     "mac_address": "fa:16:3e:00:00:02",
                     "device_owner": "compute:nova",
                     "device_id": self.SRV,
                     "fixed_ips": [{"ip_address": "10.0.0.42", "subnet_id": self.SUB}]},
                ]}
            if f"/servers/{self.SRV}" in url:
                return {"server": {"id": self.SRV, "name": "audit-vm"}}
            return {}
        mock_client.get = _get

    def test_inspect_renders_subnet_ip_usage_and_ports(self, invoke, config_dir,
                                                       mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        self._wire(mock_client)
        result = invoke(["network", "subnet", "inspect", self.SUB])
        assert result.exit_code == 0
        # Subnet header
        assert "audit-sub" in result.output
        assert "10.0.0.0/24" in result.output
        # IP availability surfaced
        assert "2 / 253" in result.output
        # Both ports listed with their IPs
        assert "10.0.0.2" in result.output
        assert "10.0.0.42" in result.output
        # compute:* port resolved to server name
        assert "audit-vm" in result.output
        # network:* port shown with the owner suffix (after the colon)
        assert "distributed" in result.output

    def test_inspect_handles_missing_ip_availability(self, invoke, config_dir,
                                                      mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.network_url = "https://neutron.example.com"
        mock_client.compute_url = "https://nova.example.com/v2.1"

        def _get(url, **kw):
            if f"/subnets/{self.SUB}" in url:
                return {"subnet": {"id": self.SUB, "name": "x",
                                    "cidr": "10.0.0.0/24",
                                    "network_id": self.NET, "ip_version": 4,
                                    "enable_dhcp": False}}
            if "/network-ip-availabilities/" in url:
                from orca_cli.core.exceptions import APIError
                raise APIError(404, "extension not enabled")
            if "/ports" in url:
                return {"ports": []}
            return {}
        mock_client.get = _get
        result = invoke(["network", "subnet", "inspect", self.SUB])
        assert result.exit_code == 0
        assert "extension not exposed" in result.output

    def test_inspect_rejects_unknown_subnet(self, invoke, config_dir,
                                             mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.network_url = "https://neutron.example.com"
        mock_client.compute_url = "https://nova.example.com/v2.1"
        mock_client.get = lambda url, **kw: {}  # empty body → no subnet
        result = invoke(["network", "subnet", "inspect", self.SUB])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()


class TestPortListFilters:
    """New ``--subnet`` / ``--device-owner`` / ``--device-id`` filters."""

    NET = "22222222-2222-2222-2222-222222222222"
    SUB = "11111111-1111-1111-1111-111111111111"

    def test_filter_by_subnet_uses_fixed_ips_param(self, invoke, mock_client):
        from unittest.mock import MagicMock
        mock_client.network_url = "https://neutron.example.com"
        mock_client.get = MagicMock(return_value={"ports": []})
        result = invoke(["network", "port", "list", "--subnet", self.SUB])
        assert result.exit_code == 0
        params = mock_client.get.call_args.kwargs.get("params")
        assert params == {"fixed_ips": f"subnet_id={self.SUB}"}

    def test_filter_by_device_owner_and_device_id(self, invoke, mock_client):
        from unittest.mock import MagicMock
        mock_client.network_url = "https://neutron.example.com"
        mock_client.get = MagicMock(return_value={"ports": []})
        invoke(["network", "port", "list",
                "--device-owner", "compute:nova",
                "--device-id", "srv-1"])
        params = mock_client.get.call_args.kwargs.get("params")
        assert params["device_owner"] == "compute:nova"
        assert params["device_id"] == "srv-1"

    def test_no_filter_sends_no_params(self, invoke, mock_client):
        from unittest.mock import MagicMock
        mock_client.network_url = "https://neutron.example.com"
        mock_client.get = MagicMock(return_value={"ports": []})
        invoke(["network", "port", "list"])
        assert mock_client.get.call_args.kwargs.get("params") is None


# ══════════════════════════════════════════════════════════════════════════
#  Ports
# ══════════════════════════════════════════════════════════════════════════


class TestPorts:

    def test_port_list(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "port-list"])
        assert result.exit_code == 0
        assert "fa:1" in result.output

    def test_port_show(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "port-show", PORT_ID])
        assert result.exit_code == 0

    def test_port_create(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "port-create", "--network-id", NET_ID])
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_port_update(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "port-update", PORT_ID, "--name", "renamed"])
        assert result.exit_code == 0
        assert "updated" in result.output.lower()

    def test_port_delete(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "port-delete", PORT_ID, "-y"])
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()


# ══════════════════════════════════════════════════════════════════════════
#  Routers
# ══════════════════════════════════════════════════════════════════════════


class TestRouters:

    def test_router_list(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "router-list"])
        assert result.exit_code == 0
        assert "my-rtr" in result.output

    def test_router_show(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "router-show", RTR_ID])
        assert result.exit_code == 0
        assert "my-rtr" in result.output

    def test_router_create(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "router-create", "new-rtr"])
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_router_create_with_ext_net(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)

        result = invoke(["network", "router-create", "new-rtr",
                         "--external-network", NET_ID])
        assert result.exit_code == 0
        assert state["posted"]["router"]["external_gateway_info"]["network_id"] == NET_ID

    def test_router_delete(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "router-delete", RTR_ID, "-y"])
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

    def test_router_add_interface(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "router-add-interface", RTR_ID,
                         "--subnet-id", SUB_ID])
        assert result.exit_code == 0
        assert "added" in result.output.lower()

    def test_router_remove_interface(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _ = _setup_mock(mock_client)

        result = invoke(["network", "router-remove-interface", RTR_ID,
                         "--subnet-id", SUB_ID])
        assert result.exit_code == 0
        assert "removed" in result.output.lower()


# ══════════════════════════════════════════════════════════════════════════
#  Topology
# ══════════════════════════════════════════════════════════════════════════


class TestTopology:

    def test_topology(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["network", "topology"])
        assert result.exit_code == 0
        assert "my-net" in result.output
        assert "10.0.0" in result.output


# ══════════════════════════════════════════════════════════════════════════
#  Help
# ══════════════════════════════════════════════════════════════════════════


FIP_ID = "44445555-6666-7777-8888-999900001111"
RBAC_ID = "55556666-7777-8888-9999-000011112222"
SG_ID = "66667777-8888-9999-0000-111122223333"


# ══════════════════════════════════════════════════════════════════════════
#  rbac-update
# ══════════════════════════════════════════════════════════════════════════


class TestRbacUpdate:

    def test_update_target_project(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "rbac-update", RBAC_ID, "--target-project", "proj-2"])
        assert result.exit_code == 0
        assert "updated" in result.output
        assert state["put_data"]["rbac_policy"]["target_tenant"] == "proj-2"

    def test_update_wildcard(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "rbac-update", RBAC_ID, "--target-project", "*"])
        assert result.exit_code == 0
        assert state["put_data"]["rbac_policy"]["target_tenant"] == "*"

    def test_update_requires_target_project(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        result = invoke(["network", "rbac-update", RBAC_ID])
        assert result.exit_code != 0


# ══════════════════════════════════════════════════════════════════════════
#  port-unset
# ══════════════════════════════════════════════════════════════════════════


class TestPortUnset:

    def test_unset_security_group(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "port-unset", PORT_ID, "--security-group", "sg-1"])
        assert result.exit_code == 0
        assert "updated" in result.output
        # The put should have security_groups without "sg-1"
        assert "sg-1" not in state["put_data"].get("port", {}).get("security_groups", ["sg-1"])

    def test_unset_qos_policy(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "port-unset", PORT_ID, "--qos-policy"])
        assert result.exit_code == 0
        assert state["put_data"]["port"]["qos_policy_id"] is None

    def test_unset_description(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "port-unset", PORT_ID, "--description"])
        assert result.exit_code == 0
        assert state["put_data"]["port"]["description"] == ""

    def test_unset_nothing(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)
        result = invoke(["network", "port-unset", PORT_ID])
        assert result.exit_code == 0
        assert "Nothing to unset" in result.output


# ══════════════════════════════════════════════════════════════════════════
#  router-set-gateway / router-unset-gateway
# ══════════════════════════════════════════════════════════════════════════


class TestRouterGateway:

    def test_set_gateway(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "router-set-gateway", RTR_ID,
                         "--external-network", NET_ID])
        assert result.exit_code == 0
        assert "Gateway set" in result.output
        gw = state["put_data"]["router"]["external_gateway_info"]
        assert gw["network_id"] == NET_ID

    def test_set_gateway_with_snat(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "router-set-gateway", RTR_ID,
                         "--external-network", NET_ID, "--enable-snat"])
        assert result.exit_code == 0
        gw = state["put_data"]["router"]["external_gateway_info"]
        assert gw["enable_snat"] is True

    def test_unset_gateway(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "router-unset-gateway", RTR_ID])
        assert result.exit_code == 0
        assert "removed" in result.output
        assert state["put_data"]["router"]["external_gateway_info"] == {}


# ══════════════════════════════════════════════════════════════════════════
#  router static routes
# ══════════════════════════════════════════════════════════════════════════


class TestRouterRoutes:

    def test_add_route(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "router-add-route", RTR_ID,
                         "--destination", "10.1.0.0/24",
                         "--nexthop", "192.168.1.1"])
        assert result.exit_code == 0
        assert "added" in result.output
        routes = state["put_data"]["router"]["routes"]
        assert {"destination": "10.1.0.0/24", "nexthop": "192.168.1.1"} in routes

    def test_add_route_url(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        invoke(["network", "router-add-route", RTR_ID,
                "--destination", "10.1.0.0/24", "--nexthop", "192.168.1.1"])
        assert "add_extraroutes" in state["put_data"]["url"]

    def test_remove_route(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        result = invoke(["network", "router-remove-route", RTR_ID,
                         "--destination", "10.1.0.0/24",
                         "--nexthop", "192.168.1.1"])
        assert result.exit_code == 0
        assert "removed" in result.output
        routes = state["put_data"]["router"]["routes"]
        assert {"destination": "10.1.0.0/24", "nexthop": "192.168.1.1"} in routes

    def test_remove_route_url(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        state = _setup_mock(mock_client)
        invoke(["network", "router-remove-route", RTR_ID,
                "--destination", "10.1.0.0/24", "--nexthop", "192.168.1.1"])
        assert "remove_extraroutes" in state["put_data"]["url"]

    def test_add_route_requires_both_options(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        result = invoke(["network", "router-add-route", RTR_ID, "--destination", "10.0.0.0/24"])
        assert result.exit_code != 0


class TestNetworkHelp:

    def test_network_help(self, invoke):
        result = invoke(["network", "--help"])
        assert result.exit_code == 0
        for cmd in ("list", "show", "create", "delete",
                    "subnet-list", "subnet-create",
                    "port-list", "port-create",
                    "router-list", "router-create",
                    "topology", "trace"):
            assert cmd in result.output

    def test_subnet_create_help(self, invoke):
        result = invoke(["network", "subnet-create", "--help"])
        assert result.exit_code == 0
        assert "--cidr" in result.output
        assert "--dns" in result.output

    def test_trace_help(self, invoke):
        result = invoke(["network", "trace", "--help"])
        assert result.exit_code == 0
