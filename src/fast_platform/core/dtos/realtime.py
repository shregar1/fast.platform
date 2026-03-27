"""Realtime (WebRTC) top-level configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .webrtc_ice_config import WebRtcIceConfigDTO


class RealtimeConfigurationDTO(IDTO):
    """Represents the RealtimeConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    webrtc: WebRtcIceConfigDTO = Field(default_factory=WebRtcIceConfigDTO)
