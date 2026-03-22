"""Tests for notifications service."""
from tests.messaging.notifications.abstraction import INotificationTests

import asyncio
from notifications.service import NotificationsService, Notification

async def _publish_and_list_since():
    svc = NotificationsService(max_items=10)
    n1 = await svc.publish('hello')
    n2 = await svc.publish('world')
    assert n1.id == 1
    assert n1.message == 'hello'
    assert n2.id == 2
    items = await svc.list_since(0)
    assert len(items) == 2
    items = await svc.list_since(1)
    assert len(items) == 1
    assert items[0].message == 'world'

class TestService(INotificationTests):

    def test_publish_and_list_since(self):
        asyncio.run(_publish_and_list_since())

    def test_notification_dataclass(self):
        from datetime import datetime
        n = Notification(id=1, message='x', created_at=datetime.utcnow())
        assert n.id == 1
        assert n.message == 'x'

    def test_run_publish_list(self):
        asyncio.run(_publish_and_list_since())
