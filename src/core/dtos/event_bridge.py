"""AWS EventBridge subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class EventBridgeDTO(IDTO):
    """Represents the EventBridgeDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    bus_name: str = ""
    source: str = ""
    detail_type: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
