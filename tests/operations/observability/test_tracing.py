from __future__ import annotations

"""Tests for ``observability.tracing``."""
from unittest.mock import MagicMock

from observability.tracing import Span, Tracer
from tests.operations.observability.abstraction import IObservabilityTests


class TestTracer(IObservabilityTests):
    def test_start_span_sets_service_attribute(self) -> None:
        exp = MagicMock()
        t = Tracer("svc-a", exporter=exp)
        span = t.start_span("op1", trace_id="trace-fixed")
        assert span.name == "op1"
        assert span.trace_id == "trace-fixed"
        assert span.attributes.get("service.name") == "svc-a"
        t.end_span(span)
        exp.export.assert_called_once()
        assert isinstance(exp.export.call_args[0][0], Span)

    def test_span_context_manager(self) -> None:
        exp = MagicMock()
        t = Tracer("svc-b", exporter=exp)
        with t.span("inner") as span:
            span.set_attribute("k", "v")
        assert exp.export.called
