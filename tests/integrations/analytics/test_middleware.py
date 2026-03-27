"""Analytics sampling middleware."""

from __future__ import annotations

from typing import Any, Optional

import pytest

pytest.importorskip("starlette")

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from integrations.analytics.base import IAnalyticsBackend
from integrations.analytics.middleware import AnalyticsSamplingMiddleware
from tests.integrations.analytics.abstraction import IAnalyticsTests


class MemBackend(IAnalyticsBackend):
    """Represents the MemBackend class."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self.events: list[tuple[str, str, dict[str, Any]]] = []

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
        self.events.append((distinct_id, event_name, dict(properties or {})))

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        pass


class TestMiddleware(IAnalyticsTests):
    """Represents the TestMiddleware class."""

    def test_middleware_tracks_request(self) -> None:
        """Execute test_middleware_tracks_request operation.

        Returns:
            The result of the operation.
        """
        inner = MemBackend()

        async def home(_: Any) -> PlainTextResponse:
            """Execute home operation.

            Args:
                _: The _ parameter.

            Returns:
                The result of the operation.
            """
            return PlainTextResponse("hi")

        app = Starlette(routes=[Route("/", home)])
        app.add_middleware(
            AnalyticsSamplingMiddleware,
            backend=inner,
            sample_rate=1.0,
            max_events_per_user_per_minute=10,
        )
        client = TestClient(app)
        r = client.get("/", headers={"x-user-id": "user-1"})
        assert r.status_code == 200
        assert len(inner.events) == 1
        assert inner.events[0][0] == "user-1"
        assert inner.events[0][1] == "http.request"
        assert inner.events[0][2]["status_code"] == 200
