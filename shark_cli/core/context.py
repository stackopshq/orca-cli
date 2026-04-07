"""Shared Click context object for shark-cli."""

from __future__ import annotations

from shark_cli.core.client import SharkClient
from shark_cli.core.config import config_is_complete, load_config
from shark_cli.core.exceptions import SharkCLIError


class SharkContext:
    """Bag object attached to ``click.Context.obj`` to share state across commands."""

    def __init__(self) -> None:
        self.client: SharkClient | None = None

    def ensure_client(self) -> SharkClient:
        """Lazily build and return the API client, raising a clear error if
        credentials are missing."""
        if self.client is not None:
            return self.client

        config = load_config()
        if not config_is_complete(config):
            raise SharkCLIError(
                "Incomplete configuration. Run 'shark setup' to provide your "
                "Sharktech credentials (auth_url, username, password, domain_id, project_id)."
            )

        self.client = SharkClient(
            auth_url=config["auth_url"],
            username=config["username"],
            password=config["password"],
            domain_id=config["domain_id"],
            project_id=config["project_id"],
            insecure=str(config.get("insecure", "false")).lower() in ("true", "1", "yes"),
        )
        return self.client
