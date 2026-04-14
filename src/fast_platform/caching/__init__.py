"""Smart caching: cache-aside, stale-while-revalidate hooks, deduplication, invalidation."""

from .abstraction import ICaching
from .redis_backend import RedisCacheBackend
from .smart_cache import (
    CacheBackend,
    CacheConfig,
    CacheEntry,
    CacheInvalidator,
    CacheStrategy,
    InMemoryCacheBackend,
    InvalidationEvent,
    SmartCacheManager,
    cache_invalidator,
    smart_cache,
)

__all__ = [
    "ICaching",
    "RedisCacheBackend",
    "SmartCacheManager",
    "smart_cache",
    "CacheConfig",
    "CacheStrategy",
    "InvalidationEvent",
    "CacheEntry",
    "CacheBackend",
    "InMemoryCacheBackend",
    "CacheInvalidator",
    "cache_invalidator",
]
