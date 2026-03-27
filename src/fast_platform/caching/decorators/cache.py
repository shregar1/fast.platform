"""FastCaching Core Cache Manager and Decorators.

Provides the primary interface for unified caching operations and the
standard `@cache` decorator for transparent data residency management.
"""

from functools import wraps
from typing import Any, Callable, List, Optional, TypeVar, Union, cast
import asyncio
import hashlib
import pickle

from ..backends.memory import InMemoryBackend
from ..core.base import ICacheBackend

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class CacheManager:
    """The central access point for the FastCaching system.
    
    Acts as a singleton by default if not manually instantiated with a backend.
    Handles backend registry and key generation for the entire ecosystem.
    """

    _instance: Optional["CacheManager"] = None
    _backend: ICacheBackend

    def __new__(cls, *args, **kwargs):
        """Standard singleton pattern for FastCaching.
        
        Returns:
            CacheManager: The globally accessible instance.
        """
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, backend: Optional[ICacheBackend] = None):
        """Initialize the global manager with a storage provider.
        
        Args:
            backend (Optional[ICacheBackend]): Persistence engine.
        """
        if not hasattr(self, "_backend"):
            self._backend = backend or InMemoryBackend()

    @property
    def backend(self) -> ICacheBackend:
        """Access the current storage engine.
        
        Returns:
            ICacheBackend: The active backend instance.
        """
        return self._backend

    def set_backend(self, backend: ICacheBackend) -> None:
        """Switch storage engine at runtime.
        
        Args:
            backend (ICacheBackend): The new backend.
        """
        self._backend = backend

    def generate_key(self, func: Callable, *args, **kwargs) -> str:
        """Create a unique string identifier based on function state.
        
        Args:
            func (Callable): The decorated function.
            *args (Any): Provided positional arguments.
            **kwargs (Any): Provided keyword arguments.
            
        Returns:
            str: Deterministic hash key.
        """
        # Create a unique represention of function name and parameters
        key_data = {
            "module": func.__module__,
            "name": func.__name__,
            "args": args,
            "kwargs": kwargs,
        }
        pickled_key = pickle.dumps(key_data)
        return hashlib.md5(pickled_key).hexdigest()

    async def get(self, key: str) -> Any:
        """Retrieve cached value.
        
        Args:
            key (str): Lookup key.
            
        Returns:
            Any: Value or None.
        """
        return await self._backend.get(key)

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None, 
        tags: Optional[List[str]] = None
    ) -> bool:
        """Persist value.
        
        Args:
            key (str): Unique identifier.
            value (Any): Data.
            ttl (Optional[int]): Time-to-live.
            tags (Optional[List[str]]): Management tags.
            
        Returns:
            bool: Success status.
        """
        return await self._backend.set(key, value, ttl, tags)

    async def invalidate(self, tags: List[str]) -> int:
        """Remove entries matching tags.
        
        Args:
            tags (List[str]): Identifiers.
            
        Returns:
            int: Number of items purged.
        """
        return await self._backend.invalidate_tags(tags)


# Global instance
fast_cache = CacheManager()


def cache(
    ttl: Optional[int] = None, 
    tags: Optional[List[str]] = None, 
    key_prefix: str = ""
) -> Callable[[F], F]:
    """Transparently handle data residency for decorated functions.
    
    Args:
        ttl (Optional[int]): Time-to-live for results.
        tags (Optional[List[str]]): Group identifiers for bulk invalidation.
        key_prefix (str): Prefixing for key collision avoidance.
        
    Returns:
        Callable: The wrapped function with cache check logic.
    """
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = f"{key_prefix}{fast_cache.generate_key(func, *args, **kwargs)}"
                
                # Check cache first
                cached_val = await fast_cache.get(key)
                if cached_val is not None:
                    return cached_val
                
                # Execute original function
                result = await func(*args, **kwargs)
                
                # Update cache
                await fast_cache.set(key, result, ttl=ttl, tags=tags)
                return result
            return cast(F, async_wrapper)
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Since all backend calls are async, we use a loop for sync functions
                # Note: In production this may lead to overhead or deadlock if not careful.
                key = f"{key_prefix}{fast_cache.generate_key(func, *args, **kwargs)}"
                
                # Get current event loop or create one
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                cached_val = loop.run_until_complete(fast_cache.get(key))
                if cached_val is not None:
                    return cached_val
                
                result = func(*args, **kwargs)
                loop.run_until_complete(fast_cache.set(key, result, ttl=ttl, tags=tags))
                return result
            return cast(F, sync_wrapper)
            
    return decorator
