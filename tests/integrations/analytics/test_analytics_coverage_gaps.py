from __future__ import annotations

"""Cover remaining branches for high coverage."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from integrations.analytics.buffer import BufferedAnalyticsBackend
from integrations.analytics.middleware import default_analytics_user_key
from integrations.analytics.pii import scrub_pii_properties
from integrations.analytics.rate_limit import RateLimitedAnalyticsBackend
from integrations.analytics.schema_registry import EventSchemaRegistry, parse_versioned_event_name
from integrations.analytics.validating_backend import ValidatingAnalyticsBackend
from tests.integrations.analytics.abstraction import IAnalyticsTests


class TestAnalyticsCoverageGaps(IAnalyticsTests):
    def test_buffer_property_alias(self) -> None:
        b = BufferedAnalyticsBackend()
        b.track("u", "e")
        assert len(b.buffer) == 1
        assert b.buffer is b._buffer

    def test_http_sink_swallows_errors(self) -> None:
        from integrations.analytics.http_sink import HttpSinkAnalyticsBackend

        with patch("urllib.request.urlopen", side_effect=OSError("nope")):
            b = HttpSinkAnalyticsBackend("http://x")
            b.track("a", "b")

    def test_default_analytics_user_key_variants(self) -> None:
        class R:
            headers = {"x-user-id": "h"}
            state = SimpleNamespace()

        assert default_analytics_user_key(R()) == "h"

        class R2:
            headers = {}

            def __init__(self) -> None:
                self.state = SimpleNamespace(user_id=42)

        r2 = R2()
        assert default_analytics_user_key(r2) == "42"

        class R3:
            headers = {}

            def __init__(self) -> None:
                self.state = SimpleNamespace()

        assert default_analytics_user_key(R3()) == "anonymous"

    def test_middleware_requires_starlette(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import integrations.analytics.middleware as mw

        monkeypatch.setattr(mw, "_STARLETTE", False)
        with pytest.raises(RuntimeError, match="starlette"):
            mw.AnalyticsSamplingMiddleware(MagicMock(), MagicMock())

    @pytest.mark.asyncio
    async def test_middleware_dispatch_skips_when_random_high(self) -> None:
        pytest.importorskip("starlette")
        from starlette.applications import Starlette
        from starlette.responses import PlainTextResponse
        from starlette.routing import Route
        from starlette.testclient import TestClient

        from integrations.analytics.middleware import AnalyticsSamplingMiddleware

        backend = MagicMock()

        async def home(_: object) -> PlainTextResponse:
            return PlainTextResponse("ok")

        app = Starlette(routes=[Route("/", home)])
        app.add_middleware(AnalyticsSamplingMiddleware, backend=backend, sample_rate=0.5)
        with patch("integrations.analytics.middleware.random.random", return_value=0.99):
            client = TestClient(app)
            client.get("/")
        assert backend.track.call_count == 0

    def test_rate_limit_unlimited_and_delete(self) -> None:
        inner = MagicMock()
        rl = RateLimitedAnalyticsBackend(inner, max_events_per_user_per_minute=0)
        for _ in range(3):
            rl.track("u", "e")
        assert inner.track.call_count == 3
        rl.delete_user("u")
        inner.delete_user.assert_called_once_with("u")

    def test_schema_register_versioned_and_require(self) -> None:
        reg = EventSchemaRegistry(require_registration=True)
        reg.register_versioned("x@1", {"type": "object", "properties": {"a": {"type": "integer"}}})
        reg.validate_properties("x@1", {"a": 1})
        with pytest.raises(ValueError):
            parse_versioned_event_name("bad")

    def test_validating_identify_and_delete(self) -> None:
        inner = MagicMock()
        reg = EventSchemaRegistry()
        v = ValidatingAnalyticsBackend(inner, reg)
        v.identify("u", {"t": 1})
        v.delete_user("u")
        inner.identify.assert_called_once()
        inner.delete_user.assert_called_once()

    def test_scrub_nested_non_dict_value(self) -> None:
        d = scrub_pii_properties({"nested": {"email": "a@b.com"}})
        assert d["nested"]["email"] == "[REDACTED]"

    def test_scrubbing_backend_nested(self) -> None:
        from integrations.analytics.pii import ScrubbingAnalyticsBackend

        inner = MagicMock()
        b = ScrubbingAnalyticsBackend(inner)
        b.identify("u", {"nested": {"phone": "555-123-4567"}})
        inner.identify.assert_called_once()

    def test_buffer_forward_identify_and_delete(self) -> None:
        inner = MagicMock()
        buf = BufferedAnalyticsBackend(inner=inner, dry_run=False)
        buf.identify("u", {"t": 1})
        buf.delete_user("u")
        inner.identify.assert_called_once()
        inner.delete_user.assert_called_once_with("u")

    def test_http_sink_delete_error_swallowed(self) -> None:
        from integrations.analytics.http_sink import HttpSinkAnalyticsBackend

        with patch("urllib.request.urlopen", side_effect=OSError("down")):
            HttpSinkAnalyticsBackend("http://x").delete_user("u")

    def test_schema_validate_unknown_versioned_when_required(self) -> None:
        reg = EventSchemaRegistry(require_registration=True)
        with pytest.raises(ValueError):
            reg.validate_properties("missing@1", {})

    def test_rate_limit_clock_prune(self) -> None:
        inner = MagicMock()
        times = {"t": 0.0}

        def fake_clock() -> float:
            return times["t"]

        rl = RateLimitedAnalyticsBackend(
            inner, max_events_per_user_per_minute=1, window_seconds=10.0, clock=fake_clock
        )
        rl.track("u", "e")
        times["t"] = 100.0
        rl.track("u", "e2")
        assert inner.track.call_count == 2

    @pytest.mark.asyncio
    async def test_middleware_sample_rate_zero_skips_track(self) -> None:
        pytest.importorskip("starlette")
        from starlette.applications import Starlette
        from starlette.responses import PlainTextResponse
        from starlette.routing import Route
        from starlette.testclient import TestClient

        from integrations.analytics.middleware import AnalyticsSamplingMiddleware

        backend = MagicMock()

        async def home(_: object) -> PlainTextResponse:
            return PlainTextResponse("ok")

        app = Starlette(routes=[Route("/", home)])
        app.add_middleware(AnalyticsSamplingMiddleware, backend=backend, sample_rate=0.0)
        client = TestClient(app)
        client.get("/")
        backend.track.assert_not_called()
