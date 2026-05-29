"""``orca coe`` — top-level OSC-parity alias for Magnum (Container
Orchestration Engine).

OSC's plugin namespaces every Magnum verb under ``openstack coe …``.
orca's primary surface lives directly under ``orca cluster``. This
module re-exposes the cluster group at the OSC path.
"""

from __future__ import annotations

import click

from orca_cli.commands.cluster import cluster as _cluster


@click.group("coe")
def coe() -> None:
    """Magnum Container Orchestration Engine — OSC parity top-level."""


coe.add_command(_cluster, name="cluster")
