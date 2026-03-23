"""
Injectable clock for tests (JWT expiry, TTLs, idempotency windows).

Default is UTC wall time; swap with :meth:`~utils.clock.registry.ClockRegistry.set`
or :class:`~utils.clock.frozen_clock.FrozenClock`.
"""

from __future__ import annotations

from .abstraction import IClockUtility
from .frozen_clock import FrozenClock
from .protocol import Clock
from .registry import ClockRegistry
from .system_clock import SystemClock

__all__ = ["Clock", "ClockRegistry", "FrozenClock", "IClockUtility", "SystemClock"]
