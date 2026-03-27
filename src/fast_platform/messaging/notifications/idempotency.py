"""Idempotency for fan-out sends: ``(user_id, template_id, dedupe_key)`` within a TTL window.

Use in-memory for single-process tests or **Redis** for distributed dedupe.
"""

from __future__ import annotations

import time
from typing import Protocol, runtime_checkable

from loguru import logger

try:
    import redis.asyncio as aioredis  # type: ignore[import]
except Exception:
    aioredis = None  # type: ignore[assignment]


def make_idempotency_key(user_id: str, template_id: str, dedupe_key: str) -> str:
    """Stable cache key component (caller may prefix with a namespace)."""
    return f"{user_id}\x1f{template_id}\x1f{dedupe_key}"


@runtime_checkable
class NotificationIdempotencyStore(Protocol):
    """First successful ``try_acquire`` within TTL wins; later calls return False."""

    async def try_acquire(self, key: str, *, ttl_seconds: int) -> bool:
        """Return True if this key was not seen within TTL (caller should send)."""
        ...


class InMemoryNotificationIdempotencyStore:
    """Single-process dedupe with expiry (not shared across workers)."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self._expiry_at: dict[str, float] = {}

    def _prune(self, now: float) -> None:
        """Execute _prune operation.

        Args:
            now: The now parameter.

        Returns:
            The result of the operation.
        """
        dead = [k for k, exp in self._expiry_at.items() if exp <= now]
        for k in dead:
            self._expiry_at.pop(k, None)

    async def try_acquire(self, key: str, *, ttl_seconds: int) -> bool:
        """Execute try_acquire operation.

        Args:
            key: The key parameter.
            ttl_seconds: The ttl_seconds parameter.

        Returns:
            The result of the operation.
        """
        now = time.time()
        self._prune(now)
        exp = self._expiry_at.get(key)
        if exp is not None and exp > now:
            logger.debug("Idempotency hit (in-memory): {}", key[:80])
            return False
        self._expiry_at[key] = now + float(ttl_seconds)
        return True


class RedisNotificationIdempotencyStore:
    """Distributed dedupe using ``SET key 1 NX EX ttl``.

    Requires ``redis`` (``pip install fast_notifications[redis]``).
    """

    def __init__(self, client: "aioredis.Redis", *, key_prefix: str = "notif:idemp:") -> None:
        """Execute __init__ operation.

        Args:
            client: The client parameter.
            key_prefix: The key_prefix parameter.
        """
        if aioredis is None:
            raise RuntimeError("redis.asyncio is not available")
        self._client = client
        self._prefix = key_prefix

    def _full_key(self, key: str) -> str:
        """Execute _full_key operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        return f"{self._prefix}{key}"

    async def try_acquire(self, key: str, *, ttl_seconds: int) -> bool:
        """Execute try_acquire operation.

        Args:
            key: The key parameter.
            ttl_seconds: The ttl_seconds parameter.

        Returns:
            The result of the operation.
        """
        fk = self._full_key(key)
        ok = await self._client.set(fk, b"1", nx=True, ex=int(ttl_seconds))
        if not ok:
            logger.debug("Idempotency hit (Redis): {}", key[:80])
        return bool(ok)
