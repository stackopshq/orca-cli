"""``orca tld`` — top-level OSC-parity alias for ``orca zone tld``
plus show/set leafs that did not exist before.
"""

from __future__ import annotations

import click

from orca_cli.commands.zone import (
    zone_tld as _zone_tld,
)
from orca_cli.commands.zone import (
    zone_tld_create as _zone_tld_create,
)
from orca_cli.commands.zone import (
    zone_tld_delete as _zone_tld_delete,
)
from orca_cli.commands.zone import (
    zone_tld_list as _zone_tld_list,
)
from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import console, output_options, print_detail
from orca_cli.services.dns import DnsService


@click.group("tld")
def tld() -> None:
    """Manage Designate Top-Level Domains (admin)."""


@click.command("show")
@click.argument("tld_id")
@output_options
@click.pass_context
def tld_show(ctx: click.Context, tld_id: str, output_format: str,
             columns: tuple[str, ...], fit_width: bool,
             max_width: int | None, noindent: bool) -> None:
    """Show a Designate TLD."""
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_tld(tld_id)
    if not data:
        raise OrcaCLIError(f"TLD {tld_id!r} not found.")
    print_detail(
        [(k, str(v)) for k, v in data.items()],
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
    )


@click.command("set")
@click.argument("tld_id")
@click.option("--name", default=None, help="New TLD name (e.g. ``com``).")
@click.option("--description", default=None, help="Update the description.")
@click.pass_context
def tld_set(ctx: click.Context, tld_id: str, name: str | None,
            description: str | None) -> None:
    """Update a Designate TLD."""
    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if not body:
        raise OrcaCLIError("Nothing to update — pass --name or --description.")
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    svc.update_tld(tld_id, body)
    console.print(f"[green]TLD {tld_id} updated.[/green]")


# Top-level ``tld`` group (OSC parity).
tld.add_command(_zone_tld_list, name="list")
tld.add_command(_zone_tld_create, name="create")
tld.add_command(_zone_tld_delete, name="delete")
tld.add_command(tld_show, name="show")
tld.add_command(tld_set, name="set")

# Also expose ``show`` / ``set`` under the existing ``zone tld`` group.
_zone_tld.add_command(tld_show, name="show")
_zone_tld.add_command(tld_set, name="set")
