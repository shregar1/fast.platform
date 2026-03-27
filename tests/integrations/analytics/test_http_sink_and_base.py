"""Module test_http_sink_and_base.py."""

from __future__ import annotations

"""HTTP sink success paths and abstract base."""
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from integrations.analytics.base import IAnalyticsBackend, build_analytics_client
from tests.integrations.analytics.abstraction import IAnalyticsTests


class _Dummy(IAnalyticsBackend):
    """Represents the _Dummy class."""

    name = "d"

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Any = None,
    ) -> None:
        """Execute track operation.

        Args:
            distinct_id: The distinct_id parameter.
            event_name: The event_name parameter.
            properties: The properties parameter.

        Returns:
            The result of the operation.
        """
        super().track(distinct_id, event_name, properties)

    def identify(self, distinct_id: str, traits: Any = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        super().identify(distinct_id, traits)


class TestHttpSinkAndBase(IAnalyticsTests):
    """Represents the TestHttpSinkAndBase class."""

    def test_http_sink_track_identify_delete_success(self) -> None:
        """Execute test_http_sink_track_identify_delete_success operation.

        Returns:
            The result of the operation.
        """
        from integrations.analytics.http_sink import HttpSinkAnalyticsBackend

        with patch("urllib.request.urlopen", return_value=MagicMock()) as m:
            b = HttpSinkAnalyticsBackend("http://example.com/collect", api_key="k")
            b.track("u", "e", {"a": 1})
            b.identify("u", {"t": 1})
            b.delete_user("u")
            assert m.call_count == 3

    def test_http_sink_identify_empty_endpoint_branch(self) -> None:
        """Execute test_http_sink_identify_empty_endpoint_branch operation.

        Returns:
            The result of the operation.
        """
        from integrations.analytics.http_sink import HttpSinkAnalyticsBackend

        with patch("urllib.request.urlopen", return_value=MagicMock()):
            b = HttpSinkAnalyticsBackend("", api_key=None)
            b.identify("x")

    def test_abstract_backend_raises(self) -> None:
        """Execute test_abstract_backend_raises operation.

        Returns:
            The result of the operation.
        """
        d = _Dummy()
        with pytest.raises(NotImplementedError):
            d.track("a", "b")
        with pytest.raises(NotImplementedError):
            d.identify("a")
        d.delete_user("a")  # default no-op

    def test_build_analytics_client_with_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Execute test_build_analytics_client_with_config operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """

        class Cfg:
            """Represents the Cfg class."""

            http_sink = type("H", (), {"enabled": True, "endpoint": "http://x", "api_key": "k"})()

        class AnalyticsConfiguration:
            """Represents the AnalyticsConfiguration class."""

            def get_config(self):
                """Execute get_config operation.

                Returns:
                    The result of the operation.
                """
                return Cfg()

        monkeypatch.setattr(
            "integrations.analytics.base.AnalyticsConfiguration", AnalyticsConfiguration
        )
        c = build_analytics_client()
        assert c is not None
