"""``shark volume`` — manage block storage volumes (Cinder)."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext
from shark_cli.core.validators import validate_id

console = Console()


def _volume_url(client) -> str:
    """Resolve the Cinder (volumev3) endpoint."""
    return client._endpoint_for("volumev3")


@click.group()
@click.pass_context
def volume(ctx: click.Context) -> None:
    """Manage block storage volumes."""
    pass


@volume.command("list")
@click.pass_context
def volume_list(ctx: click.Context) -> None:
    """List volumes."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{_volume_url(client)}/volumes/detail"
    data = client.get(url)

    volumes = data.get("volumes", [])

    if not volumes:
        console.print("[yellow]No volumes found.[/yellow]")
        return

    table = Table(title="Volumes", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Size (GB)", justify="right")
    table.add_column("Status", style="green")
    table.add_column("Type")
    table.add_column("Attached To")

    for vol in volumes:
        attachments = vol.get("attachments", [])
        attached = ", ".join(a.get("server_id", "") for a in attachments) or "—"
        table.add_row(
            vol.get("id", ""),
            vol.get("name", "") or "—",
            str(vol.get("size", "")),
            vol.get("status", ""),
            vol.get("volume_type", "") or "—",
            attached,
        )

    console.print(table)


@volume.command("show")
@click.argument("volume_id", callback=validate_id)
@click.pass_context
def volume_show(ctx: click.Context, volume_id: str) -> None:
    """Show volume details."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{_volume_url(client)}/volumes/{volume_id}"
    data = client.get(url)

    vol = data.get("volume", data)

    table = Table(title=f"Volume {vol.get('name') or volume_id}", show_lines=True)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value")

    for key, value in vol.items():
        table.add_row(str(key), str(value))

    console.print(table)


@volume.command("create")
@click.option("--name", required=True, help="Volume name.")
@click.option("--size", required=True, type=int, help="Size in GB.")
@click.option("--type", "volume_type", default=None, help="Volume type.")
@click.pass_context
def volume_create(ctx: click.Context, name: str, size: int, volume_type: str | None) -> None:
    """Create a volume."""
    client = ctx.find_object(SharkContext).ensure_client()

    body: dict = {"name": name, "size": size}
    if volume_type:
        body["volume_type"] = volume_type

    url = f"{_volume_url(client)}/volumes"
    data = client.post(url, json={"volume": body})

    vol = data.get("volume", data)
    console.print(f"[green]Volume '{vol.get('name')}' ({vol.get('id')}) created — {size} GB.[/green]")


@volume.command("delete")
@click.argument("volume_id", callback=validate_id)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def volume_delete(ctx: click.Context, volume_id: str, yes: bool) -> None:
    """Delete a volume."""
    if not yes:
        click.confirm(f"Delete volume {volume_id}?", abort=True)

    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{_volume_url(client)}/volumes/{volume_id}"
    client.delete(url)
    console.print(f"[green]Volume {volume_id} deleted.[/green]")
