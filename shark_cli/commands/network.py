"""``shark network`` — manage networks (Neutron)."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext
from shark_cli.core.validators import validate_id

console = Console()


@click.group()
@click.pass_context
def network(ctx: click.Context) -> None:
    """Manage networks."""
    pass


@network.command("list")
@click.pass_context
def network_list(ctx: click.Context) -> None:
    """List networks."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.network_url}/v2.0/networks"
    data = client.get(url)

    networks = data.get("networks", [])

    if not networks:
        console.print("[yellow]No networks found.[/yellow]")
        return

    table = Table(title="Networks", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Subnets")
    table.add_column("Status", style="green")
    table.add_column("Shared")

    for net in networks:
        subnets = ", ".join(net.get("subnets", [])) or "—"
        table.add_row(
            str(net.get("id", "")),
            net.get("name", ""),
            subnets,
            net.get("status", ""),
            str(net.get("shared", "")),
        )

    console.print(table)


@network.command("show")
@click.argument("network_id", callback=validate_id)
@click.pass_context
def network_show(ctx: click.Context, network_id: str) -> None:
    """Show network details."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.network_url}/v2.0/networks/{network_id}"
    data = client.get(url)

    net = data.get("network", data)

    table = Table(title=f"Network {net.get('name', network_id)}", show_lines=True)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value")

    for key, value in net.items():
        table.add_row(str(key), str(value))

    console.print(table)
