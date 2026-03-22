"""In-memory histogram of raw observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import List

from ..abstraction import IUtility

__all__ = ["Histogram"]


@dataclass
class Histogram(IUtility):
    """Simple histogram storing raw observations (in-memory)."""

    name: str
    _observations: List[float] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def observe(self, value: float) -> None:
        with self._lock:
            self._observations.append(value)

    def snapshot(self) -> List[float]:
        with self._lock:
            return list(self._observations)
