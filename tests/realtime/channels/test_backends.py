import asyncio
from typing import Any, AsyncGenerator, List

import pytest

from tests.realtime.channels.abstraction import IChannelTests


class FakePubSub:
    def __init__(self, messages: List[dict[str, Any]]):
        self._messages = messages
        self.subscribed_topics: list[str] = []
        self.unsubscribed_topics: list[str] = []
        self.closed = False

    async def subscribe(self, topic: str):
        self.subscribed_topics.append(topic)

    async def listen(self) -> AsyncGenerator[dict[str, Any], None]:
        for msg in self._messages:
            yield msg

    async def unsubscribe(self, topic: str):
        self.unsubscribed_topics.append(topic)

    async def close(self):
        self.closed = True


class FakeRedisChannelClient:
    def __init__(self, pubsub: FakePubSub):
        self._pubsub = pubsub
        self.published: list[tuple[str, str]] = []

    def pubsub(self) -> FakePubSub:
        return self._pubsub

    async def publish(self, topic: str, message: str):
        self.published.append((topic, message))


class TestBackends(IChannelTests):
    def test_redis_channel_backend_publish_calls_client_publish(self):
        from realtime.channels.redis_backend import RedisChannelBackend

        pubsub = FakePubSub([])
        client = FakeRedisChannelClient(pubsub)
        backend = RedisChannelBackend(client=client)
        asyncio.run(backend.publish("alerts", {"a": 1}))
        assert client.published == [("alerts", "{'a': 1}")]

    def test_redis_channel_backend_subscribe_filters_and_decodes_messages(self):
        from realtime.channels.redis_backend import RedisChannelBackend

        pubsub = FakePubSub(
            [
                {"type": "other", "data": b"ignore"},
                {"type": "message", "data": b"hello"},
                {"type": "message", "data": "world"},
            ]
        )
        client = FakeRedisChannelClient(pubsub)
        backend = RedisChannelBackend(client=client)

        async def run():
            out = []
            async for msg in backend.subscribe("alerts"):
                out.append(msg)
            return out

        msgs = asyncio.run(run())
        assert msgs == ["hello", "world"]
        assert pubsub.subscribed_topics == ["alerts"]
        assert pubsub.unsubscribed_topics == ["alerts"]
        assert pubsub.closed is True

    def test_kafka_channel_backend_is_not_implemented(self):
        from realtime.channels.kafka_backend import KafkaChannelBackend

        backend = KafkaChannelBackend()
        with pytest.raises(NotImplementedError):
            asyncio.run(backend.publish("t", "m"))
        with pytest.raises(NotImplementedError):
            asyncio.run(backend.subscribe("t"))
