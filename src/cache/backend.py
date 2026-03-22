from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Hashable, Optional, Tuple, TypeVar, Union, cast

from from fast_platform import CacheConfiguration
from from fast_platform.utils import optional_import

try:
    from loguru import logger
except Exception:  # pragma: no cover - optional
    logger = None  # type: ignore[assignment]

_redis_mod, _redis_cls = optional_import("redis.asyncio", "Redis")


class ICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any:  # pragma: no cover - interface
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class InMemoryCache(ICache):
    def __init__(self, default_ttl_seconds: int) -> None:
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._default_ttl = default_ttl_seconds
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if expires_at and expires_at < time.time():
                self._store.pop(key, None)
                return None
            return value

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds or self._default_ttl
        expires_at = time.time() + ttl if ttl > 0 else 0
        async with self._lock:
            self._store[key] = (expires_at, value)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()


class RedisCache(ICache):
    def __init__(self, url: str, namespace: str, default_ttl_seconds: int) -> None:
        if _redis_cls is None:  # pragma: no cover - optional
            raise RuntimeError("redis.asyncio is not installed")
        self._redis = _redis_cls.from_url(url)  # type: ignore[operator]
        self._ns = namespace.rstrip(":") + ":"
        self._default_ttl = default_ttl_seconds

    def _k(self, key: str) -> str:
        return f"{self._ns}{key}"

    async def get(self, key: str) -> Any:
        raw = await self._redis.get(self._k(key))
        if raw is None:
            return None
        try:
            import json

            return json.loads(raw)
        except Exception:
            return raw

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds or self._default_ttl
        payload: Union[str, bytes]
        if isinstance(value, (str, bytes)):
            payload = value
        else:
            import json

            payload = json.dumps(value)
        await self._redis.set(self._k(key), payload, ex=ttl if ttl > 0 else None)

    async def delete(self, key: str) -> None:
        await self._redis.delete(self._k(key))

    async def clear(self) -> None:
        # Best-effort: delete keys with namespace prefix
        pattern = self._k("*")
        async for key in self._redis.scan_iter(match=pattern):  # type: ignore[attr-defined]
            await self._redis.delete(key)


_CACHE_SINGLETON: Optional[ICache] = None


def get_cache() -> Optional[ICache]:
    global _CACHE_SINGLETON
    if _CACHE_SINGLETON is not None:
        return _CACHE_SINGLETON

    cfg = CacheConfiguration().get_config()
    if not cfg.enabled:
        if logger:
            logger.info("Application cache is disabled via configuration.")
        _CACHE_SINGLETON = None
        return None

    if cfg.backend == "redis":
        try:
            _CACHE_SINGLETON = RedisCache(
                url=cfg.redis_url or "redis://localhost:6379/2",
                namespace=cfg.namespace,
                default_ttl_seconds=cfg.default_ttl_seconds,
            )
            if logger:
                logger.info("Using Redis cache backend.")
            return _CACHE_SINGLETON
        except Exception as exc:  # pragma: no cover - defensive
            if logger:
                logger.warning("Failed to initialize Redis cache; falling back to in-memory: %s", exc)

    _CACHE_SINGLETON = InMemoryCache(default_ttl_seconds=cfg.default_ttl_seconds)
    if logger:
        logger.info("Using in-memory cache backend.")
    return _CACHE_SINGLETON


F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def _default_cache_key(func: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
    parts: list[Hashable] = [func.__module__, func.__qualname__]
    parts.extend(args)
    for k in sorted(kwargs.keys()):
        parts.append((k, kwargs[k]))
    return "|".join(map(str, parts))


def cache_result(
    *,
    key_builder: Optional[Callable[[Callable[..., Any], Tuple[Any, ...], Dict[str, Any]], str]] = None,
    ttl_seconds: Optional[int] = None,
) -> Callable[[F], F]:
    """
    Decorator to cache async service calls using the configured cache backend.

    If caching is disabled or the backend cannot be initialized, the decorator
    becomes a no-op and always calls through.
    """
    _log = logger

    def decorator(func: F) -> F:
        kb = key_builder or _default_cache_key

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()
            if cache is None:
                return await func(*args, **kwargs)

            key = kb(func, args, kwargs)
            try:
                cached = await cache.get(key)
            except Exception as exc:  # pragma: no cover - defensive
                if _log:
                    _log.warning("Cache get failed for %s: %s", key, exc)
                return await func(*args, **kwargs)

            if cached is not None:
                return cached

            result = await func(*args, **kwargs)

            try:
                await cache.set(key, result, ttl_seconds)
            except Exception as exc:  # pragma: no cover - defensive
                if _log:
                    _log.warning("Cache set failed for %s: %s", key, exc)
            return result

        return cast(F, wrapper)

    return decorator


__all__ = [
    "ICache",
    "InMemoryCache",
    "RedisCache",
    "get_cache",
    "cache_result",
]
