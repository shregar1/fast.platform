"""Tests for outbox publisher helpers."""

import asyncio
from unittest.mock import AsyncMock, MagicMock


def test_publish_outbox_batch():
    from kafka.outbox import OutboxMessage, publish_outbox_batch

    marks: list[int] = []
    producer = MagicMock()
    producer.send_bytes = AsyncMock()

    async def mark(i: int) -> None:
        marks.append(i)

    async def run():
        batch = [
            OutboxMessage(id=1, topic="t", value=b"a"),
            OutboxMessage(id=2, topic="t", value=b"b", headers=[("h", b"v")]),
        ]
        await publish_outbox_batch(producer, batch, mark)

    asyncio.run(run())

    assert producer.send_bytes.await_count == 2
    assert marks == [1, 2]


def test_postgres_outbox_ddl_is_non_empty():
    from kafka.outbox import POSTGRES_OUTBOX_DDL

    assert "kafka_outbox" in POSTGRES_OUTBOX_DDL
    assert "CREATE TABLE" in POSTGRES_OUTBOX_DDL


def test_run_outbox_publisher_loop_stops_when_event_set():
    from kafka.outbox import run_outbox_publisher_loop

    stop = asyncio.Event()
    stop.set()
    load = AsyncMock()
    mark = AsyncMock()
    producer = MagicMock()

    asyncio.run(
        run_outbox_publisher_loop(
            producer,
            load,
            mark,
            interval_seconds=0.01,
            stop_event=stop,
        )
    )
    load.assert_not_called()


def test_run_outbox_publisher_loop_processes_one_batch():
    from kafka.outbox import OutboxMessage, run_outbox_publisher_loop

    stop = asyncio.Event()
    seen: list[int] = []

    async def load(limit):
        if not seen:
            seen.append(1)
            return [OutboxMessage(id=1, topic="t", value=b"x")]
        return []

    async def mark_published(_id: int) -> None:
        stop.set()

    producer = MagicMock()
    producer.send_bytes = AsyncMock()

    asyncio.run(
        run_outbox_publisher_loop(
            producer,
            load,
            mark_published,
            limit=10,
            interval_seconds=0.01,
            stop_event=stop,
        )
    )
    producer.send_bytes.assert_awaited_once()
