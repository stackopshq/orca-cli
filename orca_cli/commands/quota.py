"""``orca quota`` — show project quotas (Nova + Neutron + Cinder)."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.output import console, output_options, print_list
from orca_cli.services.compute import ComputeService
from orca_cli.services.network import NetworkService
from orca_cli.services.volume import VolumeService


@click.group(invoke_without_command=True)
@click.pass_context
def quota(ctx: click.Context) -> None:
    """Inspect project quotas across Nova, Neutron and Cinder.

    With no sub-command, runs ``quota show`` for backward compatibility.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(quota_show)


@quota.command("show")
@click.option("--project", help="Project ID (default: current project).")
@output_options
@click.pass_context
def quota_show(ctx: click.Context, project: str | None,
               output_format: str, columns: tuple[str, ...], fit_width: bool,
               max_width: int | None, noindent: bool) -> None:
    """Show project quotas — Nova, Neutron and Cinder usage vs limits."""
    client = ctx.find_object(OrcaContext).ensure_client()
    project_id = (project or client.project_id
                  or (client.token_data.get("project") or {}).get("id")
                  or "current project")

    rows: list[dict] = []

    with console.status("[bold cyan]Fetching quotas…[/bold cyan]"):
        # ── Nova (compute) ───────────────────────────────────────────
        try:
            nova = ComputeService(client).get_limits()
            rows.extend([
                _row("Compute", "Instances", nova.get("totalInstancesUsed", 0), nova.get("maxTotalInstances", -1)),
                _row("Compute", "vCPUs", nova.get("totalCoresUsed", 0), nova.get("maxTotalCores", -1)),
                _row("Compute", "RAM (MB)", nova.get("totalRAMUsed", 0), nova.get("maxTotalRAMSize", -1)),
                _row("Compute", "Key Pairs", "—", nova.get("maxTotalKeypairs", -1)),
                _row("Compute", "Server Groups", nova.get("totalServerGroupsUsed", 0), nova.get("maxServerGroups", -1)),
            ])
        except Exception:
            rows.append(_row("Compute", "(unavailable)", "—", "—"))

        # ── Cinder (volume) ──────────────────────────────────────────
        try:
            cinder = VolumeService(client).get_limits()
            rows.extend([
                _row("Volume", "Volumes", cinder.get("totalVolumesUsed", 0), cinder.get("maxTotalVolumes", -1)),
                _row("Volume", "Volume Storage (GB)", cinder.get("totalGigabytesUsed", 0), cinder.get("maxTotalVolumeGigabytes", -1)),
                _row("Volume", "Snapshots", cinder.get("totalSnapshotsUsed", 0), cinder.get("maxTotalSnapshots", -1)),
                _row("Volume", "Backups", cinder.get("totalBackupsUsed", 0), cinder.get("maxTotalBackups", -1)),
                _row("Volume", "Backup Storage (GB)", cinder.get("totalBackupGigabytesUsed", 0), cinder.get("maxTotalBackupGigabytes", -1)),
            ])
        except Exception:
            rows.append(_row("Volume", "(unavailable)", "—", "—"))

        # ── Neutron (network) ────────────────────────────────────────
        try:
            net_svc = NetworkService(client)
            quotas = net_svc.find_quotas()
            if quotas:
                q = quotas[0]
            else:
                q = net_svc.get_quota(project_id)

            nets = len(net_svc.find())
            subnets = len(net_svc.find_subnets())
            ports = len(net_svc.find_ports())
            routers = len(net_svc.find_routers())
            fips = len(net_svc.find_floating_ips())
            sgs = len(net_svc.find_security_groups())

            rows.extend([
                _row("Network", "Networks", nets, q.get("network", -1)),
                _row("Network", "Subnets", subnets, q.get("subnet", -1)),
                _row("Network", "Ports", ports, q.get("port", -1)),
                _row("Network", "Routers", routers, q.get("router", -1)),
                _row("Network", "Floating IPs", fips, q.get("floatingip", -1)),
                _row("Network", "Security Groups", sgs, q.get("security_group", -1)),
                _row("Network", "SG Rules", "—", q.get("security_group_rule", -1)),
            ])
        except Exception:
            rows.append(_row("Network", "(unavailable)", "—", "—"))

    print_list(
        rows,
        [
            ("Service", "service", {"style": "bold"}),
            ("Resource", "resource"),
            ("Used", "used", {"justify": "right", "style": "cyan"}),
            ("Limit", "limit", {"justify": "right"}),
            ("Usage", "usage", {"justify": "right"}),
        ],
        title=f"Project Quotas — {project_id}",
        output_format=output_format, fit_width=fit_width, max_width=max_width, noindent=noindent,
        columns=columns,
        empty_msg="No quota information available.",
    )


@quota.command("default")
@click.option("--project", help="Project ID (only used to look up defaults; "
              "Nova/Cinder return the same answer for any project).")
@output_options
@click.pass_context
def quota_default(ctx: click.Context, project: str | None,
                  output_format: str, columns: tuple[str, ...], fit_width: bool,
                  max_width: int | None, noindent: bool) -> None:
    """Show the cloud-wide default quotas (Nova + Cinder + Neutron).

    Parity with ``openstack quota show --default`` — Nova and Cinder
    each expose a ``/os-quota-sets/<project>/defaults`` endpoint that
    returns the same values regardless of the project; Neutron uses
    ``/quotas/default``.
    """
    client = ctx.find_object(OrcaContext).ensure_client()
    project_id = (project or client.project_id
                  or (client.token_data.get("project") or {}).get("id"))
    if not project_id:
        from orca_cli.core.exceptions import OrcaCLIError
        raise OrcaCLIError("No project ID available; pass --project explicitly.")

    rows: list[dict] = []
    with console.status("[bold cyan]Fetching defaults…[/bold cyan]"):
        try:
            for k, v in ComputeService(client).get_quota_defaults(project_id).items():
                if k == "id":
                    continue
                rows.append({"service": "Compute", "resource": k, "default": str(v)})
        except Exception:
            rows.append({"service": "Compute", "resource": "(unavailable)", "default": "—"})

        try:
            for k, v in VolumeService(client).get_quota_set_defaults(project_id).items():
                if k == "id":
                    continue
                rows.append({"service": "Volume", "resource": k, "default": str(v)})
        except Exception:
            rows.append({"service": "Volume", "resource": "(unavailable)", "default": "—"})

        try:
            net_svc = NetworkService(client)
            data = net_svc._client.get(f"{net_svc._base}/quotas/default")  # noqa: SLF001
            q = data.get("quota", {}) or {}
            for k, v in q.items():
                rows.append({"service": "Network", "resource": k, "default": str(v)})
        except Exception:
            rows.append({"service": "Network", "resource": "(unavailable)", "default": "—"})

    print_list(
        rows,
        [
            ("Service", "service", {"style": "bold"}),
            ("Resource", "resource"),
            ("Default", "default", {"justify": "right", "style": "cyan"}),
        ],
        title="Default Quotas",
        output_format=output_format, fit_width=fit_width, max_width=max_width, noindent=noindent,
        columns=columns,
        empty_msg="No default quotas available.",
    )


def _row(service: str, resource: str, used: object, limit: object) -> dict:
    used_s = str(used)
    limit_s = "unlimited" if limit == -1 else str(limit)
    if used_s != "—" and limit_s != "unlimited" and limit_s != "—":
        try:
            pct = int(used) / int(limit) * 100  # type: ignore[call-overload]
            color = "green" if pct < 70 else "yellow" if pct < 90 else "red"
            usage = f"[{color}]{pct:.0f}%[/{color}]"
        except (ValueError, ZeroDivisionError):
            usage = "—"
    else:
        usage = "—"
    return {"service": service, "resource": resource, "used": used_s, "limit": limit_s, "usage": usage}
