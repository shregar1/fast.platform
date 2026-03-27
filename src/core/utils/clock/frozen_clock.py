"""Fixed instant clock for deterministic tests."""

from __future__ import annotations

from datetime import datetime, timezone

from .abstraction import IClockUtility

__all__ = ["FrozenClock"]


class FrozenClock(IClockUtility):
    """Fixed instant for deterministic tests."""

    __slots__ = ("_fixed",)

    def __init__(self, fixed: datetime) -> None:
        """Execute __init__ operation.

        Args:
            fixed: The fixed parameter.
        """
        if fixed.tzinfo is None:
            fixed = fixed.replace(tzinfo=timezone.utc)
        self._fixed = fixed.astimezone(timezone.utc)

    def now(self) -> datetime:
        """Execute now operation.

        Returns:
            The result of the operation.
        """
        return self._fixed
