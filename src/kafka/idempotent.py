"""
Idempotent consumption helpers: manual commits + pluggable dedupe by message key.

Use with ``KafkaConsumer.loop_idempotent`` and ``enable_auto_commit=False`` in config.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Protocol, runtime_checkable

from utils.digests import Digests


@runtime_checkable
class DedupeStore(Protocol):
    """Pluggable store (Redis, DB, etc.); default is :class:`InMemoryDedupeStore`."""

    async def should_skip(self, key: str) -> bool:
        """Return ``True`` if this key was already processed successfully (skip handler)."""

    async def record_success(self, key: str) -> None:
        """Record that ``key`` was processed successfully (call after handler)."""


class InMemoryDedupeStore:
    """
    Bounded in-process dedupe set. Oldest keys are evicted when over ``max_keys``;
    evicted keys may be processed again after restart or eviction.
    """

    def __init__(self, max_keys: int = 100_000) -> None:
        if max_keys < 1:
            raise ValueError("max_keys must be >= 1")
        self._max_keys = max_keys
        self._keys: OrderedDict[str, None] = OrderedDict()

    async def should_skip(self, key: str) -> bool:
        return key in self._keys

    async def record_success(self, key: str) -> None:
        if key in self._keys:
            self._keys.move_to_end(key)
        else:
            self._keys[key] = None
        while len(self._keys) > self._max_keys:
            self._keys.popitem(last=False)


class KafkaDedupeKeys:
    """Default dedupe key derivation for Kafka payloads."""

    @staticmethod
    def default_dedupe_key(value: bytes) -> str:
        """Stable id from raw payload (SHA-256 hex) when no business key exists."""
        return Digests.sha256_hex_bytes(value)
