"""
Lightweight in-process metrics (no Prometheus client required).

Use for tests, smoke dashboards, or adapters that push to OTLP/Prometheus later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List


@dataclass
class Counter:
    """Monotonic counter (thread-safe increment)."""

    name: str
    _value: int = 0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def inc(self, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("counter increment must be non-negative")
        with self._lock:
            self._value += amount

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


@dataclass
class Histogram:
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


class MetricsRegistry:
    """Named counters and histograms (process-local)."""

    def __init__(self) -> None:
        self._counters: Dict[str, Counter] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._lock = Lock()

    def counter(self, name: str) -> Counter:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name=name)
            return self._counters[name]

    def histogram(self, name: str) -> Histogram:
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name=name)
            return self._histograms[name]

    def counters(self) -> Dict[str, Counter]:
        with self._lock:
            return dict(self._counters)

    def histograms(self) -> Dict[str, Histogram]:
        with self._lock:
            return dict(self._histograms)


__all__ = ["Counter", "Histogram", "MetricsRegistry"]
