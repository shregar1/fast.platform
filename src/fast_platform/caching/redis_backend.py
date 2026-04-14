"""Redis backend for :class:`~fast_platform.caching.smart_cache.SmartCacheManager`."""

from __future__ import annotations

from ..core.constants import DEFAULT_HOST
from .constants import DEFAULT_REDIS_URL
from typing import TYPE_CHECKING, Optional

import redis.asyncio as aioredis

if TYPE_CHECKING:
    from redis.asyncio import Redis


class RedisCacheBackend:
    """Async Redis backend: raw serialized blobs with ``EX`` TTL.

    ``stale_ttl`` is accepted for API compatibility with
    :class:`~fast_platform.caching.smart_cache.InMemoryCacheBackend` but is not
    stored separately; stale-while-revalidate semantics for Redis are handled at
    the application layer if needed.
    """

    def __init__(
        self,
        *,
        redis: Optional["Redis"] = None,
        url: Optional[str] = None,
        host: str = DEFAULT_HOST,
        port: int = 6379,
        db: int = 0,
        key_prefix: str = "smartcache:",
    ) -> None:
        self._owns_client = False
        if redis is not None:
            self._redis = redis
        elif url is not None:
            self._redis = aioredis.from_url(url, decode_responses=False)
            self._owns_client = True
        else:
            self._redis = aioredis.Redis(
                host=host, port=port, db=db, decode_responses=False
            )
            self._owns_client = True
        self._prefix = key_prefix

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[bytes]:
        raw = await self._redis.get(self._full_key(key))
        if raw is None:
            return None
        return raw if isinstance(raw, (bytes, bytearray)) else bytes(raw)

    async def set(
        self,
        key: str,
        value: bytes,
        ttl: Optional[int] = None,
        stale_ttl: Optional[int] = None,
    ) -> bool:
        _ = stale_ttl
        seconds = int(ttl if ttl is not None else 300)
        await self._redis.set(self._full_key(key), value, ex=seconds)
        return True

    async def delete(self, key: str) -> bool:
        deleted = await self._redis.delete(self._full_key(key))
        return deleted > 0

    async def delete_pattern(self, pattern: str) -> int:
        match = self._full_key(pattern)
        cursor = 0
        total = 0
        while True:
            cursor, keys = await self._redis.scan(cursor, match=match, count=256)
            if keys:
                total += await self._redis.delete(*keys)
            if cursor == 0:
                break
        return total

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(self._full_key(key)))

    async def clear(self) -> bool:
        await self.delete_pattern("*")
        return True

    async def aclose(self) -> None:
        """Close the client if this backend created it."""
        if self._owns_client:
            await self._redis.aclose()
