"""Module test_heartbeat.py."""

import asyncio

from tests.realtime.channels.abstraction import IChannelTests


class FakeWebSocket:
    """Represents the FakeWebSocket class."""

    def __init__(self):
        """Execute __init__ operation."""
        self.accepted = False
        self.sent: list[str] = []

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
        self.sent.append(message)


class TestHeartbeat(IChannelTests):
    """Represents the TestHeartbeat class."""

    def test_run_heartbeat_loop_stops_via_event(self):
        """Execute test_run_heartbeat_loop_stops_via_event operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.channels.heartbeat import run_heartbeat_loop
        from fast_platform.realtime.channels.hub import ChannelsHub

        hub = ChannelsHub()
        stop = asyncio.Event()

        async def main():
            """Execute main operation.

            Returns:
                The result of the operation.
            """
            t = asyncio.create_task(
                run_heartbeat_loop(
                    hub,
                    interval_seconds=0.02,
                    stale_after_seconds=1.0,
                    ping_payload="p",
                    stop_event=stop,
                )
            )
            await asyncio.sleep(0.06)
            stop.set()
            await asyncio.wait_for(t, timeout=2.0)

        asyncio.run(main())

    def test_run_heartbeat_loop_sends_ping_and_can_sweep(self):
        """Execute test_run_heartbeat_loop_sends_ping_and_can_sweep operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.channels.heartbeat import run_heartbeat_loop
        from fast_platform.realtime.channels.hub import ChannelsHub

        hub = ChannelsHub()
        ws = FakeWebSocket()
        asyncio.run(hub.connect("t", ws))
        sub = next(iter(hub._topics["t"]))
        sub.last_pong_at = 0.0
        stop = asyncio.Event()

        async def main():
            """Execute main operation.

            Returns:
                The result of the operation.
            """
            t = asyncio.create_task(
                run_heartbeat_loop(
                    hub,
                    interval_seconds=0.02,
                    stale_after_seconds=0.01,
                    ping_payload="ping",
                    stop_event=stop,
                )
            )
            await asyncio.sleep(0.08)
            stop.set()
            await asyncio.wait_for(t, timeout=2.0)

        asyncio.run(main())
        assert "ping" in ws.sent
        assert "t" not in hub._topics
