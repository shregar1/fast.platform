"""Module test_config_loader_extra.py."""

import json
from unittest.mock import mock_open, patch

from tests.realtime.channels.abstraction import IChannelTests


class TestConfigLoaderExtra(IChannelTests):
    """Represents the TestConfigLoaderExtra class."""

    def test_channels_config_uses_explicit_env_path(self):
        """Execute test_channels_config_uses_explicit_env_path operation.

        Returns:
            The result of the operation.
        """
        from realtime.channels.config_loader import ChannelsConfiguration

        ChannelsConfiguration._instance = None
        payload = {"backend": "redis", "topics": ["alerts"]}
        env_path = "/tmp/channels/config.json"
        with patch(
            "fast_platform.realtime.channels.config_loader.open", mock_open(read_data=json.dumps(payload))
        ):
            with patch(
                "fast_platform.realtime.channels.config_loader.os.getenv",
                side_effect=lambda k: env_path if k == "FASTMVC_CHANNELS_CONFIG_PATH" else None,
            ):
                cfg = ChannelsConfiguration()
        dto = cfg.get_config()
        assert dto.backend == "redis"
        assert dto.topics == ["alerts"]

    def test_channels_config_json_decode_error_results_in_empty_config(self):
        """Execute test_channels_config_json_decode_error_results_in_empty_config operation.

        Returns:
            The result of the operation.
        """
        from realtime.channels.config_loader import ChannelsConfiguration

        ChannelsConfiguration._instance = None
        with patch("fast_platform.realtime.channels.config_loader.open", mock_open(read_data="not-json")):
            with patch(
                "fast_platform.realtime.channels.config_loader.json.load",
                side_effect=json.JSONDecodeError("bad", "doc", 0),
            ):
                with patch("fast_platform.realtime.channels.config_loader.os.getenv", return_value=None):
                    cfg = ChannelsConfiguration()
        dto = cfg.get_config()
        assert dto.backend == "none"
        assert dto.topics == []
