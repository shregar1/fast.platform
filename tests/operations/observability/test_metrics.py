from __future__ import annotations

"""Tests for ``observability.metrics``."""
from observability.metrics import Metrics
from tests.operations.observability.abstraction import IObservabilityTests


class TestMetrics(IObservabilityTests):
    def test_counter_increment_and_export(self) -> None:
        m = Metrics()
        c = m.counter("http_requests_total", "desc", ["method", "status"])
        c.inc(method="GET", status="200")
        c.inc(method="GET", status="200", value=2.0)
        out = m.export()
        assert "http_requests_total" in out
        assert "GET" in out
        assert "200" in out

    def test_same_name_returns_same_counter(self) -> None:
        m = Metrics()
        a = m.counter("x", "d")
        b = m.counter("x", "d")
        assert a is b
