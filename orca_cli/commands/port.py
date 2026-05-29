"""``orca port`` — top-level OSC-parity alias for ``orca network port``.

OSC exposes ``openstack port create / delete / list / set / show /
unset`` directly under the top-level. orca's primary path is
``orca network port …`` — this module re-exports the same group at
the top level so OSC muscle memory transfers.
"""

from __future__ import annotations

import click

from orca_cli.commands.network import network_port as _network_port


@click.group("port")
def port() -> None:
    """Manage Neutron ports (alias of ``orca network port``)."""


for _name in _network_port.list_commands(None):
    port.add_command(_network_port.get_command(None, _name), name=_name)
