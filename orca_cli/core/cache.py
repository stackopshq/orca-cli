"""Resource completion cache — per-profile JSON cache for shell completion.

The TTL is long on purpose (5 minutes): completion data — server names,
flavor IDs, region lists — changes slowly, and every cache miss pays for
a Keystone auth round-trip plus the resource GET. Short TTLs made the
tab key feel sluggish on live terminals where users type in bursts.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

CACHE_TTL = 300  # seconds — long enough to cover typical tab-complete sessions
_CACHE_DIR = Path.home() / ".orca" / "cache"


def _path(profile: str | None, resource: str) -> Path:
    return _CACHE_DIR / f"{profile or 'default'}_{resource}.json"


def load(profile: str | None, resource: str) -> list[dict] | None:
    """Return cached items if still fresh, else None."""
    try:
        p = _path(profile, resource)
        if not p.exists():
            return None
        data = json.loads(p.read_text())
        if time.time() - data.get("ts", 0) < CACHE_TTL:
            return data.get("items")
    except Exception:
        pass
    return None


def save(profile: str | None, resource: str, items: list[dict]) -> None:
    """Persist items to cache file."""
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _path(profile, resource).write_text(
            json.dumps({"ts": time.time(), "items": items})
        )
    except Exception:
        pass


def invalidate(profile: str | None, resource: str) -> None:
    """Delete a cache entry (call after create/delete operations)."""
    try:
        _path(profile, resource).unlink(missing_ok=True)
    except Exception:
        pass
