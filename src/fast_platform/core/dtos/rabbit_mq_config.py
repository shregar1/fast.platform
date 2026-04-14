"""RabbitMQ queue backend subsection."""

from __future__ import annotations

from ..constants import DEFAULT_HOST
from pydantic import ConfigDict

from .abstraction import IDTO


class RabbitMQConfigDTO(IDTO):
    """Represents the RabbitMQConfigDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    exchange: str = ""
    default_routing_key: str = ""
