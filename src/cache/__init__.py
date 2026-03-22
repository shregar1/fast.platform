"""Cache backends and decorator."""

from .backend import (
    ICache,
    InMemoryCache,
    RedisCache,
    get_cache,
    cache_result,
)

__all__ = [
    "ICache",
    "InMemoryCache",
    "RedisCache",
    "get_cache",
    "cache_result",
]
