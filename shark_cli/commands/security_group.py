"""``shark security-group`` — manage security groups (Neutron)."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext
from shark_cli.core.validators import validate_id

console = Console()


@click.group("security-group")
@click.pass_context
def security_group(ctx: click.Context) -> None:
    """Manage security groups."""
    pass


@security_group.command("list")
@click.pass_context
def sg_list(ctx: click.Context) -> None:
    """List security groups."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.network_url}/v2.0/security-groups"
    data = client.get(url)

    groups = data.get("security_groups", [])

    if not groups:
        console.print("[yellow]No security groups found.[/yellow]")
        return

    table = Table(title="Security Groups", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Rules", justify="right")

    for sg in groups:
        table.add_row(
            sg.get("id", ""),
            sg.get("name", ""),
            sg.get("description", "") or "—",
            str(len(sg.get("security_group_rules", []))),
        )

    console.print(table)


@security_group.command("show")
@click.argument("group_id", callback=validate_id)
@click.pass_context
def sg_show(ctx: click.Context, group_id: str) -> None:
    """Show security group details and rules."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.network_url}/v2.0/security-groups/{group_id}"
    data = client.get(url)

    sg = data.get("security_group", data)

    console.print(f"\n[bold]{sg.get('name', group_id)}[/bold]  ({sg.get('id', '')})")
    console.print(f"  {sg.get('description', '')}\n")

    rules = sg.get("security_group_rules", [])
    if not rules:
        console.print("[yellow]No rules.[/yellow]")
        return

    table = Table(title="Rules", show_lines=True)
    table.add_column("Direction")
    table.add_column("Ether Type")
    table.add_column("Protocol")
    table.add_column("Port Range")
    table.add_column("Remote IP / Group")

    for r in rules:
        port_min = r.get("port_range_min")
        port_max = r.get("port_range_max")
        if port_min and port_max:
            port_range = f"{port_min}-{port_max}" if port_min != port_max else str(port_min)
        else:
            port_range = "any"

        remote = r.get("remote_ip_prefix") or r.get("remote_group_id") or "any"

        table.add_row(
            r.get("direction", ""),
            r.get("ethertype", ""),
            r.get("protocol") or "any",
            port_range,
            remote,
        )

    console.print(table)
