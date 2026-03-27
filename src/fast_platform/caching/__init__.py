"""FastCaching Performance Ecosystem.

A ultra-high-performance caching engine for FastMVC applications, supporting
both in-memory and Redis backends with easy-to-use decorators and tag-based
invalidation logic.
"""

from .core.base import ICacheBackend
from .backends.memory import InMemoryBackend
from .decorators.cache import CacheManager, cache, fast_cache


__all__ = [
    "ICacheBackend",
    "InMemoryBackend",
    "CacheManager",
    "cache",
    "fast_cache",
]

# Version management
__version__ = "1.0.0"
