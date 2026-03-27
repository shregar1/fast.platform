"""Trace context propagation aligned with :class:`utils.request_id_context.RequestIdContext`.

Requires ``pip install 'fast-platform[otel]'`` (``opentelemetry-api``).
"""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional

from core.utils.optional_imports import OptionalImports
from core.utils.request_id_context import RequestIdContext

_REQUEST_ID_ATTR = "fastmvc.request_id"


class OpenTelemetryBridge:
    """OpenTelemetry trace context + request id wiring (optional dependency)."""

    @staticmethod
    def _trace_api() -> Optional[Any]:
        """Execute _trace_api operation.

        Returns:
            The result of the operation.
        """
        mod, _ = OptionalImports.optional_import("opentelemetry.trace")
        return mod

    @staticmethod
    def apply_request_id_to_current_span(*, attribute_key: str = _REQUEST_ID_ATTR) -> bool:
        """Set the current request ID on the active span, if tracing is available.

        Returns True if an attribute was set on a recording span.
        """
        trace = OpenTelemetryBridge._trace_api()
        if trace is None:
            return False
        rid = RequestIdContext.get()
        if not rid:
            return False
        span = trace.get_current_span()
        if span is None or not span.is_recording():
            return False
        span.set_attribute(attribute_key, rid)
        return True

    @staticmethod
    def inject_trace_context_into_carrier(carrier: MutableMapping[str, str]) -> bool:
        """W3C ``traceparent`` injection into a string-keyed mapping (e.g. HTTP headers).

        Returns False if OpenTelemetry is not installed.
        """
        prop_mod, _ = OptionalImports.optional_import(
            "opentelemetry.trace.propagation.tracecontext"
        )
        ctx_mod, _ = OptionalImports.optional_import("opentelemetry.context")
        if prop_mod is None or ctx_mod is None:
            return False
        TraceContextTextMapPropagator = getattr(prop_mod, "TraceContextTextMapPropagator", None)
        get_current = getattr(ctx_mod, "get_current", None)
        if TraceContextTextMapPropagator is None or get_current is None:
            return False
        propagator = TraceContextTextMapPropagator()
        propagator.inject(carrier, context=get_current())
        return True

    @staticmethod
    def extract_trace_context_from_carrier(carrier: Mapping[str, str]) -> Any | None:
        """Parse W3C trace context from *carrier* (e.g. incoming ``traceparent`` header).

        Returns an OpenTelemetry ``Context`` or None if OTEL is missing / invalid.
        """
        prop_mod, _ = OptionalImports.optional_import(
            "opentelemetry.trace.propagation.tracecontext"
        )
        if prop_mod is None:
            return None
        TraceContextTextMapPropagator = getattr(prop_mod, "TraceContextTextMapPropagator", None)
        if TraceContextTextMapPropagator is None:
            return None
        propagator = TraceContextTextMapPropagator()
        try:
            return propagator.extract(carrier, context=None)  # type: ignore[arg-type]
        except Exception:
            return None


__all__ = ["OpenTelemetryBridge"]
