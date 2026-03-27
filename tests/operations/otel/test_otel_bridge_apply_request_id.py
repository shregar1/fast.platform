"""Module test_otel_bridge_apply_request_id.py."""

from __future__ import annotations

"""OpenTelemetry bridge: apply request id to current span."""
from unittest.mock import MagicMock, patch

from fast_platform.operations.otel.bridge import OpenTelemetryBridge
from tests.operations.otel.abstraction import IOtelTests


class TestOpenTelemetryBridgeApplyRequestId(IOtelTests):
    """Represents the TestOpenTelemetryBridgeApplyRequestId class."""

    def test_apply_no_trace_module(self) -> None:
        """Execute test_apply_no_trace_module operation.

        Returns:
            The result of the operation.
        """
        with patch.object(OpenTelemetryBridge, "_trace_api", return_value=None):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is False

    def test_apply_no_request_id(self) -> None:
        """Execute test_apply_no_request_id operation.

        Returns:
            The result of the operation.
        """
        trace = MagicMock()
        trace.get_current_span.return_value = MagicMock(is_recording=lambda: True)
        with (
            patch.object(OpenTelemetryBridge, "_trace_api", return_value=trace),
            patch("fast_platform.core.utils.request_id_context.RequestIdContext.get", return_value=None),
        ):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is False

    def test_apply_sets_attribute(self) -> None:
        """Execute test_apply_sets_attribute operation.

        Returns:
            The result of the operation.
        """
        trace = MagicMock()
        span = MagicMock()
        span.is_recording.return_value = True
        trace.get_current_span.return_value = span
        with (
            patch.object(OpenTelemetryBridge, "_trace_api", return_value=trace),
            patch("fast_platform.core.utils.request_id_context.RequestIdContext.get", return_value="req-1"),
        ):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is True
        span.set_attribute.assert_called_once()

    def test_apply_span_not_recording(self) -> None:
        """Execute test_apply_span_not_recording operation.

        Returns:
            The result of the operation.
        """
        trace = MagicMock()
        span = MagicMock()
        span.is_recording.return_value = False
        trace.get_current_span.return_value = span
        with (
            patch.object(OpenTelemetryBridge, "_trace_api", return_value=trace),
            patch("fast_platform.core.utils.request_id_context.RequestIdContext.get", return_value="r"),
        ):
            assert OpenTelemetryBridge.apply_request_id_to_current_span() is False
