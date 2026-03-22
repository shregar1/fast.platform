"""Tests for consumer lag polling (mocked Kafka clients)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from aiokafka.structs import OffsetAndMetadata, TopicPartition


@patch("fast_kafka.lag.AIOKafkaAdminClient")
@patch("fast_kafka.lag.AIOKafkaConsumer")
def test_poll_consumer_lag_computes_lag(mock_consumer_cls, mock_admin_cls):
    from fast_kafka.lag import poll_consumer_lag

    tp = TopicPartition("orders", 0)

    cons = MagicMock()
    cons.start = AsyncMock()
    cons.stop = AsyncMock()
    cons.partitions_for_topic = MagicMock(return_value={tp})
    cons.end_offsets = AsyncMock(return_value={tp: 100})
    mock_consumer_cls.return_value = cons

    adm = MagicMock()
    adm.start = AsyncMock()
    adm.close = AsyncMock()
    adm.list_consumer_group_offsets = AsyncMock(
        return_value={tp: OffsetAndMetadata(90, "")}
    )
    mock_admin_cls.return_value = adm

    out = asyncio.run(poll_consumer_lag("localhost:9092", "g", ["orders"]))
    assert len(out) == 1
    assert out[0].topic == "orders"
    assert out[0].partition == 0
    assert out[0].committed_offset == 90
    assert out[0].end_offset == 100
    assert out[0].lag == 10


@patch("fast_kafka.lag.AIOKafkaConsumer")
def test_poll_consumer_lag_no_partitions(mock_consumer_cls):
    from fast_kafka.lag import poll_consumer_lag

    cons = MagicMock()
    cons.start = AsyncMock()
    cons.stop = AsyncMock()
    cons.partitions_for_topic = MagicMock(return_value=set())
    mock_consumer_cls.return_value = cons

    out = asyncio.run(poll_consumer_lag("localhost:9092", "g", ["missing"]))
    assert out == []
