"""``orca address-scope`` — Neutron address scopes (routing isolation)."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.output import console, output_options, print_detail, print_list
from orca_cli.services.network import NetworkService


@click.group("address-scope")
def address_scope() -> None:
    """Manage Neutron address scopes.

    An address scope groups subnet pools that share the same routing
    domain — useful in BGP-driven L3 deployments and overlapping-CIDR
    scenarios.
    """


def _svc(ctx: click.Context) -> NetworkService:
    return NetworkService(ctx.find_object(OrcaContext).ensure_client())


@address_scope.command("list")
@output_options
@click.pass_context
def as_list(ctx, output_format, columns, fit_width, max_width, noindent):
    """List address scopes."""
    scopes = _svc(ctx).find_address_scopes()
    print_list(
        scopes,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Name", "name", {"style": "bold"}),
            ("IP Version", "ip_version"),
            ("Shared", "shared"),
            ("Project", lambda s: s.get("project_id", "")[:8] if s.get("project_id") else "—"),
        ],
        title="Address scopes",
        output_format=output_format, fit_width=fit_width, max_width=max_width,
        noindent=noindent, columns=columns,
        empty_msg="No address scopes found.",
    )


@address_scope.command("show")
@click.argument("as_id")
@output_options
@click.pass_context
def as_show(ctx, as_id, output_format, columns, fit_width, max_width, noindent):
    """Show an address scope's details."""
    data = _svc(ctx).get_address_scope(as_id)
    fields = [(k, str(v)) for k, v in data.items()]
    print_detail(fields, output_format=output_format, fit_width=fit_width,
                 max_width=max_width, noindent=noindent, columns=columns)


@address_scope.command("create")
@click.argument("name")
@click.option("--ip-version", type=click.Choice(["4", "6"]), default="4",
              show_default=True, help="IP version: 4 or 6.")
@click.option("--shared/--unshared", default=False, show_default=True,
              help="Visible to other projects.")
@click.pass_context
def as_create(ctx, name, ip_version, shared):
    """Create an address scope."""
    body: dict = {"name": name, "ip_version": int(ip_version), "shared": shared}
    data = _svc(ctx).create_address_scope(body)
    console.print(f"[green]Address scope '{name}' created ({data.get('id', '')}).[/green]")


@address_scope.command("set")
@click.argument("as_id")
@click.option("--name", default=None, help="New name.")
@click.option("--shared/--unshared", default=None,
              help="Switch visibility.")
@click.pass_context
def as_set(ctx, as_id, name, shared):
    """Update an address scope."""
    body: dict = {}
    if name is not None:
        body["name"] = name
    if shared is not None:
        body["shared"] = shared
    if not body:
        console.print("[yellow]Nothing to update.[/yellow]")
        return
    _svc(ctx).update_address_scope(as_id, body)
    console.print(f"[green]Address scope {as_id} updated.[/green]")


@address_scope.command("delete")
@click.argument("as_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def as_delete(ctx, as_id, yes):
    """Delete an address scope."""
    if not yes:
        click.confirm(f"Delete address scope {as_id}?", abort=True)
    _svc(ctx).delete_address_scope(as_id)
    console.print(f"[green]Address scope {as_id} deleted.[/green]")
