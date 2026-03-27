"""OpenTelemetry helpers (optional ``fast-platform[otel]`` extra).

Uses ``opentelemetry-api`` only — no SDK/exporter requirement for attribute wiring.
"""

from .bridge import OpenTelemetryBridge

__all__ = [
    "OpenTelemetryBridge",
]
