"""Thread-safe monotonic counter."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock

from .abstraction import IMetricsUtility

__all__ = ["Counter"]


@dataclass
class Counter(IMetricsUtility):
    """Monotonic counter (thread-safe increment)."""

    name: str
    _value: int = 0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def inc(self, amount: int = 1) -> None:
        """Execute inc operation.

        Args:
            amount: The amount parameter.

        Returns:
            The result of the operation.
        """
        if amount < 0:
            raise ValueError("counter increment must be non-negative")
        with self._lock:
            self._value += amount

    @property
    def value(self) -> int:
        """Execute value operation.

        Returns:
            The result of the operation.
        """
        with self._lock:
            return self._value
