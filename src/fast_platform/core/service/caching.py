"""FastPlatform Caching Service.

Formal service implementation for platform-level caching, providing a 
standardized, DI-compatible interface for performance optimization.
"""

from typing import Any, List, Optional
from ...caching.service import PlatformCache
from .abstraction import IService


class CachingService(IService):
    """Platform-level caching service for high-performance data residency.
    
    Acts as a first-class citizen in the FastPlatform service registry, 
    enabling global cache management and domain-specific invalidation.
    """

    def __init__(self, default_ttl: int = 3600):
        """Initialize with default residence window.
        
        Args:
            default_ttl (int): Global default expiration.
        """
        self._default_ttl = default_ttl

    async def get(self, namespace: str, key: str) -> Any:
        """Fetch data from the platform cache.
        
        Args:
            namespace (str): Data domain.
            key (str): Unique entry identifier.
            
        Returns:
            Any: Resident data or None.
        """
        return await PlatformCache.get_state(namespace, key)

    async def set(
        self, 
        namespace: str, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Persist data in the ecosystem.
        
        Args:
            namespace (str): Data domain.
            key (str): Unique entry identifier.
            value (Any): Payload.
            ttl (Optional[int]): Personal override for residence duration.
            
        Returns:
            bool: Operation success.
        """
        return await PlatformCache.set_state(
            namespace, 
            key, 
            value, 
            ttl=ttl or self._default_ttl
        )

    async def invalidate(self, namespace: str) -> int:
        """Purge all entries across a specific domain.
        
        Args:
            namespace (str): Target domain.
            
        Returns:
            int: Purge count.
        """
        return await PlatformCache.invalidate_domain(namespace)
