"""``shark image`` — list available images (Glance via Nova)."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext

console = Console()


@click.group()
@click.pass_context
def image(ctx: click.Context) -> None:
    """Manage images."""
    pass


@image.command("list")
@click.pass_context
def image_list(ctx: click.Context) -> None:
    """List available images."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/images/detail"
    data = client.get(url)

    images = data.get("images", [])

    if not images:
        console.print("[yellow]No images found.[/yellow]")
        return

    table = Table(title="Images", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Status", style="green")
    table.add_column("Min Disk (GB)", justify="right")
    table.add_column("Min RAM (MB)", justify="right")

    for img in sorted(images, key=lambda x: x.get("name", "")):
        table.add_row(
            img.get("id", ""),
            img.get("name", ""),
            img.get("status", ""),
            str(img.get("minDisk", "")),
            str(img.get("minRam", "")),
        )

    console.print(table)
