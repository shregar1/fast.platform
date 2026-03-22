"""Tests for ICE server helpers."""

from config.dto_extras import (
    RealtimeConfigurationDTO,
    WebRtcIceConfigDTO,
    WebRtcIceServerDTO,
)

from webrtc.dto import WebRTCConfigurationDTO
from webrtc.ice_config import ice_servers_from_legacy_webrtc_dto, rtc_ice_servers_for_client


def test_rtc_ice_servers_empty_when_disabled():
    cfg = RealtimeConfigurationDTO()
    assert rtc_ice_servers_for_client(cfg) == []


def test_rtc_ice_servers_when_enabled():
    cfg = RealtimeConfigurationDTO(
        webrtc=WebRtcIceConfigDTO(
            enabled=True,
            ice_servers=[
                WebRtcIceServerDTO(urls="stun:stun.l.google.com:19302"),
                WebRtcIceServerDTO(
                    urls=["turn:turn.example.com:3478"],
                    username="u",
                    credential="p",
                ),
            ],
        )
    )
    out = rtc_ice_servers_for_client(cfg)
    assert out[0] == {"urls": "stun:stun.l.google.com:19302"}
    assert out[1]["urls"] == ["turn:turn.example.com:3478"]
    assert out[1]["username"] == "u"
    assert out[1]["credential"] == "p"


def test_legacy_flat_urls():
    dto = WebRTCConfigurationDTO(
        stun_servers=["stun:a:1"],
        turn_servers=["turn:b:2"],
    )
    assert ice_servers_from_legacy_webrtc_dto(dto) == [
        {"urls": "stun:a:1"},
        {"urls": "turn:b:2"},
    ]
