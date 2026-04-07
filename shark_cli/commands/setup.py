"""``shark setup`` — interactive assistant to configure OpenStack credentials."""

from __future__ import annotations

import click
from rich.console import Console

from shark_cli.core.config import load_config, save_config

console = Console()

_FIELDS = [
    ("auth_url", "Auth URL (Keystone)", "https://cloud-xx.sharktech.net:5000"),
    ("username", "Username", ""),
    ("password", "Password", ""),
    ("domain_id", "Domain ID", ""),
    ("project_id", "Project ID", ""),
    ("insecure", "Skip SSL verification (true/false)", "true"),
]


@click.command()
def setup() -> None:
    """Interactive assistant to configure your Sharktech Cloud credentials.

    The values can be found in your Sharktech Client Area under the cloud
    service information page.
    """
    console.print("\n[bold cyan]Sharktech CLI Setup[/bold cyan]")
    console.print(
        "[dim]Values are available in your Sharktech portal → cloud service info page.[/dim]\n"
    )

    existing = load_config()
    config_data = {}

    for key, label, placeholder in _FIELDS:
        default = existing.get(key, placeholder)
        hide = key == "password"
        value = click.prompt(
            f"  {label}",
            default=default if not hide else (default or None),
            hide_input=hide,
            confirmation_prompt=hide,
        )
        config_data[key] = value

    path = save_config(config_data)
    console.print(f"\n[green]Configuration saved to {path} (permissions 600).[/green]\n")
