"""Time helpers (timezone-aware parsing/normalization)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

__all__ = ["parse_datetime", "to_utc", "format_iso8601"]


def to_utc(dt: datetime) -> datetime:
    """Ensure ``dt`` is timezone-aware and converted to UTC."""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_datetime(value: Any) -> datetime:
    """Parse an ISO-8601 datetime string into a UTC-aware datetime."""

    if isinstance(value, datetime):
        return to_utc(value)
    if not isinstance(value, str):
        raise TypeError("parse_datetime expects a datetime or ISO-8601 string")

    # Handle common “Z” suffix from APIs.
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    dt = datetime.fromisoformat(normalized)
    return to_utc(dt)


def format_iso8601(dt: datetime) -> str:
    """Format a datetime as ISO-8601 in UTC (e.g. ``2026-03-20T12:34:56Z``)."""

    utc = to_utc(dt)
    # fromisoformat uses offset; we standardize to Z for readability.
    return utc.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

