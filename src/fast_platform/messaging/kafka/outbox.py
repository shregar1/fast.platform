from __future__ import annotations
"""Transactional outbox: portable DDL + publisher loop helpers (no ORM required).

Pair with your DB transaction: insert into ``kafka_outbox`` in the same transaction
as business writes, then run :func:`run_outbox_publisher_loop` in a worker process.
"""

from ...core.constants import DEFAULT_LIMIT

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable, Optional, Sequence

from loguru import logger

if TYPE_CHECKING:
    from .producer import KafkaProducer

# PostgreSQL — copy into a migration or run once in dev.
POSTGRES_OUTBOX_DDL = """
CREATE TABLE IF NOT EXISTS kafka_outbox (
  id BIGSERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  payload JSONB NOT NULL,
  payload_format TEXT NOT NULL DEFAULT 'json',
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  attempts INT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_kafka_outbox_pending ON kafka_outbox (status, id)
  WHERE status = 'pending';
"""


@dataclass
class OutboxMessage:
    """One row ready to publish to Kafka."""

    id: int
    topic: str
    value: bytes
    key: Optional[bytes] = None
    headers: Optional[list[tuple[str, bytes]]] = None


async def publish_outbox_batch(
    producer: KafkaProducer,
    messages: Sequence[OutboxMessage],
    mark_published: Callable[[int], Awaitable[None]],
) -> None:
    """Send each message with :meth:`~fast_kafka.producer.KafkaProducer.send_bytes`,
    then call ``mark_published(id)`` for that row. Stops on first send failure
    so the row stays pending for retry.
    """
    for m in messages:
        await producer.send_bytes(m.topic, m.value, key=m.key, headers=m.headers)
        await mark_published(m.id)


async def run_outbox_publisher_loop(
    producer: KafkaProducer,
    load_pending: Callable[[int], Awaitable[list[OutboxMessage]]],
    mark_published: Callable[[int], Awaitable[None]],
    *,
    limit: int = DEFAULT_LIMIT,
    interval_seconds: float = 1.0,
    stop_event: Optional[asyncio.Event] = None,
) -> None:
    """Poll ``load_pending(limit)`` and publish until *stop_event* is set (or cancel the task).

    * *load_pending* — e.g. ``SELECT ... FOR UPDATE SKIP LOCKED`` in your DB layer.
    * *mark_published* — e.g. ``UPDATE kafka_outbox SET status='sent' WHERE id=:id``.
    """
    evt = stop_event if stop_event is not None else asyncio.Event()

    while not evt.is_set():
        try:
            await asyncio.wait_for(evt.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass
        if evt.is_set():
            break
        batch = await load_pending(limit)
        if not batch:
            continue
        try:
            await publish_outbox_batch(producer, batch, mark_published)
        except Exception as exc:
            logger.warning("Outbox batch publish failed: {}", exc)
