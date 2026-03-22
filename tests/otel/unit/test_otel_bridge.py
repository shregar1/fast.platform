"""OpenTelemetry bridge (optional dependency)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fast_core.otel.bridge import (
    apply_request_id_to_current_span,
    extract_trace_context_from_carrier,
    inject_trace_context_into_carrier,
)


def test_apply_no_trace_module():
    with patch("fast_core.otel.bridge._trace_api", return_value=None):
        assert apply_request_id_to_current_span() is False


def test_apply_no_request_id():
    trace = MagicMock()
    trace.get_current_span.return_value = MagicMock(is_recording=lambda: True)
    with patch("fast_core.otel.bridge._trace_api", return_value=trace), patch(
        "fast_platform.otel.bridge.get_request_id", return_value=None
    ):
        assert apply_request_id_to_current_span() is False


def test_apply_sets_attribute():
    trace = MagicMock()
    span = MagicMock()
    span.is_recording.return_value = True
    trace.get_current_span.return_value = span
    with patch("fast_core.otel.bridge._trace_api", return_value=trace), patch(
        "fast_platform.otel.bridge.get_request_id", return_value="req-1"
    ):
        assert apply_request_id_to_current_span() is True
    span.set_attribute.assert_called_once()


def test_inject_without_otel():
    carrier: dict[str, str] = {}
    with patch("fast_core.otel.bridge.optional_import", return_value=(None, None)):
        assert inject_trace_context_into_carrier(carrier) is False


def test_extract_without_otel():
    with patch("fast_core.otel.bridge.optional_import", return_value=(None, None)):
        assert extract_trace_context_from_carrier({}) is None


def test_apply_span_not_recording():
    trace = MagicMock()
    span = MagicMock()
    span.is_recording.return_value = False
    trace.get_current_span.return_value = span
    with patch("fast_core.otel.bridge._trace_api", return_value=trace), patch(
        "fast_core.otel.bridge.get_request_id", return_value="r"
    ):
        assert apply_request_id_to_current_span() is False


def test_inject_success():
    carrier: dict[str, str] = {}
    prop_mod = MagicMock()
    ctx_mod = MagicMock()
    ctx_mod.get_current.return_value = object()
    inst = MagicMock()
    prop_mod.TraceContextTextMapPropagator.return_value = inst

    def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
        if "tracecontext" in name:
            return (prop_mod, None)
        if "context" in name:
            return (ctx_mod, None)
        return (None, None)

    with patch("fast_core.otel.bridge.optional_import", side_effect=oi_side_effect):
        assert inject_trace_context_into_carrier(carrier) is True
    inst.inject.assert_called_once()


def test_extract_success():
    prop_mod = MagicMock()
    inst = MagicMock()
    inst.extract.return_value = object()
    prop_mod.TraceContextTextMapPropagator.return_value = inst

    def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
        if "tracecontext" in name:
            return (prop_mod, None)
        return (None, None)

    with patch("fast_core.otel.bridge.optional_import", side_effect=oi_side_effect):
        assert extract_trace_context_from_carrier({"traceparent": "x"}) is not None


def test_extract_exception_returns_none():
    prop_mod = MagicMock()
    inst = MagicMock()
    inst.extract.side_effect = RuntimeError("bad")
    prop_mod.TraceContextTextMapPropagator.return_value = inst

    def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
        if "tracecontext" in name:
            return (prop_mod, None)
        return (None, None)

    with patch("fast_core.otel.bridge.optional_import", side_effect=oi_side_effect):
        assert extract_trace_context_from_carrier({}) is None


def test_inject_missing_propagator_class():
    prop_mod = MagicMock()
    prop_mod.TraceContextTextMapPropagator = None
    ctx_mod = MagicMock()
    ctx_mod.get_current.return_value = object()

    def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
        if "tracecontext" in name:
            return (prop_mod, None)
        if "context" in name:
            return (ctx_mod, None)
        return (None, None)

    with patch("fast_core.otel.bridge.optional_import", side_effect=oi_side_effect):
        assert inject_trace_context_into_carrier({}) is False


def test_inject_missing_get_current():
    prop_mod = MagicMock()
    inst = MagicMock()
    prop_mod.TraceContextTextMapPropagator.return_value = inst
    ctx_mod = MagicMock()
    ctx_mod.get_current = None

    def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
        if "tracecontext" in name:
            return (prop_mod, None)
        if "context" in name:
            return (ctx_mod, None)
        return (None, None)

    with patch("fast_core.otel.bridge.optional_import", side_effect=oi_side_effect):
        assert inject_trace_context_into_carrier({}) is False
