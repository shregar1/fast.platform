from __future__ import annotations
"""Consumer group lag via Admin API + end offsets (``aiokafka``)."""

from ...core.constants import DEFAULT_HOST

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Sequence

from aiokafka import AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient
from loguru import logger

if TYPE_CHECKING:
    from aiokafka.structs import OffsetAndMetadata, TopicPartition


@dataclass
class ConsumerLagEntry:
    """Per-partition lag snapshot for a consumer group."""

    topic: str
    partition: int
    committed_offset: Optional[int]
    end_offset: int
    lag: int


def _compute_lag(end_offset: int, committed: Optional[int]) -> int:
    """Lag = high-water ``end_offset`` minus next committed offset (Kafka offset space)."""
    if committed is None or committed < 0:
        return end_offset
    return max(0, end_offset - committed)


async def poll_consumer_lag(
    bootstrap_servers: str,
    group_id: str,
    topics: Sequence[str],
    *,
    request_timeout_ms: int = 10_000,
    client_id: str = "fastmvc-consumer-lag",
) -> list[ConsumerLagEntry]:
    """Return approximate lag per partition for *group_id* on the given *topics*.

    Uses :class:`AIOKafkaConsumer` to resolve partitions and end offsets, and
    :class:`AIOKafkaAdminClient` for ``list_consumer_group_offsets``. Requires
    network access to the cluster (suitable for metrics / health dashboards).
    """
    consumer = AIOKafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        client_id=client_id,
        request_timeout_ms=request_timeout_ms,
    )
    await consumer.start()
    try:
        tps: list[TopicPartition] = []
        for t in topics:
            part = consumer.partitions_for_topic(t)
            if part:
                tps.extend(sorted(part, key=lambda x: x.partition))
        if not tps:
            logger.debug("No partitions found for topics {}", list(topics))
            return []

        admin = AIOKafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            request_timeout_ms=request_timeout_ms,
        )
        await admin.start()
        try:
            committed_map: dict[
                TopicPartition, OffsetAndMetadata
            ] = await admin.list_consumer_group_offsets(
                group_id,
                partitions=tps,
            )
        finally:
            await admin.close()

        end_map = await consumer.end_offsets(set(tps))

        out: list[ConsumerLagEntry] = []
        for tp in tps:
            om = committed_map.get(tp)
            committed: Optional[int] = om.offset if om is not None else None
            end_off = int(end_map[tp])
            lag = _compute_lag(end_off, committed)
            out.append(
                ConsumerLagEntry(
                    topic=tp.topic,
                    partition=tp.partition,
                    committed_offset=committed,
                    end_offset=end_off,
                    lag=lag,
                )
            )
        return out
    finally:
        await consumer.stop()
