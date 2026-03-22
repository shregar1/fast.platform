from __future__ import annotations
"""Tests for :class:`secrets.cache.CachedSecretsBackend`."""
from tests.sec.secrets.abstraction import ISecretsTests



from typing import Any, Optional

from secrets.base import ISecretsBackend
from secrets.cache import CachedSecretsBackend


class TestCache(ISecretsTests):
    class MemoryBackend(ISecretsBackend):
        name = "memory"

        def __init__(self) -> None:
            self.store: dict[str, str] = {}
            self.get_calls = 0

        def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
            self.get_calls += 1
            return self.store.get(key)

        def set_secret(self, key: str, value: str) -> None:
            self.store[key] = value

    def test_ttl_avoids_upstream_until_expiry(self) -> None:
        inner = self.MemoryBackend()
        inner.store["a"] = "1"
        clock = {"t": 0.0}

        def fake_clock() -> float:
            return clock["t"]

        c = CachedSecretsBackend(inner, default_ttl_seconds=10.0, clock=fake_clock)
        assert c.get_secret("a") == "1"
        assert inner.get_calls == 1
        assert c.get_secret("a") == "1"
        assert inner.get_calls == 1
        clock["t"] = 11.0
        assert c.get_secret("a") == "1"
        assert inner.get_calls == 2

    def test_force_refresh_bypasses_ttl(self) -> None:
        inner = self.MemoryBackend()
        inner.store["a"] = "1"
        c = CachedSecretsBackend(inner, default_ttl_seconds=999.0)
        assert c.get_secret("a") == "1"
        assert inner.get_calls == 1
        inner.store["a"] = "2"
        assert c.get_secret("a") == "1"
        assert c.get_secret("a", force_refresh=True) == "2"
        assert inner.get_calls == 2

    def test_rotation_callback_when_value_changes_after_refresh(self) -> None:
        inner = self.MemoryBackend()
        inner.store["k"] = "old"
        events: list[tuple[str, Optional[str], Optional[str]]] = []

        def on_rot(key: str, old: Optional[str], new: Optional[str]) -> None:
            events.append((key, old, new))

        c = CachedSecretsBackend(inner, default_ttl_seconds=300.0, on_rotation=on_rot)
        assert c.get_secret("k") == "old"
        assert events == []
        inner.store["k"] = "new"
        assert c.get_secret("k", force_refresh=True) == "new"
        assert events == [("k", "old", "new")]

    def test_notify_on_first_fetch(self) -> None:
        inner = self.MemoryBackend()
        inner.store["k"] = "v"
        events: list[tuple[str, Optional[str], Optional[str]]] = []

        def on_rot(key: str, old: Optional[str], new: Optional[str]) -> None:
            events.append((key, old, new))

        c = CachedSecretsBackend(inner, on_rotation=on_rot, notify_on_first_fetch=True)
        c.get_secret("k")
        assert events == [("k", None, "v")]

    def test_set_secret_triggers_rotation_when_cached_value_differs(self) -> None:
        inner = self.MemoryBackend()
        events: list[tuple[str, Optional[str], Optional[str]]] = []

        def on_rot(key: str, old: Optional[str], new: Optional[str]) -> None:
            events.append((key, old, new))

        c = CachedSecretsBackend(inner, on_rotation=on_rot)
        c.get_secret("x")
        c.set_secret("x", "a")
        assert events == []
        c.set_secret("x", "b")
        assert events == [("x", "a", "b")]

    def test_invalidate_cache(self) -> None:
        inner = self.MemoryBackend()
        inner.store["a"] = "1"
        c = CachedSecretsBackend(inner, default_ttl_seconds=999.0)
        c.get_secret("a")
        assert inner.get_calls == 1
        c.invalidate_cache("a")
        c.get_secret("a")
        assert inner.get_calls == 2
        c.get_secret("a")
        assert inner.get_calls == 2
        c.invalidate_cache()
        c.get_secret("a")
        assert inner.get_calls == 3
