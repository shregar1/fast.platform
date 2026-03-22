from tests.realtime.channels.abstraction import IChannelTests
import asyncio

class FakeWebSocket:

    def __init__(self, *, fail_on_send: bool=False):
        self.accepted = False
        self.sent: list[str] = []
        self._fail_on_send = fail_on_send

    async def accept(self):
        self.accepted = True

    async def send_text(self, message: str):
        if self._fail_on_send:
            raise RuntimeError('send failed')
        self.sent.append(message)

class TestHub(IChannelTests):

    def test_hub_connect_broadcast_and_disconnect_cleanup(self):
        from channels.hub import ChannelsHub
        hub = ChannelsHub()
        ws1 = FakeWebSocket()
        ws2 = FakeWebSocket()
        asyncio.run(hub.connect('room1', ws1))
        asyncio.run(hub.connect('room1', ws2))
        assert 'room1' in hub._topics
        assert ws1.accepted is True
        assert ws2.accepted is True
        asyncio.run(hub.broadcast('room1', 'hello'))
        assert ws1.sent == ['hello']
        assert ws2.sent == ['hello']
        hub.disconnect('room1', ws1)
        assert 'room1' in hub._topics
        hub.disconnect('room1', ws2)
        assert 'room1' not in hub._topics

    def test_hub_broadcast_disconnects_broken_socket(self):
        from channels.hub import ChannelsHub
        hub = ChannelsHub()
        good = FakeWebSocket()
        bad = FakeWebSocket(fail_on_send=True)
        asyncio.run(hub.connect('room1', good))
        asyncio.run(hub.connect('room1', bad))
        asyncio.run(hub.broadcast('room1', 'msg'))
        assert good.sent == ['msg']
        assert 'room1' in hub._topics
        assert bad not in {s.ws for s in hub._topics['room1']}

    def test_hub_subscriber_counts_and_topic_names(self):
        from channels.hub import ChannelsHub
        hub = ChannelsHub()
        ws1 = FakeWebSocket()
        ws2 = FakeWebSocket()
        asyncio.run(hub.connect('a', ws1))
        asyncio.run(hub.connect('a', ws2))
        asyncio.run(hub.connect('b', FakeWebSocket()))
        assert hub.subscriber_count('a') == 2
        assert hub.subscriber_count('b') == 1
        assert set(hub.all_subscriber_counts().keys()) == {'a', 'b'}
        assert set(hub.topic_names()) == {'a', 'b'}

    def test_hub_send_ping_record_pong_and_sweep(self):
        from channels.hub import ChannelsHub
        hub = ChannelsHub()
        ws = FakeWebSocket()
        asyncio.run(hub.connect('room1', ws))
        asyncio.run(hub.send_ping('room1', '{"type":"ping"}'))
        assert ws.sent == ['{"type":"ping"}']
        sub = next(iter(hub._topics['room1']))
        sub.last_pong_at = 0.0
        hub.sweep_stale_connections('room1', stale_after_seconds=1.0)
        assert 'room1' not in hub._topics
        ws2 = FakeWebSocket()
        asyncio.run(hub.connect('room1', ws2))
        hub.record_pong(ws2, 'room1')
        hub.sweep_stale_connections('room1', stale_after_seconds=3600.0)
        assert hub.subscriber_count('room1') == 1

    def test_hub_record_pong_without_topic_and_sweep_all_stale(self):
        from channels.hub import ChannelsHub
        hub = ChannelsHub()
        ws = FakeWebSocket()
        asyncio.run(hub.connect('z', ws))
        hub.record_pong(ws)
        sub = next(iter(hub._topics['z']))
        sub.last_pong_at = 0.0
        hub.sweep_all_stale(stale_after_seconds=0.01)
        assert 'z' not in hub._topics

    def test_hub_send_ping_with_queue(self):
        from channels.hub import ChannelsHub

        async def run():
            hub = ChannelsHub(max_queue_depth_per_subscriber=4)
            ws = FakeWebSocket()
            await hub.connect('room1', ws)
            await hub.send_ping('room1', 'ping')
            for _ in range(100):
                if ws.sent:
                    break
                await asyncio.sleep(0.01)
            assert ws.sent == ['ping']
        asyncio.run(run())
