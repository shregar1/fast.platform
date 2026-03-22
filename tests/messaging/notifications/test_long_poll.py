"""Tests for long_poll."""
from tests.messaging.notifications.abstraction import INotificationTests


import asyncio
from unittest.mock import patch

from notifications.service import NotificationsService


async def _long_poll_returns_quickly_when_items_exist():
    svc = NotificationsService()
    await svc.publish("first")
    items = await asyncio.wait_for(svc.long_poll(0, timeout_seconds=1), timeout=2.0)
    assert len(items) == 1
    assert items[0].message == "first"


async def _long_poll_times_out_empty():
    svc = NotificationsService()
    items = await svc.long_poll(0, timeout_seconds=0)
    assert items == []


async def _long_poll_uses_get_event_loop_when_no_running_loop():
    loop = asyncio.get_running_loop()
    svc = NotificationsService()
    with patch("asyncio.get_running_loop", side_effect=RuntimeError("no running loop")):
        with patch("asyncio.get_event_loop", return_value=loop):
            items = await svc.long_poll(0, timeout_seconds=0)
    assert items == []


async def _long_poll_calls_sleep_when_waiting():
    svc = NotificationsService()
    sleeps: list[float] = []

    async def capture_sleep(delay: float) -> None:
        sleeps.append(delay)

    with patch("asyncio.sleep", side_effect=capture_sleep):
        items = await svc.long_poll(999, timeout_seconds=0.02)
    assert items == []
    assert sleeps, "long_poll should sleep while waiting for new items"


class TestLongPoll(INotificationTests):
    def test_long_poll_returns_quickly_when_items_exist(self):
        asyncio.run(_long_poll_returns_quickly_when_items_exist())

    def test_long_poll_times_out_empty(self):
        asyncio.run(_long_poll_times_out_empty())

    def test_long_poll_uses_get_event_loop_when_no_running_loop(self):
        asyncio.run(_long_poll_uses_get_event_loop_when_no_running_loop())

    def test_long_poll_calls_sleep_when_waiting(self):
        asyncio.run(_long_poll_calls_sleep_when_waiting())
