"""``orca router`` — top-level OSC-parity alias for ``orca network router``.

Same shape as ``orca/commands/port.py``. OSC exposes ``router``
directly at the top level; orca's primary lives under ``network
router``. We re-export here so users transplanting their OSC reflex
hit the same surface.
"""

from __future__ import annotations

import click

from orca_cli.commands.network import network_router as _network_router


@click.group("router")
def router() -> None:
    """Manage Neutron routers (alias of ``orca network router``)."""


for _name in _network_router.list_commands(None):
    router.add_command(_network_router.get_command(None, _name), name=_name)
