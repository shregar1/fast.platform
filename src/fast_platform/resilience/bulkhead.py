"""Bulkhead pattern (isolation) implementation."""

from typing import Optional, Callable, Any
from dataclasses import dataclass
from functools import wraps
import asyncio


@dataclass
class BulkheadConfig:
    """Bulkhead configuration."""

    max_concurrent: int = 10
    max_queue: int = 100
    queue_timeout: float = 30.0


class Bulkhead:
    """Bulkhead pattern implementation.

    Limits concurrent execution to prevent resource exhaustion.
    """

    def __init__(self, name: str, config: Optional[BulkheadConfig] = None):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
            config: The config parameter.
        """
        self.name = name
        self.config = config or BulkheadConfig()

        self._semaphore = asyncio.Semaphore(config.max_concurrent)
        self._queue_size = 0
        self._lock = asyncio.Lock()

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function within bulkhead constraints."""
        async with self._lock:
            if self._queue_size >= self.config.max_queue:
                raise BulkheadFull(f"Bulkhead {self.name} queue full ({self.config.max_queue})")
            self._queue_size += 1

        try:
            # Wait for semaphore with timeout
            acquired = await asyncio.wait_for(
                self._semaphore.acquire(), timeout=self.config.queue_timeout
            )

            if not acquired:
                raise BulkheadTimeout(f"Timeout waiting for bulkhead {self.name}")

            try:
                return await func(*args, **kwargs)
            finally:
                self._semaphore.release()
        finally:
            async with self._lock:
                self._queue_size -= 1

    @property
    def available_slots(self) -> int:
        """Number of available execution slots."""
        return self._semaphore._value

    @property
    def queue_length(self) -> int:
        """Current queue length."""
        return self._queue_size


class BulkheadFull(Exception):
    """Raised when bulkhead queue is full."""

    pass


class BulkheadTimeout(Exception):
    """Raised when waiting for bulkhead times out."""

    pass


_bulkeads: dict = {}


def bulkhead(name: Optional[str] = None, max_concurrent: int = 10, max_queue: int = 100):
    """Decorator to add bulkhead isolation to a function.

    Args:
        name: Bulkhead name
        max_concurrent: Max concurrent executions
        max_queue: Max queue size

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        bh_name = name or func.__name__

        config = BulkheadConfig(max_concurrent=max_concurrent, max_queue=max_queue)

        bh = Bulkhead(bh_name, config)
        _bulkeads[bh_name] = bh

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            return await bh.execute(func, *args, **kwargs)

        wrapper._bulkhead = bh
        return wrapper

    return decorator
