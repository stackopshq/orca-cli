"""Tests for ``orca quota`` command."""

from __future__ import annotations

from orca_cli.core.config import save_profile, set_active_profile

# ── Helpers ────────────────────────────────────────────────────────────────


def _setup_mock(mock_client, nova=None, cinder=None, neutron_quotas=None,
                nets=0, subnets=0, ports=0, routers=0, fips=0, sgs=0):
    mock_client.compute_url = "https://nova.example.com/v2.1"
    mock_client.volume_url = "https://cinder.example.com/v3"
    mock_client.network_url = "https://neutron.example.com"
    mock_client.project_id = "proj-1"

    nova = nova or {
        "limits": {"absolute": {
            "totalInstancesUsed": 3, "maxTotalInstances": 10,
            "totalCoresUsed": 8, "maxTotalCores": 20,
            "totalRAMUsed": 16384, "maxTotalRAMSize": 51200,
            "maxTotalKeypairs": 100,
            "totalServerGroupsUsed": 1, "maxServerGroups": 10,
        }}
    }
    cinder = cinder or {
        "limits": {"absolute": {
            "totalVolumesUsed": 5, "maxTotalVolumes": 20,
            "totalGigabytesUsed": 250, "maxTotalVolumeGigabytes": 1000,
            "totalSnapshotsUsed": 2, "maxTotalSnapshots": 10,
            "totalBackupsUsed": 1, "maxTotalBackups": 10,
            "totalBackupGigabytesUsed": 50, "maxTotalBackupGigabytes": 500,
        }}
    }
    neutron_quotas = neutron_quotas or {
        "network": 50, "subnet": 100, "port": 200,
        "router": 10, "floatingip": 20, "security_group": 50,
        "security_group_rule": 200,
    }

    def _get(url, **kwargs):
        # Nova limits
        if "/limits" in url and "nova" in url:
            return nova
        # Cinder limits
        if "/limits" in url and "cinder" in url:
            return cinder
        # Neutron quotas
        if "/quotas" in url:
            return {"quotas": [neutron_quotas]}
        # Neutron resource counts
        if "/networks" in url:
            return {"networks": [{}] * nets}
        if "/subnets" in url:
            return {"subnets": [{}] * subnets}
        if "/ports" in url:
            return {"ports": [{}] * ports}
        if "/routers" in url:
            return {"routers": [{}] * routers}
        if "/floatingips" in url:
            return {"floatingips": [{}] * fips}
        if "/security-groups" in url:
            return {"security_groups": [{}] * sgs}
        return {}

    mock_client.get = _get


# ══════════════════════════════════════════════════════════════════════════
#  quota
# ══════════════════════════════════════════════════════════════════════════


class TestQuota:

    def test_quota_basic(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client, nets=5, subnets=8, ports=30,
                    routers=2, fips=4, sgs=6)

        result = invoke(["quota"])
        assert result.exit_code == 0
        assert "Compute" in result.output
        assert "Volume" in result.output
        assert "Network" in result.output
        assert "Instances" in result.output

    def test_quota_shows_used(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["quota"])
        assert result.exit_code == 0
        assert "3" in result.output   # totalInstancesUsed
        assert "8" in result.output   # totalCoresUsed

    def test_quota_shows_limits(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client)

        result = invoke(["quota"])
        assert result.exit_code == 0
        assert "10" in result.output   # maxTotalInstances
        assert "20" in result.output   # maxTotalCores

    def test_quota_unlimited(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        nova = {"limits": {"absolute": {
            "totalInstancesUsed": 0, "maxTotalInstances": -1,
            "totalCoresUsed": 0, "maxTotalCores": -1,
            "totalRAMUsed": 0, "maxTotalRAMSize": -1,
            "maxTotalKeypairs": -1,
            "totalServerGroupsUsed": 0, "maxServerGroups": -1,
        }}}
        _setup_mock(mock_client, nova=nova)

        result = invoke(["quota"])
        assert result.exit_code == 0
        assert "unlimited" in result.output

    def test_quota_network_counts(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        _setup_mock(mock_client, nets=12, subnets=15, fips=7)

        result = invoke(["quota"])
        assert result.exit_code == 0
        assert "12" in result.output
        assert "15" in result.output
        assert "7" in result.output

    def test_quota_nova_unavailable(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.compute_url = "https://nova.example.com/v2.1"
        mock_client.volume_url = "https://cinder.example.com/v3"
        mock_client.network_url = "https://neutron.example.com"
        mock_client.project_id = "proj-1"

        def _get(url, **kwargs):
            if "nova" in url:
                raise Exception("Nova down")
            if "cinder" in url and "/limits" in url:
                return {"limits": {"absolute": {
                    "totalVolumesUsed": 1, "maxTotalVolumes": 10,
                    "totalGigabytesUsed": 50, "maxTotalVolumeGigabytes": 500,
                    "totalSnapshotsUsed": 0, "maxTotalSnapshots": 10,
                    "totalBackupsUsed": 0, "maxTotalBackups": 10,
                    "totalBackupGigabytesUsed": 0, "maxTotalBackupGigabytes": 500,
                }}}
            if "/quotas" in url:
                return {"quotas": [{"network": 50, "subnet": 100, "port": 200,
                                    "router": 10, "floatingip": 20,
                                    "security_group": 50, "security_group_rule": 200}]}
            if "/networks" in url:
                return {"networks": []}
            if "/subnets" in url:
                return {"subnets": []}
            if "/ports" in url:
                return {"ports": []}
            if "/routers" in url:
                return {"routers": []}
            if "/floatingips" in url:
                return {"floatingips": []}
            if "/security-groups" in url:
                return {"security_groups": []}
            return {}

        mock_client.get = _get

        result = invoke(["quota"])
        assert result.exit_code == 0
        assert "unavailable" in result.output
        assert "Volume" in result.output  # other sections still render


# ══════════════════════════════════════════════════════════════════════════
#  _row helper
# ══════════════════════════════════════════════════════════════════════════


class TestRow:

    def test_row_percentage(self):
        from orca_cli.commands.quota import _row
        r = _row("Compute", "Instances", 3, 10)
        assert r["service"] == "Compute"
        assert r["resource"] == "Instances"
        assert r["used"] == "3"
        assert r["limit"] == "10"
        assert "30%" in r["usage"]

    def test_row_unlimited(self):
        from orca_cli.commands.quota import _row
        r = _row("Compute", "Instances", 5, -1)
        assert r["limit"] == "unlimited"
        assert r["usage"] == "—"

    def test_row_dash_used(self):
        from orca_cli.commands.quota import _row
        r = _row("Compute", "Key Pairs", "—", 100)
        assert r["used"] == "—"
        assert r["usage"] == "—"

    def test_row_zero_limit(self):
        from orca_cli.commands.quota import _row
        r = _row("Network", "FIPs", 0, 0)
        assert r["usage"] == "—"  # ZeroDivisionError handled

    def test_row_high_usage_yellow(self):
        from orca_cli.commands.quota import _row
        r = _row("Compute", "vCPUs", 17, 20)
        assert "yellow" in r["usage"]
        assert "85%" in r["usage"]

    def test_row_critical_usage_red(self):
        from orca_cli.commands.quota import _row
        r = _row("Compute", "vCPUs", 19, 20)
        assert "red" in r["usage"]
        assert "95%" in r["usage"]

    def test_row_low_usage_green(self):
        from orca_cli.commands.quota import _row
        r = _row("Compute", "vCPUs", 5, 20)
        assert "green" in r["usage"]
        assert "25%" in r["usage"]


# ══════════════════════════════════════════════════════════════════════════
#  Help
# ══════════════════════════════════════════════════════════════════════════


class TestQuotaHelp:

    def test_quota_help(self, invoke):
        result = invoke(["quota", "--help"])
        assert result.exit_code == 0
        assert "quota" in result.output.lower()


# ══════════════════════════════════════════════════════════════════════════
#  set / delete / list (admin)
# ══════════════════════════════════════════════════════════════════════════


class TestQuotaSet:

    def _mock_writes(self, mock_client):
        mock_client.compute_url = "https://nova.example.com/v2.1"
        mock_client.volume_url = "https://cinder.example.com/v3"
        mock_client.network_url = "https://neutron.example.com"
        mock_client.project_id = "proj-1"
        calls: list[tuple[str, str, dict]] = []

        def _put(url, json=None, **kwargs):
            calls.append(("PUT", url, json or {}))
            # Echo back the quota_set / quota body so the service helpers
            # return something truthy.
            return {"quota_set": (json or {}).get("quota_set", {}),
                    "quota": (json or {}).get("quota", {})}

        def _delete(url, **kwargs):
            calls.append(("DELETE", url, {}))
            return None

        mock_client.put = _put
        mock_client.delete = _delete
        return calls

    def test_set_compute_only(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        calls = self._mock_writes(mock_client)

        result = invoke(["quota", "set", "--instances", "50", "--cores", "100"])
        assert result.exit_code == 0, result.output
        # Only Nova should have received a PUT.
        puts = [c for c in calls if c[0] == "PUT"]
        assert len(puts) == 1
        assert "/os-quota-sets/proj-1" in puts[0][1]
        assert puts[0][2]["quota_set"]["instances"] == 50
        assert puts[0][2]["quota_set"]["cores"] == 100
        assert "compute" in result.output

    def test_set_three_services(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        calls = self._mock_writes(mock_client)

        result = invoke([
            "quota", "set",
            "--instances", "30",
            "--volumes", "20",
            "--networks", "10",
        ])
        assert result.exit_code == 0, result.output
        puts = [c for c in calls if c[0] == "PUT"]
        assert len(puts) == 3
        urls = " ".join(c[1] for c in puts)
        assert "/os-quota-sets/" in urls  # nova + cinder
        assert "/quotas/proj-1" in urls   # neutron
        # Neutron flag mapping: --networks → ``network`` in payload.
        neutron = next(c for c in puts if "/quotas/proj-1" in c[1])
        assert neutron[2]["quota"]["network"] == 10

    def test_set_force_flag(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        calls = self._mock_writes(mock_client)

        result = invoke(["quota", "set", "--instances", "5", "--force"])
        assert result.exit_code == 0
        puts = [c for c in calls if c[0] == "PUT"]
        assert puts[0][2]["quota_set"]["force"] is True

    def test_set_nothing_to_do(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        self._mock_writes(mock_client)

        result = invoke(["quota", "set"])
        assert result.exit_code != 0
        assert "Nothing to update" in result.output


class TestQuotaDelete:

    def test_delete_all_yes(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.compute_url = "https://nova.example.com/v2.1"
        mock_client.volume_url = "https://cinder.example.com/v3"
        mock_client.network_url = "https://neutron.example.com"
        mock_client.project_id = "proj-1"
        seen: list[str] = []

        def _delete(url, **kwargs):
            seen.append(url)
            return None

        mock_client.delete = _delete

        result = invoke(["quota", "delete", "--yes"])
        assert result.exit_code == 0, result.output
        # One DELETE per service (compute / volume / network).
        assert len(seen) == 3
        assert any("/os-quota-sets/proj-1" in u and "nova" in u for u in seen)
        assert any("/os-quota-sets/proj-1" in u and "cinder" in u for u in seen)
        assert any("/quotas/proj-1" in u for u in seen)

    def test_delete_single_service(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.network_url = "https://neutron.example.com"
        mock_client.compute_url = "https://nova.example.com/v2.1"
        mock_client.volume_url = "https://cinder.example.com/v3"
        mock_client.project_id = "proj-1"
        seen: list[str] = []

        def _delete(url, **kwargs):
            seen.append(url)
            return None

        mock_client.delete = _delete
        result = invoke(["quota", "delete", "--service", "network", "--yes"])
        assert result.exit_code == 0
        assert len(seen) == 1
        assert "/quotas/proj-1" in seen[0]

    def test_delete_aborted(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.compute_url = "https://nova.example.com/v2.1"
        mock_client.volume_url = "https://cinder.example.com/v3"
        mock_client.network_url = "https://neutron.example.com"
        mock_client.project_id = "proj-1"
        seen: list[str] = []
        mock_client.delete = lambda *a, **kw: seen.append("nope")

        # Decline the confirmation prompt.
        result = invoke(["quota", "delete"], input="n\n")
        assert result.exit_code == 0
        assert "Aborted" in result.output
        assert not seen


class TestQuotaList:

    def test_list_neutron(self, invoke, config_dir, mock_client, sample_profile):
        save_profile("p", sample_profile)
        set_active_profile("p")
        mock_client.network_url = "https://neutron.example.com"
        mock_client.project_id = "proj-1"

        def _get(url, **kwargs):
            if "/quotas" in url:
                return {"quotas": [
                    {"project_id": "alpha", "network": 5, "port": 50},
                    {"project_id": "beta", "network": 99, "router": 7},
                ]}
            return {}

        mock_client.get = _get
        result = invoke(["quota", "list"])
        assert result.exit_code == 0, result.output
        assert "alpha" in result.output
        assert "beta" in result.output
        assert "99" in result.output
