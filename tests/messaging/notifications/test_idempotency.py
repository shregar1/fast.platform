"""Tests for notification idempotency stores."""

import asyncio

from messaging.notifications.idempotency import (
    InMemoryNotificationIdempotencyStore,
    RedisNotificationIdempotencyStore,
    make_idempotency_key,
)
from tests.messaging.notifications.abstraction import INotificationTests


class TestIdempotency(INotificationTests):
    """Represents the TestIdempotency class."""

    def test_make_idempotency_key_stable(self):
        """Execute test_make_idempotency_key_stable operation.

        Returns:
            The result of the operation.
        """
        k = make_idempotency_key("u", "tpl", "d")
        assert "\x1f" in k
        assert k == make_idempotency_key("u", "tpl", "d")

    def test_in_memory_try_acquire(self):
        """Execute test_in_memory_try_acquire operation.

        Returns:
            The result of the operation.
        """
        store = InMemoryNotificationIdempotencyStore()
        key = make_idempotency_key("a", "b", "c")

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            assert await store.try_acquire(key, ttl_seconds=3600) is True
            assert await store.try_acquire(key, ttl_seconds=3600) is False

        asyncio.run(run())

    def test_redis_try_acquire_with_fake_client(self):
        """Execute test_redis_try_acquire_with_fake_client operation.

        Returns:
            The result of the operation.
        """

        class FakeRedis:
            """Represents the FakeRedis class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self._kv: dict[str, bytes] = {}

            async def set(self, name, value, nx=False, ex=None):
                """Execute set operation.

                Args:
                    name: The name parameter.
                    value: The value parameter.
                    nx: The nx parameter.
                    ex: The ex parameter.

                Returns:
                    The result of the operation.
                """
                if nx and name in self._kv:
                    return False
                self._kv[name] = value
                return True

        store = RedisNotificationIdempotencyStore(FakeRedis())
        key = make_idempotency_key("x", "y", "z")

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            assert await store.try_acquire(key, ttl_seconds=60) is True
            assert await store.try_acquire(key, ttl_seconds=60) is False

        asyncio.run(run())
