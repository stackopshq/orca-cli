"""``shark keypair`` — manage SSH key pairs (Nova)."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from shark_cli.core.context import SharkContext

console = Console()

_DEFAULT_KEY_DIR = Path.home() / ".ssh"


@click.group()
@click.pass_context
def keypair(ctx: click.Context) -> None:
    """Manage SSH key pairs."""
    pass


# ── list ──────────────────────────────────────────────────────────────────

@keypair.command("list")
@click.pass_context
def keypair_list(ctx: click.Context) -> None:
    """List key pairs."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/os-keypairs"
    data = client.get(url)

    keypairs = data.get("keypairs", [])

    if not keypairs:
        console.print("[yellow]No key pairs found.[/yellow]")
        return

    table = Table(title="Key Pairs", show_lines=True)
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Fingerprint", style="dim")

    for kp_wrapper in keypairs:
        kp = kp_wrapper.get("keypair", kp_wrapper)
        table.add_row(
            kp.get("name", ""),
            kp.get("type", "ssh"),
            kp.get("fingerprint", ""),
        )

    console.print(table)


# ── show ──────────────────────────────────────────────────────────────────

@keypair.command("show")
@click.argument("name")
@click.pass_context
def keypair_show(ctx: click.Context, name: str) -> None:
    """Show key pair details (fingerprint & public key)."""
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/os-keypairs/{name}"
    data = client.get(url)

    kp = data.get("keypair", data)

    table = Table(title=f"Key Pair: {kp.get('name', name)}", show_lines=True)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value")

    table.add_row("Name", kp.get("name", ""))
    table.add_row("Type", kp.get("type", "ssh"))
    table.add_row("Fingerprint", kp.get("fingerprint", ""))
    table.add_row("Created", kp.get("created_at", ""))

    console.print(table)

    pub_key = kp.get("public_key", "")
    if pub_key:
        console.print("\n[bold]Public key:[/bold]")
        console.print(pub_key.strip())
        console.print()


# ── create ────────────────────────────────────────────────────────────────

@keypair.command("create")
@click.argument("name")
@click.option(
    "--save-to",
    type=click.Path(),
    default=None,
    help="Path to save the private key. Default: ~/.ssh/<name>.pem",
)
@click.pass_context
def keypair_create(ctx: click.Context, name: str, save_to: str | None) -> None:
    """Generate a new key pair.

    OpenStack generates both keys. The private key is returned ONCE
    and saved locally. The public key is stored server-side.
    """
    client = ctx.find_object(SharkContext).ensure_client()

    url = f"{client.compute_url}/os-keypairs"
    data = client.post(url, json={"keypair": {"name": name}})

    kp = data.get("keypair", data)
    fingerprint = kp.get("fingerprint", "")
    private_key = kp.get("private_key", "")

    console.print(f"\n[bold green]Key pair '{kp.get('name')}' created.[/bold green]")
    console.print(f"  [cyan]Fingerprint:[/cyan] {fingerprint}")

    if private_key:
        # Determine save path
        dest = Path(save_to) if save_to else _DEFAULT_KEY_DIR / f"{name}.pem"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(private_key)
        dest.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600

        console.print(f"  [cyan]Private key saved to:[/cyan] {dest}")
        console.print(f"  [dim]Permissions set to 600.[/dim]")
        console.print(f"\n[bold yellow]This private key will NOT be shown again.[/bold yellow]")
        console.print(f"\n  ssh -i {dest} <user>@<ip>\n")
    else:
        console.print("[yellow]No private key returned (unexpected).[/yellow]")


# ── generate (local keygen + upload) ──────────────────────────────────────

@keypair.command("generate")
@click.argument("name")
@click.option(
    "--type", "key_type",
    type=click.Choice(["ed25519", "rsa", "ecdsa"], case_sensitive=False),
    default="ed25519",
    show_default=True,
    help="Key algorithm.",
)
@click.option("--bits", default=None, type=int, help="Key size (RSA only, default 4096).")
@click.option(
    "--save-to",
    type=click.Path(),
    default=None,
    help="Private key path. Default: ~/.ssh/shark-<name>",
)
@click.pass_context
def keypair_generate(ctx: click.Context, name: str, key_type: str, bits: int | None, save_to: str | None) -> None:
    """Generate a key pair locally and upload the public key.

    The private key NEVER leaves your machine.

    \b
    Examples:
      shark keypair generate my-key
      shark keypair generate my-key --type rsa --bits 4096
    """
    import subprocess

    # Determine paths
    priv_path = Path(save_to) if save_to else _DEFAULT_KEY_DIR / f"shark-{name}"
    pub_path = Path(f"{priv_path}.pub")

    if priv_path.exists():
        raise click.ClickException(f"File already exists: {priv_path}")

    priv_path.parent.mkdir(parents=True, exist_ok=True)

    # Build ssh-keygen command
    cmd = [
        "ssh-keygen",
        "-t", key_type.lower(),
        "-f", str(priv_path),
        "-N", "",  # no passphrase
        "-C", f"shark-cli:{name}",
    ]
    if key_type.lower() == "rsa":
        cmd.extend(["-b", str(bits or 4096)])

    console.print(f"[dim]Generating {key_type} key pair...[/dim]")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise click.ClickException(f"ssh-keygen failed: {result.stderr.strip()}")

    # Set permissions
    priv_path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600

    console.print(f"  [cyan]Private key:[/cyan] {priv_path}")
    console.print(f"  [cyan]Public key:[/cyan]  {pub_path}")

    # Upload public key to OpenStack
    pub_content = pub_path.read_text().strip()
    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/os-keypairs"
    data = client.post(url, json={"keypair": {"name": name, "public_key": pub_content}})

    kp = data.get("keypair", data)
    console.print(f"\n[bold green]Key pair '{name}' generated and uploaded![/bold green]")
    console.print(f"  [cyan]Fingerprint:[/cyan] {kp.get('fingerprint', '')}")
    console.print(f"\n  ssh -i {priv_path} <user>@<ip>\n")


# ── upload (import public key) ────────────────────────────────────────────

@keypair.command("upload")
@click.argument("name")
@click.option(
    "--public-key-file",
    type=click.Path(exists=True),
    default=None,
    help="Path to public key file. Default: ~/.ssh/id_rsa.pub",
)
@click.option(
    "--public-key",
    "public_key_string",
    default=None,
    help="Public key content as string (e.g. 'ssh-rsa AAAA...').",
)
@click.pass_context
def keypair_upload(ctx: click.Context, name: str, public_key_file: str | None, public_key_string: str | None) -> None:
    """Import an existing public key.

    \b
    Examples:
      shark keypair upload my-key --public-key-file ~/.ssh/id_ed25519.pub
      shark keypair upload my-key --public-key "ssh-ed25519 AAAA..."
    """
    # Resolve the public key content
    if public_key_string:
        pub_content = public_key_string.strip()
    elif public_key_file:
        pub_content = Path(public_key_file).read_text().strip()
    else:
        # Default: try ~/.ssh/id_rsa.pub, then id_ed25519.pub
        for default_name in ("id_rsa.pub", "id_ed25519.pub"):
            default_path = _DEFAULT_KEY_DIR / default_name
            if default_path.exists():
                pub_content = default_path.read_text().strip()
                console.print(f"[dim]Using {default_path}[/dim]")
                break
        else:
            raise click.ClickException(
                "No public key provided and no default key found in ~/.ssh/. "
                "Use --public-key-file or --public-key."
            )

    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/os-keypairs"
    data = client.post(url, json={"keypair": {"name": name, "public_key": pub_content}})

    kp = data.get("keypair", data)
    console.print(f"\n[bold green]Public key '{kp.get('name')}' uploaded.[/bold green]")
    console.print(f"  [cyan]Fingerprint:[/cyan] {kp.get('fingerprint', '')}\n")


# ── delete ────────────────────────────────────────────────────────────────

@keypair.command("delete")
@click.argument("name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@click.pass_context
def keypair_delete(ctx: click.Context, name: str, yes: bool) -> None:
    """Delete a key pair."""
    if not yes:
        click.confirm(f"Delete key pair '{name}'?", abort=True)

    client = ctx.find_object(SharkContext).ensure_client()
    url = f"{client.compute_url}/os-keypairs/{name}"
    client.delete(url)
    console.print(f"[green]Key pair '{name}' deleted.[/green]")
