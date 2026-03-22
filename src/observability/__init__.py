"""
Observability: structured logging, metrics, tracing, audit, Datadog, OpenTelemetry.

Prefer ``from fast_observability import …`` in new code; ``core.observability`` in pyfastmvc re-exports the same API.
"""

from fast_observability.audit import AuditLog, audit_log
from fast_observability.datadog import configure_datadog
from fast_observability.logging import StructuredLogger
from fast_observability.metrics import Metrics, MetricsMiddleware
from fast_observability.otel import configure_otel
from fast_observability.tracing import Tracer, TracingMiddleware

__all__ = [
    "StructuredLogger",
    "configure_datadog",
    "configure_otel",
    "Metrics",
    "MetricsMiddleware",
    "Tracer",
    "TracingMiddleware",
    "AuditLog",
    "audit_log",
]
