"""Production clock using wall time in UTC."""

from __future__ import annotations

from datetime import datetime, timezone

from .abstraction import IClockUtility

__all__ = ["SystemClock"]


class SystemClock(IClockUtility):
    """Production clock: ``datetime.now(timezone.utc)``."""

    def now(self) -> datetime:
        """Execute now operation.

        Returns:
            The result of the operation.
        """
        return datetime.now(timezone.utc)
