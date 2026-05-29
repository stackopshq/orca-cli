"""``orca object-store`` — top-level OSC-parity alias for the Swift
``account`` admin verbs.

OSC moves account-level metadata under ``openstack object store
account …``. orca's primary lives under ``object account …``.
This module re-exposes the same callbacks at the OSC path.
"""

from __future__ import annotations

import click

from orca_cli.commands.object_store import (
    object_account_set as _account_set,
)
from orca_cli.commands.object_store import (
    object_account_show as _account_show,
)
from orca_cli.commands.object_store import (
    object_account_unset as _account_unset,
)


@click.group("object-store")
def object_store() -> None:
    """OSC parity: ``openstack object store …`` admin verbs."""


@object_store.group("account")
def object_store_account() -> None:
    """Swift account-level metadata."""


object_store_account.add_command(_account_set, name="set")
object_store_account.add_command(_account_show, name="show")
object_store_account.add_command(_account_unset, name="unset")
