"""Coverage tests for the Neutron audit lots 2-12 (2026-04-28).

Smoke + URL/body shape checks for the new commands and service methods.
Lots covered: address group (2), address scope (2), FIP port forwarding (3),
metering (4), network flavor + service profile (5), segment range (6),
L3 conntrack helper (7), router NDP proxy (8), local IP + association (9),
IP availability (10), agent network/router binding (11),
subnet-pool unset + trunk unset (12).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

NET = "https://neutron.example.com"

AG = "11111111-1111-1111-1111-111111111111"
AS = "22222222-2222-2222-2222-222222222222"
FIP = "33333333-3333-3333-3333-333333333333"
PF = "44444444-4444-4444-4444-444444444444"
ML = "55555555-5555-5555-5555-555555555555"
MR = "66666666-6666-6666-6666-666666666666"
NF = "77777777-7777-7777-7777-777777777777"
SP = "88888888-8888-8888-8888-888888888888"
SR = "99999999-9999-9999-9999-999999999999"
RT = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
CH = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
ND = "cccccccc-cccc-cccc-cccc-cccccccccccc"
LIP = "dddddddd-dddd-dddd-dddd-dddddddddddd"
AGENT = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
NET_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff"
ROUTER_ID = "11111111-1111-1111-1111-111111111122"
PORT_ID = "11111111-1111-1111-1111-111111111133"
POOL = "11111111-1111-1111-1111-111111111144"


@pytest.fixture(autouse=True)
def _wire(mock_client):
    mock_client.network_url = NET


# ── lot 2: address group ───────────────────────────────────────────────

class TestAddressGroup:

    def test_help(self, invoke):
        for path in (["address-group", "--help"],
                     ["address-group", "list", "--help"],
                     ["address-group", "create", "--help"],
                     ["address-group", "set", "--help"],
                     ["address-group", "unset", "--help"],
                     ["address-group", "show", "--help"],
                     ["address-group", "delete", "--help"]):
            assert invoke(path).exit_code == 0

    def test_list(self, invoke, mock_client):
        mock_client.get = MagicMock(return_value={"address_groups": [
            {"id": AG, "name": "office", "addresses": ["10.0.0.0/24"]},
        ]})
        result = invoke(["address-group", "list", "-f", "value", "-c", "Name"])
        assert result.exit_code == 0
        assert "office" in result.output
        assert "/address-groups" in mock_client.get.call_args[0][0]

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"address_group": {"id": AG, "name": "ag"}})
        invoke(["address-group", "create", "ag",
                "--address", "10.0.0.0/24", "--address", "10.1.0.0/24"])
        body = mock_client.post.call_args.kwargs["json"]["address_group"]
        assert body == {"name": "ag", "addresses": ["10.0.0.0/24", "10.1.0.0/24"]}

    def test_set_add_remove_addresses(self, invoke, mock_client):
        mock_client.put = MagicMock(return_value={"address_group": {}})
        invoke(["address-group", "set", AG,
                "--add-address", "10.2.0.0/24",
                "--remove-address", "10.0.0.0/24"])
        # Two PUTs: add_addresses + remove_addresses
        urls = [c.args[0] for c in mock_client.put.call_args_list]
        assert any("/add_addresses" in u for u in urls)
        assert any("/remove_addresses" in u for u in urls)


# ── lot 2: address scope ───────────────────────────────────────────────

class TestAddressScope:

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"address_scope": {"id": AS}})
        invoke(["address-scope", "create", "v6scope",
                "--ip-version", "6", "--shared"])
        body = mock_client.post.call_args.kwargs["json"]["address_scope"]
        assert body == {"name": "v6scope", "ip_version": 6, "shared": True}

    def test_set_name(self, invoke, mock_client):
        mock_client.put = MagicMock(return_value={"address_scope": {}})
        invoke(["address-scope", "set", AS, "--name", "renamed"])
        body = mock_client.put.call_args.kwargs["json"]["address_scope"]
        assert body == {"name": "renamed"}


# ── lot 3: floating IP port forwarding ─────────────────────────────────

class TestFipPortForwarding:

    def test_create_full(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"port_forwarding": {"id": PF}})
        invoke(["floating-ip", "port-forwarding", "create", FIP,
                "--internal-port-id", PORT_ID,
                "--internal-ip-address", "10.0.0.5",
                "--internal-port", "22",
                "--external-port", "2222"])
        body = mock_client.post.call_args.kwargs["json"]["port_forwarding"]
        assert body == {"internal_port_id": PORT_ID,
                        "internal_ip_address": "10.0.0.5",
                        "internal_port": 22, "external_port": 2222,
                        "protocol": "tcp"}
        assert f"/floatingips/{FIP}/port_forwardings" in mock_client.post.call_args.args[0]

    def test_set(self, invoke, mock_client):
        mock_client.put = MagicMock(return_value={"port_forwarding": {}})
        invoke(["floating-ip", "port-forwarding", "set", FIP, PF,
                "--external-port", "8080"])
        body = mock_client.put.call_args.kwargs["json"]["port_forwarding"]
        assert body == {"external_port": 8080}


# ── lot 4: metering ────────────────────────────────────────────────────

class TestMetering:

    def test_label_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"metering_label": {"id": ML}})
        invoke(["network", "meter", "create", "transit", "--shared"])
        body = mock_client.post.call_args.kwargs["json"]["metering_label"]
        assert body == {"name": "transit", "shared": True}

    def test_rule_create_with_excluded(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"metering_label_rule": {"id": MR}})
        invoke(["network", "meter-rule", "create",
                "--label-id", ML, "--direction", "egress",
                "--remote-ip-prefix", "10.0.0.0/8", "--excluded"])
        body = mock_client.post.call_args.kwargs["json"]["metering_label_rule"]
        assert body["metering_label_id"] == ML
        assert body["direction"] == "egress"
        assert body["remote_ip_prefix"] == "10.0.0.0/8"
        assert body["excluded"] is True


# ── lot 5: network flavor + service profile ────────────────────────────

class TestNetworkFlavor:

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"flavor": {"id": NF}})
        invoke(["network", "flavor", "create", "gold",
                "--service-type", "FIREWALL_V2"])
        body = mock_client.post.call_args.kwargs["json"]["flavor"]
        assert body == {"name": "gold", "service_type": "FIREWALL_V2", "enabled": True}

    def test_add_profile(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={})
        invoke(["network", "flavor", "add", NF, SP])
        url = mock_client.post.call_args.args[0]
        body = mock_client.post.call_args.kwargs["json"]
        assert f"/flavors/{NF}/service_profiles" in url
        assert body == {"service_profile": {"id": SP}}

    def test_remove_profile(self, invoke, mock_client):
        mock_client.delete = MagicMock(return_value=None)
        invoke(["network", "flavor", "remove", NF, SP])
        url = mock_client.delete.call_args[0][0]
        assert f"/flavors/{NF}/service_profiles/{SP}" in url


class TestServiceProfile:

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"service_profile": {"id": SP}})
        invoke(["network", "flavor-profile", "create",
                "--driver", "neutron.driver", "--metainfo", "{}"])
        body = mock_client.post.call_args.kwargs["json"]["service_profile"]
        assert body == {"enabled": True, "driver": "neutron.driver", "metainfo": "{}"}


# ── lot 6: segment range ───────────────────────────────────────────────

class TestSegmentRange:

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"network_segment_range": {"id": SR}})
        invoke(["network", "segment-range", "create", "vlan-pool",
                "--network-type", "vlan",
                "--physical-network", "physnet1",
                "--minimum", "100", "--maximum", "200"])
        body = mock_client.post.call_args.kwargs["json"]["network_segment_range"]
        assert body == {"name": "vlan-pool", "network_type": "vlan",
                        "minimum": 100, "maximum": 200, "shared": False,
                        "physical_network": "physnet1"}


# ── lot 7: L3 conntrack helper ─────────────────────────────────────────

class TestConntrackHelper:

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"conntrack_helper": {"id": CH}})
        invoke(["network", "l3-conntrack-helper", "create", RT,
                "--helper", "ftp", "--port", "21"])
        url = mock_client.post.call_args.args[0]
        body = mock_client.post.call_args.kwargs["json"]["conntrack_helper"]
        assert f"/routers/{RT}/conntrack_helpers" in url
        assert body == {"helper": "ftp", "protocol": "tcp", "port": 21}


# ── lot 8: router NDP proxy ────────────────────────────────────────────

class TestNdpProxy:

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"ndp_proxy": {"id": ND}})
        invoke(["network", "router", "ndp-proxy", "create",
                "--router-id", RT, "--port-id", PORT_ID,
                "--ip-address", "fd00::5"])
        body = mock_client.post.call_args.kwargs["json"]["ndp_proxy"]
        assert body == {"router_id": RT, "port_id": PORT_ID,
                        "ip_address": "fd00::5"}


# ── lot 9: local IP ────────────────────────────────────────────────────

class TestLocalIP:

    def test_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"local_ip": {"id": LIP}})
        invoke(["local-ip", "create", "lip1",
                "--network-id", NET_ID, "--ip-mode", "translate"])
        body = mock_client.post.call_args.kwargs["json"]["local_ip"]
        assert body == {"name": "lip1", "network_id": NET_ID, "ip_mode": "translate"}

    def test_association_create(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={"port_association": {}})
        invoke(["local-ip", "association", "create", LIP, "--port-id", PORT_ID])
        url = mock_client.post.call_args.args[0]
        body = mock_client.post.call_args.kwargs["json"]["port_association"]
        assert f"/local_ips/{LIP}/port_associations" in url
        assert body == {"fixed_port_id": PORT_ID}


# ── lot 10: IP availability ────────────────────────────────────────────

class TestIpAvailability:

    def test_list(self, invoke, mock_client):
        mock_client.get = MagicMock(return_value={"network_ip_availabilities": [
            {"network_id": NET_ID, "network_name": "ext-net",
             "total_ips": 100, "used_ips": 42},
        ]})
        result = invoke(["ip-availability", "list", "-f", "value", "-c", "Network"])
        assert result.exit_code == 0
        assert "ext-net" in result.output
        assert "/network-ip-availabilities" in mock_client.get.call_args[0][0]

    def test_show(self, invoke, mock_client):
        mock_client.get = MagicMock(return_value={"network_ip_availability": {
            "network_id": NET_ID, "network_name": "ext-net",
            "total_ips": 100, "used_ips": 42,
            "subnet_ip_availability": [{"subnet_name": "s1", "used_ips": 42,
                                         "total_ips": 100, "cidr": "10.0.0.0/24"}],
        }})
        result = invoke(["ip-availability", "show", NET_ID])
        assert result.exit_code == 0


# ── lot 11: agent bindings ─────────────────────────────────────────────

class TestAgentBindings:

    def test_add_network(self, invoke, mock_client):
        mock_client.post = MagicMock(return_value={})
        invoke(["network", "agent", "add", "network", AGENT, NET_ID])
        url = mock_client.post.call_args.args[0]
        body = mock_client.post.call_args.kwargs["json"]
        assert f"/agents/{AGENT}/dhcp-networks" in url
        assert body == {"network_id": NET_ID}

    def test_remove_router(self, invoke, mock_client):
        mock_client.delete = MagicMock(return_value=None)
        invoke(["network", "agent", "remove", "router", AGENT, ROUTER_ID])
        url = mock_client.delete.call_args[0][0]
        assert f"/agents/{AGENT}/l3-routers/{ROUTER_ID}" in url


# ── lot 12: subnet-pool unset + trunk unset ────────────────────────────

class TestSubnetPoolUnset:

    def test_unset_removes_matching_prefixes(self, invoke, mock_client):
        mock_client.get = MagicMock(return_value={"subnetpool": {
            "id": POOL, "prefixes": ["10.0.0.0/16", "10.1.0.0/16", "10.2.0.0/16"],
        }})
        mock_client.put = MagicMock(return_value={"subnetpool": {}})
        result = invoke(["subnet-pool", "unset", POOL, "--prefix", "10.1.0.0/16"])
        assert result.exit_code == 0
        body = mock_client.put.call_args.kwargs["json"]["subnetpool"]
        assert body == {"prefixes": ["10.0.0.0/16", "10.2.0.0/16"]}

    def test_unset_no_match(self, invoke, mock_client):
        mock_client.get = MagicMock(return_value={"subnetpool": {
            "id": POOL, "prefixes": ["10.0.0.0/16"],
        }})
        mock_client.put = MagicMock()
        result = invoke(["subnet-pool", "unset", POOL, "--prefix", "192.0.0.0/8"])
        assert result.exit_code == 0
        assert "nothing removed" in result.output.lower()
        mock_client.put.assert_not_called()


class TestTrunkUnset:

    def test_clear_description(self, invoke, mock_client):
        mock_client.put = MagicMock(return_value={"trunk": {}})
        invoke(["trunk", "unset", "11111111-2222-3333-4444-555555555555",
                "--description"])
        body = mock_client.put.call_args.kwargs["json"]["trunk"]
        assert body == {"description": ""}

    def test_nothing_to_unset(self, invoke, mock_client):
        from unittest.mock import MagicMock
        mock_client.put = MagicMock()
        result = invoke(["trunk", "unset", "11111111-2222-3333-4444-555555555555"])
        assert result.exit_code == 0
        assert "Nothing to unset" in result.output
        mock_client.put.assert_not_called()
