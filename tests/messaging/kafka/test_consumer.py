"""Tests for Kafka consumer."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from tests.messaging.kafka.abstraction import IKafkaTests


class _Msg:
    __slots__ = ("topic", "partition", "offset", "value")

    def __init__(self, value: bytes, offset: int = 0) -> None:
        self.topic = "t1"
        self.partition = 0
        self.offset = offset
        self.value = value


class _AsyncConsumerMock:
    """Minimal async-iterable consumer with a ``commit`` hook."""

    def __init__(self, messages: list[_Msg]) -> None:
        self._messages = messages
        self.commit = AsyncMock()

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for m in self._messages:
            yield m


class TestConsumer(IKafkaTests):
    @patch("messaging.kafka.consumer.KafkaConfiguration")
    def test_consumer_start_when_disabled(self, mock_cfg_cls):
        from messaging.kafka.consumer import KafkaConsumer

        mock_cfg = MagicMock()
        mock_cfg.get_config.return_value = MagicMock(
            enabled=False, topics=[], bootstrap_servers="", group_id="", enable_auto_commit=True
        )
        mock_cfg_cls.return_value = mock_cfg
        c = KafkaConsumer()
        asyncio.run(c.start())
        assert c._consumer is None

    @patch("messaging.kafka.consumer.KafkaConfiguration")
    def test_consumer_stop_no_consumer(self, mock_cfg_cls):
        from messaging.kafka.consumer import KafkaConsumer

        mock_cfg = MagicMock()
        mock_cfg.get_config.return_value = MagicMock(enabled=False)
        mock_cfg_cls.return_value = mock_cfg
        c = KafkaConsumer()
        asyncio.run(c.stop())

    @patch("messaging.kafka.consumer.KafkaConfiguration")
    def test_consumer_loop_when_not_running(self, mock_cfg_cls):
        from messaging.kafka.consumer import KafkaConsumer

        mock_cfg = MagicMock()
        mock_cfg.get_config.return_value = MagicMock(enabled=False)
        mock_cfg_cls.return_value = mock_cfg
        c = KafkaConsumer()

        async def handler(t, v):
            pass

        asyncio.run(c.loop(handler))

    @patch("messaging.kafka.consumer.KafkaConfiguration")
    def test_consumer_loop_idempotent_dedupes_and_commits(self, mock_cfg_cls):
        from messaging.kafka.consumer import KafkaConsumer

        mock_cfg = MagicMock()
        mock_cfg.get_config.return_value = MagicMock(
            enabled=True,
            enable_auto_commit=False,
            topics=["t1"],
            bootstrap_servers="localhost:9092",
            group_id="g",
        )
        mock_cfg_cls.return_value = mock_cfg
        same = b"payload"
        msgs = [_Msg(same, 0), _Msg(same, 1)]
        c = KafkaConsumer()
        c._consumer = _AsyncConsumerMock(msgs)
        c._cfg = mock_cfg.get_config.return_value
        calls: list[int] = []

        async def handler(t, v):
            calls.append(1)

        asyncio.run(c.loop_idempotent(handler))
        assert len(calls) == 1
        assert c._consumer.commit.await_count == 2

    @patch("messaging.kafka.consumer.KafkaConfiguration")
    def test_consumer_loop_idempotent_requires_manual_commit(self, mock_cfg_cls):
        from messaging.kafka.consumer import KafkaConsumer

        mock_cfg = MagicMock()
        mock_cfg.get_config.return_value = MagicMock(
            enabled=True,
            enable_auto_commit=True,
            topics=["t1"],
            bootstrap_servers="localhost:9092",
            group_id="g",
        )
        mock_cfg_cls.return_value = mock_cfg
        c = KafkaConsumer()
        c._consumer = _AsyncConsumerMock([_Msg(b"x", 0)])
        c._cfg = mock_cfg.get_config.return_value

        async def handler(t, v):
            pass

        try:
            asyncio.run(c.loop_idempotent(handler))
        except ValueError as e:
            assert "enable_auto_commit" in str(e).lower()
        else:
            raise AssertionError("expected ValueError")

    @patch("messaging.kafka.consumer.KafkaConfiguration")
    def test_consumer_loop_idempotent_when_not_running(self, mock_cfg_cls):
        from messaging.kafka.consumer import KafkaConsumer

        mock_cfg = MagicMock()
        mock_cfg.get_config.return_value = MagicMock(enabled=False)
        mock_cfg_cls.return_value = mock_cfg
        c = KafkaConsumer()

        async def handler(t, v):
            pass

        asyncio.run(c.loop_idempotent(handler))

    @patch("messaging.kafka.consumer.AIOKafkaConsumer")
    @patch("messaging.kafka.consumer.KafkaConfiguration")
    def test_consumer_start_stop_when_enabled(self, mock_cfg_cls, mock_aio_cls):
        from messaging.kafka.consumer import KafkaConsumer

        mock_cfg = MagicMock()
        mock_cfg.get_config.return_value = MagicMock(
            enabled=True,
            topics=["t1"],
            bootstrap_servers="localhost:9092",
            group_id="g",
            enable_auto_commit=True,
        )
        mock_cfg_cls.return_value = mock_cfg
        inst = MagicMock()
        inst.start = AsyncMock()
        inst.stop = AsyncMock()
        mock_aio_cls.return_value = inst
        c = KafkaConsumer()
        asyncio.run(c.start())
        asyncio.run(c.stop())
        inst.start.assert_awaited_once()
        inst.stop.assert_awaited_once()
