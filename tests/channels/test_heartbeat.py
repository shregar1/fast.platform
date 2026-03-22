import asyncio


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent: list[str] = []

    async def accept(self):
        self.accepted = True

    async def send_text(self, message: str):
        self.sent.append(message)


def test_run_heartbeat_loop_stops_via_event():
    from fast_channels.heartbeat import run_heartbeat_loop
    from fast_channels.hub import ChannelsHub

    hub = ChannelsHub()
    stop = asyncio.Event()

    async def main():
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


def test_run_heartbeat_loop_sends_ping_and_can_sweep():
    from fast_channels.heartbeat import run_heartbeat_loop
    from fast_channels.hub import ChannelsHub

    hub = ChannelsHub()
    ws = FakeWebSocket()
    asyncio.run(hub.connect("t", ws))
    sub = next(iter(hub._topics["t"]))
    sub.last_pong_at = 0.0

    stop = asyncio.Event()

    async def main():
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
