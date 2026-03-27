"""TTL cache and optional rotation callbacks around any :class:`ISecretsBackend`."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Protocol, Tuple

from .base import ISecretsBackend


class RotationCallback(Protocol):
    def __call__(self, key: str, old_value: Optional[str], new_value: str) -> None: ...


class CachedSecretsBackend(ISecretsBackend):
    """Wraps a backend with a per-key TTL cache.

    Pass ``force_refresh=True`` to bypass the cache. Optional ``on_rotation`` is invoked
    when a newly fetched value differs from the previously cached one (or on first fetch
    if ``notify_on_first_fetch`` is True). :meth:`set_secret` may invoke ``on_rotation``
    when the value written differs from what was previously stored upstream.
    """

    def __init__(
        self,
        inner: ISecretsBackend,
        *,
        default_ttl_seconds: Optional[float] = None,
        ttl_seconds: Optional[int] = None,
        clock: Optional[Callable[[], float]] = None,
        name: str = "cached",
        on_rotation: Optional[Callable[[str, Optional[str], str], None]] = None,
        notify_on_first_fetch: bool = False,
    ) -> None:
        ttl = default_ttl_seconds if default_ttl_seconds is not None else ttl_seconds
        if ttl is None:
            ttl = 300.0
        self._ttl = max(0.001, float(ttl))
        self._inner = inner
        self._clock = clock or time.monotonic
        self.name = name
        self._on_rotation = on_rotation
        self._notify_first = notify_on_first_fetch
        self._cache: Dict[str, Tuple[Optional[str], float]] = {}

    def _now(self) -> float:
        return float(self._clock())

    def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
        force_refresh = bool(kwargs.pop("force_refresh", False))
        if not force_refresh and key in self._cache:
            val, expires_at = self._cache[key]
            if self._now() < expires_at:
                return val

        new_val = self._inner.get_secret(key, **kwargs)
        old_val: Optional[str] = None
        if key in self._cache:
            old_val = self._cache[key][0]

        self._cache[key] = (new_val, self._now() + self._ttl)

        if self._on_rotation:
            if old_val is None and self._notify_first and new_val is not None:
                self._on_rotation(key, None, new_val)
            elif old_val is not None and new_val is not None and old_val != new_val:
                self._on_rotation(key, old_val, new_val)
            elif old_val is not None and new_val is None:
                self._on_rotation(key, old_val, "")

        return new_val

    def set_secret(self, key: str, value: str) -> None:
        prev_inner = self._inner.get_secret(key)
        self._cache.pop(key, None)
        self._inner.set_secret(key, value)
        if self._on_rotation and prev_inner is not None and prev_inner != value:
            self._on_rotation(key, prev_inner, value)

    def invalidate_cache(self, key: Optional[str] = None) -> None:
        """Drop one key or the entire cache."""
        if key is None:
            self._cache.clear()
        else:
            self._cache.pop(key, None)
