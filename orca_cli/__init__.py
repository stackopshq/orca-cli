"""orca — OpenStack Rich Command-line Alternative."""

from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover — py<3.8
    from importlib_metadata import PackageNotFoundError, version  # type: ignore[no-redef]

try:
    __version__ = version("orca-openstackclient")
except PackageNotFoundError:  # pragma: no cover — editable source w/o install
    __version__ = "0.0.0+dev"
