"""Process-wide :class:`~utils.clock.protocol.Clock` override (tests)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .system_clock import SystemClock

if TYPE_CHECKING:
    from .protocol import Clock

__all__ = ["ClockRegistry"]

_DEFAULT = SystemClock()
_override: Clock | None = None


class ClockRegistry:
    """Process-wide :class:`~utils.clock.protocol.Clock` override (tests)."""

    @staticmethod
    def get() -> Clock:
        """Return the process-wide clock (default :class:`~utils.clock.system_clock.SystemClock`)."""
        return _override or _DEFAULT

    @staticmethod
    def set(clock: Clock | None) -> None:
        """
        Replace the global clock (``None`` restores :class:`~utils.clock.system_clock.SystemClock`).

        Use in tests::

            ClockRegistry.set(FrozenClock(datetime(2026, 1, 1, tzinfo=timezone.utc)))
            try:
                ...
            finally:
                ClockRegistry.set(None)
        """
        global _override
        _override = clock
