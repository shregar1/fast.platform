from __future__ import annotations
"""Queue / messaging abstraction layer.

Provides a minimal interface over RabbitMQ, Amazon SQS, and NATS.
Concrete integrations use optional third-party libraries; if they are
not installed, calls will log warnings instead of crashing.
"""

from .constants import RABBITMQ_BACKEND, KAFKA_BACKEND, SQS_BACKEND, NATS_BACKEND

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fast_platform import QueuesConfiguration
from ...core.utils.optional_imports import OptionalImports

from .abstraction import IQueue

try:
    from loguru import logger
except Exception:  # pragma: no cover - optional
    logger = None  # type: ignore[assignment]

boto3, _ = OptionalImports.optional_import("boto3")
pika, _ = OptionalImports.optional_import("pika")
nats, _ = OptionalImports.optional_import(NATS_BACKEND)
_sb_mod, ServiceBusClient = OptionalImports.optional_import("azure.servicebus", "ServiceBusClient")


@dataclass
class QueueMessage:
    """Represents the QueueMessage class."""

    body: bytes
    attributes: Dict[str, Any] | None = None


class IQueueBackend(IQueue, ABC):
    """Minimal interface for queue backends."""

    name: str

    @abstractmethod
    async def publish(
        self, message: QueueMessage, *, routing_key: Optional[str] = None
    ) -> None:  # pragma: no cover - interface
        """Execute publish operation.

        Args:
            message: The message parameter.
            routing_key: The routing_key parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError


class RabbitMQBackend(IQueueBackend):
    """Represents the RabbitMQBackend class."""

    def __init__(self, url: str, exchange: str, default_routing_key: str) -> None:
        """Execute __init__ operation.

        Args:
            url: The url parameter.
            exchange: The exchange parameter.
            default_routing_key: The default_routing_key parameter.
        """
        self.name = RABBITMQ_BACKEND
        self._url = url
        self._exchange = exchange
        self._default_routing_key = default_routing_key

    async def publish(self, message: QueueMessage, *, routing_key: Optional[str] = None) -> None:
        """Execute publish operation.

        Args:
            message: The message parameter.
            routing_key: The routing_key parameter.

        Returns:
            The result of the operation.
        """
        if pika is None:  # pragma: no cover - optional
            if logger:
                logger.warning("pika is not installed; RabbitMQ publish skipped.")
            return

        routing_key = routing_key or self._default_routing_key

        def _publish_sync() -> None:
            """Execute _publish_sync operation.

            Returns:
                The result of the operation.
            """
            params = pika.URLParameters(self._url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.exchange_declare(exchange=self._exchange, exchange_type="topic", durable=True)
            channel.basic_publish(
                exchange=self._exchange,
                routing_key=routing_key,
                body=message.body,
            )
            connection.close()

        await asyncio.to_thread(_publish_sync)


class SQSBackend(IQueueBackend):
    """Represents the SQSBackend class."""

    def __init__(
        self,
        region: str,
        queue_url: str,
        access_key_id: Optional[str],
        secret_access_key: Optional[str],
    ) -> None:
        """Execute __init__ operation.

        Args:
            region: The region parameter.
            queue_url: The queue_url parameter.
            access_key_id: The access_key_id parameter.
            secret_access_key: The secret_access_key parameter.
        """
        self.name = SQS_BACKEND
        self._region = region
        self._queue_url = queue_url
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key

    async def publish(
        self, message: QueueMessage, *, routing_key: Optional[str] = None
    ) -> None:  # routing_key unused
        """Execute publish operation.

        Args:
            message: The message parameter.
            routing_key: The routing_key parameter.

        Returns:
            The result of the operation.
        """
        if boto3 is None:  # pragma: no cover - optional
            if logger:
                logger.warning("boto3 is not installed; SQS publish skipped.")
            return

        def _send_sync() -> None:
            """Execute _send_sync operation.

            Returns:
                The result of the operation.
            """
            session_kwargs: Dict[str, Any] = {}
            if self._access_key_id and self._secret_access_key:
                session_kwargs.update(
                    aws_access_key_id=self._access_key_id,
                    aws_secret_access_key=self._secret_access_key,
                )
            sqs = boto3.client(SQS_BACKEND, region_name=self._region, **session_kwargs)
            sqs.send_message(
                QueueUrl=self._queue_url,
                MessageBody=message.body.decode("utf-8"),
                MessageAttributes={
                    k: {"StringValue": str(v), "DataType": "String"}
                    for k, v in (message.attributes or {}).items()
                },
            )

        await asyncio.to_thread(_send_sync)


class NATSBackend(IQueueBackend):
    """Represents the NATSBackend class."""

    def __init__(self, servers: list[str], subject: str) -> None:
        """Execute __init__ operation.

        Args:
            servers: The servers parameter.
            subject: The subject parameter.
        """
        self.name = NATS_BACKEND
        self._servers = servers
        self._subject = subject

    async def publish(self, message: QueueMessage, *, routing_key: Optional[str] = None) -> None:
        """Execute publish operation.

        Args:
            message: The message parameter.
            routing_key: The routing_key parameter.

        Returns:
            The result of the operation.
        """
        if nats is None:  # pragma: no cover - optional
            if logger:
                logger.warning("nats-py is not installed; NATS publish skipped.")
            return

        servers = ",".join(self._servers)
        nc = await nats.connect(servers=servers)
        await nc.publish(self._subject, message.body)
        await nc.drain()


class AzureServiceBusBackend(IQueueBackend):
    """Represents the AzureServiceBusBackend class."""

    def __init__(self, connection_string: str, queue_name: str) -> None:
        """Execute __init__ operation.

        Args:
            connection_string: The connection_string parameter.
            queue_name: The queue_name parameter.
        """
        if ServiceBusClient is None:  # pragma: no cover - optional
            raise RuntimeError("azure-servicebus is not installed")
        self.name = "service_bus"
        self._connection_string = connection_string
        self._queue_name = queue_name

    async def publish(self, message: QueueMessage, *, routing_key: Optional[str] = None) -> None:
        """Execute publish operation.

        Args:
            message: The message parameter.
            routing_key: The routing_key parameter.

        Returns:
            The result of the operation.
        """
        if ServiceBusClient is None:  # pragma: no cover - optional
            if logger:
                logger.warning("azure-servicebus is not installed; Service Bus publish skipped.")
            return

        def _send_sync() -> None:
            """Execute _send_sync operation.

            Returns:
                The result of the operation.
            """
            with ServiceBusClient.from_connection_string(self._connection_string) as client:
                sender = client.get_queue_sender(queue_name=self._queue_name)
                with sender:
                    from azure.servicebus import ServiceBusMessage  # type: ignore[import]

                    sb_message = ServiceBusMessage(
                        message.body.decode("utf-8"),
                        application_properties=message.attributes or {},
                    )
                    sender.send_messages(sb_message)

        await asyncio.to_thread(_send_sync)


class QueueBroker:
    """High-level facade over multiple queue backends.

    It instantiates enabled backends from fast_platform.core.configuration and lets callers
    publish messages by backend name.
    """

    def __init__(self) -> None:
        """Execute __init__ operation."""
        cfg = QueuesConfiguration().get_config()
        self._backends: Dict[str, IQueueBackend] = {}

        if cfg.rabbitmq.enabled and cfg.rabbitmq.url:
            self._backends[RABBITMQ_BACKEND] = RabbitMQBackend(
                url=cfg.rabbitmq.url,
                exchange=cfg.rabbitmq.exchange,
                default_routing_key=cfg.rabbitmq.default_routing_key,
            )

        if cfg.sqs.enabled and cfg.sqs.queue_url:
            self._backends[SQS_BACKEND] = SQSBackend(
                region=cfg.sqs.region,
                queue_url=cfg.sqs.queue_url,
                access_key_id=cfg.sqs.access_key_id,
                secret_access_key=cfg.sqs.secret_access_key,
            )

        if cfg.nats.enabled and cfg.nats.servers:
            self._backends[NATS_BACKEND] = NATSBackend(
                servers=cfg.nats.servers,
                subject=cfg.nats.subject,
            )

        if (
            cfg.service_bus.enabled
            and cfg.service_bus.connection_string
            and cfg.service_bus.queue_name
        ):
            self._backends["service_bus"] = AzureServiceBusBackend(
                connection_string=cfg.service_bus.connection_string,
                queue_name=cfg.service_bus.queue_name,
            )

        if not self._backends and logger:
            logger.info(
                "No queue backends are enabled. "
                "Configure config/queues/config.json to enable RabbitMQ/SQS/NATS.",
            )

    async def publish(
        self,
        backend: str,
        body: bytes | str,
        *,
        routing_key: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Execute publish operation.

        Args:
            backend: The backend parameter.
            body: The body parameter.
            routing_key: The routing_key parameter.
            attributes: The attributes parameter.

        Returns:
            The result of the operation.
        """
        if isinstance(body, str):
            body_bytes = body.encode("utf-8")
        else:
            body_bytes = body

        backend_instance = self._backends.get(backend)
        if not backend_instance:
            if logger:
                logger.warning("Queue backend %s is not configured/enabled.", backend)
            return

        await backend_instance.publish(
            QueueMessage(body=body_bytes, attributes=attributes),
            routing_key=routing_key,
        )


__all__ = [
    "QueueMessage",
    "IQueueBackend",
    "QueueBroker",
]
