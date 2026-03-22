"""
Vendor-neutral structured logging contract (JSON-friendly fields).

Use this to build log lines or payloads that work with any backend (stdout,
Loguru, structlog, OpenTelemetry) without importing those libraries here.
"""

from __future__ import annotations

from .fields import StructuredLogFields
from .log import StructuredLog
from .sink import StructuredLogSink

__all__ = ["StructuredLog", "StructuredLogFields", "StructuredLogSink"]
