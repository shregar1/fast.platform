"""Module test_subscriber_counters.py."""

import asyncio
from typing import Any, Dict, Optional

from tests.realtime.channels.abstraction import IChannelTests


class FakeRedisForCounters:
    """Represents the FakeRedisForCounters class."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self._kv: Dict[str, str] = {}

    async def incr(self, key: str) -> int:
        """Execute incr operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        n = int(self._kv.get(key, "0")) + 1
        self._kv[key] = str(n)
        return n

    async def decr(self, key: str) -> int:
        """Execute decr operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        n = int(self._kv.get(key, "0")) - 1
        self._kv[key] = str(n)
        return n

    async def get(self, key: str) -> Optional[str]:
        """Execute get operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        return self._kv.get(key)

    async def set(self, key: str, value: Any) -> None:
        """Execute set operation.

        Args:
            key: The key parameter.
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._kv[key] = str(value)

    async def delete(self, key: str) -> None:
        """Execute delete operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        self._kv.pop(key, None)


class TestSubscriberCounters(IChannelTests):
    """Represents the TestSubscriberCounters class."""

    def test_inmemory_subscriber_counters(self):
        """Execute test_inmemory_subscriber_counters operation.

        Returns:
            The result of the operation.
        """
        from realtime.channels.subscriber_counters import InMemorySubscriberCounters

        c = InMemorySubscriberCounters()
        assert asyncio.run(c.count("x")) == 0
        assert asyncio.run(c.increment("x")) == 1
        assert asyncio.run(c.increment("x")) == 2
        assert asyncio.run(c.decrement("x")) == 1
        assert asyncio.run(c.decrement("x")) == 0
        assert asyncio.run(c.all_counts()) == {}

    def test_redis_subscriber_counters(self):
        """Execute test_redis_subscriber_counters operation.

        Returns:
            The result of the operation.
        """
        from realtime.channels.subscriber_counters import RedisSubscriberCounters

        client = FakeRedisForCounters()
        c = RedisSubscriberCounters(client, key_prefix="t:")
        assert asyncio.run(c.increment("a")) == 1
        assert asyncio.run(c.count("a")) == 1
        assert asyncio.run(c.decrement("a")) == 0
        assert asyncio.run(c.count("a")) == 0
        assert asyncio.run(c.all_counts()) == {}
