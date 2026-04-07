"""Configuration loader — env vars take precedence over the YAML config file.

Required fields for Sharktech (OpenStack Keystone) authentication:
  - ``auth_url``   : Keystone endpoint, e.g. ``https://cloud-xx.sharktech.net:5000``
  - ``username``   : OpenStack user name
  - ``password``   : OpenStack password
  - ``domain_id``  : OpenStack domain name / ID
  - ``project_id`` : OpenStack project name / ID
"""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

CONFIG_DIR = Path.home() / ".shark"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

# Mapping: env-var name → config key
_ENV_MAP = {
    "SHARK_AUTH_URL": "auth_url",
    "SHARK_USERNAME": "username",
    "SHARK_PASSWORD": "password",
    "SHARK_DOMAIN_ID": "domain_id",
    "SHARK_PROJECT_ID": "project_id",
    "SHARK_INSECURE": "insecure",
}

REQUIRED_KEYS = ("auth_url", "username", "password", "domain_id", "project_id")


def load_config() -> Dict[str, Any]:
    """Load configuration with the following priority:

    1. Environment variables (``SHARK_AUTH_URL``, ``SHARK_USERNAME``, …).
    2. YAML config file (``~/.shark/config.yaml``).
    """
    config: Dict[str, Any] = {}

    # --- YAML file (lowest priority) ---
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as fh:
            file_config = yaml.safe_load(fh) or {}
            config.update(file_config)

    # --- Environment variables (highest priority) ---
    for env_var, key in _ENV_MAP.items():
        value = os.environ.get(env_var)
        if value:
            config[key] = value

    return config


def config_is_complete(config: Optional[Dict[str, Any]] = None) -> bool:
    """Return ``True`` if all required credentials are present."""
    if config is None:
        config = load_config()
    return all(config.get(k) for k in REQUIRED_KEYS)


def save_config(data: Dict[str, Any]) -> Path:
    """Persist *data* to ``~/.shark/config.yaml`` with ``0600`` permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as fh:
        yaml.dump(data, fh, default_flow_style=False)

    # Force 600 permissions (owner read/write only)
    CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return CONFIG_FILE
