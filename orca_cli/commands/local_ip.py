"""``orca local-ip`` — Neutron local IPs (Yoga+ tenant overlay feature)."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.output import console, output_options, print_detail, print_list
from orca_cli.services.network import NetworkService


@click.group("local-ip")
def local_ip() -> None:
    """Manage Neutron local IPs (Yoga+ — tenant-local virtual IPs).

    A local IP is a virtual IP allocated within a single project that
    can be associated with multiple ports for an east-west floating-IP
    pattern (no SNAT, no L3 router).
    """


@local_ip.group("association")
def local_ip_assoc() -> None:
    """Manage local-IP-to-port associations."""


def _svc(ctx: click.Context) -> NetworkService:
    return NetworkService(ctx.find_object(OrcaContext).ensure_client())


@local_ip.command("list")
@output_options
@click.pass_context
def lip_list(ctx, output_format, columns, fit_width, max_width, noindent):
    """List local IPs."""
    items = _svc(ctx).find_local_ips()
    print_list(
        items,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Name", "name", {"style": "bold"}),
            ("IP", "local_ip_address"),
            ("Network", "network_id"),
            ("Project", lambda i: i.get("project_id", "")[:8] if i.get("project_id") else "—"),
        ],
        title="Local IPs",
        output_format=output_format, fit_width=fit_width, max_width=max_width,
        noindent=noindent, columns=columns,
        empty_msg="No local IPs found.",
    )


@local_ip.command("show")
@click.argument("lip_id")
@output_options
@click.pass_context
def lip_show(ctx, lip_id, output_format, columns, fit_width, max_width, noindent):
    """Show a local IP."""
    data = _svc(ctx).get_local_ip(lip_id)
    fields = [(k, str(v)) for k, v in data.items()]
    print_detail(fields, output_format=output_format, fit_width=fit_width,
                 max_width=max_width, noindent=noindent, columns=columns)


@local_ip.command("create")
@click.argument("name")
@click.option("--network-id", required=True, help="Local network ID.")
@click.option("--local-port-id", default=None,
              help="Port ID to anchor the local IP.")
@click.option("--ip-address", default=None,
              help="Specific IP within the network's CIDR (autopicked otherwise).")
@click.option("--ip-mode", type=click.Choice(["translate", "passthrough"]),
              default=None, help="Translate (SNAT-like) or passthrough.")
@click.pass_context
def lip_create(ctx, name, network_id, local_port_id, ip_address, ip_mode):
    """Create a local IP."""
    body: dict = {"name": name, "network_id": network_id}
    if local_port_id:
        body["local_port_id"] = local_port_id
    if ip_address:
        body["local_ip_address"] = ip_address
    if ip_mode:
        body["ip_mode"] = ip_mode
    data = _svc(ctx).create_local_ip(body)
    console.print(f"[green]Local IP '{name}' created ({data.get('id', '')}).[/green]")


@local_ip.command("set")
@click.argument("lip_id")
@click.option("--name", default=None, help="New name.")
@click.option("--description", default=None, help="New description.")
@click.pass_context
def lip_set(ctx, lip_id, name, description):
    """Update a local IP."""
    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if not body:
        console.print("[yellow]Nothing to update.[/yellow]")
        return
    _svc(ctx).update_local_ip(lip_id, body)
    console.print(f"[green]Local IP {lip_id} updated.[/green]")


@local_ip.command("delete")
@click.argument("lip_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def lip_delete(ctx, lip_id, yes):
    """Delete a local IP."""
    if not yes:
        click.confirm(f"Delete local IP {lip_id}?", abort=True)
    _svc(ctx).delete_local_ip(lip_id)
    console.print(f"[green]Local IP {lip_id} deleted.[/green]")


# ── associations ──────────────────────────────────────────────────────

@local_ip_assoc.command("list")
@click.argument("lip_id")
@output_options
@click.pass_context
def assoc_list(ctx, lip_id, output_format, columns, fit_width, max_width, noindent):
    """List port associations on a local IP."""
    items = _svc(ctx).find_local_ip_associations(lip_id)
    print_list(
        items,
        [
            ("Port ID", "fixed_port_id", {"style": "cyan", "no_wrap": True}),
            ("Fixed IP", "fixed_ip"),
            ("Host", "host"),
        ],
        title=f"Port associations on local IP {lip_id}",
        output_format=output_format, fit_width=fit_width, max_width=max_width,
        noindent=noindent, columns=columns,
        empty_msg="No associations.",
    )


@local_ip_assoc.command("create")
@click.argument("lip_id")
@click.option("--port-id", required=True, help="Port to associate.")
@click.option("--fixed-ip", default=None,
              help="Specific fixed IP of the port (autopicked otherwise).")
@click.pass_context
def assoc_create(ctx, lip_id, port_id, fixed_ip):
    """Associate a port with a local IP."""
    body: dict = {"fixed_port_id": port_id}
    if fixed_ip:
        body["fixed_ip"] = fixed_ip
    _svc(ctx).create_local_ip_association(lip_id, body)
    console.print(f"[green]Port {port_id} associated with {lip_id}.[/green]")


@local_ip_assoc.command("delete")
@click.argument("lip_id")
@click.argument("port_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def assoc_delete(ctx, lip_id, port_id, yes):
    """Remove a port association from a local IP."""
    if not yes:
        click.confirm(f"Remove port {port_id} from local IP {lip_id}?", abort=True)
    _svc(ctx).delete_local_ip_association(lip_id, port_id)
    console.print(f"[green]Port {port_id} removed from {lip_id}.[/green]")
