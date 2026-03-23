"""
Observability: structured logging, metrics, tracing, audit, Datadog, OpenTelemetry.

Import as ``import observability`` (package lives under ``src/observability``).
"""

from .audit import AuditLog, audit_log
from .datadog import configure_datadog
from .logging import StructuredLogger
from .metrics import Metrics, MetricsMiddleware
from .otel import configure_otel
from .tracing import Tracer, TracingMiddleware

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
