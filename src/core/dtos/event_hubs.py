"""Azure Event Hubs subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class EventHubsDTO(IDTO):
    """Represents the EventHubsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_string: str = ""
    event_hub_name: str = ""
