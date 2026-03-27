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
    ) -> None:
        """Execute __init__ operation.

        Args:
            inner: The inner parameter.
            max_events_per_user_per_minute: The max_events_per_user_per_minute parameter.
            max_events: The max_events parameter.
            window_seconds: The window_seconds parameter.
            clock: The clock parameter.
        """
        self._inner = inner
        self._max = max_events if max_events is not None else max_events_per_user_per_minute
        self._window = window_seconds
        self._clock = clock or time.monotonic
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def _allow(self, distinct_id: str) -> bool:
        """Execute _allow operation.

        Args:
            distinct_id: The distinct_id parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute track operation.

        Args:
            distinct_id: The distinct_id parameter.
            event_name: The event_name parameter.
            properties: The properties parameter.

        Returns:
            The result of the operation.
        """
        if not self._allow(distinct_id):
            return
        self._inner.track(distinct_id, event_name, properties)

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        if not self._allow(distinct_id):
            return
        self._inner.identify(distinct_id, traits)

    def delete_user(self, distinct_id: str) -> None:
        """Execute delete_user operation.

        Args:
            distinct_id: The distinct_id parameter.

        Returns:
            The result of the operation.
        """
        self._hits.pop(distinct_id, None)
        self._inner.delete_user(distinct_id)
