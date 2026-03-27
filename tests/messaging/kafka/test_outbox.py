"""Tests for outbox publisher helpers."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from tests.messaging.kafka.abstraction import IKafkaTests


class TestOutbox(IKafkaTests):
    """Represents the TestOutbox class."""

    def test_publish_outbox_batch(self):
        """Execute test_publish_outbox_batch operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.kafka.outbox import OutboxMessage, publish_outbox_batch

        marks: list[int] = []
        producer = MagicMock()
        producer.send_bytes = AsyncMock()

        async def mark(i: int) -> None:
            """Execute mark operation.

            Args:
                i: The i parameter.

            Returns:
                The result of the operation.
            """
            marks.append(i)

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            batch = [
                OutboxMessage(id=1, topic="t", value=b"a"),
                OutboxMessage(id=2, topic="t", value=b"b", headers=[("h", b"v")]),
            ]
            await publish_outbox_batch(producer, batch, mark)

        asyncio.run(run())
        assert producer.send_bytes.await_count == 2
        assert marks == [1, 2]

    def test_postgres_outbox_ddl_is_non_empty(self):
        """Execute test_postgres_outbox_ddl_is_non_empty operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.kafka.outbox import POSTGRES_OUTBOX_DDL

        assert "kafka_outbox" in POSTGRES_OUTBOX_DDL
        assert "CREATE TABLE" in POSTGRES_OUTBOX_DDL

    def test_run_outbox_publisher_loop_stops_when_event_set(self):
        """Execute test_run_outbox_publisher_loop_stops_when_event_set operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.kafka.outbox import run_outbox_publisher_loop

        stop = asyncio.Event()
        stop.set()
        load = AsyncMock()
        mark = AsyncMock()
        producer = MagicMock()
        asyncio.run(
            run_outbox_publisher_loop(producer, load, mark, interval_seconds=0.01, stop_event=stop)
        )
        load.assert_not_called()

    def test_run_outbox_publisher_loop_processes_one_batch(self):
        """Execute test_run_outbox_publisher_loop_processes_one_batch operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.kafka.outbox import OutboxMessage, run_outbox_publisher_loop

        stop = asyncio.Event()
        seen: list[int] = []

        async def load(limit):
            """Execute load operation.

            Args:
                limit: The limit parameter.

            Returns:
                The result of the operation.
            """
            if not seen:
                seen.append(1)
                return [OutboxMessage(id=1, topic="t", value=b"x")]
            return []

        async def mark_published(_id: int) -> None:
            """Execute mark_published operation.

            Args:
                _id: The _id parameter.

            Returns:
                The result of the operation.
            """
            stop.set()

        producer = MagicMock()
        producer.send_bytes = AsyncMock()
        asyncio.run(
            run_outbox_publisher_loop(
                producer, load, mark_published, limit=10, interval_seconds=0.01, stop_event=stop
            )
        )
        producer.send_bytes.assert_awaited_once()
