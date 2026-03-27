"""Ensure ``src`` package names (e.g. ``db``) win over same-named test folders like ``tests/db``."""

from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure(config: object) -> None:
    """Execute pytest_configure operation.

    Args:
        config: The config parameter.

    Returns:
        The result of the operation.
    """
    root = Path(getattr(config, "rootpath", Path(__file__).resolve().parents[1]))
    src = root / "src"
    s = str(src.resolve())
    while s in sys.path:
        sys.path.remove(s)
    sys.path.insert(0, s)
