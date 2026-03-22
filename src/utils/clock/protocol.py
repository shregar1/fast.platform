"""Protocol for injectable UTC clocks."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

__all__ = ["Clock"]


@runtime_checkable
class Clock(Protocol):
    """Callable surface for “current time” in UTC."""

    def now(self) -> datetime:
        """Return timezone-aware UTC *now*."""
