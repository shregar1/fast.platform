"""Cache package for Fast Platform.

Provides caching decorators and backends.
"""

from fast_platform.data.cache.abstraction import ICaching
from fast_platform.data.cache.decorator import cached, cache_evict, clear_cache, invalidate_pattern

__all__ = [
    "ICaching",
    "cached",
    "cache_evict",
    "clear_cache",
    "invalidate_pattern",
]
