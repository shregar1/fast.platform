"""Simple in-memory notifications service used for realtime HTTP examples."""

from ...core.constants import DEFAULT_TIMEOUT_SECONDS
import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, List

from loguru import logger


@dataclass
class Notification:
    """Represents the Notification class."""

    id: int
    message: str
    created_at: datetime


class NotificationsService:
    """Keeps a small in-memory buffer of notifications for demo purposes."""

    def __init__(self, max_items: int = 100) -> None:
        """Execute __init__ operation.

        Args:
            max_items: The max_items parameter.
        """
        self._max_items = max_items
        self._items: Deque[Notification] = deque(maxlen=max_items)
        self._next_id: int = 1
        self._lock = asyncio.Lock()

    async def publish(self, message: str) -> Notification:
        """Execute publish operation.

        Args:
            message: The message parameter.

        Returns:
            The result of the operation.
        """
        async with self._lock:
            item = Notification(
                id=self._next_id,
                message=message,
                created_at=datetime.utcnow(),
            )
            self._next_id += 1
            self._items.append(item)
            logger.debug(f"Published notification {item.id}: {item.message}")
            return item

    async def list_since(self, last_id: int) -> List[Notification]:
        """Execute list_since operation.

        Args:
            last_id: The last_id parameter.

        Returns:
            The result of the operation.
        """
        async with self._lock:
            return [n for n in self._items if n.id > last_id]

    async def long_poll(self, last_id: int, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> List[Notification]:
        """Execute long_poll operation.

        Args:
            last_id: The last_id parameter.
            timeout_seconds: The timeout_seconds parameter.

        Returns:
            The result of the operation.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        deadline = loop.time() + timeout_seconds

        while True:
            items = await self.list_since(last_id)
            if items:
                return items
            remaining = deadline - loop.time()
            if remaining <= 0:
                return []
            await asyncio.sleep(min(1.0, remaining))
