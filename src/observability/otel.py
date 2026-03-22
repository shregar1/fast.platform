"""
OpenTelemetry integration helpers.

This module configures OpenTelemetry tracing for FastAPI based on
`config/telemetry/config.json`. It is optional and only activated
when enabled in configuration.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from from fast_platform import TelemetryConfiguration
from loguru import logger


def configure_otel(app: FastAPI) -> None:
    """
    Configure OpenTelemetry tracing for the given FastAPI app.
    """
    cfg = TelemetryConfiguration().get_config()
    if not cfg.enabled:
        logger.info("OpenTelemetry is disabled in configuration.")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter as OTLPSpanExporterGrpc,
        )
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter as OTLPSpanExporterHttp,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except Exception:  # pragma: no cover - optional dependency
        logger.warning(
            "OpenTelemetry dependencies are not installed. "
            "Install with `pip install opentelemetry-sdk "
            "opentelemetry-exporter-otlp opentelemetry-instrumentation-fastapi` "
            "to enable telemetry."
        )
        return

    resource = Resource.create(
        {
            "service.name": cfg.service_name,
            "deployment.environment": cfg.environment,
        }
    )
    provider = TracerProvider(resource=resource)

    exporter: Any
    if cfg.exporter == "otlp":
        endpoint = cfg.endpoint or "http://localhost:4317"
        if cfg.protocol == "http/protobuf":
            exporter = OTLPSpanExporterHttp(endpoint=endpoint)
        else:
            exporter = OTLPSpanExporterGrpc(endpoint=endpoint)
    else:
        # console or none – fall back to console exporter behavior via OTLP HTTP to stdout
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        exporter = ConsoleSpanExporter()

    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    logger.info(
        "Configured OpenTelemetry tracing",
        exporter=cfg.exporter,
        endpoint=cfg.endpoint or "default",
        protocol=cfg.protocol,
        service_name=cfg.service_name,
        environment=cfg.environment,
    )

