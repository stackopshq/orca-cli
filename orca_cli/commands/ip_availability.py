"""``orca ip-availability`` — Neutron network IP availability (admin)."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.output import output_options, print_detail, print_list
from orca_cli.services.network import NetworkService


@click.group("ip-availability")
def ip_availability() -> None:
    """Inspect IP availability across networks (admin).

    Reports allocated vs total addresses per subnet — useful for
    sizing planning before quota changes.
    """


def _svc(ctx: click.Context) -> NetworkService:
    return NetworkService(ctx.find_object(OrcaContext).ensure_client())


@ip_availability.command("list")
@click.option("--network-id", default=None, help="Filter by network ID.")
@click.option("--ip-version", type=click.Choice(["4", "6"]), default=None,
              help="Filter by IP version.")
@output_options
@click.pass_context
def ipa_list(ctx, network_id, ip_version,
             output_format, columns, fit_width, max_width, noindent):
    """List IP availability across networks."""
    params: dict = {}
    if network_id:
        params["network_id"] = network_id
    if ip_version:
        params["ip_version"] = int(ip_version)
    items = _svc(ctx).find_ip_availabilities(params=params or None)
    print_list(
        items,
        [
            ("Network ID", "network_id", {"style": "cyan", "no_wrap": True}),
            ("Network", "network_name", {"style": "bold"}),
            ("Total", lambda i: str(i.get("total_ips", 0)), {"justify": "right"}),
            ("Used", lambda i: str(i.get("used_ips", 0)), {"justify": "right"}),
            ("Project", lambda i: i.get("project_id", "")[:8] if i.get("project_id") else "—"),
        ],
        title="Network IP availability",
        output_format=output_format, fit_width=fit_width, max_width=max_width,
        noindent=noindent, columns=columns,
        empty_msg="No networks reported.",
    )


@ip_availability.command("show")
@click.argument("network_id")
@output_options
@click.pass_context
def ipa_show(ctx, network_id, output_format, columns, fit_width, max_width, noindent):
    """Show IP availability for a network (with subnet breakdown)."""
    data = _svc(ctx).get_ip_availability(network_id)
    fields = [
        ("network_id", data.get("network_id", "")),
        ("network_name", data.get("network_name", "")),
        ("project_id", data.get("project_id", "")),
        ("total_ips", str(data.get("total_ips", 0))),
        ("used_ips", str(data.get("used_ips", 0))),
    ]
    subnets = data.get("subnet_ip_availability", []) or []
    if subnets:
        fields.append(("", ""))
        fields.append(("── Subnets ──", ""))
        for sub in subnets:
            label = f"  {sub.get('subnet_name') or sub.get('subnet_id', '')[:8]}"
            fields.append((label,
                          f"used={sub.get('used_ips', 0)}/{sub.get('total_ips', 0)} "
                          f"cidr={sub.get('cidr', '')}"))
    print_detail(fields, output_format=output_format, fit_width=fit_width,
                 max_width=max_width, noindent=noindent, columns=columns)
