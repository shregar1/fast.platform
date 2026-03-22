"""WebRTC ICE block under realtime config."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from pydantic import ConfigDict, Field

from .abstraction import IDTO

if TYPE_CHECKING:
    from .webrtc_ice_server import WebRtcIceServerDTO


class WebRtcIceConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    ice_servers: List[WebRtcIceServerDTO] = Field(default_factory=list)
