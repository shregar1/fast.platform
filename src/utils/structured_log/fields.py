"""Typed keys for JSON-friendly structured log records."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["StructuredLogFields"]


class StructuredLogFields(TypedDict, total=False):
    """Suggested keys for JSON log lines; all optional."""

    timestamp: str
    level: str
    logger: str
    message: str
    request_id: str
    service: str
    environment: str
