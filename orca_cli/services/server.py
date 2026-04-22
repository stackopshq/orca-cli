"""High-level operations on Nova servers."""

from __future__ import annotations

from typing import Any

from orca_cli.core.client import OrcaClient
from orca_cli.models.server import Server


class ServerService:
    """Typed wrapper around the Nova ``/servers`` endpoints.

    Owns URL construction; commands import this service instead of
    building ``f"{client.compute_url}/servers/..."`` strings themselves.
    Retry, auth, and rate-limit handling live in OrcaClient — the
    service is purely a translation layer between the Nova API and the
    typed model.
    """

    def __init__(self, client: OrcaClient) -> None:
        self._client = client
        self._base = f"{client.compute_url}/servers"

    # ── reads ──────────────────────────────────────────────────────────

    def find(self, limit: int = 50, *,
             params: dict[str, Any] | None = None) -> list[Server]:
        """Return up to ``limit`` servers with their detail payload.

        Named ``find`` rather than ``list`` to avoid shadowing the
        builtin within the class scope (mypy then can't resolve
        ``list[Server]`` annotations on sibling methods).
        """
        merged = {"limit": limit, **(params or {})}
        data = self._client.get(f"{self._base}/detail", params=merged)
        return data.get("servers", [])

    def find_all(self, page_size: int = 1000, *,
                 params: dict[str, Any] | None = None) -> list[Server]:
        """Paginate through every server in the project (no silent cap)."""
        return self._client.paginate(f"{self._base}/detail", "servers",
                                     page_size=page_size, params=params)

    def get(self, server_id: str) -> Server:
        """Fetch one server by ID. Raises APIError if not found."""
        data = self._client.get(f"{self._base}/{server_id}")
        return data.get("server", data)

    def get_password(self, server_id: str) -> str:
        """Return the (still-encrypted) admin password set at boot, or ''."""
        data = self._client.get(f"{self._base}/{server_id}/os-server-password")
        return data.get("password", "") if data else ""

    def get_console_log(self, server_id: str, length: int | None = None) -> str:
        body: dict[str, Any] = {}
        if length is not None:
            body["length"] = length
        data = self._client.post(f"{self._base}/{server_id}/action",
                                 json={"os-getConsoleOutput": body})
        return data.get("output", "") if data else ""

    def get_console_url(self, server_id: str, *, protocol: str,
                        console_type: str) -> str:
        """Return a one-shot console URL via the modern /remote-consoles endpoint.

        ``protocol`` is one of ``vnc``/``spice``/``rdp``/``serial``;
        ``console_type`` is the corresponding subtype (e.g. ``novnc``,
        ``spice-html5``). Replaces the deprecated ``os-get*Console``
        action verbs.
        """
        data = self._client.post(
            f"{self._base}/{server_id}/remote-consoles",
            json={"remote_console": {"protocol": protocol, "type": console_type}},
        )
        if data and "remote_console" in data:
            return data["remote_console"].get("url", "")
        return ""

    def list_volume_attachments(self, server_id: str) -> list[dict]:
        data = self._client.get(f"{self._base}/{server_id}/os-volume_attachments")
        return data.get("volumeAttachments", [])

    def list_interfaces(self, server_id: str) -> list[dict]:
        data = self._client.get(f"{self._base}/{server_id}/os-interface")
        return data.get("interfaceAttachments", [])

    def list_metadata(self, server_id: str) -> dict[str, str]:
        data = self._client.get(f"{self._base}/{server_id}/metadata")
        return data.get("metadata", {})

    def list_tags(self, server_id: str) -> list[str]:
        data = self._client.get(f"{self._base}/{server_id}/tags")
        return data.get("tags", [])

    def list_migrations(self, server_id: str) -> list[dict]:
        data = self._client.get(f"{self._base}/{server_id}/migrations")
        return data.get("migrations", [])

    def get_migration(self, server_id: str, migration_id: str) -> dict:
        data = self._client.get(f"{self._base}/{server_id}/migrations/{migration_id}")
        return data.get("migration", data) if data else {}

    # ── writes ─────────────────────────────────────────────────────────

    def create(self, body: dict[str, Any]) -> Server:
        """POST /servers with the full body. Returns the created server."""
        data = self._client.post(self._base, json={"server": body})
        return data.get("server", data) if data else {}

    def update(self, server_id: str, body: dict[str, Any]) -> Server:
        """PUT /servers/{id} with a partial body (e.g. {'name': 'new'})."""
        data = self._client.put(f"{self._base}/{server_id}", json={"server": body})
        return data.get("server", data) if data else {}

    def rename(self, server_id: str, new_name: str) -> Server:
        return self.update(server_id, {"name": new_name})

    def delete(self, server_id: str) -> None:
        """Issue an asynchronous delete; the server transitions to DELETED."""
        self._client.delete(f"{self._base}/{server_id}")

    def set_metadata(self, server_id: str, kv: dict[str, str]) -> dict[str, str]:
        """Merge keys into the server metadata (POST is a partial update)."""
        data = self._client.post(f"{self._base}/{server_id}/metadata",
                                 json={"metadata": kv})
        return data.get("metadata", {}) if data else {}

    def delete_metadata_key(self, server_id: str, key: str) -> None:
        self._client.delete(f"{self._base}/{server_id}/metadata/{key}")

    def add_tag(self, server_id: str, tag: str) -> None:
        self._client.put(f"{self._base}/{server_id}/tags/{tag}")

    def delete_tag(self, server_id: str, tag: str) -> None:
        self._client.delete(f"{self._base}/{server_id}/tags/{tag}")

    def set_tags(self, server_id: str, tags: list[str]) -> list[str]:
        """Bulk replace the server's tag set (Nova ``PUT /servers/{id}/tags``)."""
        data = self._client.put(f"{self._base}/{server_id}/tags",
                                json={"tags": list(tags)})
        return data.get("tags", []) if data else []

    def delete_all_tags(self, server_id: str) -> None:
        self._client.delete(f"{self._base}/{server_id}/tags")

    # ── volume attachments ─────────────────────────────────────────────

    def attach_volume(self, server_id: str, volume_id: str,
                      device: str | None = None) -> dict:
        body: dict[str, Any] = {"volumeId": volume_id}
        if device:
            body["device"] = device
        data = self._client.post(f"{self._base}/{server_id}/os-volume_attachments",
                                 json={"volumeAttachment": body})
        return data.get("volumeAttachment", data) if data else {}

    def detach_volume(self, server_id: str, volume_id: str) -> None:
        self._client.delete(
            f"{self._base}/{server_id}/os-volume_attachments/{volume_id}"
        )

    # ── network interface attachments ──────────────────────────────────

    def attach_interface(self, server_id: str, *,
                         port_id: str | None = None,
                         net_id: str | None = None,
                         fixed_ips: list[dict] | None = None) -> dict:
        body: dict[str, Any] = {}
        if port_id:
            body["port_id"] = port_id
        if net_id:
            body["net_id"] = net_id
        if fixed_ips:
            body["fixed_ips"] = fixed_ips
        data = self._client.post(f"{self._base}/{server_id}/os-interface",
                                 json={"interfaceAttachment": body})
        return data.get("interfaceAttachment", data) if data else {}

    def detach_interface(self, server_id: str, port_id: str) -> None:
        self._client.delete(f"{self._base}/{server_id}/os-interface/{port_id}")

    # ── action verbs ───────────────────────────────────────────────────

    def action(self, server_id: str, body: dict[str, Any]) -> dict | None:
        """POST a Nova action verb (returns the response if any)."""
        return self._client.post(f"{self._base}/{server_id}/action", json=body)

    def start(self, server_id: str) -> None:
        self.action(server_id, {"os-start": None})

    def stop(self, server_id: str) -> None:
        self.action(server_id, {"os-stop": None})

    def reboot(self, server_id: str, *, hard: bool = False) -> None:
        self.action(server_id, {"reboot": {"type": "HARD" if hard else "SOFT"}})

    def pause(self, server_id: str) -> None:
        self.action(server_id, {"pause": None})

    def unpause(self, server_id: str) -> None:
        self.action(server_id, {"unpause": None})

    def suspend(self, server_id: str) -> None:
        self.action(server_id, {"suspend": None})

    def resume(self, server_id: str) -> None:
        self.action(server_id, {"resume": None})

    def lock(self, server_id: str) -> None:
        self.action(server_id, {"lock": None})

    def unlock(self, server_id: str) -> None:
        self.action(server_id, {"unlock": None})

    def shelve(self, server_id: str) -> None:
        self.action(server_id, {"shelve": None})

    def unshelve(self, server_id: str) -> None:
        self.action(server_id, {"unshelve": None})

    def rescue(self, server_id: str, *, image: str | None = None,
               admin_pass: str | None = None) -> dict | None:
        body: dict[str, Any] = {}
        if image:
            body["rescue_image_ref"] = image
        if admin_pass:
            body["adminPass"] = admin_pass
        return self.action(server_id, {"rescue": body if body else None})

    def unrescue(self, server_id: str) -> None:
        self.action(server_id, {"unrescue": None})

    def resize(self, server_id: str, flavor_id: str) -> None:
        self.action(server_id, {"resize": {"flavorRef": flavor_id}})

    def confirm_resize(self, server_id: str) -> None:
        self.action(server_id, {"confirmResize": None})

    def revert_resize(self, server_id: str) -> None:
        self.action(server_id, {"revertResize": None})

    def rebuild(self, server_id: str, image: str, *,
                name: str | None = None,
                admin_pass: str | None = None) -> Server:
        body: dict[str, Any] = {"imageRef": image}
        if name:
            body["name"] = name
        if admin_pass:
            body["adminPass"] = admin_pass
        data = self.action(server_id, {"rebuild": body})
        return data.get("server", data) if data else {}

    def create_image(self, server_id: str, image_name: str,
                     metadata: dict[str, str] | None = None) -> None:
        body: dict[str, Any] = {"name": image_name}
        if metadata:
            body["metadata"] = metadata
        self.action(server_id, {"createImage": body})

    def add_security_group(self, server_id: str, sg_name: str) -> None:
        self.action(server_id, {"addSecurityGroup": {"name": sg_name}})

    def remove_security_group(self, server_id: str, sg_name: str) -> None:
        self.action(server_id, {"removeSecurityGroup": {"name": sg_name}})

    def add_fixed_ip(self, server_id: str, network_id: str) -> None:
        self.action(server_id, {"addFixedIp": {"networkId": network_id}})

    def remove_fixed_ip(self, server_id: str, address: str) -> None:
        self.action(server_id, {"removeFixedIp": {"address": address}})

    def evacuate(self, server_id: str, *, host: str | None = None,
                 admin_pass: str | None = None,
                 on_shared_storage: bool = False) -> dict | None:
        body: dict[str, Any] = {"onSharedStorage": on_shared_storage}
        if host:
            body["host"] = host
        if admin_pass:
            body["adminPass"] = admin_pass
        return self.action(server_id, {"evacuate": body})

    def migrate(self, server_id: str, host: str | None = None) -> None:
        body: dict[str, Any] = {}
        if host:
            body["host"] = host
        self.action(server_id, {"migrate": body if body else None})

    def live_migrate(self, server_id: str, *, host: str | None = None,
                     block_migration: bool = False) -> None:
        body: dict[str, Any] = {"host": host, "block_migration": block_migration}
        self.action(server_id, {"os-migrateLive": body})

    def dump_create(self, server_id: str) -> None:
        self.action(server_id, {"trigger_crash_dump": None})

    def restore(self, server_id: str) -> None:
        """Restore a soft-deleted server."""
        self.action(server_id, {"restore": None})

    # ── migration sub-resource ─────────────────────────────────────────

    def abort_migration(self, server_id: str, migration_id: str) -> None:
        self._client.delete(f"{self._base}/{server_id}/migrations/{migration_id}")

    def force_complete_migration(self, server_id: str, migration_id: str) -> None:
        self._client.post(
            f"{self._base}/{server_id}/migrations/{migration_id}/action",
            json={"force_complete": None},
        )
