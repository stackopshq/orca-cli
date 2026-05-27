"""``orca extension`` — list and inspect API extensions advertised by services."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import output_options, print_detail, print_list
from orca_cli.services.network import NetworkService


@click.group("extension")
def extension() -> None:
    """List or inspect API extensions enabled on this cloud.

    Currently surfaces Neutron extensions (the most actively used). OSC's
    cross-service ``openstack extension list`` aggregates several services
    — orca focuses on Neutron because that's where the meaningful
    discoverability lives (port-forwarding, metering, segment-range,
    QoS rule types, RBAC scopes, …).
    """


@extension.command("list")
@output_options
@click.pass_context
def extension_list(
    ctx: click.Context,
    output_format: str,
    columns: tuple[str, ...],
    fit_width: bool,
    max_width: int | None,
    noindent: bool,
) -> None:
    """List enabled Neutron extensions."""
    svc = NetworkService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_extensions()
    print_list(
        sorted(items, key=lambda e: e.get("alias", "")),
        [
            ("Alias", "alias", {"style": "cyan", "no_wrap": True}),
            ("Name", "name", {"style": "bold"}),
            ("Description", lambda e: (e.get("description", "") or "")[:80]),
        ],
        title="Neutron extensions",
        output_format=output_format,
        fit_width=fit_width,
        max_width=max_width,
        noindent=noindent,
        columns=columns,
        empty_msg="No extensions reported.",
    )


@extension.command("show")
@click.argument("alias")
@output_options
@click.pass_context
def extension_show(
    ctx: click.Context,
    alias: str,
    output_format: str,
    columns: tuple[str, ...],
    fit_width: bool,
    max_width: int | None,
    noindent: bool,
) -> None:
    """Show details of a single Neutron extension by alias."""
    svc = NetworkService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_extension(alias)
    if not data:
        raise OrcaCLIError(f"Extension {alias!r} not found.")
    fields = [
        ("alias", data.get("alias", "")),
        ("name", data.get("name", "")),
        ("description", data.get("description", "") or "—"),
        ("namespace", data.get("namespace", "") or "—"),
        ("updated", data.get("updated", "") or "—"),
    ]
    links = data.get("links") or []
    if links:
        fields.append(("", ""))
        fields.append(("── Links ──", ""))
        for link in links:
            fields.append((f"  {link.get('rel', '')}", link.get("href", "")))
    print_detail(
        fields,
        output_format=output_format,
        fit_width=fit_width,
        max_width=max_width,
        noindent=noindent,
        columns=columns,
    )
