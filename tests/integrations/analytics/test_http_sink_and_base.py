from __future__ import annotations

"""HTTP sink success paths and abstract base."""
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from integrations.analytics.base import IAnalyticsBackend, build_analytics_client
from tests.integrations.analytics.abstraction import IAnalyticsTests


class _Dummy(IAnalyticsBackend):
    name = "d"

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Any = None,
    ) -> None:
        super().track(distinct_id, event_name, properties)

    def identify(self, distinct_id: str, traits: Any = None) -> None:
        super().identify(distinct_id, traits)


class TestHttpSinkAndBase(IAnalyticsTests):
    def test_http_sink_track_identify_delete_success(self) -> None:
        from integrations.analytics.http_sink import HttpSinkAnalyticsBackend

        with patch("urllib.request.urlopen", return_value=MagicMock()) as m:
            b = HttpSinkAnalyticsBackend("http://example.com/collect", api_key="k")
            b.track("u", "e", {"a": 1})
            b.identify("u", {"t": 1})
            b.delete_user("u")
            assert m.call_count == 3

    def test_http_sink_identify_empty_endpoint_branch(self) -> None:
        from integrations.analytics.http_sink import HttpSinkAnalyticsBackend

        with patch("urllib.request.urlopen", return_value=MagicMock()):
            b = HttpSinkAnalyticsBackend("", api_key=None)
            b.identify("x")

    def test_abstract_backend_raises(self) -> None:
        d = _Dummy()
        with pytest.raises(NotImplementedError):
            d.track("a", "b")
        with pytest.raises(NotImplementedError):
            d.identify("a")
        d.delete_user("a")  # default no-op

    def test_build_analytics_client_with_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class Cfg:
            http_sink = type("H", (), {"enabled": True, "endpoint": "http://x", "api_key": "k"})()

        class AnalyticsConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("integrations.analytics.base.AnalyticsConfiguration", AnalyticsConfiguration)
        c = build_analytics_client()
        assert c is not None
