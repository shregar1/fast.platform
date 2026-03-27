"""Module test_backends.py."""

import asyncio
from typing import Any, AsyncGenerator, List

import pytest

from tests.realtime.channels.abstraction import IChannelTests


class FakePubSub:
    """Represents the FakePubSub class."""

    def __init__(self, messages: List[dict[str, Any]]):
        """Execute __init__ operation.

        Args:
            messages: The messages parameter.
        """
        self._messages = messages
        self.subscribed_topics: list[str] = []
        self.unsubscribed_topics: list[str] = []
        self.closed = False

    async def subscribe(self, topic: str):
        """Execute subscribe operation.

        Args:
            topic: The topic parameter.

        Returns:
            The result of the operation.
        """
        self.subscribed_topics.append(topic)

    async def listen(self) -> AsyncGenerator[dict[str, Any], None]:
        """Execute listen operation.

        Returns:
            The result of the operation.
        """
        for msg in self._messages:
            yield msg

    async def unsubscribe(self, topic: str):
        """Execute unsubscribe operation.

        Args:
            topic: The topic parameter.

        Returns:
            The result of the operation.
        """
        self.unsubscribed_topics.append(topic)

    async def close(self):
        """Execute close operation.

        Returns:
            The result of the operation.
        """
        self.closed = True


class FakeRedisChannelClient:
    """Represents the FakeRedisChannelClient class."""

    def __init__(self, pubsub: FakePubSub):
        """Execute __init__ operation.

        Args:
            pubsub: The pubsub parameter.
        """
        self._pubsub = pubsub
        self.published: list[tuple[str, str]] = []

    def pubsub(self) -> FakePubSub:
        """Execute pubsub operation.

        Returns:
            The result of the operation.
        """
        return self._pubsub

    async def publish(self, topic: str, message: str):
        """Execute publish operation.

        Args:
            topic: The topic parameter.
            message: The message parameter.

        Returns:
            The result of the operation.
        """
        self.published.append((topic, message))


class TestBackends(IChannelTests):
    """Represents the TestBackends class."""

    def test_redis_channel_backend_publish_calls_client_publish(self):
        """Execute test_redis_channel_backend_publish_calls_client_publish operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.channels.redis_backend import RedisChannelBackend

        pubsub = FakePubSub([])
        client = FakeRedisChannelClient(pubsub)
        backend = RedisChannelBackend(client=client)
        asyncio.run(backend.publish("alerts", {"a": 1}))
        assert client.published == [("alerts", "{'a': 1}")]

    def test_redis_channel_backend_subscribe_filters_and_decodes_messages(self):
        """Execute test_redis_channel_backend_subscribe_filters_and_decodes_messages operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.channels.redis_backend import RedisChannelBackend

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
            """Execute run operation.

            Returns:
                The result of the operation.
            """
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
        """Execute test_kafka_channel_backend_is_not_implemented operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.channels.kafka_backend import KafkaChannelBackend

        backend = KafkaChannelBackend()
        with pytest.raises(NotImplementedError):
            asyncio.run(backend.publish("t", "m"))
        with pytest.raises(NotImplementedError):
            asyncio.run(backend.subscribe("t"))
