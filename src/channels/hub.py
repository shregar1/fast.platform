"""
In-memory WebSocket channels hub.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Dict, Optional, Set

from loguru import logger

if TYPE_CHECKING:
    from fastapi import WebSocket

    from .metrics import ChannelMetrics


class _HubSubscriber:
    __slots__ = ("ws", "queue", "_sender_task", "last_pong_at")

    def __init__(self, ws: WebSocket, *, queue_maxsize: Optional[int]) -> None:
        self.ws = ws
        self.queue: Optional[asyncio.Queue[str]] = None
        self._sender_task: Optional[asyncio.Task[None]] = None
        self.last_pong_at: float = time.time()
        if queue_maxsize is not None:
            self.queue = asyncio.Queue(maxsize=queue_maxsize)


class ChannelsHub:
    """
    Tracks WebSocket connections per topic and dispatches messages.

    * ``metrics`` — optional :class:`~fast_channels.metrics.ChannelMetrics`
      (e.g. :class:`~fast_channels.metrics.InMemoryChannelMetrics`).
    * ``max_queue_depth_per_subscriber`` — when set, each connection uses an
      ``asyncio.Queue`` of that size; a background task drains to ``send_text``.
      If the queue is full (slow consumer), that subscriber is dropped. When
      ``None``, messages are sent inline (previous behavior).
    """

    def __init__(
        self,
        *,
        metrics: Optional["ChannelMetrics"] = None,
        max_queue_depth_per_subscriber: Optional[int] = None,
    ) -> None:
        if max_queue_depth_per_subscriber is not None and max_queue_depth_per_subscriber < 1:
            raise ValueError("max_queue_depth_per_subscriber must be >= 1 when set")
        self._metrics = metrics
        self._max_queue_depth_per_subscriber = max_queue_depth_per_subscriber
        self._topics: Dict[str, Set[_HubSubscriber]] = {}

    async def connect(self, topic: str, ws: WebSocket) -> None:
        await ws.accept()
        sub = _HubSubscriber(ws, queue_maxsize=self._max_queue_depth_per_subscriber)
        self._topics.setdefault(topic, set()).add(sub)
        if sub.queue is not None:
            sub._sender_task = asyncio.create_task(self._drain_sender(topic, sub))
        if self._metrics:
            self._metrics.record_subscribe(topic)
        logger.debug("WebSocket joined topic {}", topic)

    def disconnect(self, topic: str, ws: WebSocket) -> None:
        subs = self._topics.get(topic)
        if not subs:
            return
        sub: Optional[_HubSubscriber] = None
        for s in subs:
            if s.ws is ws:
                sub = s
                break
        if sub is None:
            return
        subs.discard(sub)
        if not subs:
            del self._topics[topic]
        if sub._sender_task is not None and not sub._sender_task.done():
            sub._sender_task.cancel()
        if self._metrics:
            self._metrics.record_unsubscribe(topic)
        logger.debug("WebSocket left topic {}", topic)

    async def broadcast(self, topic: str, message: str) -> None:
        subs = list(self._topics.get(topic, set()))
        if self._metrics and subs:
            self._metrics.record_publish(topic, recipient_count=len(subs))
        for sub in subs:
            if sub.queue is None:
                try:
                    await sub.ws.send_text(message)
                except Exception as exc:
                    logger.warning("Failed to send message on topic {}: {}", topic, exc)
                    self.disconnect(topic, sub.ws)
            else:
                try:
                    sub.queue.put_nowait(message)
                except asyncio.QueueFull:
                    logger.warning(
                        "Subscriber queue full on topic {} (max depth {}); disconnecting slow client",
                        topic,
                        self._max_queue_depth_per_subscriber,
                    )
                    self.disconnect(topic, sub.ws)

    async def _drain_sender(self, topic: str, sub: _HubSubscriber) -> None:
        assert sub.queue is not None
        try:
            while True:
                msg = await sub.queue.get()
                try:
                    await sub.ws.send_text(msg)
                except Exception as exc:
                    logger.warning("Failed to send message on topic {}: {}", topic, exc)
                    self.disconnect(topic, sub.ws)
                    return
        except asyncio.CancelledError:
            return

    def subscriber_count(self, topic: str) -> int:
        """In-process WebSocket subscriber count for *topic* (same as ``len`` of internal set)."""
        return len(self._topics.get(topic, set()))

    def all_subscriber_counts(self) -> Dict[str, int]:
        """Map topic name → subscriber count for observability / presence-style APIs."""
        return {t: len(subs) for t, subs in self._topics.items()}

    def topic_names(self) -> list[str]:
        """Active topic keys."""
        return list(self._topics.keys())

    def record_pong(self, ws: WebSocket, topic: Optional[str] = None) -> None:
        """
        Mark *ws* as alive (call when the client responds to a JSON/text ping).

        If *topic* is omitted, searches all topics (slightly slower).
        """
        now = time.time()

        def _touch(sub: _HubSubscriber) -> None:
            sub.last_pong_at = now

        if topic is not None:
            for sub in self._topics.get(topic, set()):
                if sub.ws is ws:
                    _touch(sub)
                    return
            return
        for subs in self._topics.values():
            for sub in subs:
                if sub.ws is ws:
                    _touch(sub)
                    return

    async def send_ping(self, topic: str, payload: str = '{"type":"ping"}') -> None:
        """Send *payload* to every subscriber on *topic* (keep-alive / heartbeat)."""
        for sub in list(self._topics.get(topic, set())):
            if sub.queue is None:
                try:
                    await sub.ws.send_text(payload)
                except Exception as exc:
                    logger.warning("Ping failed on topic {}: {}", topic, exc)
                    self.disconnect(topic, sub.ws)
            else:
                try:
                    sub.queue.put_nowait(payload)
                except asyncio.QueueFull:
                    logger.warning("Subscriber queue full on ping for topic {}", topic)
                    self.disconnect(topic, sub.ws)

    def sweep_stale_connections(self, topic: str, *, stale_after_seconds: float) -> None:
        """Disconnect subscribers whose last pong timestamp is older than *stale_after_seconds*."""
        now = time.time()
        for sub in list(self._topics.get(topic, set())):
            if now - sub.last_pong_at > stale_after_seconds:
                self.disconnect(topic, sub.ws)

    def sweep_all_stale(self, stale_after_seconds: float) -> None:
        """Run :meth:`sweep_stale_connections` for every active topic."""
        for topic in list(self._topics.keys()):
            self.sweep_stale_connections(topic, stale_after_seconds=stale_after_seconds)
