"""Tests for Kafka worker."""

from unittest.mock import AsyncMock, patch, MagicMock


@patch("fast_kafka.worker.KafkaConsumer")
def test_worker_run(mock_consumer_cls):
    from fast_kafka.worker import run
    mock_consumer = MagicMock()
    mock_consumer.start = AsyncMock(return_value=None)
    mock_consumer.stop = AsyncMock(return_value=None)
    mock_consumer.loop = AsyncMock(return_value=None)
    mock_consumer_cls.return_value = mock_consumer
    run()
    mock_consumer.start.assert_called_once()
    mock_consumer.stop.assert_called_once()
