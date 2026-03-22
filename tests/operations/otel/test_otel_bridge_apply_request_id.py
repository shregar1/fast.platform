from __future__ import annotations

"""OpenTelemetry bridge: apply request id to current span."""
from unittest.mock import MagicMock, patch

from otel.bridge import OpenTelemetryBridge
from tests.operations.otel.abstraction import IOtelTests


class TestOpenTelemetryBridgeApplyRequestId(IOtelTests):
    def test_apply_no_trace_module(self) -> None:
        with patch.object(OpenTelemetryBridge, "_trace_api", return_value=None):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is False

    def test_apply_no_request_id(self) -> None:
        trace = MagicMock()
        trace.get_current_span.return_value = MagicMock(is_recording=lambda: True)
        with (
            patch.object(OpenTelemetryBridge, "_trace_api", return_value=trace),
            patch("utils.request_id_context.RequestIdContext.get", return_value=None),
        ):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is False

    def test_apply_sets_attribute(self) -> None:
        trace = MagicMock()
        span = MagicMock()
        span.is_recording.return_value = True
        trace.get_current_span.return_value = span
        with (
            patch.object(OpenTelemetryBridge, "_trace_api", return_value=trace),
            patch("utils.request_id_context.RequestIdContext.get", return_value="req-1"),
        ):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is True
        span.set_attribute.assert_called_once()

    def test_apply_span_not_recording(self) -> None:
        trace = MagicMock()
        span = MagicMock()
        span.is_recording.return_value = False
        trace.get_current_span.return_value = span
        with (
            patch.object(OpenTelemetryBridge, "_trace_api", return_value=trace),
            patch("utils.request_id_context.RequestIdContext.get", return_value="r"),
        ):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is False
