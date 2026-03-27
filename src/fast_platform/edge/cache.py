"""Edge Cache API."""

from typing import Optional
import hashlib
import time

from .core import EdgeRequest, EdgeResponse


class EdgeCache:
    """Programmatic cache control at the edge.

    In production, this integrates with CDN cache APIs like
    Cloudflare Cache API or Fastly's cache control.
    """

    # In-memory cache for development/testing
    _cache: dict = {}

    def __init__(self, cache_name: str = "default"):
        """Execute __init__ operation.

        Args:
            cache_name: The cache_name parameter.
        """
        self.cache_name = cache_name
        if cache_name not in self._cache:
            self._cache[cache_name] = {}

    def _make_cache_key(self, request: EdgeRequest) -> str:
        """Generate cache key from request."""
        key_parts = [
            request.method,
            request.url,
            # Include vary headers in key
        ]
        return hashlib.sha256("|".join(key_parts).encode()).hexdigest()

    async def match(self, request: EdgeRequest) -> Optional[EdgeResponse]:
        """Check if request matches cache."""
        cache_key = self._make_cache_key(request)
        cache = self._cache[self.cache_name]

        if cache_key not in cache:
            return None

        entry = cache[cache_key]

        # Check expiration
        if entry.get("expires") < time.time():
            del cache[cache_key]
            return None

        # Return cached response with HIT header
        response = entry["response"]
        response.headers["x-cache-status"] = "HIT"
        response.headers["x-cache-age"] = str(int(time.time() - entry["created"]))

        return response

    async def put(self, request: EdgeRequest, response: EdgeResponse) -> None:
        """Cache a response."""
        if not response.cache_ttl:
            return

        cache_key = self._make_cache_key(request)
        cache = self._cache[self.cache_name]

        cache[cache_key] = {
            "response": response,
            "created": time.time(),
            "expires": time.time() + response.cache_ttl,
            "tags": response.cache_tags,
        }

    async def delete(self, cache_key: str) -> bool:
        """Delete from cache by key."""
        cache = self._cache[self.cache_name]
        if cache_key in cache:
            del cache[cache_key]
            return True
        return False

    async def purge_by_tag(self, tag: str) -> int:
        """Purge all entries with tag."""
        cache = self._cache[self.cache_name]
        to_delete = []

        for key, entry in cache.items():
            if tag in entry.get("tags", []):
                to_delete.append(key)

        for key in to_delete:
            del cache[key]

        return len(to_delete)

    async def purge_all(self) -> int:
        """Purge entire cache."""
        cache = self._cache[self.cache_name]
        count = len(cache)
        cache.clear()
        return count

    async def get_stats(self) -> dict:
        """Get cache statistics."""
        cache = self._cache[self.cache_name]

        total_entries = len(cache)
        total_size = sum(len(str(e["response"].body or "")) for e in cache.values())

        expired = sum(1 for e in cache.values() if e.get("expires", 0) < time.time())

        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "expired_entries": expired,
            "cache_name": self.cache_name,
        }


# Convenience functions for common caching patterns


async def cached_fetch(
    request: EdgeRequest, fetch_func, ttl: int = 300, tags: Optional[list] = None
) -> EdgeResponse:
    """Fetch with caching - checks cache first, then fetches if miss."""
    cache = EdgeCache()

    # Check cache
    cached = await cache.match(request)
    if cached:
        return cached

    # Fetch from origin
    response = await fetch_func(request)

    # Cache if successful
    if response.status == 200:
        response.cache_ttl = ttl
        response.cache_tags = tags or []
        await cache.put(request, response)

    response.headers["x-cache-status"] = "MISS"
    return response


async def cache_invalidate(tags: list) -> dict:
    """Invalidate cache by tags."""
    cache = EdgeCache()
    results = {}

    for tag in tags:
        count = await cache.purge_by_tag(tag)
        results[tag] = count

    return results
