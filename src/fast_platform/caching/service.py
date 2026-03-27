"""FastCaching Platform Service.

Provides the PlatformCache service class for integration with the platform service layer.
"""

from typing import Any, Optional

from .decorators.cache import CacheManager


class PlatformCache:
    """Platform-level cache service for global state management.
    
    Provides namespace-isolated caching primitives for the FastPlatform ecosystem,
    enabling domain-specific cache management and invalidation.
    """

    _manager: Optional[CacheManager] = None

    @classmethod
    def initialize(cls, manager: CacheManager) -> None:
        """Set the global cache manager instance.
        
        Args:
            manager: The CacheManager instance to use.
        """
        cls._manager = manager

    @classmethod
    async def get_state(cls, namespace: str, key: str) -> Any:
        """Fetch data from the platform cache.
        
        Args:
            namespace: Data domain/namespace.
            key: Unique entry identifier.
            
        Returns:
            The cached value or None if not found.
        """
        if cls._manager is None:
            return None
        full_key = f"{namespace}:{key}"
        return await cls._manager.get(full_key)

    @classmethod
    async def set_state(
        cls, 
        namespace: str, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Persist data in the platform cache.
        
        Args:
            namespace: Data domain/namespace.
            key: Unique entry identifier.
            value: The value to cache.
            ttl: Time-to-live in seconds.
            
        Returns:
            True if the operation succeeded.
        """
        if cls._manager is None:
            return False
        full_key = f"{namespace}:{key}"
        await cls._manager.set(full_key, value, ttl=ttl)
        return True

    @classmethod
    async def invalidate_domain(cls, namespace: str) -> int:
        """Purge all entries in a namespace.
        
        Args:
            namespace: Target domain to invalidate.
            
        Returns:
            Number of entries purged.
        """
        if cls._manager is None:
            return 0
        # Note: This is a simplified implementation
        # A full implementation would track keys per namespace
        return 0


__all__ = ["PlatformCache"]
