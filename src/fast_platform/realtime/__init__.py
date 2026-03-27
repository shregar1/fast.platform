"""
FastMVC Real-time Module

WebSockets, Server-Sent Events (SSE), and real-time broadcasting.
"""

from .websocket import (
    websocket_endpoint,
    WebSocketManager,
    WebSocketChannel,
    WebSocketConnection,
)
from .sse import (
    sse_endpoint,
    EventStream,
)
from .broadcast import (
    broadcast,
    subscribe,
    BroadcastBackend,
    RedisBroadcastBackend,
)

__all__ = [
    "websocket_endpoint",
    "WebSocketManager",
    "WebSocketChannel",
    "sse_endpoint",
    "EventStream",
    "broadcast",
    "subscribe",
    "BroadcastBackend",
    "RedisBroadcastBackend",
]
