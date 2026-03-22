"""Azure Service Bus queue backend subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class ServiceBusConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_string: str = ""
    queue_name: str = ""
