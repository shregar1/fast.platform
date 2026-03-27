"""Module test_metrics.py."""

from __future__ import annotations

"""Tests for ``operations.observability.metrics``."""
from operations.observability.metrics import Metrics
from tests.operations.observability.abstraction import IObservabilityTests


class TestMetrics(IObservabilityTests):
    """Represents the TestMetrics class."""

    def test_counter_increment_and_export(self) -> None:
        """Execute test_counter_increment_and_export operation.

        Returns:
            The result of the operation.
        """
        m = Metrics()
        c = m.counter("http_requests_total", "desc", ["method", "status"])
        c.inc(method="GET", status="200")
        c.inc(method="GET", status="200", value=2.0)
        out = m.export()
        assert "http_requests_total" in out
        assert "GET" in out
        assert "200" in out

    def test_same_name_returns_same_counter(self) -> None:
        """Execute test_same_name_returns_same_counter operation.

        Returns:
            The result of the operation.
        """
        m = Metrics()
        a = m.counter("x", "d")
        b = m.counter("x", "d")
        assert a is b
