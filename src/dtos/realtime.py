"""Realtime (WebRTC) top-level configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict, Field

from .webrtc_ice_config import WebRtcIceConfigDTO


class RealtimeConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    webrtc: WebRtcIceConfigDTO = Field(default_factory=WebRtcIceConfigDTO)
