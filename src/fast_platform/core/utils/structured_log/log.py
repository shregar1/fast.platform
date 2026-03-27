"""Build and format JSON-friendly log records."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping

from .abstraction import IStructuredLogUtility

__all__ = ["StructuredLog"]


class StructuredLog(IStructuredLogUtility):
    """Build and format JSON-friendly log records."""

    @staticmethod
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

    @staticmethod
    def utc_timestamp_iso() -> str:
        """RFC 3339 timestamp in UTC."""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def build_structured_record(
        message: str,
        *,
        level: str = "INFO",
        logger: str = "",
        request_id: str | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        """Build a single log record dict with stable keys for JSON serialization."""
        rec: dict[str, Any] = {
            "timestamp": StructuredLog.utc_timestamp_iso(),
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

    @staticmethod
    def format_json_log_line(record: Mapping[str, Any]) -> str:
        """One JSON object per line (newline-terminated by caller if needed)."""
        return json.dumps(record, default=str, ensure_ascii=False)
