"""Tests for notification idempotency stores."""

import asyncio

from messaging.notifications.idempotency import (
    InMemoryNotificationIdempotencyStore,
    RedisNotificationIdempotencyStore,
    make_idempotency_key,
)
from tests.messaging.notifications.abstraction import INotificationTests


class TestIdempotency(INotificationTests):
    def test_make_idempotency_key_stable(self):
        k = make_idempotency_key("u", "tpl", "d")
        assert "\x1f" in k
        assert k == make_idempotency_key("u", "tpl", "d")

    def test_in_memory_try_acquire(self):
        store = InMemoryNotificationIdempotencyStore()
        key = make_idempotency_key("a", "b", "c")

        async def run():
            assert await store.try_acquire(key, ttl_seconds=3600) is True
            assert await store.try_acquire(key, ttl_seconds=3600) is False

        asyncio.run(run())

    def test_redis_try_acquire_with_fake_client(self):
        class FakeRedis:
            def __init__(self) -> None:
                self._kv: dict[str, bytes] = {}

            async def set(self, name, value, nx=False, ex=None):
                if nx and name in self._kv:
                    return False
                self._kv[name] = value
                return True

        store = RedisNotificationIdempotencyStore(FakeRedis())
        key = make_idempotency_key("x", "y", "z")

        async def run():
            assert await store.try_acquire(key, ttl_seconds=60) is True
            assert await store.try_acquire(key, ttl_seconds=60) is False

        asyncio.run(run())
