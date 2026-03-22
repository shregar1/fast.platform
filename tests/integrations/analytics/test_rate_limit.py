from __future__ import annotations
"""Rate-limited analytics backend."""
from tests.integrations.analytics.abstraction import IAnalyticsTests

from typing import Any, List, Optional
from analytics.base import IAnalyticsBackend
from analytics.rate_limit import RateLimitedAnalyticsBackend

class MemBackend(IAnalyticsBackend):

    def __init__(self) -> None:
        self.tracks: List[tuple[str, str]] = []

    def track(self, distinct_id: str, event_name: str, properties: Optional[dict[str, Any]]=None) -> None:
        self.tracks.append((distinct_id, event_name))

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]]=None) -> None:
        pass

class TestRateLimit(IAnalyticsTests):

    def test_rate_limit_per_user(self) -> None:
        inner = MemBackend()
        clock = {'t': 0.0}

        def fake_clock() -> float:
            return clock['t']
        b = RateLimitedAnalyticsBackend(inner, max_events=2, window_seconds=10.0, clock=fake_clock)
        b.track('a', 'e')
        b.track('a', 'e')
        b.track('a', 'e')
        assert len(inner.tracks) == 2
        b.track('b', 'e')
        assert len(inner.tracks) == 3
