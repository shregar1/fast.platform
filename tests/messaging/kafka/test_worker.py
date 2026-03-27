"""Tests for Kafka worker."""

from unittest.mock import AsyncMock, MagicMock, patch

from tests.messaging.kafka.abstraction import IKafkaTests


class TestWorker(IKafkaTests):
    """Represents the TestWorker class."""

    @patch("fast_platform.messaging.kafka.worker.KafkaConsumer")
    def test_worker_run(self, mock_consumer_cls):
        """Execute test_worker_run operation.

        Args:
            mock_consumer_cls: The mock_consumer_cls parameter.

        Returns:
            The result of the operation.
        """
        from messaging.kafka.worker import run

        mock_consumer = MagicMock()
        mock_consumer.start = AsyncMock(return_value=None)
        mock_consumer.stop = AsyncMock(return_value=None)
        mock_consumer.loop = AsyncMock(return_value=None)
        mock_consumer_cls.return_value = mock_consumer
        run()
        mock_consumer.start.assert_called_once()
        mock_consumer.stop.assert_called_once()
