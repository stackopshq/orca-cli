"""``orca block-storage`` — OSC-parity top-level for Cinder admin verbs.

OSC moved a chunk of Cinder admin commands under the top-level
``openstack block storage …`` namespace : ``cluster``, ``log level``,
``resource filter``, ``cleanup``, ``volume manageable list`` and
``snapshot manageable list``. orca's primary path is ``orca volume
…`` for the same operations — this module re-exposes those sub-
groups at the OSC path so muscle memory transfers.

ADR-0008: ``block-storage`` is a compound noun (single concept,
written with a hyphen), so the hyphenated top-level name is
allowed.
"""

from __future__ import annotations

import click

from orca_cli.commands.volume import (
    volume_cluster as _volume_cluster,
)
from orca_cli.commands.volume import (
    volume_log_level as _volume_log_level,
)
from orca_cli.commands.volume import (
    volume_manageable as _volume_manageable,
)
from orca_cli.commands.volume import (
    volume_resource_filter as _volume_resource_filter,
)
from orca_cli.commands.volume import (
    volume_snapshot as _volume_snapshot,
)
from orca_cli.core.context import OrcaContext
from orca_cli.core.output import console
from orca_cli.services.volume import VolumeService


@click.group("block-storage")
def block_storage() -> None:
    """OSC parity: ``openstack block storage …`` admin verbs."""


# Re-export the volume-level groups by name.
block_storage.add_command(_volume_cluster, name="cluster")
block_storage.add_command(_volume_log_level, name="log-level")
block_storage.add_command(_volume_resource_filter, name="resource-filter")


# ``block storage volume manageable list`` is identical to ``volume
# manageable list``. We expose a ``volume`` group under block-storage
# whose only sub-cmd is ``manageable`` (which itself has ``list``).
@block_storage.group("volume")
def block_storage_volume() -> None:
    """Volume-level admin verbs under ``block-storage``."""


block_storage_volume.add_command(_volume_manageable, name="manageable")


# ``block storage snapshot manageable list`` is identical to ``volume
# snapshot manageable list``. Re-expose the ``manageable`` sub-group.
@block_storage.group("snapshot")
def block_storage_snapshot() -> None:
    """Snapshot-level admin verbs under ``block-storage``."""


# The ``volume snapshot`` group has a ``manageable`` sub-group itself.
_snap_manageable = _volume_snapshot.get_command(None, "manageable")
if _snap_manageable is not None:
    block_storage_snapshot.add_command(_snap_manageable, name="manageable")


@block_storage.command("cleanup")
@click.option("--cluster", "cluster_name", default=None,
              help="Cluster on which to run the cleanup.")
@click.option("--host", default=None, help="Host on which to run the cleanup.")
@click.option("--binary", default=None,
              help="Service binary (e.g. cinder-volume).")
@click.option("--is-up/--not-up", "is_up", default=None,
              help="Filter on service liveness.")
@click.option("--disabled/--enabled", "disabled", default=None,
              help="Filter on the service disabled flag.")
@click.option("--resource-id", default=None,
              help="Restrict the cleanup to one resource.")
@click.option("--resource-type", default=None,
              help="Restrict the cleanup to one resource type (Volume, Snapshot, …).")
@click.option("--service-id", type=int, default=None,
              help="Restrict the cleanup to a single Cinder service ID.")
@click.pass_context
def block_storage_cleanup(ctx: click.Context, cluster_name: str | None,
                          host: str | None, binary: str | None,
                          is_up: bool | None, disabled: bool | None,
                          resource_id: str | None, resource_type: str | None,
                          service_id: int | None) -> None:
    """Run a Cinder admin cleanup (``POST /workers/cleanup``).

    Parity with ``openstack block storage cleanup`` — clears
    abandoned operations from a failed node.
    """
    svc = VolumeService(ctx.find_object(OrcaContext).ensure_client())
    filters: dict = {}
    if cluster_name:
        filters["cluster_name"] = cluster_name
    if host:
        filters["host"] = host
    if binary:
        filters["binary"] = binary
    if is_up is not None:
        filters["is_up"] = is_up
    if disabled is not None:
        filters["disabled"] = disabled
    if resource_id:
        filters["resource_id"] = resource_id
    if resource_type:
        filters["resource_type"] = resource_type
    if service_id is not None:
        filters["service_id"] = service_id
    result = svc.workers_cleanup(filters)
    cleaning = result.get("cleaning", []) or []
    unavailable = result.get("unavailable", []) or []
    console.print(
        f"[green]Cleanup triggered:[/green] "
        f"{len(cleaning)} cleaning, {len(unavailable)} unavailable."
    )
