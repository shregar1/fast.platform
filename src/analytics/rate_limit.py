"""Per-user rate limiting for analytics backends."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Callable, Deque, Dict, Optional

from .base import IAnalyticsBackend


class RateLimitedAnalyticsBackend(IAnalyticsBackend):
    """Fixed-window cap on ``track`` / ``identify`` per ``distinct_id`` (``delete_user`` is not limited)."""

    def __init__(
        self,
        inner: IAnalyticsBackend,
        *,
        max_events_per_user_per_minute: int = 60,
        max_events: Optional[int] = None,
        window_seconds: float = 60.0,
        clock: Optional[Callable[[], float]] = None,
    ):
        self._inner = inner
        self._max = max_events if max_events is not None else max_events_per_user_per_minute
        self._window = window_seconds
        self._clock = clock or time.monotonic
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def _allow(self, distinct_id: str) -> bool:
        if self._max <= 0:
            return True
        now = self._clock()
        q = self._hits[distinct_id]
        cutoff = now - self._window
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= self._max:
            return False
        q.append(now)
        return True

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        if not self._allow(distinct_id):
            return
        self._inner.track(distinct_id, event_name, properties)

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        if not self._allow(distinct_id):
            return
        self._inner.identify(distinct_id, traits)

    def delete_user(self, distinct_id: str) -> None:
        self._hits.pop(distinct_id, None)
        self._inner.delete_user(distinct_id)
