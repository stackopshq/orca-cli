"""``orca resource`` — top-level OSC-parity alias for the Placement
``resource class``, ``resource provider`` and ``resource usage`` verbs.
"""

from __future__ import annotations

import click

from orca_cli.commands.placement import (
    placement_resource_class as _rc_group,
)
from orca_cli.commands.placement import (
    placement_resource_provider as _rp_group,
)
from orca_cli.commands.placement import (
    placement_usage as _usage_group,
)


@click.group("resource")
def resource() -> None:
    """Placement resources (class / provider / usage) — OSC parity."""


resource.add_command(_rc_group, name="class")
resource.add_command(_rp_group, name="provider")
resource.add_command(_usage_group, name="usage")
