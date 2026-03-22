"""
Kafka consumer integration using aiokafka.
"""

from __future__ import annotations

from typing import Awaitable, Callable, Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition
from loguru import logger

from .config_loader import KafkaConfiguration
from .idempotent import DedupeStore, InMemoryDedupeStore, default_dedupe_key


class KafkaConsumer:
    """High-level Kafka consumer wrapper."""

    def __init__(self) -> None:
        cfg = KafkaConfiguration().get_config()
        self._cfg = cfg
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        if not self._cfg.enabled:
            logger.info("Kafka consumer not started (disabled in config).")
            return
        self._consumer = AIOKafkaConsumer(
            *self._cfg.topics,
            bootstrap_servers=self._cfg.bootstrap_servers,
            group_id=self._cfg.group_id,
            enable_auto_commit=self._cfg.enable_auto_commit,
        )
        await self._consumer.start()
        logger.info("Kafka consumer started.")

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer stopped.")

    async def loop(self, handler: Callable[[str, bytes], Awaitable[None]]) -> None:
        if not self._consumer:
            logger.warning("Kafka consumer is not running; loop exited.")
            return
        async for msg in self._consumer:
            await handler(msg.topic, msg.value)

    async def loop_idempotent(
        self,
        handler: Callable[[str, bytes], Awaitable[None]],
        *,
        dedupe_store: Optional[DedupeStore] = None,
        dedupe_key: Optional[Callable[[bytes], str]] = None,
    ) -> None:
        """
        Consume with **manual commits** after each successful handler, and optional **dedupe**
        by key so duplicate payloads can be skipped while still advancing offsets.

        Requires ``enable_auto_commit=False`` in Kafka config (otherwise offset commits may race).

        If ``handler`` raises, the offset is not committed and the message may be redelivered.
        """
        if not self._consumer:
            logger.warning("Kafka consumer is not running; idempotent loop exited.")
            return
        if self._cfg.enable_auto_commit:
            raise ValueError(
                "loop_idempotent requires enable_auto_commit=False in Kafka configuration"
            )
        store = dedupe_store or InMemoryDedupeStore()
        key_fn = dedupe_key or default_dedupe_key

        async for msg in self._consumer:
            dkey = key_fn(msg.value)
            if await store.should_skip(dkey):
                await self._commit_offset(msg)
                continue
            await handler(msg.topic, msg.value)
            await self._commit_offset(msg)
            await store.record_success(dkey)

    async def _commit_offset(self, msg) -> None:
        assert self._consumer is not None
        tp = TopicPartition(msg.topic, msg.partition)
        await self._consumer.commit({tp: msg.offset + 1})
