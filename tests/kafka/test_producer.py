"""Tests for Kafka producer."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_start_when_disabled(mock_cfg_cls):
    from fast_kafka.producer import KafkaProducer
    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=False, bootstrap_servers="localhost:9092")
    mock_cfg_cls.return_value = mock_cfg
    p = KafkaProducer()
    asyncio.run(p.start())
    assert p._producer is None


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_stop_no_producer(mock_cfg_cls):
    from fast_kafka.producer import KafkaProducer
    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=False)
    mock_cfg_cls.return_value = mock_cfg
    p = KafkaProducer()
    asyncio.run(p.stop())  # no-op


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_when_running(mock_cfg_cls):
    from unittest.mock import AsyncMock, MagicMock as MM

    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=True, bootstrap_servers="localhost:9092")
    mock_cfg_cls.return_value = mock_cfg

    p = KafkaProducer()
    p._producer = MM()
    p._producer.send_and_wait = AsyncMock()

    asyncio.run(p.send("topic", {"a": 1}))
    p._producer.send_and_wait.assert_awaited_once()


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_when_not_running(mock_cfg_cls):
    from fast_kafka.producer import KafkaProducer
    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=False)
    mock_cfg_cls.return_value = mock_cfg
    p = KafkaProducer()
    asyncio.run(p.send("topic", "msg"))  # no-op, drops message


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_json_envelope(mock_cfg_cls):
    from unittest.mock import AsyncMock, MagicMock as MM

    from fast_kafka.dto import KafkaJsonEnvelope
    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=True, bootstrap_servers="localhost:9092")
    mock_cfg_cls.return_value = mock_cfg

    p = KafkaProducer()
    p._producer = MM()
    p._producer.send_and_wait = AsyncMock()

    env = KafkaJsonEnvelope(message_type="Ping", payload={"ok": True})
    asyncio.run(p.send_json_envelope("events", env))

    p._producer.send_and_wait.assert_awaited_once()
    topic, payload = p._producer.send_and_wait.await_args[0]
    assert topic == "events"
    assert b"Ping" in payload


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_json_envelope_from_dict(mock_cfg_cls):
    from unittest.mock import AsyncMock, MagicMock as MM

    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=True, bootstrap_servers="localhost:9092")
    mock_cfg_cls.return_value = mock_cfg

    p = KafkaProducer()
    p._producer = MM()
    p._producer.send_and_wait = AsyncMock()

    asyncio.run(
        p.send_json_envelope(
            "events",
            {"message_type": "Ping", "payload": {"ok": True}, "schema_version": "2"},
        )
    )
    assert p._producer.send_and_wait.await_count == 1


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_json_envelope_when_disabled(mock_cfg_cls):
    from fast_kafka.dto import KafkaJsonEnvelope
    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=False)
    mock_cfg_cls.return_value = mock_cfg

    p = KafkaProducer()
    asyncio.run(p.send_json_envelope("t", KafkaJsonEnvelope(message_type="x", payload={})))


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_bytes_with_headers(mock_cfg_cls):
    from unittest.mock import AsyncMock, MagicMock as MM

    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MM(
        enabled=True,
        bootstrap_servers="localhost:9092",
        dlq_topic=None,
    )
    mock_cfg_cls.return_value = mock_cfg

    p = KafkaProducer()
    p._producer = MM()
    p._producer.send_and_wait = AsyncMock()

    asyncio.run(
        p.send_bytes(
            "topic-a",
            b"hello",
            headers=[("x", b"y")],
            key=b"k",
        )
    )
    p._producer.send_and_wait.assert_awaited_once()
    ca = p._producer.send_and_wait.await_args
    assert ca.args[:2] == ("topic-a", b"hello")
    assert ca.kwargs["key"] == b"k"
    assert ca.kwargs["headers"] == [("x", b"y")]


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_json_envelope_to_dlq(mock_cfg_cls):
    from unittest.mock import AsyncMock, MagicMock as MM

    from fast_kafka.dto import KafkaConfigurationDTO, KafkaJsonEnvelope
    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = KafkaConfigurationDTO(
        enabled=True,
        bootstrap_servers="localhost:9092",
        dlq_topic="app.dlq",
    )
    mock_cfg_cls.return_value = mock_cfg

    p = KafkaProducer()
    p._producer = MM()
    p._producer.send_and_wait = AsyncMock()

    env = KafkaJsonEnvelope(message_type="Err", payload={"n": 1})
    asyncio.run(
        p.send_json_envelope_to_dlq(
            env,
            original_topic="orders",
            error="boom",
            partition=2,
            offset=9,
        )
    )
    p._producer.send_and_wait.assert_awaited_once()
    ca = p._producer.send_and_wait.await_args
    topic, body = ca.args[:2]
    assert topic == "app.dlq"
    assert b"Err" in body
    assert ca.kwargs.get("headers")


@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_send_json_envelope_to_dlq_requires_topic(mock_cfg_cls):
    from fast_kafka.dto import KafkaConfigurationDTO, KafkaJsonEnvelope
    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = KafkaConfigurationDTO(
        enabled=True,
        bootstrap_servers="localhost:9092",
    )
    mock_cfg_cls.return_value = mock_cfg

    p = KafkaProducer()
    p._cfg = mock_cfg.get_config.return_value

    with pytest.raises(ValueError, match="dlq_topic"):
        asyncio.run(
            p.send_json_envelope_to_dlq(
                KafkaJsonEnvelope(message_type="E", payload={}),
                original_topic="t",
                error="e",
            )
        )


@patch("fast_kafka.producer.AIOKafkaProducer")
@patch("fast_kafka.producer.KafkaConfiguration")
def test_producer_start_stop_when_enabled(mock_cfg_cls, mock_aio_cls):
    from fast_kafka.producer import KafkaProducer

    mock_cfg = MagicMock()
    mock_cfg.get_config.return_value = MagicMock(enabled=True, bootstrap_servers="localhost:9092")
    mock_cfg_cls.return_value = mock_cfg
    inst = MagicMock()
    inst.start = AsyncMock()
    inst.stop = AsyncMock()
    mock_aio_cls.return_value = inst

    p = KafkaProducer()
    asyncio.run(p.start())
    asyncio.run(p.stop())
    inst.start.assert_awaited_once()
    inst.stop.assert_awaited_once()
