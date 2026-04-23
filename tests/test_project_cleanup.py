"""Tests for ``orca project cleanup`` helpers handling router and network deps."""

from __future__ import annotations

from unittest.mock import MagicMock

from orca_cli.commands import project as proj_mod


def _make_net_svc(monkeypatch, **attrs):
    net_svc = MagicMock()
    for k, v in attrs.items():
        setattr(net_svc, k, v)
    monkeypatch.setattr(proj_mod, "NetworkService", lambda _c: net_svc)
    return net_svc


class TestDeleteRouter:
    def test_clears_gateway_before_detaching_and_deleting(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = []

        proj_mod._delete_router(object(), "r-1")

        net.update_router.assert_called_once_with(
            "r-1", {"external_gateway_info": None}
        )
        net.delete_router.assert_called_once_with("r-1")

    def test_detaches_all_router_interface_flavors(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = [
            {"id": "p-legacy", "device_owner": "network:router_interface"},
            {"id": "p-dvr",
             "device_owner": "network:router_interface_distributed"},
            {"id": "p-ha",
             "device_owner": "network:ha_router_replicated_interface"},
        ]

        proj_mod._delete_router(object(), "r-1")

        assert net.remove_router_interface.call_count == 3
        detached = {
            c.args[1]["port_id"]
            for c in net.remove_router_interface.call_args_list
        }
        assert detached == {"p-legacy", "p-dvr", "p-ha"}

    def test_ignores_non_interface_ports(self, monkeypatch):
        """Gateway / SNAT / foreign ports must not go through remove_router_interface."""
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = [
            {"id": "p-gw", "device_owner": "network:router_gateway"},
            {"id": "p-snat", "device_owner": "network:router_centralized_snat"},
            {"id": "p-dhcp", "device_owner": "network:dhcp"},
            {"id": "p-orphan", "device_owner": ""},
        ]

        proj_mod._delete_router(object(), "r-1")

        net.remove_router_interface.assert_not_called()
        net.delete_router.assert_called_once_with("r-1")

    def test_lists_ports_by_device_id_only(self, monkeypatch):
        """Broader filter: device_owner is applied Python-side, not in the query."""
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = []

        proj_mod._delete_router(object(), "r-xyz")

        net.find_ports.assert_called_once_with(params={"device_id": "r-xyz"})

    def test_continues_when_update_router_fails(self, monkeypatch):
        """Some clouds reject gateway clear if no gateway set — must not abort."""
        net = _make_net_svc(monkeypatch)
        net.update_router.side_effect = RuntimeError("no gateway")
        net.find_ports.return_value = [
            {"id": "p1", "device_owner": "network:router_interface"},
        ]

        proj_mod._delete_router(object(), "r-1")

        net.remove_router_interface.assert_called_once_with(
            "r-1", {"port_id": "p1"}
        )
        net.delete_router.assert_called_once_with("r-1")

    def test_continues_when_find_ports_fails(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.side_effect = RuntimeError("neutron down")

        proj_mod._delete_router(object(), "r-1")

        net.remove_router_interface.assert_not_called()
        net.delete_router.assert_called_once_with("r-1")

    def test_continues_when_remove_interface_fails(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = [
            {"id": "p1", "device_owner": "network:router_interface"},
            {"id": "p2", "device_owner": "network:router_interface"},
        ]
        net.remove_router_interface.side_effect = [RuntimeError("boom"), None]

        proj_mod._delete_router(object(), "r-1")

        assert net.remove_router_interface.call_count == 2
        net.delete_router.assert_called_once_with("r-1")


class TestDeleteNetwork:
    def test_deletes_orphan_and_stale_compute_ports(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = [
            {"id": "p-orphan", "device_owner": ""},
            {"id": "p-vif", "device_owner": "compute:nova"},
            {"id": "p-dhcp", "device_owner": "network:dhcp"},
            {"id": "p-router", "device_owner": "network:router_interface"},
            {"id": "p-fip", "device_owner": "network:floatingip"},
        ]

        proj_mod._delete_network(object(), "n-1")

        deleted = {c.args[0] for c in net.delete_port.call_args_list}
        assert deleted == {"p-orphan", "p-vif"}
        net.delete.assert_called_once_with("n-1")

    def test_lists_ports_by_network_id(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = []

        proj_mod._delete_network(object(), "n-42")

        net.find_ports.assert_called_once_with(params={"network_id": "n-42"})
        net.delete.assert_called_once_with("n-42")

    def test_continues_when_port_delete_fails(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.return_value = [
            {"id": "p1", "device_owner": ""},
            {"id": "p2", "device_owner": "compute:nova"},
        ]
        net.delete_port.side_effect = [RuntimeError("boom"), None]

        proj_mod._delete_network(object(), "n-1")

        assert net.delete_port.call_count == 2
        net.delete.assert_called_once_with("n-1")

    def test_continues_when_find_ports_fails(self, monkeypatch):
        net = _make_net_svc(monkeypatch)
        net.find_ports.side_effect = RuntimeError("neutron down")

        proj_mod._delete_network(object(), "n-1")

        net.delete_port.assert_not_called()
        net.delete.assert_called_once_with("n-1")
