"""FastCaching In-Memory Backend Implementation.

Provides a thread-safe, high-performance local memory caching engine
with built-in TTL support and tag-based invalidation logic.
"""

from ..constants import MEMORY_BACKEND
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, List, Optional, Set
import asyncio

from ..core.base import ICacheBackend


@dataclass
class CacheEntry:
    """Represents a single entry in the in-memory cache.
    
    Attributes:
        value (Any): The cached data.
        expires (Optional[datetime]): When the entry becomes stale.
        tags (Set[str]): Associated tags for invalidation.
    """
    value: Any
    expires: Optional[datetime] = None
    tags: Optional[Set[str]] = None

    @property
    def is_expired(self) -> bool:
        """Evaluate if the cache entry has reached its TTL.
        
        Returns:
            bool: True if expiration is set and reached, else False.
        """
        if self.expires is None:
            return False
        return datetime.now() > self.expires


class InMemoryBackend(ICacheBackend):
    """Local volatile caching storage with tagging and expiration.
    
    This implementation is designed for lightweight caching and rapid
    development cycles without external infrastructure requirements.
    """

    def __init__(self, max_size: int = 10000):
        """Initialize the backend with internal storage structures.
        
        Args:
            max_size (int): The maximum number of entries to store.
        """
        self._store: Dict[str, CacheEntry] = {}
        self._tag_map: Dict[str, Set[str]] = defaultdict(set)
        self._lock = Lock()
        self._max_size = max_size

    async def get(self, key: str) -> Any:
        """Synchronously check and retrieve cached values.
        
        Args:
            key (str): The specific identifier.
            
        Returns:
            Any: The cached object or None if expired or missing.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry:
                if entry.is_expired:
                    self._delete_internal(key)
                    return None
                return entry.value
        return None

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None, 
        tags: Optional[List[str]] = None
    ) -> bool:
        """Persist data into local memory.
        
        Args:
            key (str): Unique identifier.
            value (Any): Object to store.
            ttl (Optional[int]): Expiration window in seconds.
            tags (Optional[List[str]]): Invalidation identifiers.
            
        Returns:
            bool: Always True for successful storage.
        """
        with self._lock:
            # Handle max size overflow - simple trim
            if len(self._store) >= self._max_size:
                # Basic eviction of any expired entries first
                expired_keys = [k for k, v in self._store.items() if v.is_expired]
                for k in expired_keys:
                    self._delete_internal(k)
                # If still too large, pop the first key
                if len(self._store) >= self._max_size:
                    first_key = next(iter(self._store))
                    self._delete_internal(first_key)
            
            expires = datetime.now() + timedelta(seconds=ttl) if ttl else None
            tag_set = set(tags) if tags else set()
            
            entry = CacheEntry(value=value, expires=expires, tags=tag_set)
            self._store[key] = entry
            
            # Update tag index
            for tag in tag_set:
                self._tag_map[tag].add(key)
        return True

    async def delete(self, key: str) -> bool:
        """Remove a single entry.
        
        Args:
            key (str): The key to purge.
            
        Returns:
            bool: True if key was present, else False.
        """
        with self._lock:
            return self._delete_internal(key)

    def _delete_internal(self, key: str) -> bool:
        """Internal helper for deletion with tag cleanup.
        
        Args:
            key (str): Key to remove.
            
        Returns:
            bool: Operation success status.
        """
        entry = self._store.pop(key, None)
        if entry and entry.tags:
            for tag in entry.tags:
                self._tag_map[tag].discard(key)
                if not self._tag_map[tag]:
                    del self._tag_map[tag]
            return True
        return False

    async def invalidate_tags(self, tags: List[str]) -> int:
        """Invalidate all keys associated with any of the provided tags.
        
        Args:
            tags (List[str]): List of tags to purge.
            
        Returns:
            int: The total count of invalidated entries.
        """
        count = 0
        with self._lock:
            keys_to_purge = set()
            for tag in tags:
                keys_to_purge.update(self._tag_map.get(tag, set()))
            
            for key in keys_to_purge:
                if self._delete_internal(key):
                    count += 1
        return count

    async def clear(self) -> bool:
        """Wipe the entire cache store.
        
        Returns:
            bool: Hard reset success and mapping cleanup.
        """
        with self._lock:
            self._store.clear()
            self._tag_map.clear()
        return True

    async def exists(self, key: str) -> bool:
        """Verify presence and validity.
        
        Args:
            key (str): Key to verify.
            
        Returns:
            bool: True if present and not expired.
        """
        return await self.get(key) is not None
