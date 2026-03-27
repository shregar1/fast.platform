"""Base interface for channels (pub-sub) backends."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from .abstraction import IChannel

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class IChannelBackend(IChannel, abc.ABC):
    """Abstract base class for pub-sub channels."""

    @abc.abstractmethod
    async def publish(self, topic: str, message: Any) -> None:
        """Publish a message to a topic."""

    @abc.abstractmethod
    async def subscribe(self, topic: str) -> AsyncIterator[Any]:
        """Subscribe to a topic and yield messages (async generator)."""
