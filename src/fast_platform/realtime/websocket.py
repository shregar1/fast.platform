"""WebSocket support for FastMVC."""

from typing import Dict, Set, Callable, Any, Optional, List
from dataclasses import dataclass, field
from functools import wraps
import json
import asyncio


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection."""

    id: str
    user_id: Optional[str]
    groups: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # These will be set by the manager
    _send_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    _recv_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    _closed: bool = False

    async def send(self, message: Any) -> None:
        """Send a message to this connection."""
        if self._closed:
            raise ConnectionError("WebSocket is closed")
        await self._send_queue.put(message)

    async def send_json(self, data: dict) -> None:
        """Send JSON data."""
        await self.send({"type": "json", "data": data})

    async def send_text(self, text: str) -> None:
        """Send text message."""
        await self.send({"type": "text", "data": text})

    async def send_bytes(self, data: bytes) -> None:
        """Send binary data."""
        await self.send({"type": "bytes", "data": data})

    async def receive(self) -> Any:
        """Receive a message."""
        if self._closed:
            raise ConnectionError("WebSocket is closed")
        return await self._recv_queue.get()

    async def receive_json(self) -> dict:
        """Receive JSON data."""
        message = await self.receive()
        if isinstance(message, str):
            return json.loads(message)
        return message.get("data", {})

    async def receive_text(self) -> str:
        """Receive text message."""
        message = await self.receive()
        if isinstance(message, str):
            return message
        return str(message.get("data", ""))

    async def close(self, code: int = 1000, reason: str = "") -> None:
        """Close the connection."""
        self._closed = True
        await self._send_queue.put({"type": "close", "code": code, "reason": reason})

    def join_group(self, group: str) -> None:
        """Join a group for broadcasting."""
        self.groups.add(group)

    def leave_group(self, group: str) -> None:
        """Leave a group."""
        self.groups.discard(group)


class WebSocketManager:
    """Manages WebSocket connections and groups."""

    _instance: Optional["WebSocketManager"] = None

    def __new__(cls):
        """Execute __new__ operation.

        Returns:
            The result of the operation.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connections: Dict[str, WebSocketConnection] = {}
            cls._instance._groups: Dict[str, Set[str]] = {}
        return cls._instance

    def connect(self, connection_id: str, user_id: Optional[str] = None) -> WebSocketConnection:
        """Create a new connection."""
        conn = WebSocketConnection(id=connection_id, user_id=user_id)
        self._connections[connection_id] = conn
        return conn

    def disconnect(self, connection_id: str) -> None:
        """Remove a connection."""
        if connection_id in self._connections:
            conn = self._connections[connection_id]
            # Remove from all groups
            for group in list(conn.groups):
                self.leave_group(connection_id, group)
            del self._connections[connection_id]

    def join_group(self, connection_id: str, group: str) -> None:
        """Add connection to a group."""
        if connection_id not in self._connections:
            return

        conn = self._connections[connection_id]
        conn.join_group(group)

        if group not in self._groups:
            self._groups[group] = set()
        self._groups[group].add(connection_id)

    def leave_group(self, connection_id: str, group: str) -> None:
        """Remove connection from a group."""
        if group in self._groups:
            self._groups[group].discard(connection_id)

    async def broadcast_to_group(self, group: str, message: Any) -> int:
        """Broadcast a message to all connections in a group."""
        if group not in self._groups:
            return 0

        sent = 0
        for conn_id in self._groups[group]:
            if conn_id in self._connections:
                try:
                    await self._connections[conn_id].send(message)
                    sent += 1
                except Exception:
                    pass  # Connection might be closed
        return sent

    async def broadcast_to_user(self, user_id: str, message: Any) -> int:
        """Broadcast to all connections of a user."""
        sent = 0
        for conn in self._connections.values():
            if conn.user_id == user_id:
                try:
                    await conn.send(message)
                    sent += 1
                except Exception:
                    pass
        return sent

    async def broadcast_all(self, message: Any) -> int:
        """Broadcast to all connections."""
        sent = 0
        for conn in self._connections.values():
            try:
                await conn.send(message)
                sent += 1
            except Exception:
                pass
        return sent

    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get a connection by ID."""
        return self._connections.get(connection_id)

    def get_connection_count(self) -> int:
        """Get total number of connections."""
        return len(self._connections)

    def get_group_count(self, group: str) -> int:
        """Get number of connections in a group."""
        return len(self._groups.get(group, set()))


class WebSocketChannel:
    """Context manager for WebSocket channels with automatic cleanup."""

    def __init__(self, connection: WebSocketConnection, group: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            connection: The connection parameter.
            group: The group parameter.
        """
        self.connection = connection
        self.group = group

    async def __aenter__(self):
        """Execute __aenter__ operation.

        Returns:
            The result of the operation.
        """
        if self.group:
            manager = WebSocketManager()
            manager.join_group(self.connection.id, self.group)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Execute __aexit__ operation.

        Args:
            exc_type: The exc_type parameter.
            exc_val: The exc_val parameter.
            exc_tb: The exc_tb parameter.

        Returns:
            The result of the operation.
        """
        manager = WebSocketManager()
        if self.group:
            manager.leave_group(self.connection.id, self.group)
        manager.disconnect(self.connection.id)


def websocket_endpoint(
    path: str,
    auth_required: bool = False,
    max_message_size: int = 1024 * 1024,  # 1MB
    ping_interval: float = 20.0,
    ping_timeout: float = 20.0,
):
    """Decorator for WebSocket endpoints.

    Args:
        path: WebSocket endpoint path
        auth_required: Whether authentication is required
        max_message_size: Maximum message size in bytes
        ping_interval: Ping interval in seconds
        ping_timeout: Ping timeout in seconds

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        func._is_websocket_endpoint = True
        func._websocket_path = path
        func._websocket_auth_required = auth_required
        func._websocket_config = {
            "max_message_size": max_message_size,
            "ping_interval": ping_interval,
            "ping_timeout": ping_timeout,
        }

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            # This would be called by the framework with the WebSocket object
            # For now, just call the handler
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Global manager instance
manager = WebSocketManager()
