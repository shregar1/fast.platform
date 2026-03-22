"""AWS EventBridge subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class EventBridgeDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    bus_name: str = ""
    source: str = ""
    detail_type: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
