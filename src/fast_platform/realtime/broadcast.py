"""
Broadcast system for real-time messaging
"""

from typing import AsyncIterator, Optional, Dict, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
import json


@dataclass
class BroadcastMessage:
    """A broadcast message"""
    channel: str
    data: Any
    sender: Optional[str] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        return json.dumps({
            "channel": self.channel,
            "data": self.data,
            "sender": self.sender,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "BroadcastMessage":
        data = json.loads(json_str)
        return cls(**data)


class BroadcastBackend(ABC):
    """Abstract base class for broadcast backends"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the backend"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the backend"""
        pass
    
    @abstractmethod
    async def publish(self, channel: str, message: BroadcastMessage) -> None:
        """Publish a message to a channel"""
        pass
    
    @abstractmethod
    async def subscribe(self, channel: str) -> AsyncIterator[BroadcastMessage]:
        """Subscribe to a channel"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel"""
        pass


class InMemoryBroadcastBackend(BroadcastBackend):
    """In-memory broadcast backend for development/testing"""
    
    def __init__(self):
        self._connected = False
        self._channels: Dict[str, asyncio.Queue] = {}
        self._subscribers: Dict[str, set] = {}
    
    async def connect(self) -> None:
        self._connected = True
    
    async def disconnect(self) -> None:
        self._connected = False
    
    async def publish(self, channel: str, message: BroadcastMessage) -> None:
        if not self._connected:
            raise ConnectionError("Backend not connected")
        
        if channel not in self._channels:
            self._channels[channel] = asyncio.Queue()
        
        await self._channels[channel].put(message)
    
    async def subscribe(self, channel: str) -> AsyncIterator[BroadcastMessage]:
        if not self._connected:
            raise ConnectionError("Backend not connected")
        
        if channel not in self._channels:
            self._channels[channel] = asyncio.Queue()
        
        queue = self._channels[channel]
        
        while self._connected:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield message
            except asyncio.TimeoutError:
                continue
    
    async def unsubscribe(self, channel: str) -> None:
        pass  # In-memory cleanup happens automatically


class RedisBroadcastBackend(BroadcastBackend):
    """Redis-based broadcast backend for production"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis = None
        self._pubsub = None
        self._connected = False
    
    async def connect(self) -> None:
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(self.redis_url)
            self._pubsub = self._redis.pubsub()
            self._connected = True
        except ImportError:
            raise ImportError("redis package required for RedisBroadcastBackend")
    
    async def disconnect(self) -> None:
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
        self._connected = False
    
    async def publish(self, channel: str, message: BroadcastMessage) -> None:
        if not self._connected:
            raise ConnectionError("Backend not connected")
        
        await self._redis.publish(channel, message.to_json())
    
    async def subscribe(self, channel: str) -> AsyncIterator[BroadcastMessage]:
        if not self._connected:
            raise ConnectionError("Backend not connected")
        
        await self._pubsub.subscribe(channel)
        
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                yield BroadcastMessage.from_json(message["data"])
    
    async def unsubscribe(self, channel: str) -> None:
        if self._pubsub:
            await self._pubsub.unsubscribe(channel)


# Global backend instance
_default_backend: Optional[BroadcastBackend] = None


def setup_broadcast(backend: BroadcastBackend) -> None:
    """Setup the global broadcast backend"""
    global _default_backend
    _default_backend = backend


async def broadcast(
    channel: str,
    data: Any,
    sender: Optional[str] = None,
    backend: Optional[BroadcastBackend] = None
) -> None:
    """
    Broadcast a message to a channel
    
    Args:
        channel: Channel name
        data: Message data
        sender: Sender identifier
        backend: Optional backend to use (uses default if not specified)
    """
    backend = backend or _default_backend
    if backend is None:
        raise RuntimeError("No broadcast backend configured. Call setup_broadcast() first.")
    
    message = BroadcastMessage(
        channel=channel,
        data=data,
        sender=sender
    )
    
    await backend.publish(channel, message)


async def subscribe(
    channel: str,
    backend: Optional[BroadcastBackend] = None
) -> AsyncIterator[BroadcastMessage]:
    """
    Subscribe to a channel
    
    Args:
        channel: Channel name
        backend: Optional backend to use
        
    Yields:
        BroadcastMessage objects
    """
    backend = backend or _default_backend
    if backend is None:
        raise RuntimeError("No broadcast backend configured. Call setup_broadcast() first.")
    
    async for message in backend.subscribe(channel):
        yield message


class ChannelLayer:
    """
    High-level channel layer for group communication
    """
    
    def __init__(self, backend: Optional[BroadcastBackend] = None):
        self.backend = backend or _default_backend
        if self.backend is None:
            raise RuntimeError("No broadcast backend configured")
    
    async def group_add(self, group: str, channel: str) -> None:
        """Add a channel to a group"""
        # In Redis, we use a set to track group membership
        pass  # Implementation depends on backend
    
    async def group_discard(self, group: str, channel: str) -> None:
        """Remove a channel from a group"""
        pass
    
    async def group_send(self, group: str, message: dict) -> None:
        """Send a message to all channels in a group"""
        await broadcast(f"group:{group}", message, backend=self.backend)
    
    async def send(self, channel: str, message: dict) -> None:
        """Send a message to a specific channel"""
        await broadcast(f"channel:{channel}", message, backend=self.backend)
