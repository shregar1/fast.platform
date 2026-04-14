from __future__ import annotations
"""Webhook idempotency: avoid double-processing the same provider event (e.g. Stripe ``event.id``)."""

from ...core.constants import DEFAULT_LIMIT

import asyncio
from collections import OrderedDict
from typing import Protocol, runtime_checkable


@runtime_checkable
class WebhookIdempotencyStore(Protocol):
    """Pluggable store (Redis, DB, …). Default: :class:`InMemoryWebhookIdempotencyStore`.

    * ``is_duplicate`` — ``True`` if this key was already processed (return 2xx without side effects).
    * ``mark_processed`` — call after successful handling.
    """

    async def is_duplicate(self, key: str) -> bool:
        """Return ``True`` if ``key`` was already seen (skip business logic)."""

    async def mark_processed(self, key: str) -> None:
        """Record that ``key`` completed successfully."""


class InMemoryWebhookIdempotencyStore:
    """Bounded in-process store. Oldest keys are evicted when over ``max_keys``;
    evicted keys may be processed again.
    """

    def __init__(self, max_keys: int = DEFAULT_LIMIT) -> None:
        """Execute __init__ operation.

        Args:
            max_keys: The max_keys parameter.
        """
        if max_keys < 1:
            raise ValueError("max_keys must be >= 1")
        self._max_keys = max_keys
        self._keys: OrderedDict[str, None] = OrderedDict()
        self._lock = asyncio.Lock()

    async def is_duplicate(self, key: str) -> bool:
        """Execute is_duplicate operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        async with self._lock:
            return key in self._keys

    async def mark_processed(self, key: str) -> None:
        """Execute mark_processed operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        async with self._lock:
            if key in self._keys:
                self._keys.move_to_end(key)
            else:
                self._keys[key] = None
            while len(self._keys) > self._max_keys:
                self._keys.popitem(last=False)
