"""Tests for WebRTC config loader."""

import json
from unittest.mock import mock_open, patch

from tests.realtime.webrtc.abstraction import IWebRTCTests
from fast_platform.realtime.webrtc.dto import WebRTCConfigurationDTO


class TestConfig(IWebRTCTests):
    """Represents the TestConfig class."""

    def test_webrtc_dto_defaults(self):
        """Execute test_webrtc_dto_defaults operation.

        Returns:
            The result of the operation.
        """
        d = WebRTCConfigurationDTO()
        assert d.enabled is False
        assert d.max_peers_per_room == 8
        assert d.stun_servers == []
        assert d.turn_servers == []

    def test_webrtc_config_load(self):
        """Execute test_webrtc_config_load operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.webrtc.config_loader import WebRTCConfiguration

        WebRTCConfiguration._instance = None
        data = {
            "enabled": True,
            "max_peers_per_room": 4,
            "stun_servers": ["stun:stun.l.google.com:19302"],
        }
        with patch("fast_platform.realtime.webrtc.config_loader.open", mock_open(read_data=json.dumps(data))):
            with patch("fast_platform.realtime.webrtc.config_loader.os.getenv", return_value=None):
                cfg = WebRTCConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is True
        assert dto.max_peers_per_room == 4
        assert len(dto.stun_servers) == 1

    def test_webrtc_config_file_not_found(self):
        """Execute test_webrtc_config_file_not_found operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.webrtc.config_loader import WebRTCConfiguration

        WebRTCConfiguration._instance = None
        with patch("fast_platform.realtime.webrtc.config_loader.open", side_effect=FileNotFoundError()):
            with patch("fast_platform.realtime.webrtc.config_loader.os.getenv", return_value=None):
                cfg = WebRTCConfiguration()
        dto = cfg.get_config()
        assert dto.enabled is False
        assert dto.max_peers_per_room == 8

    def test_webrtc_config_invalid_json(self):
        """Execute test_webrtc_config_invalid_json operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.realtime.webrtc.config_loader import WebRTCConfiguration

        WebRTCConfiguration._instance = None
        with patch("fast_platform.realtime.webrtc.config_loader.open", mock_open(read_data="{not valid json")):
            with patch("fast_platform.realtime.webrtc.config_loader.os.getenv", return_value=None):
                cfg = WebRTCConfiguration()
        assert cfg.get_config().enabled is False
