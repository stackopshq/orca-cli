"""``orca allocation`` — top-level OSC-parity alias for ``placement
allocation`` (notably ``allocation candidate list``).
"""

from __future__ import annotations

import click

from orca_cli.commands.placement import placement_allocation as _alloc_group


@click.group("allocation")
def allocation() -> None:
    """Placement allocations — OSC parity."""


for _n in _alloc_group.list_commands(None):
    # Skip hyphenated names (legacy aliases). The OSC-friendly forms
    # (``allocation candidate list``, ``allocation show``, etc.) are
    # re-exposed through the canonical sub-groups.
    if "-" in _n:
        continue
    allocation.add_command(_alloc_group.get_command(None, _n), name=_n)
