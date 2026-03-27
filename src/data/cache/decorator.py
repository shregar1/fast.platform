"""
Cache Decorator for Fast Platform

Lightweight caching with Redis support.

Usage:
    from core.cache_decorator import cached
    
    @cached(ttl=300)
    async def get_user(user_id: str) -> User:
        return await db.get(User, user_id)
    
    @cached(ttl=600, key="posts:{category}:{page}")
    async def list_posts(category: str, page: int = 1):
        return await db.query(Post).filter_by(category=category).offset((page-1)*10).limit(10).all()
    
    # Invalidate cache
    from core.cache_decorator import invalidate
    invalidate("posts:{category}:*", category="tech")
    
    # Or use the decorator's invalidate method
    list_posts.invalidate(category="tech", page=1)

Configuration:
    REDIS_URL=redis://localhost:6379/0
    CACHE_PREFIX=fastmvc
    CACHE_DEFAULT_TTL=300
"""

import functools
import hashlib
import json
import pickle
from typing import Any, Callable, Optional
from datetime import timedelta

try:
    from redis import Redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

# In-memory fallback when Redis is not available
_memory_cache: dict[str, tuple[Any, float]] = {}


def _get_redis() -> Optional[Any]:
    """Get Redis connection or None."""
    if not HAS_REDIS:
        return None
    
    try:
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        return Redis.from_url(redis_url, decode_responses=False)
    except Exception:
        return None


def _build_key(func: Callable, key_template: Optional[str], args, kwargs) -> str:
    """Build cache key from template or function signature."""
    if key_template:
        # Build from template
        try:
            # Get function argument names
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            cache_key = key_template.format(**bound.arguments)
        except Exception:
            # Fall back to hash if template fails
            cache_key = _hash_args(args, kwargs)
    else:
        # Use function name + arguments hash
        cache_key = f"{func.__module__}.{func.__name__}:{_hash_args(args, kwargs)}"
    
    # Add prefix
    import os
    prefix = os.getenv("CACHE_PREFIX", "fastmvc")
    return f"{prefix}:{cache_key}"


def _hash_args(args, kwargs) -> str:
    """Create hash of arguments."""
    try:
        data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(data.encode()).hexdigest()
    except Exception:
        return hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()


def cached(
    ttl: int = 300,
    key: Optional[str] = None,
    unless: Optional[Callable] = None
):
    """
    Cache decorator for functions.
    
    Args:
        ttl: Time to live in seconds (default: 300)
        key: Cache key template, e.g., "user:{user_id}"
        unless: Function that returns True if result should not be cached
    
    Usage:
        @cached(ttl=300)
        async def get_user(user_id: str):
            return await db.get(User, user_id)
        
        @cached(ttl=600, key="posts:{category}")
        async def get_posts(category: str):
            return await db.query(Post).filter_by(category=category).all()
    """
    def decorator(func: Callable) -> Callable:
        is_async = callable(func) and func.__code__.co_flags & 0x80
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check unless condition
            if unless and unless(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Build cache key
            cache_key = _build_key(func, key, args, kwargs)
            
            # Try to get from cache
            redis = _get_redis()
            try:
                if redis:
                    cached_value = redis.get(cache_key)
                    if cached_value:
                        return pickle.loads(cached_value)
                else:
                    # Use memory cache
                    import time
                    if cache_key in _memory_cache:
                        value, expiry = _memory_cache[cache_key]
                        if expiry > time.time():
                            return value
                        else:
                            del _memory_cache[cache_key]
            except Exception:
                # Cache failure - continue to function
                pass
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                if redis:
                    redis.setex(cache_key, ttl, pickle.dumps(result))
                else:
                    import time
                    _memory_cache[cache_key] = (result, time.time() + ttl)
            except Exception:
                # Cache failure - ignore
                pass
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check unless condition
            if unless and unless(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Build cache key
            cache_key = _build_key(func, key, args, kwargs)
            
            # Try to get from cache
            redis = _get_redis()
            try:
                if redis:
                    cached_value = redis.get(cache_key)
                    if cached_value:
                        return pickle.loads(cached_value)
                else:
                    import time
                    if cache_key in _memory_cache:
                        value, expiry = _memory_cache[cache_key]
                        if expiry > time.time():
                            return value
                        else:
                            del _memory_cache[cache_key]
            except Exception:
                pass
            
            # Call function
            result = func(*args, **kwargs)
            
            # Store in cache
            try:
                if redis:
                    redis.setex(cache_key, ttl, pickle.dumps(result))
                else:
                    import time
                    _memory_cache[cache_key] = (result, time.time() + ttl)
            except Exception:
                pass
            
            return result
        
        wrapper = async_wrapper if is_async else sync_wrapper
        
        # Add invalidate method
        def invalidate(*args, **kwargs):
            """Invalidate cache for this function with given args."""
            cache_key = _build_key(func, key, args, kwargs)
            redis = _get_redis()
            try:
                if redis:
                    redis.delete(cache_key)
                elif cache_key in _memory_cache:
                    del _memory_cache[cache_key]
            except Exception:
                pass
        
        wrapper.invalidate = invalidate
        
        return wrapper
    return decorator


def invalidate_pattern(pattern: str) -> int:
    """
    Invalidate cache keys matching pattern.
    
    Args:
        pattern: Glob pattern, e.g., "user:*" or "posts:{category}:*"
    
    Returns:
        Number of keys deleted
    """
    redis = _get_redis()
    if not redis:
        # Memory cache - simple matching
        keys_to_delete = [
            k for k in _memory_cache.keys()
            if _match_glob(k, pattern)
        ]
        for k in keys_to_delete:
            del _memory_cache[k]
        return len(keys_to_delete)
    
    # Redis - use SCAN and DELETE
    import os
    prefix = os.getenv("CACHE_PREFIX", "fastmvc")
    full_pattern = f"{prefix}:{pattern}"
    
    deleted = 0
    for key in redis.scan_iter(match=full_pattern):
        redis.delete(key)
        deleted += 1
    return deleted


def _match_glob(key: str, pattern: str) -> bool:
    """Simple glob matching for memory cache."""
    import fnmatch
    return fnmatch.fnmatch(key, pattern)


def clear_cache() -> None:
    """Clear all cache entries."""
    redis = _get_redis()
    if redis:
        import os
        prefix = os.getenv("CACHE_PREFIX", "fastmvc")
        for key in redis.scan_iter(match=f"{prefix}:*"):
            redis.delete(key)
    else:
        _memory_cache.clear()


# Decorator for cache eviction
def cache_evict(key: str):
    """
    Decorator to evict cache entries after function execution.
    
    Usage:
        @cache_evict("user:{user_id}")
        async def update_user(user_id: str, data: dict):
            # After this runs, "user:{user_id}" cache is cleared
            return await db.update(User, user_id, data)
    """
    def decorator(func: Callable) -> Callable:
        is_async = callable(func) and func.__code__.co_flags & 0x80
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Build key and evict
            cache_key = _build_key(func, key, args, kwargs)
            redis = _get_redis()
            try:
                if redis:
                    redis.delete(cache_key)
                elif cache_key in _memory_cache:
                    del _memory_cache[cache_key]
            except Exception:
                pass
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            cache_key = _build_key(func, key, args, kwargs)
            redis = _get_redis()
            try:
                if redis:
                    redis.delete(cache_key)
                elif cache_key in _memory_cache:
                    del _memory_cache[cache_key]
            except Exception:
                pass
            
            return result
        
        return async_wrapper if is_async else sync_wrapper
    return decorator
