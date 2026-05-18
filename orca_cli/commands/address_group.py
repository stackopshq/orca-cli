"""``orca address-group`` — Neutron address groups."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import console, output_options, print_detail, print_list
from orca_cli.services.network import NetworkService


@click.group("address-group")
def address_group() -> None:
    """Manage Neutron address groups (collections of CIDRs).

    Used as the ``remote_address_group_id`` of security-group rules to
    reuse a curated list of CIDRs across multiple rules.
    """


def _svc(ctx: click.Context) -> NetworkService:
    return NetworkService(ctx.find_object(OrcaContext).ensure_client())


@address_group.command("list")
@output_options
@click.pass_context
def ag_list(ctx, output_format, columns, fit_width, max_width, noindent):
    """List address groups."""
    groups = _svc(ctx).find_address_groups()
    print_list(
        groups,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Name", "name", {"style": "bold"}),
            ("Project", lambda g: g.get("project_id", "")[:8] if g.get("project_id") else "—"),
            ("Addresses",
             lambda g: ", ".join(g.get("addresses", []) or []) or "—"),
        ],
        title="Address groups",
        output_format=output_format, fit_width=fit_width, max_width=max_width,
        noindent=noindent, columns=columns,
        empty_msg="No address groups found.",
    )


@address_group.command("show")
@click.argument("ag_id")
@output_options
@click.pass_context
def ag_show(ctx, ag_id, output_format, columns, fit_width, max_width, noindent):
    """Show an address group's details."""
    data = _svc(ctx).get_address_group(ag_id)
    fields = [
        ("id", data.get("id", "")),
        ("name", data.get("name", "")),
        ("description", data.get("description", "") or "—"),
        ("project_id", data.get("project_id", "")),
        ("addresses", ", ".join(data.get("addresses", []) or []) or "—"),
    ]
    print_detail(fields, output_format=output_format, fit_width=fit_width,
                 max_width=max_width, noindent=noindent, columns=columns)


@address_group.command("create")
@click.argument("name")
@click.option("--description", default=None, help="Free-text description.")
@click.option("--address", "addresses", multiple=True,
              help="CIDR to include (repeatable).")
@click.pass_context
def ag_create(ctx, name, description, addresses):
    """Create an address group.

    \b
    Examples:
      orca address-group create office-network --address 10.0.0.0/24 --address 10.1.0.0/24
    """
    body: dict = {"name": name}
    if description:
        body["description"] = description
    if addresses:
        body["addresses"] = list(addresses)
    data = _svc(ctx).create_address_group(body)
    console.print(f"[green]Address group '{name}' created ({data.get('id', '')}).[/green]")


@address_group.command("set")
@click.argument("ag_id")
@click.option("--name", default=None, help="New name.")
@click.option("--description", default=None, help="New description.")
@click.option("--add-address", "add_addresses", multiple=True,
              help="CIDR to append (repeatable).")
@click.option("--remove-address", "remove_addresses", multiple=True,
              help="CIDR to remove (repeatable).")
@click.pass_context
def ag_set(ctx, ag_id, name, description, add_addresses, remove_addresses):
    """Update an address group's name / description / member CIDRs."""
    svc = _svc(ctx)
    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if body:
        svc.update_address_group(ag_id, body)
    if add_addresses:
        svc.add_addresses_to_group(ag_id, list(add_addresses))
    if remove_addresses:
        svc.remove_addresses_from_group(ag_id, list(remove_addresses))
    if not (body or add_addresses or remove_addresses):
        console.print("[yellow]Nothing to update.[/yellow]")
        return
    console.print(f"[green]Address group {ag_id} updated.[/green]")


@address_group.command("unset")
@click.argument("ag_id")
@click.option("--address", "addresses", multiple=True, required=True,
              help="CIDR to remove (repeatable).")
@click.pass_context
def ag_unset(ctx, ag_id, addresses):
    """Remove addresses from an address group."""
    _svc(ctx).remove_addresses_from_group(ag_id, list(addresses))
    console.print(
        f"[green]Removed {len(addresses)} address(es) from {ag_id}.[/green]"
    )


@address_group.command("delete")
@click.argument("ag_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def ag_delete(ctx, ag_id, yes):
    """Delete an address group."""
    if not yes:
        click.confirm(f"Delete address group {ag_id}?", abort=True)
    _svc(ctx).delete_address_group(ag_id)
    console.print(f"[green]Address group {ag_id} deleted.[/green]")


# Silence unused-import warning if OrcaCLIError ever becomes needed.
_ = OrcaCLIError
