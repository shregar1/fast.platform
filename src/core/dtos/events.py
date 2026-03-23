"""Cloud events / bus configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .event_bridge import EventBridgeDTO
from .event_hubs import EventHubsDTO
from .kafka_event import KafkaEventDTO
from .sns_notification import SnsNotificationDTO


class EventsConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    sns: SnsNotificationDTO = Field(default_factory=SnsNotificationDTO)
    event_hubs: EventHubsDTO = Field(default_factory=EventHubsDTO)
    kafka: KafkaEventDTO = Field(default_factory=KafkaEventDTO)
    event_bridge: EventBridgeDTO = Field(default_factory=EventBridgeDTO)
