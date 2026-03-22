"""Azure Event Hubs subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class EventHubsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_string: str = ""
    event_hub_name: str = ""
