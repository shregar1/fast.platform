"""Event System for FastMVC.

Lightweight pub/sub using Redis or in-memory fallback.

Usage:
from ...caching.constants import DEFAULT_REDIS_URL
    from fast_platform.core.events import event, on, emit

    # Define event handler
    @on("user.created")
    async def handle_user_created(event):
        await send_welcome_email(event.data["email"])

    # Emit event
    await emit("user.created", {"user_id": "123", "email": "user@example.com"})

    # Or with decorator
    @event("order.completed")
    async def process_order(event):
        await send_confirmation(event.data["order_id"])

    # Emit and handle automatically
    await emit("order.completed", {"order_id": "456"})

Configuration:
    EVENT_BACKEND=redis  # or 'memory' for testing
    REDIS_URL=redis://localhost:6379/0
"""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Represents an event."""

    name: str
    data: Any
    timestamp: datetime
    id: Optional[str] = None

    def to_dict(self) -> dict:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        return {
            "name": self.name,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "id": self.id,
        }


# In-memory handlers registry
_handlers: Dict[str, List[Callable]] = {}

# Redis connection (lazy loaded)
_redis_client = None


def _get_redis():
    """Get or create Redis connection."""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        from redis import Redis
        import os

        redis_url = os.getenv("REDIS_URL", DEFAULT_REDIS_URL)
        _redis_client = Redis.from_url(redis_url, decode_responses=True)
        return _redis_client
    except Exception:
        return None


def _get_backend() -> str:
    """Get configured event backend."""
    import os

    return os.getenv("EVENT_BACKEND", "memory")


class EventBus:
    """Event bus for pub/sub operations.

    Usage:
        bus = EventBus()

        @bus.on("user.created")
        async def handle_user(event):
            print(f"User created: {event.data}")

        await bus.emit("user.created", {"id": "123"})
    """

    def __init__(self, backend: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            backend: The backend parameter.
        """
        self.backend = backend or _get_backend()
        self._local_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._listener_task = None

    def on(self, event_name: str):
        """Decorator to register an event handler.

        Usage:
            @bus.on("user.created")
            async def handle_user(event):
                await process_user(event.data)
        """

        def decorator(func: Callable) -> Callable:
            """Execute decorator operation.

            Args:
                func: The func parameter.

            Returns:
                The result of the operation.
            """
            if event_name not in self._local_handlers:
                self._local_handlers[event_name] = []
            self._local_handlers[event_name].append(func)

            # Also register in global handlers for compatibility
            if event_name not in _handlers:
                _handlers[event_name] = []
            _handlers[event_name].append(func)

            return func

        return decorator

    async def emit(self, event_name: str, data: Any, delay: Optional[int] = None) -> Event:
        """Emit an event.

        Args:
            event_name: Name of the event
            data: Event data (must be JSON serializable)
            delay: Delay in seconds before processing

        Returns:
            Event object

        """
        import uuid

        event = Event(name=event_name, data=data, timestamp=datetime.utcnow(), id=str(uuid.uuid4()))

        if delay and delay > 0:
            # Schedule for later
            await asyncio.sleep(delay)

        if self.backend == "redis":
            await self._emit_redis(event)
        else:
            await self._emit_memory(event)

        return event

    async def _emit_memory(self, event: Event) -> None:
        """Emit to in-memory handlers."""
        handlers = self._local_handlers.get(event.name, [])

        if not handlers:
            handlers = _handlers.get(event.name, [])

        # Run all handlers
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(asyncio.create_task(handler(event)))
                else:
                    handler(event)
            except Exception as e:
                print(f"Event handler error: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _emit_redis(self, event: Event) -> None:
        """Emit via Redis pub/sub."""
        redis = _get_redis()
        if not redis:
            # Fallback to memory
            await self._emit_memory(event)
            return

        # Publish to Redis channel
        channel = f"events:{event.name}"
        message = json.dumps(event.to_dict())

        try:
            redis.publish(channel, message)

            # Also trigger local handlers
            await self._emit_memory(event)
        except Exception as e:
            print(f"Redis emit error: {e}")
            await self._emit_memory(event)

    async def start_listener(self):
        """Start Redis pub/sub listener (for workers)."""
        if self.backend != "redis":
            return

        redis = _get_redis()
        if not redis:
            return

        self._running = True

        # Subscribe to all event channels
        pubsub = redis.pubsub()
        patterns = [f"events:{name}" for name in self._local_handlers.keys()]

        if patterns:
            pubsub.psubscribe(*patterns)

        while self._running:
            try:
                message = pubsub.get_message(timeout=1)
                if message and message["type"] == "pmessage":
                    # Parse event
                    data = json.loads(message["data"])
                    event = Event(
                        name=data["name"],
                        data=data["data"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        id=data.get("id"),
                    )

                    # Handle locally
                    await self._emit_memory(event)

                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Listener error: {e}")
                await asyncio.sleep(1)

    def stop_listener(self):
        """Stop the Redis listener."""
        self._running = False

    async def wait_for_event(
        self, event_name: str, timeout: Optional[float] = None, predicate: Optional[Callable] = None
    ) -> Optional[Event]:
        """Wait for an event to occur.

        Usage:
            event = await bus.wait_for_event("order.completed", timeout=30)
            if event:
                print(f"Order {event.data['order_id']} completed")

        Args:
            event_name: Event to wait for
            timeout: Maximum time to wait (seconds)
            predicate: Optional function to filter events

        Returns:
            Event or None if timeout

        """
        future = asyncio.Future()

        @self.on(event_name)
        async def handler(event):
            """Execute handler operation.

            Args:
                event: The event parameter.

            Returns:
                The result of the operation.
            """
            if future.done():
                return

            if predicate is None or predicate(event):
                future.set_result(event)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None


# Global event bus instance
_default_bus = None


def get_event_bus() -> EventBus:
    """Get the default event bus instance."""
    global _default_bus
    if _default_bus is None:
        _default_bus = EventBus()
    return _default_bus


# Convenience functions using global bus
def on(event_name: str):
    """Decorator to register an event handler on the global bus.

    Usage:
        @on("user.created")
        async def handle_user(event):
            await send_email(event.data["email"])
    """
    return get_event_bus().on(event_name)


async def emit(event_name: str, data: Any, delay: Optional[int] = None) -> Event:
    """Emit an event on the global bus.

    Usage:
        await emit("user.created", {"id": "123", "email": "user@example.com"})
    """
    return await get_event_bus().emit(event_name, data, delay)


# Alias for emit
publish = emit


def event(event_name: str):
    """Decorator that both registers and documents an event.

    This is an alias for @on() but makes the intent clearer.

    Usage:
        @event("order.completed")
        async def handle_order(event):
            await process_order(event.data)
    """
    return on(event_name)


class EventRecorder:
    """Records events for testing/debugging.

    Usage:
        recorder = EventRecorder()

        with recorder:
            await emit("user.created", {"id": "123"})
            await emit("user.created", {"id": "456"})

        assert len(recorder.events) == 2
        assert recorder.events[0].data["id"] == "123"
    """

    def __init__(self):
        """Execute __init__ operation."""
        self.events: List[Event] = []
        self._handlers = []

    def __enter__(self):
        """Start recording all events."""

        @on("*")
        async def catch_all(event):
            """Execute catch_all operation.

            Args:
                event: The event parameter.

            Returns:
                The result of the operation.
            """
            self.events.append(event)

        self._handlers.append(catch_all)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop recording."""
        # Remove handlers
        for event_name, handlers in list(_handlers.items()):
            for handler in self._handlers:
                if handler in handlers:
                    handlers.remove(handler)

        return False

    def clear(self):
        """Clear recorded events."""
        self.events.clear()


# Background task runner for events
class BackgroundEventRunner:
    """Runs event handlers in background tasks.

    Usage:
        runner = BackgroundEventRunner()

        @runner.handler("user.created")
        async def process_user(event):
            # This runs in background
            await send_email(event.data["email"])

        await runner.start()
    """

    def __init__(self, max_workers: int = 10):
        """Execute __init__ operation.

        Args:
            max_workers: The max_workers parameter.
        """
        self.max_workers = max_workers
        self._handlers: Dict[str, List[Callable]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._workers = []

    def handler(self, event_name: str):
        """Decorator to register a background handler."""

        def decorator(func: Callable):
            """Execute decorator operation.

            Args:
                func: The func parameter.

            Returns:
                The result of the operation.
            """
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            self._handlers[event_name].append(func)
            return func

        return decorator

    async def start(self):
        """Start background workers."""
        self._running = True

        for _ in range(self.max_workers):
            worker = asyncio.create_task(self._worker())
            self._workers.append(worker)

    async def stop(self):
        """Stop background workers."""
        self._running = False

        # Wait for all workers
        await asyncio.gather(*self._workers, return_exceptions=True)

    async def _worker(self):
        """Worker that processes events."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1)

                handlers = self._handlers.get(event.name, [])
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        print(f"Background handler error: {e}")

                self._queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def emit(self, event_name: str, data: Any):
        """Queue an event for background processing."""
        event = Event(name=event_name, data=data, timestamp=datetime.utcnow())
        await self._queue.put(event)
