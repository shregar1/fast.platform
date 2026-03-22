"""Azure Service Bus queue backend subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class ServiceBusConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_string: str = ""
    queue_name: str = ""
