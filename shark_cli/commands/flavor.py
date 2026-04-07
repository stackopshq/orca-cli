"""``shark flavor`` — list available flavors (Nova)."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext

console = Console()


@click.group()
@click.pass_context
def flavor(ctx: click.Context) -> None:
    """Manage flavors."""
    pass


@flavor.command("list")
@click.pass_context
def flavor_list(ctx: click.Context) -> None:
    """List available flavors."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/flavors/detail"
    data = client.get(url)

    flavors = data.get("flavors", [])

    if not flavors:
        console.print("[yellow]No flavors found.[/yellow]")
        return

    table = Table(title="Flavors", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("vCPUs", justify="right")
    table.add_column("RAM (MB)", justify="right")
    table.add_column("Disk (GB)", justify="right")

    for f in sorted(flavors, key=lambda x: (x.get("vcpus", 0), x.get("ram", 0))):
        table.add_row(
            f.get("id", ""),
            f.get("name", ""),
            str(f.get("vcpus", "")),
            str(f.get("ram", "")),
            str(f.get("disk", "")),
        )

    console.print(table)
