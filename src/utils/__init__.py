"""Shared utilities for fast_core."""

from .optional_imports import optional_import

from .clock import Clock, FrozenClock, SystemClock, get_clock, set_clock
from .currency_utils import currency_exponent, major_to_minor, minor_to_major
from .decimal_utils import quantize_decimal, round_money, to_decimal
from .idempotency import make_idempotency_key, sha256_hex, stable_json_dumps
from .nutrition import kcal_from_macros
from .retry import retry_async
from .metrics import Counter, Histogram, MetricsRegistry
from .time_utils import format_iso8601, parse_datetime, to_utc
from .request_id_context import get_request_id, reset_request_id, set_request_id
from .structured_log import (
    StructuredLogFields,
    StructuredLogSink,
    build_structured_record,
    format_json_log_line,
    merge_log_fields,
    utc_timestamp_iso,
)

__all__ = [
    "Clock",
    "FrozenClock",
    "SystemClock",
    "get_clock",
    "set_clock",
    "Counter",
    "Histogram",
    "MetricsRegistry",
    "optional_import",
    "to_decimal",
    "quantize_decimal",
    "round_money",
    "currency_exponent",
    "major_to_minor",
    "minor_to_major",
    "stable_json_dumps",
    "sha256_hex",
    "make_idempotency_key",
    "retry_async",
    "parse_datetime",
    "to_utc",
    "format_iso8601",
    "kcal_from_macros",
    "get_request_id",
    "set_request_id",
    "reset_request_id",
    "StructuredLogFields",
    "StructuredLogSink",
    "build_structured_record",
    "format_json_log_line",
    "merge_log_fields",
    "utc_timestamp_iso",
]
