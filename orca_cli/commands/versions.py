"""``orca versions`` — list Keystone API versions exposed by the cloud."""

from __future__ import annotations

import click

from orca_cli.core.context import OrcaContext
from orca_cli.core.output import output_options, print_list
from orca_cli.services.identity import IdentityService


@click.group("versions")
def versions() -> None:
    """List API versions advertised by Keystone."""


@versions.command("show")
@output_options
@click.pass_context
def versions_show(
    ctx: click.Context,
    output_format: str,
    columns: tuple[str, ...],
    fit_width: bool,
    max_width: int | None,
    noindent: bool,
) -> None:
    """List Keystone API versions and their state (stable / deprecated)."""
    svc = IdentityService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_versions()
    rows = [
        {
            "id": v.get("id", ""),
            "status": v.get("status", ""),
            "updated": v.get("updated", ""),
            "url": (v.get("links", [{}])[0] or {}).get("href", ""),
        }
        for v in items
    ]
    print_list(
        rows,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Status", "status", {"style": "green"}),
            ("Updated", "updated"),
            ("URL", "url"),
        ],
        title="Keystone API versions",
        output_format=output_format,
        fit_width=fit_width,
        max_width=max_width,
        noindent=noindent,
        columns=columns,
        empty_msg="No versions advertised.",
    )
