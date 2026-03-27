"""fast_webrtc – WebRTC signaling extension for FastMVC."""

from __future__ import annotations

from .config_loader import WebRTCConfiguration
from .consent import (
    AllowAllMediaConsent,
    BeforeMediaConsentCallback,
    StaticDeniedPeers,
)
from .dto import WebRTCConfigurationDTO
from .ice_config import ice_servers_from_legacy_webrtc_dto, rtc_ice_servers_for_client
from .rooms import InMemoryRoomRegistry, Participant, Room
from .signaling import SessionExpiredCallback, WebRTCSignalingService
from .turn_twilio import fetch_twilio_turn_ice_servers, twilio_tokens_url

__version__ = "0.3.0"

__all__ = [
    "AllowAllMediaConsent",
    "BeforeMediaConsentCallback",
    "InMemoryRoomRegistry",
    "Participant",
    "Room",
    "SessionExpiredCallback",
    "StaticDeniedPeers",
    "WebRTCConfiguration",
    "WebRTCConfigurationDTO",
    "WebRTCSignalingService",
    "__version__",
    "fetch_twilio_turn_ice_servers",
    "ice_servers_from_legacy_webrtc_dto",
    "rtc_ice_servers_for_client",
    "twilio_tokens_url",
]
