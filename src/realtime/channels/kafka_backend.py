"""Kafka-based channels backend (stub)."""

from typing import Any, AsyncGenerator

from .base import IChannelBackend


class KafkaChannelBackend(IChannelBackend):
    """Represents the KafkaChannelBackend class."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        pass

    async def publish(self, topic: str, message: Any) -> None:
        """Execute publish operation.

        Args:
            topic: The topic parameter.
            message: The message parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError("Kafka backend is not yet implemented.")

    async def subscribe(self, topic: str) -> AsyncGenerator[str, None]:
        """Execute subscribe operation.

        Args:
            topic: The topic parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError("Kafka backend is not yet implemented.")
