"""
Dead-letter and quarantine queue naming, plus DLQ/quarantine message wrapping.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict, Optional, Tuple

from fast_core.services.queues import QueueMessage

DEFAULT_DLQ_SUFFIX = ".dlq"
DEFAULT_QUARANTINE_SUFFIX = ".quarantine"


def dlq_name(primary_queue: str) -> str:
    """Return the conventional DLQ name for a primary queue (idempotent if already suffixed)."""
    if is_dlq_name(primary_queue):
        return primary_queue
    return primary_queue + DEFAULT_DLQ_SUFFIX


def is_dlq_name(name: str) -> bool:
    return name.endswith(DEFAULT_DLQ_SUFFIX)


def primary_queue_from_dlq(dlq_name_str: str) -> str:
    """Strip ``.dlq`` suffix; if absent, return the name unchanged."""
    if is_dlq_name(dlq_name_str):
        return dlq_name_str[: -len(DEFAULT_DLQ_SUFFIX)]
    return dlq_name_str


def quarantine_name(primary_queue: str) -> str:
    """Return the poison / quarantine queue name (``<primary>.quarantine``)."""
    base = primary_queue_from_dlq(primary_queue) if is_dlq_name(primary_queue) else primary_queue
    if is_quarantine_name(base):
        return base
    return base + DEFAULT_QUARANTINE_SUFFIX


def is_quarantine_name(name: str) -> bool:
    return name.endswith(DEFAULT_QUARANTINE_SUFFIX)


def primary_queue_from_quarantine(quarantine_name_str: str) -> str:
    if is_quarantine_name(quarantine_name_str):
        return quarantine_name_str[: -len(DEFAULT_QUARANTINE_SUFFIX)]
    return quarantine_name_str


def prepare_dlq_message(
    primary_queue: str,
    msg: QueueMessage,
    *,
    reason: str,
    error: Optional[str] = None,
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Build a DLQ body (JSON) and attribute metadata for a failed message.

    The body includes base64-encoded original bytes and copies of relevant attributes.
    """
    attrs = dict(msg.attributes or {})
    attrs["x-fastmvc-primary-queue"] = primary_queue
    attrs["x-fastmvc-dlq-reason"] = reason
    if error:
        attrs["x-fastmvc-dlq-error"] = error[:4000]

    body: Dict[str, Any] = {
        "kind": "fast_dlq",
        "primary_queue": primary_queue,
        "reason": reason,
        "original_body_b64": base64.b64encode(msg.body or b"").decode("ascii"),
        "original_attributes": dict(msg.attributes or {}),
    }
    if error:
        body["error"] = error[:8000]

    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return raw, attrs


def prepare_quarantine_message(
    primary_queue: str,
    msg: QueueMessage,
    *,
    failure_count: int,
    max_failures: int,
    reason: str = "poison_threshold_exceeded",
    last_error: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Build a quarantine queue body after ``failure_count`` failures (>= ``max_failures``).

    ``extra_metadata`` is merged into the JSON document for operators (ids, traces, etc.).
    """
    attrs = dict(msg.attributes or {})
    attrs["x-fastmvc-primary-queue"] = primary_queue
    attrs["x-fastmvc-quarantine-reason"] = reason
    attrs["x-fastmvc-failure-count"] = str(failure_count)
    attrs["x-fastmvc-max-failures"] = str(max_failures)
    if last_error:
        attrs["x-fastmvc-last-error"] = last_error[:4000]

    doc: Dict[str, Any] = {
        "kind": "fast_quarantine",
        "primary_queue": primary_queue,
        "reason": reason,
        "failure_count": failure_count,
        "max_failures": max_failures,
        "original_body_b64": base64.b64encode(msg.body or b"").decode("ascii"),
        "original_attributes": dict(msg.attributes or {}),
    }
    if last_error:
        doc["last_error"] = last_error[:8000]
    if extra_metadata:
        doc["metadata"] = dict(extra_metadata)

    raw = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return raw, attrs
