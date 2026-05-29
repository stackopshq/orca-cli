"""``orca trait`` — top-level OSC-parity alias for ``placement trait``."""

from __future__ import annotations

import click

from orca_cli.commands.placement import placement_trait as _trait_group


@click.group("trait")
def trait() -> None:
    """Placement traits — OSC parity."""


for _n in _trait_group.list_commands(None):
    trait.add_command(_trait_group.get_command(None, _n), name=_n)
