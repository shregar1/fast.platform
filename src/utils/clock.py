"""
Injectable clock for tests (JWT expiry, TTLs, idempotency windows).

Default is UTC wall time; swap with :func:`set_clock` or :class:`FrozenClock`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Callable surface for “current time” in UTC."""

    def now(self) -> datetime:
        """Return timezone-aware UTC *now*."""


class SystemClock:
    """Production clock: ``datetime.now(timezone.utc)``."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FrozenClock:
    """Fixed instant for deterministic tests."""

    __slots__ = ("_fixed",)

    def __init__(self, fixed: datetime) -> None:
        if fixed.tzinfo is None:
            fixed = fixed.replace(tzinfo=timezone.utc)
        self._fixed = fixed.astimezone(timezone.utc)

    def now(self) -> datetime:
        return self._fixed


_DEFAULT = SystemClock()
_override: Clock | None = None


def get_clock() -> Clock:
    """Return the process-wide clock (default :class:`SystemClock`)."""
    return _override or _DEFAULT


def set_clock(clock: Clock | None) -> None:
    """
    Replace the global clock (``None`` restores :class:`SystemClock`).

    Use in tests::

        set_clock(FrozenClock(datetime(2026, 1, 1, tzinfo=timezone.utc)))
        try:
            ...
        finally:
            set_clock(None)
    """
    global _override
    _override = clock


__all__ = ["Clock", "FrozenClock", "SystemClock", "get_clock", "set_clock"]
