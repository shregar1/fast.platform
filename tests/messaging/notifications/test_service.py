"""Tests for notifications service."""

import asyncio

from messaging.notifications.service import Notification, NotificationsService
from tests.messaging.notifications.abstraction import INotificationTests


async def _publish_and_list_since():
    """Execute _publish_and_list_since operation.

    Returns:
        The result of the operation.
    """
    svc = NotificationsService(max_items=10)
    n1 = await svc.publish("hello")
    n2 = await svc.publish("world")
    assert n1.id == 1
    assert n1.message == "hello"
    assert n2.id == 2
    items = await svc.list_since(0)
    assert len(items) == 2
    items = await svc.list_since(1)
    assert len(items) == 1
    assert items[0].message == "world"


class TestService(INotificationTests):
    """Represents the TestService class."""

    def test_publish_and_list_since(self):
        """Execute test_publish_and_list_since operation.

        Returns:
            The result of the operation.
        """
        asyncio.run(_publish_and_list_since())

    def test_notification_dataclass(self):
        """Execute test_notification_dataclass operation.

        Returns:
            The result of the operation.
        """
        from datetime import datetime

        n = Notification(id=1, message="x", created_at=datetime.utcnow())
        assert n.id == 1
        assert n.message == "x"

    def test_run_publish_list(self):
        """Execute test_run_publish_list operation.

        Returns:
            The result of the operation.
        """
        asyncio.run(_publish_and_list_since())
