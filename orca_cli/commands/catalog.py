"""``orca catalog`` — list / inspect the Keystone service catalog."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import console, output_options, print_detail, print_list


@click.group("catalog", invoke_without_command=True)
@output_options
@click.pass_context
def catalog(
    ctx: click.Context,
    output_format: str,
    columns: tuple[str, ...],
    fit_width: bool,
    max_width: int | None,
    noindent: bool,
) -> None:
    """List available service endpoints from the Keystone catalog.

    Bare ``orca catalog`` keeps the historical behaviour (equivalent to
    ``orca catalog list``); use ``orca catalog show <service>`` to drill
    into a specific service.
    """
    if ctx.invoked_subcommand is None:
        _list(ctx, output_format, columns, fit_width, max_width, noindent)


def _list(
    ctx: click.Context,
    output_format: str,
    columns: tuple[str, ...],
    fit_width: bool,
    max_width: int | None,
    noindent: bool,
) -> None:
    client = ctx.find_object(OrcaContext).ensure_client()
    if not client.catalog:
        console.print("[yellow]No service catalog available.[/yellow]")
        return

    items = []
    for svc in client.catalog:
        for ep in svc.get("endpoints", []):
            items.append(
                {
                    "service": svc.get("name", ""),
                    "type": svc.get("type", ""),
                    "interface": ep.get("interface", ""),
                    "region": ep.get("region", "") or ep.get("region_id", ""),
                    "url": ep.get("url", ""),
                }
            )

    print_list(
        items,
        [
            ("Service", "service", {"style": "bold"}),
            ("Type", "type", {"style": "cyan"}),
            ("Interface", "interface"),
            ("Region", "region"),
            ("URL", "url"),
        ],
        title="Service Catalog",
        output_format=output_format,
        fit_width=fit_width,
        max_width=max_width,
        noindent=noindent,
        columns=columns,
        empty_msg="No service catalog available.",
    )


@catalog.command("list")
@output_options
@click.pass_context
def catalog_list(
    ctx: click.Context,
    output_format: str,
    columns: tuple[str, ...],
    fit_width: bool,
    max_width: int | None,
    noindent: bool,
) -> None:
    """List all service endpoints from the Keystone catalog (OSC parity)."""
    _list(ctx, output_format, columns, fit_width, max_width, noindent)


@catalog.command("show")
@click.argument("service")
@output_options
@click.pass_context
def catalog_show(
    ctx: click.Context,
    service: str,
    output_format: str,
    columns: tuple[str, ...],
    fit_width: bool,
    max_width: int | None,
    noindent: bool,
) -> None:
    """Show all endpoints for a service (by name or type).

    \b
    Examples:
      orca catalog show compute
      orca catalog show nova
      orca catalog show identity
    """
    client = ctx.find_object(OrcaContext).ensure_client()
    matches = [svc for svc in (client.catalog or []) if svc.get("name") == service or svc.get("type") == service]
    if not matches:
        raise OrcaCLIError(f"Service {service!r} not in catalog.")

    svc = matches[0]
    fields = [
        ("name", svc.get("name", "")),
        ("type", svc.get("type", "")),
        ("id", svc.get("id", "")),
    ]
    eps = svc.get("endpoints", []) or []
    if eps:
        fields.append(("", ""))
        fields.append(("── Endpoints ──", ""))
        for ep in eps:
            label = f"  {ep.get('interface', '')} {ep.get('region', '') or ep.get('region_id', '')}"
            fields.append((label, ep.get("url", "")))

    print_detail(
        fields,
        output_format=output_format,
        fit_width=fit_width,
        max_width=max_width,
        noindent=noindent,
        columns=columns,
    )
