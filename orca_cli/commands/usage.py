"""``orca usage`` — project resource usage (Nova simple-tenant-usage)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.output import console, output_options, print_list
from orca_cli.services.compute import ComputeService


def _period(start: str | None, end: str | None) -> tuple[str, str, datetime, datetime]:
    now = datetime.now(timezone.utc)
    end_dt = (datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
              if end else now)
    start_dt = (datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if start else end_dt - timedelta(days=30))
    return (
        start_dt.strftime("%Y-%m-%dT00:00:00"),
        end_dt.strftime("%Y-%m-%dT23:59:59"),
        start_dt, end_dt,
    )


@click.group(invoke_without_command=True)
@click.option("--start", default=None, help="Start date (YYYY-MM-DD). Default: 30 days ago.")
@click.option("--end", default=None, help="End date (YYYY-MM-DD). Default: today.")
@output_options
@click.pass_context
def usage(ctx: click.Context, start: str | None, end: str | None,
          output_format: str, columns: tuple[str, ...], fit_width: bool,
          max_width: int | None, noindent: bool) -> None:
    """Inspect Nova tenant usage.

    With no sub-command, runs ``usage show`` for the current project
    (backward-compatible). OSC parity: ``usage show`` and ``usage list``.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(usage_show, project=None, start=start, end=end,
                   output_format=output_format, columns=columns,
                   fit_width=fit_width, max_width=max_width, noindent=noindent)


@usage.command("show")
@click.option("--project", help="Project ID (default: current project).")
@click.option("--start", default=None, help="Start date (YYYY-MM-DD). Default: 30 days ago.")
@click.option("--end", default=None, help="End date (YYYY-MM-DD). Default: today.")
@output_options
@click.pass_context
def usage_show(ctx: click.Context, project: str | None,
               start: str | None, end: str | None,
               output_format: str, columns: tuple[str, ...], fit_width: bool,
               max_width: int | None, noindent: bool) -> None:
    """Show CPU/RAM/disk hours and per-server breakdown for one project.

    \b
    Examples:
      orca usage show
      orca usage show --start 2026-04-01 --end 2026-04-14
      orca usage show --project <uuid>
    """
    client = ctx.find_object(OrcaContext).ensure_client()
    project_id = (project or client.project_id
                  or (client.token_data.get("project") or {}).get("id"))
    if not project_id:
        from orca_cli.core.exceptions import OrcaCLIError
        raise OrcaCLIError("No project ID available; pass --project explicitly.")
    svc = ComputeService(client)

    start_str, end_str, start_dt, end_dt = _period(start, end)

    with console.status("[bold cyan]Fetching usage data…[/bold cyan]"):
        # Nova's per-project endpoint returns server_usages by default
        # and rejects ``detailed`` on recent micro-versions.
        tenant = svc.get_tenant_usage(
            project_id,
            params={"start": start_str, "end": end_str},
        ) or {}

    if not tenant:
        console.print("[yellow]No usage data for this period.[/yellow]")
        return

    if output_format == "table":
        from rich.table import Table

        summary = Table(title=f"Usage Summary — {project_id}  ({start_dt.date()} → {end_dt.date()})", show_lines=False)
        summary.add_column("Metric", style="bold")
        summary.add_column("Value", justify="right", style="cyan")
        summary.add_row("Total vCPU·hours", f"{tenant.get('total_vcpus_usage', 0):.1f}")
        summary.add_row("Total RAM·hours (MB)", f"{tenant.get('total_memory_mb_usage', 0):.1f}")
        summary.add_row("Total Disk·hours (GB)", f"{tenant.get('total_local_gb_usage', 0):.1f}")
        summary.add_row("Total Server·hours", f"{tenant.get('total_hours', 0):.1f}")
        summary.add_row("Active Servers", str(len(tenant.get("server_usages", []))))
        console.print()
        console.print(summary)
        console.print()

    rows = []
    for su in sorted(tenant.get("server_usages", []), key=lambda x: x.get("hours", 0), reverse=True):
        rows.append({
            "name": su.get("name", ""),
            "instance_id": su.get("instance_id", ""),
            "state": su.get("state", ""),
            "vcpus": su.get("vcpus", 0),
            "ram_mb": su.get("memory_mb", 0),
            "disk_gb": su.get("local_gb", 0),
            "hours": f"{su.get('hours', 0):.1f}",
            "started": str(su.get("started_at", ""))[:19],
            "ended": str(su.get("ended_at", "") or "—")[:19],
        })
    print_list(
        rows,
        [
            ("Name", "name", {"style": "bold"}),
            ("Instance ID", "instance_id", {"style": "cyan", "no_wrap": True}),
            ("State", "state", {"style": "green"}),
            ("vCPUs", "vcpus", {"justify": "right"}),
            ("RAM (MB)", "ram_mb", {"justify": "right"}),
            ("Disk (GB)", "disk_gb", {"justify": "right"}),
            ("Hours", "hours", {"justify": "right"}),
            ("Started", "started"),
            ("Ended", "ended"),
        ],
        title="Per-Server Usage",
        output_format=output_format, fit_width=fit_width, max_width=max_width, noindent=noindent,
        columns=columns,
        empty_msg="No per-server data.",
    )


@usage.command("list")
@click.option("--start", default=None, help="Start date (YYYY-MM-DD). Default: 30 days ago.")
@click.option("--end", default=None, help="End date (YYYY-MM-DD). Default: today.")
@output_options
@click.pass_context
def usage_list(ctx: click.Context, start: str | None, end: str | None,
               output_format: str, columns: tuple[str, ...], fit_width: bool,
               max_width: int | None, noindent: bool) -> None:
    """List per-project resource usage across the whole cloud (admin).

    Parity with ``openstack usage list`` — hits Nova
    ``/os-simple-tenant-usage`` without a tenant filter, which returns
    one row per project active during the window.
    """
    svc = ComputeService(ctx.find_object(OrcaContext).ensure_client())
    start_str, end_str, start_dt, end_dt = _period(start, end)

    with console.status("[bold cyan]Fetching cross-project usage…[/bold cyan]"):
        tenants = svc.find_tenant_usages(
            params={"start": start_str, "end": end_str},
        )

    rows = [
        {
            "tenant_id": t.get("tenant_id", ""),
            "servers": len(t.get("server_usages", []) or []),
            "vcpu_h": f"{t.get('total_vcpus_usage', 0):.1f}",
            "ram_mb_h": f"{t.get('total_memory_mb_usage', 0):.1f}",
            "disk_gb_h": f"{t.get('total_local_gb_usage', 0):.1f}",
            "hours": f"{t.get('total_hours', 0):.1f}",
        }
        for t in tenants
    ]
    print_list(
        rows,
        [
            ("Project", "tenant_id", {"style": "cyan", "no_wrap": True}),
            ("Servers", "servers", {"justify": "right"}),
            ("vCPU·h", "vcpu_h", {"justify": "right"}),
            ("RAM·h (MB)", "ram_mb_h", {"justify": "right"}),
            ("Disk·h (GB)", "disk_gb_h", {"justify": "right"}),
            ("Server·h", "hours", {"justify": "right"}),
        ],
        title=f"Cross-project usage ({start_dt.date()} → {end_dt.date()})",
        output_format=output_format, fit_width=fit_width, max_width=max_width, noindent=noindent,
        columns=columns,
        empty_msg="No tenant usage data for this period.",
    )
