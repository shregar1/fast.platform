from __future__ import annotations

"""Redis subscriber counters and import guard."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.realtime.channels.abstraction import IChannelTests


class TestSubscriberCountersRedis(IChannelTests):
    @pytest.mark.asyncio
    async def test_redis_counters_increment_decrement_negative_fix(self) -> None:
        from channels.subscriber_counters import RedisSubscriberCounters

        client = MagicMock()
        client.incr = AsyncMock(return_value=1)
        client.decr = AsyncMock(return_value=-1)
        client.set = AsyncMock()
        client.delete = AsyncMock()
        c = RedisSubscriberCounters(client)
        assert await c.increment("ch") == 1
        client.decr.return_value = -1
        assert await c.decrement("ch") == 0
        client.set.assert_called()
        client.delete.assert_called()

    @pytest.mark.asyncio
    async def test_redis_counters_count_and_all_counts(self) -> None:
        from channels.subscriber_counters import RedisSubscriberCounters

        client = MagicMock()
        client.incr = AsyncMock(return_value=1)
        client.decr = AsyncMock(return_value=0)
        client.delete = AsyncMock()
        client.get = AsyncMock(return_value=None)
        c = RedisSubscriberCounters(client)
        assert await c.count("x") == 0
        client.get = AsyncMock(return_value=b"3")
        assert await c.count("x") == 3
        assert await c.all_counts() == {}

    def test_redis_unavailable_raises(self) -> None:
        import channels.subscriber_counters as sc

        with patch.object(sc, "aioredis", None):
            from channels.subscriber_counters import RedisSubscriberCounters

            with pytest.raises(RuntimeError, match="redis"):
                RedisSubscriberCounters(MagicMock())
