"""
OpenTelemetry helpers (optional ``fast-platform[otel]`` extra).

Uses ``opentelemetry-api`` only — no SDK/exporter requirement for attribute wiring.
"""

from .bridge import (
    apply_request_id_to_current_span,
    extract_trace_context_from_carrier,
    inject_trace_context_into_carrier,
)

__all__ = [
    "apply_request_id_to_current_span",
    "extract_trace_context_from_carrier",
    "inject_trace_context_into_carrier",
]
