"""Fixed instant clock for deterministic tests."""

from __future__ import annotations

from datetime import datetime, timezone

from utils.abstraction import IUtility

__all__ = ["FrozenClock"]


class FrozenClock(IUtility):
    """Fixed instant for deterministic tests."""

    __slots__ = ("_fixed",)

    def __init__(self, fixed: datetime) -> None:
        if fixed.tzinfo is None:
            fixed = fixed.replace(tzinfo=timezone.utc)
        self._fixed = fixed.astimezone(timezone.utc)

    def now(self) -> datetime:
        return self._fixed
