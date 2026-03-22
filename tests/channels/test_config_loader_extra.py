import json
from unittest.mock import mock_open, patch


def test_channels_config_uses_explicit_env_path():
    from channels.config_loader import ChannelsConfiguration

    ChannelsConfiguration._instance = None
    payload = {"backend": "redis", "topics": ["alerts"]}
    env_path = "/tmp/channels/config.json"

    with patch("channels.config_loader.open", mock_open(read_data=json.dumps(payload))):
        with patch("channels.config_loader.os.getenv", side_effect=lambda k: env_path if k == "FASTMVC_CHANNELS_CONFIG_PATH" else None):
            cfg = ChannelsConfiguration()

    dto = cfg.get_config()
    assert dto.backend == "redis"
    assert dto.topics == ["alerts"]


def test_channels_config_json_decode_error_results_in_empty_config():
    from channels.config_loader import ChannelsConfiguration

    ChannelsConfiguration._instance = None
    with patch("channels.config_loader.open", mock_open(read_data="not-json")):
        with patch("channels.config_loader.json.load", side_effect=json.JSONDecodeError("bad", "doc", 0)):
            with patch("channels.config_loader.os.getenv", return_value=None):
                cfg = ChannelsConfiguration()

    dto = cfg.get_config()
    assert dto.backend == "none"
    assert dto.topics == []

