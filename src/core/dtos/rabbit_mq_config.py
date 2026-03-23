"""RabbitMQ queue backend subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class RabbitMQConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    exchange: str = ""
    default_routing_key: str = ""
