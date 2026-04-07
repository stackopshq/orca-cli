"""``shark floating-ip`` — manage floating IPs (Neutron)."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext
from shark_cli.core.validators import validate_id

console = Console()


@click.group("floating-ip")
@click.pass_context
def floating_ip(ctx: click.Context) -> None:
    """Manage floating IPs."""
    pass


@floating_ip.command("list")
@click.pass_context
def fip_list(ctx: click.Context) -> None:
    """List floating IPs."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.network_url}/v2.0/floatingips"
    data = client.get(url)

    fips = data.get("floatingips", [])

    if not fips:
        console.print("[yellow]No floating IPs found.[/yellow]")
        return

    table = Table(title="Floating IPs", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Floating IP", style="bold")
    table.add_column("Fixed IP")
    table.add_column("Port ID")
    table.add_column("Status", style="green")

    for fip in fips:
        table.add_row(
            fip.get("id", ""),
            fip.get("floating_ip_address", ""),
            fip.get("fixed_ip_address", "") or "—",
            fip.get("port_id", "") or "—",
            fip.get("status", ""),
        )

    console.print(table)


@floating_ip.command("create")
@click.option("--network", "network_id", required=True, help="External network ID.")
@click.pass_context
def fip_create(ctx: click.Context, network_id: str) -> None:
    """Allocate a floating IP from an external network."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.network_url}/v2.0/floatingips"
    data = client.post(url, json={"floatingip": {"floating_network_id": network_id}})

    fip = data.get("floatingip", data)
    console.print(f"[green]Floating IP {fip.get('floating_ip_address')} allocated ({fip.get('id')}).[/green]")


@floating_ip.command("delete")
@click.argument("floating_ip_id", callback=validate_id)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def fip_delete(ctx: click.Context, floating_ip_id: str, yes: bool) -> None:
    """Release a floating IP."""
    if not yes:
        click.confirm(f"Release floating IP {floating_ip_id}?", abort=True)

    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.network_url}/v2.0/floatingips/{floating_ip_id}"
    client.delete(url)
    console.print(f"[green]Floating IP {floating_ip_id} released.[/green]")
