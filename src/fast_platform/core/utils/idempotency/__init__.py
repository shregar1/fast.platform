"""Idempotency helpers.

These utilities are useful for fintech and other domains where repeated
requests must resolve to the same logical operation.
"""

from __future__ import annotations

import json
from typing import Any

from ..digests import Digests

from .abstraction import IIdempotencyUtility

__all__ = ["IIdempotencyUtility", "Idempotency"]


class Idempotency(IIdempotencyUtility):
    """Stable JSON + digest helpers for idempotency keys."""

    @staticmethod
    def stable_json_dumps(data: Any) -> str:
        """Serialize JSON with stable ordering for deterministic hashing."""
        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def sha256_hex(text: str) -> str:
        """Same digest as :meth:`Digests.sha256_hex_utf8` (string input)."""
        return Digests.sha256_hex_utf8(text)

    @staticmethod
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

        payload = Idempotency.stable_json_dumps(data)
        digest = Idempotency.sha256_hex(payload)
        digest_part = digest[:max_length]
        return f"{namespace}:{digest_part}"
