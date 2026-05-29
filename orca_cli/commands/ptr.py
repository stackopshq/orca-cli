"""``orca ptr`` — Designate floating-IP reverse-DNS (PTR) records."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import console, output_options, print_detail, print_list
from orca_cli.services.dns import DnsService


@click.group("ptr")
def ptr() -> None:
    """Floating-IP reverse-DNS (PTR) records."""


@ptr.group("record")
def ptr_record() -> None:
    """Per-floating-IP PTR records."""


@ptr_record.command("list")
@output_options
@click.pass_context
def ptr_record_list(ctx: click.Context, output_format: str,
                    columns: tuple[str, ...], fit_width: bool,
                    max_width: int | None, noindent: bool) -> None:
    """List PTR records on all floating-IPs visible to the caller."""
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_reverse_floatingips()
    print_list(
        items,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Address", "address"),
            ("PTRDNAME", "ptrdname"),
            ("TTL", "ttl"),
            ("Status", "status"),
        ],
        title="Floating-IP PTR records",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No PTR records.",
    )


@ptr_record.command("show")
@click.argument("fip_ref", metavar="REGION:FIP_UUID")
@output_options
@click.pass_context
def ptr_record_show(ctx: click.Context, fip_ref: str, output_format: str,
                    columns: tuple[str, ...], fit_width: bool,
                    max_width: int | None, noindent: bool) -> None:
    """Show the PTR record of a floating-IP.

    REGION:FIP_UUID — same format Designate accepts on
    ``/v2/reverse/floatingips/{region}:{uuid}``.
    """
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_reverse_floatingip(fip_ref)
    if not data:
        raise OrcaCLIError(f"PTR record {fip_ref!r} not found.")
    print_detail(
        [(k, str(v)) for k, v in data.items()],
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
    )


@ptr_record.command("set")
@click.argument("fip_ref", metavar="REGION:FIP_UUID")
@click.option("--ptrdname", required=True, help="Reverse DNS name.")
@click.option("--description", default=None)
@click.option("--ttl", type=int, default=None, help="TTL in seconds.")
@click.pass_context
def ptr_record_set(ctx: click.Context, fip_ref: str, ptrdname: str,
                   description: str | None, ttl: int | None) -> None:
    """Set or update a PTR record on a floating-IP."""
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    svc.set_reverse_floatingip(fip_ref, ptrdname, description=description, ttl=ttl)
    console.print(f"[green]PTR record set on {fip_ref} → {ptrdname}.[/green]")


@ptr_record.command("unset")
@click.argument("fip_ref", metavar="REGION:FIP_UUID")
@click.pass_context
def ptr_record_unset(ctx: click.Context, fip_ref: str) -> None:
    """Clear the PTR record of a floating-IP."""
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    svc.set_reverse_floatingip(fip_ref, None)
    console.print(f"[green]PTR record cleared on {fip_ref}.[/green]")
