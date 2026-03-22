"""Process-local named counters and histograms."""

from __future__ import annotations

from threading import Lock
from typing import Dict

from ..abstraction import IUtility
from .counter import Counter
from .histogram import Histogram

__all__ = ["MetricsRegistry"]


class MetricsRegistry(IUtility):
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
