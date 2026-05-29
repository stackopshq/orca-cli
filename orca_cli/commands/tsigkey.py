"""``orca tsigkey`` — Designate TSIG keys (admin)."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import console, output_options, print_detail, print_list
from orca_cli.services.dns import DnsService

_ALGORITHMS = (
    "hmac-md5", "hmac-sha1", "hmac-sha224", "hmac-sha256",
    "hmac-sha384", "hmac-sha512",
)

_SCOPES = ("POOL", "ZONE")


@click.group("tsigkey")
def tsigkey() -> None:
    """Manage Designate TSIG keys (admin)."""


@tsigkey.command("list")
@output_options
@click.pass_context
def tsigkey_list(ctx: click.Context, output_format: str,
                 columns: tuple[str, ...], fit_width: bool,
                 max_width: int | None, noindent: bool) -> None:
    """List TSIG keys."""
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_tsigkeys()
    print_list(
        items,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Name", "name", {"style": "bold"}),
            ("Algorithm", "algorithm"),
            ("Scope", "scope"),
            ("Resource", "resource_id"),
        ],
        title="TSIG keys",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No TSIG keys.",
    )


@tsigkey.command("show")
@click.argument("tsigkey_id")
@output_options
@click.pass_context
def tsigkey_show(ctx: click.Context, tsigkey_id: str, output_format: str,
                 columns: tuple[str, ...], fit_width: bool,
                 max_width: int | None, noindent: bool) -> None:
    """Show a TSIG key."""
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_tsigkey(tsigkey_id)
    if not data:
        raise OrcaCLIError(f"TSIG key {tsigkey_id!r} not found.")
    print_detail(
        [(k, str(v)) for k, v in data.items()],
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
    )


@tsigkey.command("create")
@click.option("--name", required=True, help="TSIG key name.")
@click.option("--algorithm", required=True,
              type=click.Choice(_ALGORITHMS, case_sensitive=False))
@click.option("--secret", required=True, help="Base64 shared secret.")
@click.option("--scope", default="POOL", show_default=True,
              type=click.Choice(_SCOPES, case_sensitive=False),
              help="Scope of the key.")
@click.option("--resource-id", required=True,
              help="UUID of the pool (scope=POOL) or zone (scope=ZONE).")
@click.pass_context
def tsigkey_create(ctx: click.Context, name: str, algorithm: str,
                   secret: str, scope: str, resource_id: str) -> None:
    """Create a TSIG key."""
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    body = {
        "name": name,
        "algorithm": algorithm.lower(),
        "secret": secret,
        "scope": scope.upper(),
        "resource_id": resource_id,
    }
    data = svc.create_tsigkey(body)
    console.print(f"[green]TSIG key {name!r} created: {data.get('id', '?')}[/green]")


@tsigkey.command("set")
@click.argument("tsigkey_id")
@click.option("--name", default=None)
@click.option("--algorithm", default=None,
              type=click.Choice(_ALGORITHMS, case_sensitive=False))
@click.option("--secret", default=None)
@click.option("--scope", default=None,
              type=click.Choice(_SCOPES, case_sensitive=False))
@click.option("--resource-id", default=None)
@click.pass_context
def tsigkey_set(ctx: click.Context, tsigkey_id: str, name: str | None,
                algorithm: str | None, secret: str | None,
                scope: str | None, resource_id: str | None) -> None:
    """Update a TSIG key."""
    body: dict = {}
    if name is not None:
        body["name"] = name
    if algorithm is not None:
        body["algorithm"] = algorithm.lower()
    if secret is not None:
        body["secret"] = secret
    if scope is not None:
        body["scope"] = scope.upper()
    if resource_id is not None:
        body["resource_id"] = resource_id
    if not body:
        raise OrcaCLIError("Nothing to update — pass at least one flag.")
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    svc.update_tsigkey(tsigkey_id, body)
    console.print(f"[green]TSIG key {tsigkey_id} updated.[/green]")


@tsigkey.command("delete")
@click.argument("tsigkey_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def tsigkey_delete(ctx: click.Context, tsigkey_id: str, yes: bool) -> None:
    """Delete a TSIG key."""
    if not yes:
        click.confirm(f"Delete TSIG key {tsigkey_id}?", abort=True)
    svc = DnsService(ctx.find_object(OrcaContext).ensure_client())
    svc.delete_tsigkey(tsigkey_id)
    console.print(f"[green]TSIG key {tsigkey_id} deleted.[/green]")
