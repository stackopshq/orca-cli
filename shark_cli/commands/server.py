"""``shark server`` — manage servers (Nova)."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext
from shark_cli.core.validators import validate_id

console = Console()


@click.group()
@click.pass_context
def server(ctx: click.Context) -> None:
    """Manage compute servers."""
    pass


# ── list ──────────────────────────────────────────────────────────────────

@server.command("list")
@click.option("--limit", default=50, show_default=True, help="Max number of servers to return.")
@click.pass_context
def server_list(ctx: click.Context, limit: int) -> None:
    """List servers."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/servers/detail"
    data = client.get(url, params={"limit": limit})

    servers = data.get("servers", [])

    if not servers:
        console.print("[yellow]No servers found.[/yellow]")
        return

    table = Table(title="Servers", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Status", style="green")
    table.add_column("Networks")
    table.add_column("Flavor")

    for srv in servers:
        addr_parts = []
        for net_name, addrs in srv.get("addresses", {}).items():
            for a in addrs:
                addr_parts.append(f"{net_name}={a.get('addr', '?')}")
        addresses = ", ".join(addr_parts) or "—"

        flavor = srv.get("flavor", {})
        flavor_label = flavor.get("original_name", flavor.get("id", ""))

        table.add_row(
            srv.get("id", ""),
            srv.get("name", ""),
            srv.get("status", ""),
            addresses,
            str(flavor_label),
        )

    console.print(table)


# ── show ──────────────────────────────────────────────────────────────────

@server.command("show")
@click.argument("server_id", callback=validate_id)
@click.pass_context
def server_show(ctx: click.Context, server_id: str) -> None:
    """Show server details."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/servers/{server_id}"
    data = client.get(url)

    srv = data.get("server", data)

    # Build a clean detail view
    table = Table(title=f"Server {srv.get('name', server_id)}", show_lines=True)
    table.add_column("Property", style="bold cyan", no_wrap=True)
    table.add_column("Value")

    table.add_row("ID", srv.get("id", ""))
    table.add_row("Name", srv.get("name", ""))
    table.add_row("Status", srv.get("status", ""))

    flavor = srv.get("flavor", {})
    table.add_row("Flavor", flavor.get("original_name", flavor.get("id", "")))

    image = srv.get("image", {})
    if isinstance(image, dict):
        table.add_row("Image", image.get("id", ""))

    # Addresses
    for net_name, addrs in srv.get("addresses", {}).items():
        ips = ", ".join(a.get("addr", "") for a in addrs)
        table.add_row(f"Network ({net_name})", ips)

    table.add_row("Key Name", srv.get("key_name", "") or "—")
    table.add_row("Created", srv.get("created", ""))
    table.add_row("Updated", srv.get("updated", ""))
    table.add_row("Host ID", srv.get("hostId", ""))

    # Volumes attached
    volumes = srv.get("os-extended-volumes:volumes_attached", [])
    if volumes:
        vol_ids = ", ".join(v.get("id", "") for v in volumes)
        table.add_row("Volumes", vol_ids)

    console.print(table)


# ── create ────────────────────────────────────────────────────────────────

@server.command("create")
@click.option("--name", required=True, help="Server name.")
@click.option("--flavor", "flavor_id", required=True, help="Flavor ID (see 'shark flavor list').")
@click.option("--image", "image_id", required=True, help="Image ID (see 'shark image list').")
@click.option("--disk-size", type=int, default=20, show_default=True, help="Boot volume size in GB.")
@click.option("--network", "network_id", default=None, help="Network ID (see 'shark network list').")
@click.option("--key-name", default=None, help="SSH key pair name (see 'shark keypair list').")
@click.option("--security-group", "security_groups", multiple=True, help="Security group name (repeatable).")
@click.pass_context
def server_create(
    ctx: click.Context,
    name: str,
    flavor_id: str,
    image_id: str,
    disk_size: int,
    network_id: str | None,
    key_name: str | None,
    security_groups: tuple[str, ...],
) -> None:
    """Create a new server (boot from volume).

    \b
    Example:
      shark server create \\
        --name my-vm \\
        --flavor <flavor-id> \\
        --image <image-id> \\
        --disk-size 30 \\
        --network <network-id> \\
        --key-name my-key
    """
    client = ctx.find_object(SharkContext).ensure_client()

    body: dict = {
        "name": name,
        "flavorRef": flavor_id,
        "block_device_mapping_v2": [
            {
                "boot_index": 0,
                "uuid": image_id,
                "source_type": "image",
                "destination_type": "volume",
                "volume_size": disk_size,
                "delete_on_termination": True,
            }
        ],
    }

    if network_id:
        body["networks"] = [{"uuid": network_id}]
    if key_name:
        body["key_name"] = key_name
    if security_groups:
        body["security_groups"] = [{"name": sg} for sg in security_groups]

    url = f"{client.compute_url}/servers"
    data = client.post(url, json={"server": body})

    srv = data.get("server", data)
    srv_id = srv.get("id", "?")
    admin_pass = srv.get("adminPass", "")

    console.print(f"\n[bold green]Server created successfully![/bold green]")
    console.print(f"  [cyan]ID:[/cyan]       {srv_id}")
    console.print(f"  [cyan]Name:[/cyan]     {name}")
    console.print(f"  [cyan]Disk:[/cyan]     {disk_size} GB (boot volume)")
    if admin_pass:
        console.print(f"  [cyan]Password:[/cyan] {admin_pass}")
    console.print(f"\nUse [bold]shark server show {srv_id}[/bold] to track provisioning.\n")


# ── delete ────────────────────────────────────────────────────────────────

@server.command("delete")
@click.argument("server_id", callback=validate_id)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def server_delete(ctx: click.Context, server_id: str, yes: bool) -> None:
    """Delete a server."""
    if not yes:
        click.confirm(f"Delete server {server_id}?", abort=True)

    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/servers/{server_id}"
    client.delete(url)
    console.print(f"[green]Server {server_id} deleted.[/green]")


# ── start / stop / reboot ─────────────────────────────────────────────────

def _server_action(ctx: click.Context, server_id: str, action: dict, label: str) -> None:
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/servers/{server_id}/action"
    client.post(url, json=action)
    console.print(f"[green]{label} request sent for {server_id}.[/green]")


@server.command("start")
@click.argument("server_id", callback=validate_id)
@click.pass_context
def server_start(ctx: click.Context, server_id: str) -> None:
    """Start (resume) a stopped server."""
    _server_action(ctx, server_id, {"os-start": None}, "Start")


@server.command("stop")
@click.argument("server_id", callback=validate_id)
@click.pass_context
def server_stop(ctx: click.Context, server_id: str) -> None:
    """Stop (shut down) a server."""
    _server_action(ctx, server_id, {"os-stop": None}, "Stop")


@server.command("reboot")
@click.argument("server_id", callback=validate_id)
@click.option("--hard", is_flag=True, help="Perform a hard reboot.")
@click.pass_context
def server_reboot(ctx: click.Context, server_id: str, hard: bool) -> None:
    """Reboot a server."""
    reboot_type = "HARD" if hard else "SOFT"
    _server_action(ctx, server_id, {"reboot": {"type": reboot_type}}, f"Reboot ({reboot_type})")


# ── password ──────────────────────────────────────────────────────────────

@server.command("password")
@click.argument("server_id", callback=validate_id)
@click.option(
    "--key", "private_key_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to the RSA private key used to decrypt. Tries ~/.ssh/shark-* if omitted.",
)
@click.option("--raw", is_flag=True, help="Print the encrypted password without decrypting.")
@click.pass_context
def server_password(ctx: click.Context, server_id: str, private_key_path: str | None, raw: bool) -> None:
    """Retrieve and decrypt the server admin password.

    \b
    The password is encrypted with your SSH public key at boot and
    stored in the server metadata. This command fetches it and
    decrypts it locally with your private key (RSA only).

    \b
    Examples:
      shark server password <server-id>
      shark server password <server-id> --key ~/.ssh/shark-my-key
      shark server password <server-id> --raw
    """
    import base64
    import subprocess
    import tempfile
    from pathlib import Path

    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/servers/{server_id}/os-server-password"
    data = client.get(url)

    encrypted_b64 = data.get("password", "")

    if not encrypted_b64:
        console.print("[yellow]No password set for this server (metadata empty).[/yellow]")
        console.print("[dim]The password may not be available yet if the server is still booting.[/dim]")
        return

    if raw:
        console.print(f"[bold]Encrypted password (base64):[/bold]\n{encrypted_b64}")
        return

    # Resolve private key
    key_path: Path | None = None
    if private_key_path:
        key_path = Path(private_key_path)
    else:
        ssh_dir = Path.home() / ".ssh"
        # Try shark-* keys first, then common defaults
        candidates = sorted(ssh_dir.glob("shark-*"))
        candidates = [c for c in candidates if not c.name.endswith(".pub")]
        candidates += [
            ssh_dir / "id_rsa",
            ssh_dir / "id_ecdsa",
        ]
        for candidate in candidates:
            if candidate.exists() and not candidate.name.endswith(".pub"):
                key_path = candidate
                break

    if not key_path or not key_path.exists():
        raise click.ClickException(
            "No private key found. Use --key <path> to specify your RSA private key."
        )

    console.print(f"[dim]Using key: {key_path}[/dim]")

    # Decode the base64 encrypted password
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
    except Exception:
        raise click.ClickException("Failed to decode encrypted password (invalid base64).")

    # Decrypt with openssl
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
        tmp.write(encrypted_bytes)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                "openssl", "pkeyutl", "-decrypt",
                "-inkey", str(key_path),
                "-in", tmp_path,
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            # Fallback to older rsautl for compatibility
            result = subprocess.run(
                [
                    "openssl", "rsautl", "-decrypt",
                    "-inkey", str(key_path),
                    "-in", tmp_path,
                ],
                capture_output=True,
            )

        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace").strip()
            raise click.ClickException(
                f"Decryption failed. Make sure you use the matching RSA private key.\n"
                f"  openssl error: {stderr}"
            )

        password = result.stdout.decode().strip()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    console.print(f"\n[bold green]Admin password for {server_id}:[/bold green]")
    console.print(f"  [bold]{password}[/bold]\n")


# ── console-log ───────────────────────────────────────────────────────────

@server.command("console-log")
@click.argument("server_id", callback=validate_id)
@click.option("--lines", "length", default=50, show_default=True, help="Number of lines to retrieve (0 = all).")
@click.pass_context
def server_console_log(ctx: click.Context, server_id: str, length: int) -> None:
    """Show the server console output (boot log).

    \b
    Examples:
      shark server console-log <server-id>
      shark server console-log <server-id> --lines 100
      shark server console-log <server-id> --lines 0   # all output
    """
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/servers/{server_id}/action"

    body: dict = {"os-getConsoleOutput": {}}
    if length > 0:
        body["os-getConsoleOutput"]["length"] = length

    data = client.post(url, json=body)

    output = ""
    if data:
        output = data.get("output", "")

    if not output:
        console.print("[yellow]No console output available yet.[/yellow]")
        return

    console.print(f"[bold]Console log for {server_id}[/bold] (last {length} lines):\n")
    console.print(output)


# ── console-url ───────────────────────────────────────────────────────────

@server.command("console-url")
@click.argument("server_id", callback=validate_id)
@click.option(
    "--type", "console_type",
    type=click.Choice(["novnc", "xvpvnc", "spice-html5", "rdp-html5", "serial"], case_sensitive=False),
    default="novnc",
    show_default=True,
    help="Console type.",
)
@click.pass_context
def server_console_url(ctx: click.Context, server_id: str, console_type: str) -> None:
    """Get a URL to access the server console (VNC/SPICE/serial).

    \b
    Examples:
      shark server console-url <server-id>
      shark server console-url <server-id> --type spice-html5
      shark server console-url <server-id> --type serial
    """
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/servers/{server_id}/action"

    # Map console type to the Nova action name
    action_map = {
        "novnc": "os-getVNCConsole",
        "xvpvnc": "os-getVNCConsole",
        "spice-html5": "os-getSPICEConsole",
        "rdp-html5": "os-getRDPConsole",
        "serial": "os-getSerialConsole",
    }

    action = action_map.get(console_type, "os-getVNCConsole")

    # Try the modern remote-consoles API first (microversion 2.6+)
    try:
        modern_url = f"{client.compute_url}/servers/{server_id}/remote-consoles"
        protocol_map = {
            "novnc": ("vnc", "novnc"),
            "xvpvnc": ("vnc", "xvpvnc"),
            "spice-html5": ("spice", "spice-html5"),
            "rdp-html5": ("rdp", "rdp-html5"),
            "serial": ("serial", "serial"),
        }
        protocol, remote_type = protocol_map.get(console_type, ("vnc", "novnc"))
        data = client.post(modern_url, json={
            "remote_console": {"protocol": protocol, "type": remote_type}
        })
        console_data = data.get("remote_console", data)
    except Exception:
        # Fallback to legacy action API
        data = client.post(url, json={action: {"type": console_type}})
        console_data = data.get("console", data)

    console_url = console_data.get("url", "")

    if not console_url:
        console.print("[yellow]No console URL returned.[/yellow]")
        return

    console.print(f"\n[bold]Console URL ({console_type}):[/bold]")
    console.print(f"  [cyan]{console_url}[/cyan]")
    console.print(f"\n[dim]Open this URL in your browser to access the console.[/dim]\n")
