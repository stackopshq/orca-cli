"""``orca ca`` — Barbican Certificate Authorities (OSC parity).

OSC paths: ``ca list``, ``ca get CA_ID``.
"""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import output_options, print_detail, print_list
from orca_cli.services.key_manager import KeyManagerService


@click.group("ca")
def ca() -> None:
    """Barbican Certificate Authorities (admin)."""


@ca.command("list")
@output_options
@click.pass_context
def ca_list(ctx: click.Context, output_format: str,
            columns: tuple[str, ...], fit_width: bool,
            max_width: int | None, noindent: bool) -> None:
    """List Certificate Authorities registered with Barbican."""
    svc = KeyManagerService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_cas()
    print_list(
        items,
        [
            ("ID", "ca_id", {"style": "cyan", "no_wrap": True}),
            ("Plugin", "plugin_name"),
            ("Plugin CA ID", "plugin_ca_id"),
            ("Description", "description"),
        ],
        title="Barbican Certificate Authorities",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No CAs registered.",
    )


@ca.command("get")
@click.argument("ca_id")
@output_options
@click.pass_context
def ca_get(ctx: click.Context, ca_id: str, output_format: str,
           columns: tuple[str, ...], fit_width: bool,
           max_width: int | None, noindent: bool) -> None:
    """Show a Certificate Authority by ID."""
    svc = KeyManagerService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_ca(ca_id)
    if not data:
        raise OrcaCLIError(f"Certificate Authority {ca_id!r} not found.")
    print_detail(
        [(k, str(v)) for k, v in data.items()],
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
    )
