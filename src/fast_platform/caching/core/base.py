"""FastCaching Base Module.

This module provides the core interfaces and abstractions for the FastCaching
performance engine, supporting both sync and async caching operations.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union


class ICacheBackend(ABC):
    """Base interface for all cache backends.
    
    All FastCaching backends must implement this interface to ensure
    consistent behavior across different storage engines (Redis, In-Memory, etc.).
    """

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Retrieve a value from the cache.
        
        Args:
            key (str): The unique cache key.
            
        Returns:
            Any: The cached value if found, else None.
        """
        pass

    @abstractmethod
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None, 
        tags: Optional[List[str]] = None
    ) -> bool:
        """Store a value in the cache with optional TTL and tagging.
        
        Args:
            key (str): The unique cache key.
            value (Any): The data to cache.
            ttl (Optional[int]): Time-to-live in seconds.
            tags (Optional[List[str]]): List of tags for grouping and invalidation.
            
        Returns:
            bool: True if storage was successful, else False.
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a specific key from the cache.
        
        Args:
            key (str): The key to remove.
            
        Returns:
            bool: True if deletion was successful, else False.
        """
        pass

    @abstractmethod
    async def invalidate_tags(self, tags: List[str]) -> int:
        """Remove all cache entries associated with the specified tags.
        
        Args:
            tags (List[str]): The tags to invalidate.
            
        Returns:
            int: Number of entries removed.
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all entries from the cache backend.
        
        Returns:
            bool: True if clearing was successful, else False.
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.
        
        Args:
            key (str): The key to check.
            
        Returns:
            bool: True if key exists, else False.
        """
        pass
