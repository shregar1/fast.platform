"""Module test_rate_limit.py."""

from __future__ import annotations

"""Rate-limited analytics backend."""
from typing import Any, List, Optional

from fast_platform.integrations.analytics.base import IAnalyticsBackend
from fast_platform.integrations.analytics.rate_limit import RateLimitedAnalyticsBackend
from tests.integrations.analytics.abstraction import IAnalyticsTests


class MemBackend(IAnalyticsBackend):
    """Represents the MemBackend class."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self.tracks: List[tuple[str, str]] = []

    def track(
        self, distinct_id: str, event_name: str, properties: Optional[dict[str, Any]] = None
    ) -> None:
        """Execute track operation.

        Args:
            distinct_id: The distinct_id parameter.
            event_name: The event_name parameter.
            properties: The properties parameter.

        Returns:
            The result of the operation.
        """
        self.tracks.append((distinct_id, event_name))

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        pass


class TestRateLimit(IAnalyticsTests):
    """Represents the TestRateLimit class."""

    def test_rate_limit_per_user(self) -> None:
        """Execute test_rate_limit_per_user operation.

        Returns:
            The result of the operation.
        """
        inner = MemBackend()
        clock = {"t": 0.0}

        def fake_clock() -> float:
            """Execute fake_clock operation.

            Returns:
                The result of the operation.
            """
            return clock["t"]

        b = RateLimitedAnalyticsBackend(inner, max_events=2, window_seconds=10.0, clock=fake_clock)
        b.track("a", "e")
        b.track("a", "e")
        b.track("a", "e")
        assert len(inner.tracks) == 2
        b.track("b", "e")
        assert len(inner.tracks) == 3
