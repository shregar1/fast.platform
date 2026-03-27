"""Module test_hub_metrics_backpressure.py."""

import asyncio

import pytest

from fast_platform.realtime.channels.hub import ChannelsHub
from fast_platform.realtime.channels.metrics import InMemoryChannelMetrics
from tests.realtime.channels.abstraction import IChannelTests


class FakeWebSocket:
    """Represents the FakeWebSocket class."""

    def __init__(self, *, fail_on_send: bool = False):
        """Execute __init__ operation.

        Args:
            fail_on_send: The fail_on_send parameter.
        """
        self.accepted = False
        self.sent: list[str] = []
        self._fail_on_send = fail_on_send

    async def accept(self):
        """Execute accept operation.

        Returns:
            The result of the operation.
        """
        self.accepted = True

    async def send_text(self, message: str):
        """Execute send_text operation.

        Args:
            message: The message parameter.

        Returns:
            The result of the operation.
        """
        if self._fail_on_send:
            raise RuntimeError("send failed")
        self.sent.append(message)


class SlowWebSocket:
    """Represents the SlowWebSocket class."""

    def __init__(self):
        """Execute __init__ operation."""
        self.accepted = False

    async def accept(self):
        """Execute accept operation.

        Returns:
            The result of the operation.
        """
        self.accepted = True

    async def send_text(self, message: str):
        """Execute send_text operation.

        Args:
            message: The message parameter.

        Returns:
            The result of the operation.
        """
        await asyncio.sleep(10.0)


class TestHubMetricsBackpressure(IChannelTests):
    """Represents the TestHubMetricsBackpressure class."""

    def test_hub_rejects_invalid_queue_depth(self):
        """Execute test_hub_rejects_invalid_queue_depth operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError, match="max_queue_depth"):
            ChannelsHub(max_queue_depth_per_subscriber=0)

    def test_hub_metrics_in_memory(self):
        """Execute test_hub_metrics_in_memory operation.

        Returns:
            The result of the operation.
        """
        metrics = InMemoryChannelMetrics()
        hub = ChannelsHub(metrics=metrics)
        ws = FakeWebSocket()

        asyncio.run(hub.connect("room1", ws))
        assert metrics.subscribe_count == 1
        assert metrics.by_topic["room1"]["subscribes"] == 1

        asyncio.run(hub.broadcast("room1", "x"))
        assert metrics.publish_count == 1
        assert metrics.recipient_fanout_total == 1

        hub.disconnect("room1", ws)
        assert metrics.unsubscribe_count == 1

    def test_hub_metrics_no_publish_when_empty_topic(self):
        """Execute test_hub_metrics_no_publish_when_empty_topic operation.

        Returns:
            The result of the operation.
        """
        metrics = InMemoryChannelMetrics()
        hub = ChannelsHub(metrics=metrics)
        asyncio.run(hub.broadcast("empty", "noop"))
        assert metrics.publish_count == 0

    def test_hub_queue_full_disconnects_slow_consumer(self):
        """Execute test_hub_queue_full_disconnects_slow_consumer operation.

        Returns:
            The result of the operation.
        """

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            hub = ChannelsHub(max_queue_depth_per_subscriber=1)
            ws = SlowWebSocket()
            await hub.connect("t", ws)
            await hub.broadcast("t", "a")
            await hub.broadcast("t", "b")
            await hub.broadcast("t", "c")
            assert "t" not in hub._topics

        asyncio.run(run())
