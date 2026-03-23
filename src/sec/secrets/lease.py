"""
Secret lease with background refresh before TTL expiry (long-lived workers).
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from .base import ISecretsBackend
from .cache import CachedSecretsBackend


class LeasedSecretsBackend(ISecretsBackend):
    """
    Wraps a backend with a :class:`CachedSecretsBackend` and schedules **proactive**
    refreshes on a daemon timer so values stay warm before the TTL expires.

    After each successful ``get_secret``, a timer fires at ``ttl_seconds * refresh_at_ratio``
    to call ``get_secret(..., force_refresh=True)`` on the inner cache (which refetches
    from the real backend). Call :meth:`stop` on shutdown to cancel pending timers.

    ``refresh_at_ratio`` is in ``(0, 1)``: e.g. ``0.85`` refreshes 85% of the way through
    the TTL window (15% of TTL remaining before hard expiry).
    """

    def __init__(
        self,
        inner: ISecretsBackend,
        ttl_seconds: int = 300,
        *,
        refresh_at_ratio: float = 0.85,
        name: str = "leased",
        on_rotation: Any = None,
        notify_on_first_fetch: bool = False,
    ) -> None:
        if not 0 < refresh_at_ratio < 1:
            raise ValueError("refresh_at_ratio must be between 0 and 1 (exclusive)")
        self._cached = CachedSecretsBackend(
            inner,
            default_ttl_seconds=float(ttl_seconds),
            name=f"{name}-cache",
            on_rotation=on_rotation,
            notify_on_first_fetch=notify_on_first_fetch,
        )
        self._ttl = max(1, int(ttl_seconds))
        self._ratio = float(refresh_at_ratio)
        self.name = name
        self._timers: Dict[str, threading.Timer] = {}
        self._lock = threading.Lock()
        self._stopped = False

    def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
        force_refresh = bool(kwargs.get("force_refresh", False))
        val = self._cached.get_secret(key, **kwargs)
        if val is not None and not force_refresh and not self._stopped:
            self._schedule_refresh(key)
        return val

    def set_secret(self, key: str, value: str) -> None:
        self._cancel_timer(key)
        self._cached.set_secret(key, value)

    def _cancel_timer(self, key: str) -> None:
        with self._lock:
            t = self._timers.pop(key, None)
        if t is not None:
            t.cancel()

    def _schedule_refresh(self, key: str) -> None:
        with self._lock:
            if self._stopped:
                return
            old = self._timers.pop(key, None)
            if old is not None:
                old.cancel()
            delay = max(0.05, self._ttl * self._ratio)
            timer = threading.Timer(delay, self._on_timer, args=(key,))
            timer.daemon = True
            timer.start()
            self._timers[key] = timer

    def _on_timer(self, key: str) -> None:
        with self._lock:
            self._timers.pop(key, None)
        if self._stopped:
            return
        try:
            val = self._cached.get_secret(key, force_refresh=True)
        except Exception:
            return
        if val is not None and not self._stopped:
            self._schedule_refresh(key)

    def stop(self) -> None:
        """Cancel all pending refresh timers (call from worker shutdown)."""
        with self._lock:
            self._stopped = True
            timers = list(self._timers.values())
            self._timers.clear()
        for t in timers:
            t.cancel()

    def invalidate_cache(self, key: Optional[str] = None) -> None:
        """Forward to the inner cache (same semantics as :class:`CachedSecretsBackend`)."""
        self._cached.invalidate_cache(key)
