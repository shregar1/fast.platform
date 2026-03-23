"""Time helpers (timezone-aware parsing/normalization)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .abstraction import ITimeUtility

__all__ = ["ITimeUtility", "TimeUtility"]


class TimeUtility(ITimeUtility):
    """UTC normalization and ISO-8601 parsing/formatting."""

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Ensure ``dt`` is timezone-aware and converted to UTC."""

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def parse_datetime(value: Any) -> datetime:
        """Parse an ISO-8601 datetime string into a UTC-aware datetime."""

        if isinstance(value, datetime):
            return TimeUtility.to_utc(value)
        if not isinstance(value, str):
            raise TypeError("parse_datetime expects a datetime or ISO-8601 string")

        normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
        dt = datetime.fromisoformat(normalized)
        return TimeUtility.to_utc(dt)

    @staticmethod
    def format_iso8601(dt: datetime) -> str:
        """Format a datetime as ISO-8601 in UTC (e.g. ``2026-03-20T12:34:56Z``)."""

        utc = TimeUtility.to_utc(dt)
        return utc.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
