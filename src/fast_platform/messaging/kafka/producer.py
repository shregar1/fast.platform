from __future__ import annotations
"""Kafka producer integration using aiokafka."""

from ...core.constants import DEFAULT_TIMEOUT_SECONDS, DEFAULT_ENCODING

from typing import Any, Optional, Union

from aiokafka import AIOKafkaProducer  # pyright: ignore[reportMissingTypeStubs]
from loguru import logger

from ...core.configuration.kafka import KafkaConfiguration
from ...core.dtos.kafka import KafkaJsonEnvelope

from .dlq import make_dlq_headers


class KafkaProducer:
    """High-level Kafka producer wrapper."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        cfg = KafkaConfiguration().get_config()
        self._cfg = cfg
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Execute start operation.

        Returns:
            The result of the operation.
        """
        if not self._cfg.enabled:
            logger.info("Kafka producer not started (disabled in config).")
            return
        self._producer = AIOKafkaProducer(bootstrap_servers=self._cfg.bootstrap_servers)
        await self._producer.start()
        logger.info("Kafka producer started.")

    async def stop(self) -> None:
        """Execute stop operation.

        Returns:
            The result of the operation.
        """
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped.")

    async def send(self, topic: str, value: Any) -> None:
        """Execute send operation.

        Args:
            topic: The topic parameter.
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        if not self._producer:
            logger.warning("Kafka producer is not running; message dropped.")
            return
        await self._producer.send_and_wait(topic, str(value).encode(DEFAULT_ENCODING))

    async def send_bytes(
        self,
        topic: str,
        value: bytes,
        *,
        key: Optional[bytes] = None,
        headers: Optional[list[tuple[str, bytes]]] = None,
    ) -> None:
        """Publish raw bytes with optional key and Kafka headers (e.g. DLQ metadata)."""
        if not self._producer:
            logger.warning("Kafka producer is not running; message dropped.")
            return
        await self._producer.send_and_wait(topic, value, key=key, headers=headers)

    async def send_json_envelope(
        self, topic: str, envelope: Union[KafkaJsonEnvelope, dict[str, Any]]
    ) -> None:
        """Publish a :class:`~fast_kafka.dto.KafkaJsonEnvelope` (or dict) as UTF-8 JSON bytes."""
        if not self._producer:
            logger.warning("Kafka producer is not running; message dropped.")
            return
        if isinstance(envelope, dict):
            payload = KafkaJsonEnvelope.model_validate(envelope)
        else:
            payload = envelope
        await self._producer.send_and_wait(topic, payload.to_json_bytes())

    async def send_json_envelope_to_dlq(
        self,
        envelope: Union[KafkaJsonEnvelope, dict[str, Any]],
        *,
        original_topic: str,
        error: str,
        dlq_topic: Optional[str] = None,
        partition: Optional[int] = None,
        offset: Optional[int] = None,
        extra_headers: Optional[list[tuple[str, bytes]]] = None,
    ) -> None:
        """Publish a JSON envelope to the configured (or explicit) DLQ topic with
        :func:`~fast_kafka.dlq.make_dlq_headers` for routing metadata.
        """
        if isinstance(envelope, dict):
            payload = KafkaJsonEnvelope.model_validate(envelope)
        else:
            payload = envelope
        body = payload.to_json_bytes()
        headers = make_dlq_headers(
            original_topic=original_topic,
            error=error,
            partition=partition,
            offset=offset,
            extra=extra_headers,
        )
        t = dlq_topic if dlq_topic is not None else getattr(self._cfg, "dlq_topic", None)
        if not isinstance(t, str) or not t.strip():
            raise ValueError("dlq_topic not set in Kafka config and not passed explicitly")
        await self.send_bytes(t.strip(), body, headers=headers)
