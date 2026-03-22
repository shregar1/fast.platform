"""
Vendor-neutral structured logging contract (JSON-friendly fields).

Use this to build log lines or payloads that work with any backend (stdout,
Loguru, structlog, OpenTelemetry) without importing those libraries here.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, TypedDict, runtime_checkable


class StructuredLogFields(TypedDict, total=False):
    """Suggested keys for JSON log lines; all optional."""

    timestamp: str
    level: str
    logger: str
    message: str
    request_id: str
    service: str
    environment: str


def merge_log_fields(
    base: Mapping[str, Any],
    **extra: Any,
) -> dict[str, Any]:
    """Shallow merge *extra* into a copy of *base* (suitable for JSON output)."""
    out: dict[str, Any] = dict(base)
    for k, v in extra.items():
        if v is not None:
            out[k] = v
    return out


def utc_timestamp_iso() -> str:
    """RFC 3339 timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_structured_record(
    message: str,
    *,
    level: str = "INFO",
    logger: str = "",
    request_id: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """
    Build a single log record dict with stable keys for JSON serialization.

    Unknown keyword arguments are merged into the top level (flat), which
    matches common JSON logging conventions.
    """
    rec: dict[str, Any] = {
        "timestamp": utc_timestamp_iso(),
        "level": level.upper(),
        "message": message,
    }
    if logger:
        rec["logger"] = logger
    if request_id:
        rec["request_id"] = request_id
    for k, v in extra.items():
        if v is not None:
            rec[k] = v
    return rec


def format_json_log_line(record: Mapping[str, Any]) -> str:
    """One JSON object per line (newline-terminated by caller if needed)."""
    return json.dumps(record, default=str, ensure_ascii=False)


@runtime_checkable
class StructuredLogSink(Protocol):
    """Protocol for adapters (stdout, loguru, etc.)."""

    def emit(self, record: Mapping[str, Any]) -> None:
        """Deliver a structured record (e.g. write JSON line)."""
        ...
