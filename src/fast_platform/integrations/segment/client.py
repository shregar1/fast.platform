"""Segment Analytics client."""

from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from functools import wraps
import asyncio


@dataclass
class SegmentEvent:
    """Segment event."""

    user_id: Optional[str]
    event: Optional[str]
    properties: Dict[str, Any]
    timestamp: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class SegmentClient:
    """Segment Analytics client."""

    def __init__(self, write_key: str, flush_at: int = 20, flush_interval: float = 10.0):
        """Execute __init__ operation.

        Args:
            write_key: The write_key parameter.
            flush_at: The flush_at parameter.
            flush_interval: The flush_interval parameter.
        """
        self.write_key = write_key
        self.flush_at = flush_at
        self.flush_interval = flush_interval
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                import segment.analytics as analytics

                analytics.write_key = self.write_key
                analytics.flush_at = self.flush_at
                analytics.flush_interval = self.flush_interval

                self._client = analytics

            except ImportError:
                raise ImportError("segment-analytics-python required for SegmentClient")

        return self._client

    async def track(
        self,
        user_id: str,
        event: str,
        properties: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Track an event."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.track(
                    user_id=user_id, event=event, properties=properties or {}, context=context or {}
                ),
            )

        return True

    async def identify(
        self,
        user_id: str,
        traits: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Identify a user."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.identify(
                    user_id=user_id, traits=traits or {}, context=context or {}
                ),
            )

        return True

    async def group(
        self, user_id: str, group_id: str, traits: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Associate user with a group."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool, lambda: client.group(user_id=user_id, group_id=group_id, traits=traits or {})
            )

        return True

    async def page(
        self, user_id: str, name: Optional[str] = None, properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track a page view."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool, lambda: client.page(user_id=user_id, name=name, properties=properties or {})
            )

        return True

    async def flush(self) -> bool:
        """Flush pending events."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, client.flush)

        return True


# Decorators


def track(event: str, properties: Optional[Dict[str, Any]] = None):
    """Decorator to track function calls in Segment.

    Args:
        event: Event name
        properties: Additional properties

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            # Would need a global client instance
            result = await func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def identify(user_id_func: Callable):
    """Decorator to identify users.

    Args:
        user_id_func: Function to extract user_id from arguments

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            result = await func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def group(group_id_func: Callable):
    """Decorator for group calls."""

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            result = await func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def page(name: str):
    """Decorator for page tracking."""

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            result = await func(*args, **kwargs)
            return result

        return wrapper

    return decorator
