"""Module test_otel_bridge_carrier.py."""

from __future__ import annotations

"""OpenTelemetry bridge: trace context carrier inject/extract."""
from unittest.mock import MagicMock, patch

from fast_platform.operations.otel.bridge import OpenTelemetryBridge
from tests.operations.otel.abstraction import IOtelTests


class TestOpenTelemetryBridgeCarrier(IOtelTests):
    """Represents the TestOpenTelemetryBridgeCarrier class."""

    def test_inject_without_otel(self) -> None:
        """Execute test_inject_without_otel operation.

        Returns:
            The result of the operation.
        """
        carrier: dict[str, str] = {}
        with patch(
            "fast_platform.core.utils.optional_imports.OptionalImports.optional_import", return_value=(None, None)
        ):
            assert OpenTelemetryBridge.inject_trace_context_into_carrier(carrier) is False

    def test_extract_without_otel(self) -> None:
        """Execute test_extract_without_otel operation.

        Returns:
            The result of the operation.
        """
        with patch(
            "fast_platform.core.utils.optional_imports.OptionalImports.optional_import", return_value=(None, None)
        ):
            assert OpenTelemetryBridge.extract_trace_context_from_carrier({}) is None

    def test_inject_success(self) -> None:
        """Execute test_inject_success operation.

        Returns:
            The result of the operation.
        """
        carrier: dict[str, str] = {}
        prop_mod = MagicMock()
        ctx_mod = MagicMock()
        ctx_mod.get_current.return_value = object()
        inst = MagicMock()
        prop_mod.TraceContextTextMapPropagator.return_value = inst

        def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
            """Execute oi_side_effect operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if "tracecontext" in name:
                return (prop_mod, None)
            if "context" in name:
                return (ctx_mod, None)
            return (None, None)

        with patch(
            "fast_platform.core.utils.optional_imports.OptionalImports.optional_import",
            side_effect=oi_side_effect,
        ):
            assert OpenTelemetryBridge.inject_trace_context_into_carrier(carrier) is True
        inst.inject.assert_called_once()

    def test_extract_success(self) -> None:
        """Execute test_extract_success operation.

        Returns:
            The result of the operation.
        """
        prop_mod = MagicMock()
        inst = MagicMock()
        inst.extract.return_value = object()
        prop_mod.TraceContextTextMapPropagator.return_value = inst

        def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
            """Execute oi_side_effect operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if "tracecontext" in name:
                return (prop_mod, None)
            return (None, None)

        with patch(
            "fast_platform.core.utils.optional_imports.OptionalImports.optional_import",
            side_effect=oi_side_effect,
        ):
            assert (
                OpenTelemetryBridge.extract_trace_context_from_carrier({"traceparent": "x"})
                is not None
            )

    def test_extract_exception_returns_none(self) -> None:
        """Execute test_extract_exception_returns_none operation.

        Returns:
            The result of the operation.
        """
        prop_mod = MagicMock()
        inst = MagicMock()
        inst.extract.side_effect = RuntimeError("bad")
        prop_mod.TraceContextTextMapPropagator.return_value = inst

        def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
            """Execute oi_side_effect operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if "tracecontext" in name:
                return (prop_mod, None)
            return (None, None)

        with patch(
            "fast_platform.core.utils.optional_imports.OptionalImports.optional_import",
            side_effect=oi_side_effect,
        ):
            assert OpenTelemetryBridge.extract_trace_context_from_carrier({}) is None

    def test_inject_missing_propagator_class(self) -> None:
        """Execute test_inject_missing_propagator_class operation.

        Returns:
            The result of the operation.
        """
        prop_mod = MagicMock()
        prop_mod.TraceContextTextMapPropagator = None
        ctx_mod = MagicMock()
        ctx_mod.get_current.return_value = object()

        def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
            """Execute oi_side_effect operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if "tracecontext" in name:
                return (prop_mod, None)
            if "context" in name:
                return (ctx_mod, None)
            return (None, None)

        with patch(
            "fast_platform.core.utils.optional_imports.OptionalImports.optional_import",
            side_effect=oi_side_effect,
        ):
            assert OpenTelemetryBridge.inject_trace_context_into_carrier({}) is False

    def test_inject_missing_get_current(self) -> None:
        """Execute test_inject_missing_get_current operation.

        Returns:
            The result of the operation.
        """
        prop_mod = MagicMock()
        inst = MagicMock()
        prop_mod.TraceContextTextMapPropagator.return_value = inst
        ctx_mod = MagicMock()
        ctx_mod.get_current = None

        def oi_side_effect(name: str, *_a: object) -> tuple[MagicMock | None, None]:
            """Execute oi_side_effect operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if "tracecontext" in name:
                return (prop_mod, None)
            if "context" in name:
                return (ctx_mod, None)
            return (None, None)

        with patch(
            "fast_platform.core.utils.optional_imports.OptionalImports.optional_import",
            side_effect=oi_side_effect,
        ):
            assert OpenTelemetryBridge.inject_trace_context_into_carrier({}) is False
