"""
Dead-letter topic helpers: standard metadata headers for DLQ messages.
"""

from __future__ import annotations

from typing import Optional

# Public header names (Kafka record headers are case-sensitive; use these consistently).
DLQ_HEADER_ORIGINAL_TOPIC = "x-dlq-original-topic"
DLQ_HEADER_ERROR = "x-dlq-error"
DLQ_HEADER_PARTITION = "x-dlq-partition"
DLQ_HEADER_OFFSET = "x-dlq-offset"


def make_dlq_headers(
    *,
    original_topic: str,
    error: str,
    partition: Optional[int] = None,
    offset: Optional[int] = None,
    extra: Optional[list[tuple[str, bytes]]] = None,
) -> list[tuple[str, bytes]]:
    """
    Build Kafka producer headers for a dead-letter record.

    * *original_topic* — topic the message came from (or was intended for).
    * *error* — short failure reason (truncate in your app if needed).
    * *partition* / *offset* — optional source coordinates when known.
    * *extra* — additional ``(name, bytes)`` pairs (e.g. trace id).
    """
    headers: list[tuple[str, bytes]] = [
        (DLQ_HEADER_ORIGINAL_TOPIC, original_topic.encode("utf-8")),
        (DLQ_HEADER_ERROR, error.encode("utf-8")),
    ]
    if partition is not None:
        headers.append((DLQ_HEADER_PARTITION, str(partition).encode("ascii")))
    if offset is not None:
        headers.append((DLQ_HEADER_OFFSET, str(offset).encode("ascii")))
    if extra:
        headers.extend(extra)
    return headers
