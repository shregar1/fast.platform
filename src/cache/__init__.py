"""Cache backends and decorator."""

from .backend import (
    ICache,
    InMemoryCache,
    RedisCache,
    cache_result,
    get_cache,
)

__all__ = [
    "ICache",
    "InMemoryCache",
    "RedisCache",
    "get_cache",
    "cache_result",
]
