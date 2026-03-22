"""
Optional per-channel subscriber counters (in-memory or Redis).

Use alongside :class:`~fast_channels.hub.ChannelsHub` by calling
``increment`` / ``decrement`` when WebSockets join or leave a topic, or read
:meth:`~fast_channels.hub.ChannelsHub.subscriber_count` for in-process counts only.
"""

from __future__ import annotations

from typing import Dict

from loguru import logger

try:
    import redis.asyncio as aioredis  # type: ignore[import]
except Exception:
    aioredis = None  # type: ignore[assignment]


class InMemorySubscriberCounters:
    """Per-process subscriber counts per channel/topic id."""

    def __init__(self) -> None:
        self._counts: Dict[str, int] = {}

    async def increment(self, channel_id: str) -> int:
        n = self._counts.get(channel_id, 0) + 1
        self._counts[channel_id] = n
        logger.debug("Subscriber count {} -> {}", channel_id, n)
        return n

    async def decrement(self, channel_id: str) -> int:
        n = max(0, self._counts.get(channel_id, 0) - 1)
        if n == 0:
            self._counts.pop(channel_id, None)
        else:
            self._counts[channel_id] = n
        logger.debug("Subscriber count {} -> {}", channel_id, n)
        return n

    async def count(self, channel_id: str) -> int:
        return self._counts.get(channel_id, 0)

    async def all_counts(self) -> Dict[str, int]:
        return dict(self._counts)


class RedisSubscriberCounters:
    """
    Distributed subscriber counts using Redis INCR/DECR.

    Requires ``redis.asyncio`` (optional dependency is satisfied via the package's ``redis`` dep).
    """

    def __init__(self, client: "aioredis.Redis", *, key_prefix: str = "channels:subscribers:") -> None:
        if aioredis is None:
            raise RuntimeError("redis.asyncio is not available")
        self._client = client
        self._key_prefix = key_prefix

    def _key(self, channel_id: str) -> str:
        return f"{self._key_prefix}{channel_id}"

    async def increment(self, channel_id: str) -> int:
        key = self._key(channel_id)
        n = int(await self._client.incr(key))
        logger.debug("[Redis] Subscriber count {} -> {}", channel_id, n)
        return n

    async def decrement(self, channel_id: str) -> int:
        key = self._key(channel_id)
        n = int(await self._client.decr(key))
        if n < 0:
            await self._client.set(key, 0)
            n = 0
        if n == 0:
            await self._client.delete(key)
        logger.debug("[Redis] Subscriber count {} -> {}", channel_id, n)
        return n

    async def count(self, channel_id: str) -> int:
        key = self._key(channel_id)
        raw = await self._client.get(key)
        if raw is None:
            return 0
        return int(raw)

    async def all_counts(self) -> Dict[str, int]:
        """Not implemented efficiently; returns ``{}`` (use SCAN in your app if needed)."""
        logger.debug("RedisSubscriberCounters.all_counts is not implemented; use per-channel count()")
        return {}
