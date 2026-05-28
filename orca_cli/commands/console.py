"""``orca console`` — OSC-parity top-level for server console access.

OSC exposes ``openstack console log show <server>`` and ``console url
show <server>``. orca's primary path is ``orca server console log``
and ``orca server console url`` — this module re-exposes them under
the top-level ``console`` group so OSC muscle memory transfers.
"""

from __future__ import annotations

import click

from orca_cli.commands.server import (
    server_console_log as _server_console_log,
)
from orca_cli.commands.server import (
    server_console_url as _server_console_url,
)


@click.group("console")
def console() -> None:
    """Inspect server consoles (log, URL) — OSC-parity alias.

    Equivalent to the primary ``orca server console …`` group.
    """


@console.group("log")
def console_log() -> None:
    """Server boot log."""


@console.group("url")
def console_url() -> None:
    """Server remote console URL."""


console_log.add_command(_server_console_log, name="show")
console_url.add_command(_server_console_url, name="show")
