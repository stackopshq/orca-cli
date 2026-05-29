"""``orca subnet`` — top-level OSC-parity alias for ``orca network subnet``.

OSC exposes ``subnet`` at the top level. orca's primary lives under
``network subnet``. Re-exported here for parity.

Note: this does **not** collide with ``subnet-pool`` (a sibling
top-level group); they are distinct names.
"""

from __future__ import annotations

import click

from orca_cli.commands.network import network_subnet as _network_subnet


@click.group("subnet")
def subnet() -> None:
    """Manage Neutron subnets (alias of ``orca network subnet``)."""


for _name in _network_subnet.list_commands(None):
    subnet.add_command(_network_subnet.get_command(None, _name), name=_name)
