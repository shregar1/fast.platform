"""
Kafka-based channels backend (stub).
"""

from typing import Any, AsyncGenerator

from .base import ChannelBackend


class KafkaChannelBackend(ChannelBackend):
    def __init__(self) -> None:
        pass

    async def publish(self, topic: str, message: Any) -> None:
        raise NotImplementedError("Kafka backend is not yet implemented.")

    async def subscribe(self, topic: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError("Kafka backend is not yet implemented.")
