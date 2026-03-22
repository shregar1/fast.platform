"""Analytics sampling middleware."""

from __future__ import annotations

from typing import Any, Optional

import pytest

pytest.importorskip("starlette")

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from analytics.base import IAnalyticsBackend
from analytics.middleware import AnalyticsSamplingMiddleware


class MemBackend(IAnalyticsBackend):
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, Any]]] = []

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        self.events.append((distinct_id, event_name, dict(properties or {})))

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        pass


def test_middleware_tracks_request() -> None:
    inner = MemBackend()

    async def home(_: Any) -> PlainTextResponse:
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
