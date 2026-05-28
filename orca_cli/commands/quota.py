"""``orca quota`` — show project quotas (Nova + Neutron + Cinder)."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import console, output_options, print_list
from orca_cli.services.compute import ComputeService
from orca_cli.services.network import NetworkService
from orca_cli.services.volume import VolumeService

# OSC ``quota set`` flags mapped to (service, API field).
_COMPUTE_FLAGS = {
    "instances": "instances",
    "cores": "cores",
    "ram": "ram",
    "key_pairs": "key_pairs",
    "server_groups": "server_groups",
    "server_group_members": "server_group_members",
    "metadata_items": "metadata_items",
}
_VOLUME_FLAGS = {
    "volumes": "volumes",
    "snapshots": "snapshots",
    "backups": "backups",
    "gigabytes": "gigabytes",
    "backup_gigabytes": "backup_gigabytes",
    "per_volume_gigabytes": "per_volume_gigabytes",
}
_NETWORK_FLAGS = {
    "networks": "network",
    "subnets": "subnet",
    "ports": "port",
    "routers": "router",
    "floating_ips": "floatingip",
    "security_groups": "security_group",
    "security_group_rules": "security_group_rule",
    "subnetpools": "subnetpool",
    "rbac_policies": "rbac_policy",
}


def _resolve_project_id(ctx: click.Context, project: str | None) -> str:
    client = ctx.find_object(OrcaContext).ensure_client()
    pid = (project or client.project_id
           or (client.token_data.get("project") or {}).get("id"))
    if not pid:
        raise OrcaCLIError("No project ID available; pass --project explicitly.")
    return pid


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


# ── set / delete / list ──────────────────────────────────────────────────


@quota.command("set")
@click.option("--project", help="Project ID (default: current project).")
# Compute
@click.option("--instances", type=int, help="Compute: max instances.")
@click.option("--cores", type=int, help="Compute: max vCPUs.")
@click.option("--ram", type=int, help="Compute: max RAM (MB).")
@click.option("--key-pairs", type=int, help="Compute: max key pairs.")
@click.option("--server-groups", type=int, help="Compute: max server groups.")
@click.option("--server-group-members", type=int, help="Compute: max members per server group.")
@click.option("--metadata-items", type=int, help="Compute: max metadata items per server.")
# Volume
@click.option("--volumes", type=int, help="Volume: max volumes.")
@click.option("--snapshots", type=int, help="Volume: max snapshots.")
@click.option("--backups", type=int, help="Volume: max backups.")
@click.option("--gigabytes", type=int, help="Volume: total volume storage (GB).")
@click.option("--backup-gigabytes", type=int, help="Volume: total backup storage (GB).")
@click.option("--per-volume-gigabytes", type=int, help="Volume: max size per volume (GB).")
# Network (Neutron)
@click.option("--networks", type=int, help="Network: max networks.")
@click.option("--subnets", type=int, help="Network: max subnets.")
@click.option("--ports", type=int, help="Network: max ports.")
@click.option("--routers", type=int, help="Network: max routers.")
@click.option("--floating-ips", type=int, help="Network: max floating IPs.")
@click.option("--security-groups", type=int, help="Network: max security groups.")
@click.option("--security-group-rules", type=int, help="Network: max security-group rules.")
@click.option("--subnetpools", type=int, help="Network: max subnet pools.")
@click.option("--rbac-policies", type=int, help="Network: max RBAC policies.")
# Catch-all
@click.option("--force", is_flag=True,
              help="Compute only: bypass the over-limit check on resources in use.")
@click.pass_context
def quota_set(ctx: click.Context, project: str | None, force: bool, **kwargs) -> None:
    """Set quotas on Nova / Cinder / Neutron (admin).

    Pass any combination of resource flags — only services with at least
    one flag receive a PUT. Use ``-1`` for unlimited (Compute / Volume)
    or the explicit Neutron sentinel.

    \b
    Examples:
      orca quota set --instances 50 --cores 100
      orca quota set --project <uuid> --volumes 20 --gigabytes 1000
      orca quota set --networks 200 --routers 50
    """
    client = ctx.find_object(OrcaContext).ensure_client()
    project_id = _resolve_project_id(ctx, project)

    compute_body = {k: kwargs[k] for k in _COMPUTE_FLAGS if kwargs.get(k) is not None}
    volume_body = {k: kwargs[k] for k in _VOLUME_FLAGS if kwargs.get(k) is not None}
    network_body = {
        _NETWORK_FLAGS[k]: kwargs[k]
        for k in _NETWORK_FLAGS if kwargs.get(k) is not None
    }

    if not (compute_body or volume_body or network_body):
        raise OrcaCLIError(
            "Nothing to update — pass at least one resource flag (see --help)."
        )

    updated: list[str] = []
    if compute_body:
        ComputeService(client).update_quota(project_id, compute_body, force=force)
        updated.append(f"compute ({len(compute_body)})")
    if volume_body:
        VolumeService(client).update_quota_set(project_id, volume_body)
        updated.append(f"volume ({len(volume_body)})")
    if network_body:
        NetworkService(client).update_quota(project_id, network_body)
        updated.append(f"network ({len(network_body)})")

    console.print(
        f"[green]Quota updated on {project_id}:[/green] " + ", ".join(updated)
    )


@quota.command("delete")
@click.option("--project", help="Project ID (default: current project).")
@click.option("--service",
              type=click.Choice(["all", "compute", "volume", "network"],
                                case_sensitive=False),
              default="all", show_default=True,
              help="Which service's quota to reset.")
@click.option("--yes", is_flag=True, help="Skip the confirmation prompt.")
@click.pass_context
def quota_delete(ctx: click.Context, project: str | None,
                 service: str, yes: bool) -> None:
    """Reset project quotas to the cloud defaults (admin).

    Parity with ``openstack quota delete``. With ``--service all`` (default)
    issues DELETE on Nova, Cinder and Neutron quota-sets for the project.
    """
    client = ctx.find_object(OrcaContext).ensure_client()
    project_id = _resolve_project_id(ctx, project)
    svc = service.lower()
    targets = ["compute", "volume", "network"] if svc == "all" else [svc]

    if not yes and not click.confirm(
        f"Reset quotas to defaults on project {project_id} "
        f"({', '.join(targets)}) ?",
        default=False,
    ):
        console.print("[yellow]Aborted.[/yellow]")
        return

    resets: list[str] = []
    for t in targets:
        try:
            if t == "compute":
                ComputeService(client).delete_quota(project_id)
            elif t == "volume":
                VolumeService(client).delete_quota_set(project_id)
            elif t == "network":
                NetworkService(client).delete_quota(project_id)
            resets.append(t)
        except Exception as exc:
            console.print(f"[red]{t}: {exc}[/red]")

    if resets:
        console.print(
            f"[green]Quota reset to defaults on {project_id}:[/green] "
            + ", ".join(resets)
        )


@quota.command("list")
@click.option("--service",
              type=click.Choice(["network"], case_sensitive=False),
              default="network", show_default=True,
              help="Only Neutron exposes a list-all endpoint; Compute "
                   "and Volume require a per-project fan-out (use "
                   "``orca quota show --project <id>`` instead).")
@output_options
@click.pass_context
def quota_list(ctx: click.Context, service: str,
               output_format: str, columns: tuple[str, ...], fit_width: bool,
               max_width: int | None, noindent: bool) -> None:
    """List projects with non-default quotas (admin).

    Parity with ``openstack quota list`` — restricted to Neutron because
    Nova and Cinder do not expose a cross-project list endpoint.
    """
    client = ctx.find_object(OrcaContext).ensure_client()
    quotas = NetworkService(client).find_quotas()
    rows = [
        {
            "project_id": q.get("project_id") or q.get("tenant_id", ""),
            "networks": q.get("network", "—"),
            "subnets": q.get("subnet", "—"),
            "ports": q.get("port", "—"),
            "routers": q.get("router", "—"),
            "floating_ips": q.get("floatingip", "—"),
            "security_groups": q.get("security_group", "—"),
        }
        for q in quotas
    ]
    print_list(
        rows,
        [
            ("Project", "project_id", {"style": "cyan", "no_wrap": True}),
            ("Networks", "networks", {"justify": "right"}),
            ("Subnets", "subnets", {"justify": "right"}),
            ("Ports", "ports", {"justify": "right"}),
            ("Routers", "routers", {"justify": "right"}),
            ("Floating IPs", "floating_ips", {"justify": "right"}),
            ("SGs", "security_groups", {"justify": "right"}),
        ],
        title="Neutron quotas (non-default)",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No project has custom Neutron quotas.",
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
