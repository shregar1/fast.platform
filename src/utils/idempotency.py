"""Idempotency helpers.

These utilities are useful for fintech and other domains where repeated
requests must resolve to the same logical operation.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

__all__ = [
    "stable_json_dumps",
    "sha256_hex",
    "make_idempotency_key",
]


def stable_json_dumps(data: Any) -> str:
    """Serialize JSON with stable ordering for deterministic hashing."""

    # default=str helps with Decimal, datetime, UUID, etc. where the caller
    # knows their app-level meaning.
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def sha256_hex(text: str) -> str:
    """Return SHA-256 hex digest for the input string."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_idempotency_key(
    *,
    namespace: str,
    data: Any,
    max_length: int = 64,
) -> str:
    """Create an idempotency key from stable JSON.

    The key is namespaced so you can use the same hashing strategy across
    payment, onboarding, fulfillment, etc.
    """

    if not namespace:
        raise ValueError("namespace is required")
    if max_length <= 0:
        raise ValueError("max_length must be > 0")

    payload = stable_json_dumps(data)
    digest = sha256_hex(payload)
    digest_part = digest[:max_length]
    return f"{namespace}:{digest_part}"

