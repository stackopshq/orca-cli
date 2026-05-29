"""``orca acl`` — top-level OSC-parity alias for Barbican ACL verbs."""

from __future__ import annotations

import click

from orca_cli.commands.secret import (
    secret_acl_delete as _acl_delete,
)
from orca_cli.commands.secret import (
    secret_acl_get as _acl_get,
)
from orca_cli.commands.secret import (
    secret_acl_set as _acl_submit,
)
from orca_cli.commands.secret import (
    secret_acl_user as _acl_user_grp,
)


@click.group("acl")
def acl() -> None:
    """Barbican secret ACLs — OSC parity top-level."""


acl.add_command(_acl_get, name="get")
acl.add_command(_acl_submit, name="submit")
acl.add_command(_acl_delete, name="delete")
acl.add_command(_acl_user_grp, name="user")
