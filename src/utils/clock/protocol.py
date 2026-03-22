"""Protocol for injectable UTC clocks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from datetime import datetime

__all__ = ["Clock"]


@runtime_checkable
class Clock(Protocol):
    """Callable surface for “current time” in UTC."""

    def now(self) -> datetime:
        """Return timezone-aware UTC *now*."""
