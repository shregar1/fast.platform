"""Cloud event bus and notification abstractions.

Provides:
- INotificationBus for user/system notifications (SNS)
- IEventBus for high-volume event streams (EventBridge, Event Hubs, Kafka)
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from asyncio import to_thread
from typing import Any, Dict, Optional

from loguru import logger

from fast_platform import EventsConfiguration
from ...core.utils.optional_imports import OptionalImports

from .abstraction import IEvents

_boto3, _ = OptionalImports.optional_import("boto3")
_eventhub_mod, EventHubProducerClient = OptionalImports.optional_import(
    "azure.eventhub", "EventHubProducerClient"
)
_eventhub_data_mod, EventData = OptionalImports.optional_import("azure.eventhub", "EventData")

try:
    from fast_platform.messaging.kafka import KafkaProducer
except Exception:  # pragma: no cover - optional
    KafkaProducer = None  # type: ignore[assignment]


class INotificationBus(IEvents, ABC):
    """Represents the INotificationBus class."""

    @abstractmethod
    async def publish(
        self, subject: str, payload: Dict[str, Any]
    ) -> None:  # pragma: no cover - interface
        """Execute publish operation.

        Args:
            subject: The subject parameter.
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError


class IEventBus(IEvents, ABC):
    """Represents the IEventBus class."""

    @abstractmethod
    async def publish(
        self, channel: str, payload: Dict[str, Any]
    ) -> None:  # pragma: no cover - interface
        """Execute publish operation.

        Args:
            channel: The channel parameter.
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError


class SnsNotificationBus(INotificationBus):
    """Represents the SnsNotificationBus class."""

    def __init__(
        self,
        region: str,
        topic_arn: str,
        access_key_id: Optional[str],
        secret_access_key: Optional[str],
    ) -> None:
        """Execute __init__ operation.

        Args:
            region: The region parameter.
            topic_arn: The topic_arn parameter.
            access_key_id: The access_key_id parameter.
            secret_access_key: The secret_access_key parameter.
        """
        if _boto3 is None:  # pragma: no cover - optional
            raise RuntimeError("boto3 is not installed")
        session_kwargs: Dict[str, Any] = {}
        if access_key_id and secret_access_key:
            session_kwargs.update(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
            )
        self._client = _boto3.client("sns", region_name=region, **session_kwargs)  # type: ignore[operator]
        self._topic_arn = topic_arn

    async def publish(self, subject: str, payload: Dict[str, Any]) -> None:
        """Execute publish operation.

        Args:
            subject: The subject parameter.
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        if _boto3 is None:  # pragma: no cover - optional
            logger.warning("boto3 is not installed; SNS publish skipped.")
            return

        def _send_sync() -> None:
            """Execute _send_sync operation.

            Returns:
                The result of the operation.
            """
            self._client.publish(
                TopicArn=self._topic_arn,
                Subject=subject,
                Message=json.dumps(payload),
            )

        await to_thread(_send_sync)


class EventBridgeEventBus(IEventBus):
    """Represents the EventBridgeEventBus class."""

    def __init__(
        self,
        region: str,
        bus_name: str,
        source: str,
        detail_type: str,
        access_key_id: Optional[str],
        secret_access_key: Optional[str],
    ) -> None:
        """Execute __init__ operation.

        Args:
            region: The region parameter.
            bus_name: The bus_name parameter.
            source: The source parameter.
            detail_type: The detail_type parameter.
            access_key_id: The access_key_id parameter.
            secret_access_key: The secret_access_key parameter.
        """
        if _boto3 is None:  # pragma: no cover - optional
            raise RuntimeError("boto3 is not installed")
        session_kwargs: Dict[str, Any] = {}
        if access_key_id and secret_access_key:
            session_kwargs.update(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
            )
        self._client = _boto3.client("events", region_name=region, **session_kwargs)  # type: ignore[operator]
        self._bus_name = bus_name
        self._source = source
        self._detail_type = detail_type

    async def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Execute publish operation.

        Args:
            channel: The channel parameter.
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        if _boto3 is None:  # pragma: no cover - optional
            logger.warning("boto3 is not installed; EventBridge publish skipped.")
            return

        entry = {
            "Source": self._source,
            "DetailType": self._detail_type,
            "Detail": json.dumps({"channel": channel, "payload": payload}),
            "EventBusName": self._bus_name,
        }

        def _send_sync() -> None:
            """Execute _send_sync operation.

            Returns:
                The result of the operation.
            """
            self._client.put_events(Entries=[entry])

        await to_thread(_send_sync)


class EventHubsEventBus(IEventBus):
    """Represents the EventHubsEventBus class."""

    def __init__(self, connection_string: str, event_hub_name: str) -> None:
        """Execute __init__ operation.

        Args:
            connection_string: The connection_string parameter.
            event_hub_name: The event_hub_name parameter.
        """
        if EventHubProducerClient is None or EventData is None:  # pragma: no cover - optional
            raise RuntimeError("azure-eventhub is not installed")
        self._client = EventHubProducerClient.from_connection_string(
            conn_str=connection_string,
            eventhub_name=event_hub_name,
        )

    async def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Execute publish operation.

        Args:
            channel: The channel parameter.
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        if EventHubProducerClient is None or EventData is None:  # pragma: no cover - optional
            logger.warning("azure-eventhub is not installed; Event Hubs publish skipped.")
            return

        body = json.dumps({"channel": channel, "payload": payload})

        def _send_sync() -> None:
            """Execute _send_sync operation.

            Returns:
                The result of the operation.
            """
            with self._client:
                event_data_batch = self._client.create_batch()
                event_data_batch.add(EventData(body))  # type: ignore[call-arg]
                self._client.send_batch(event_data_batch)

        await to_thread(_send_sync)


class KafkaEventBus(IEventBus):
    """Represents the KafkaEventBus class."""

    def __init__(self, topic: str) -> None:
        """Execute __init__ operation.

        Args:
            topic: The topic parameter.
        """
        if KafkaProducer is None:  # pragma: no cover - optional
            raise RuntimeError("KafkaProducer wrapper is not available")
        self._topic = topic
        self._producer = KafkaProducer()

    async def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Execute publish operation.

        Args:
            channel: The channel parameter.
            payload: The payload parameter.

        Returns:
            The result of the operation.
        """
        if KafkaProducer is None:  # pragma: no cover - optional
            logger.warning("KafkaProducer wrapper is not available; Kafka publish skipped.")
            return
        body = {"channel": channel, "payload": payload}
        await self._producer.send(self._topic, json.dumps(body))


def build_notification_bus() -> Optional[INotificationBus]:
    """Execute build_notification_bus operation.

    Returns:
        The result of the operation.
    """
    cfg = EventsConfiguration.instance().get_config()
    if cfg.sns.enabled and cfg.sns.topic_arn:
        try:
            return SnsNotificationBus(
                region=cfg.sns.region,
                topic_arn=cfg.sns.topic_arn,
                access_key_id=cfg.sns.access_key_id,
                secret_access_key=cfg.sns.secret_access_key,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize SNS notification bus: %s", exc)
    logger.info("No notification bus is enabled.")
    return None


def build_event_bus() -> Optional[IEventBus]:
    """Build a primary event bus for high-volume events.

    Priority:
      - Azure Event Hubs
      - Kafka bridge
      - AWS EventBridge
    """
    cfg = EventsConfiguration.instance().get_config()

    if (
        cfg.event_hubs.enabled
        and cfg.event_hubs.connection_string
        and cfg.event_hubs.event_hub_name
    ):
        try:
            return EventHubsEventBus(
                connection_string=cfg.event_hubs.connection_string,
                event_hub_name=cfg.event_hubs.event_hub_name,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Event Hubs event bus: %s", exc)

    if cfg.kafka.enabled and cfg.kafka.topic:
        try:
            return KafkaEventBus(topic=cfg.kafka.topic)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Kafka event bus: %s", exc)

    if cfg.event_bridge.enabled:
        try:
            return EventBridgeEventBus(
                region=cfg.event_bridge.region,
                bus_name=cfg.event_bridge.bus_name,
                source=cfg.event_bridge.source,
                detail_type=cfg.event_bridge.detail_type,
                access_key_id=cfg.event_bridge.access_key_id,
                secret_access_key=cfg.event_bridge.secret_access_key,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize EventBridge event bus: %s", exc)

    logger.info("No event bus is enabled.")
    return None


__all__ = [
    "INotificationBus",
    "IEventBus",
    "SnsNotificationBus",
    "EventBridgeEventBus",
    "EventHubsEventBus",
    "KafkaEventBus",
    "build_notification_bus",
    "build_event_bus",
]
