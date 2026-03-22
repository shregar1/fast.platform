"""RabbitMQ queue backend subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class RabbitMQConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    exchange: str = ""
    default_routing_key: str = ""
