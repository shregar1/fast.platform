"""Redis-based implementation of the channels backend."""

from typing import Any, AsyncGenerator

import redis.asyncio as aioredis

from .base import IChannelBackend


class RedisChannelBackend(IChannelBackend):
    """Represents the RedisChannelBackend class."""

    def __init__(self, client: aioredis.Redis) -> None:
        """Execute __init__ operation.

        Args:
            client: The client parameter.
        """
        self._client = client

    async def publish(self, topic: str, message: Any) -> None:
        """Execute publish operation.

        Args:
            topic: The topic parameter.
            message: The message parameter.

        Returns:
            The result of the operation.
        """
        await self._client.publish(topic, str(message))

    async def subscribe(self, topic: str) -> AsyncGenerator[str, None]:
        """Execute subscribe operation.

        Args:
            topic: The topic parameter.

        Returns:
            The result of the operation.
        """
        pubsub = self._client.pubsub()
        await pubsub.subscribe(topic)
        try:
            async for msg in pubsub.listen():
                if msg["type"] != "message":
                    continue
                data = msg["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                yield data
        finally:
            await pubsub.unsubscribe(topic)
            await pubsub.close()
