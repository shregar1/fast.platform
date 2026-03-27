"""Queues / messaging configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .nats_config import NATSConfigDTO
from .rabbit_mq_config import RabbitMQConfigDTO
from .service_bus_config import ServiceBusConfigDTO
from .sqs_config import SQSConfigDTO


class QueuesConfigurationDTO(IDTO):
    """Represents the QueuesConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    rabbitmq: RabbitMQConfigDTO = Field(default_factory=RabbitMQConfigDTO)
    sqs: SQSConfigDTO = Field(default_factory=SQSConfigDTO)
    nats: NATSConfigDTO = Field(default_factory=NATSConfigDTO)
    service_bus: ServiceBusConfigDTO = Field(default_factory=ServiceBusConfigDTO)
