"""Tests for WebRTC config loader."""

import json
from unittest.mock import mock_open, patch
from fast_webrtc.dto import WebRTCConfigurationDTO


def test_webrtc_dto_defaults():
    d = WebRTCConfigurationDTO()
    assert d.enabled is False
    assert d.max_peers_per_room == 8
    assert d.stun_servers == []
    assert d.turn_servers == []


def test_webrtc_config_load():
    from fast_webrtc.config_loader import WebRTCConfiguration
    WebRTCConfiguration._instance = None
    data = {"enabled": True, "max_peers_per_room": 4, "stun_servers": ["stun:stun.l.google.com:19302"]}
    with patch("fast_webrtc.config_loader.open", mock_open(read_data=json.dumps(data))):
        with patch("fast_webrtc.config_loader.os.getenv", return_value=None):
            cfg = WebRTCConfiguration()
    dto = cfg.get_config()
    assert dto.enabled is True
    assert dto.max_peers_per_room == 4
    assert len(dto.stun_servers) == 1


def test_webrtc_config_file_not_found():
    from fast_webrtc.config_loader import WebRTCConfiguration
    WebRTCConfiguration._instance = None
    with patch("fast_webrtc.config_loader.open", side_effect=FileNotFoundError()):
        with patch("fast_webrtc.config_loader.os.getenv", return_value=None):
            cfg = WebRTCConfiguration()
    dto = cfg.get_config()
    assert dto.enabled is False
    assert dto.max_peers_per_room == 8


def test_webrtc_config_invalid_json():
    from fast_webrtc.config_loader import WebRTCConfiguration
    WebRTCConfiguration._instance = None
    with patch("fast_webrtc.config_loader.open", mock_open(read_data="{not valid json")):
        with patch("fast_webrtc.config_loader.os.getenv", return_value=None):
            cfg = WebRTCConfiguration()
    assert cfg.get_config().enabled is False
