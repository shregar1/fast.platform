import asyncio
from typing import Any, Dict, Optional


class FakeRedisForCounters:
    def __init__(self) -> None:
        self._kv: Dict[str, str] = {}

    async def incr(self, key: str) -> int:
        n = int(self._kv.get(key, "0")) + 1
        self._kv[key] = str(n)
        return n

    async def decr(self, key: str) -> int:
        n = int(self._kv.get(key, "0")) - 1
        self._kv[key] = str(n)
        return n

    async def get(self, key: str) -> Optional[str]:
        return self._kv.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._kv[key] = str(value)

    async def delete(self, key: str) -> None:
        self._kv.pop(key, None)


def test_inmemory_subscriber_counters():
    from fast_channels.subscriber_counters import InMemorySubscriberCounters

    c = InMemorySubscriberCounters()
    assert asyncio.run(c.count("x")) == 0
    assert asyncio.run(c.increment("x")) == 1
    assert asyncio.run(c.increment("x")) == 2
    assert asyncio.run(c.decrement("x")) == 1
    assert asyncio.run(c.decrement("x")) == 0
    assert asyncio.run(c.all_counts()) == {}


def test_redis_subscriber_counters():
    from fast_channels.subscriber_counters import RedisSubscriberCounters

    client = FakeRedisForCounters()
    c = RedisSubscriberCounters(client, key_prefix="t:")
    assert asyncio.run(c.increment("a")) == 1
    assert asyncio.run(c.count("a")) == 1
    assert asyncio.run(c.decrement("a")) == 0
    assert asyncio.run(c.count("a")) == 0
    assert asyncio.run(c.all_counts()) == {}
