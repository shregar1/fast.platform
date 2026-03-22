"""Tests for channels config loader."""

import json
from unittest.mock import mock_open, patch


def test_channels_config_dto():
    from fast_channels.dto import ChannelsConfigurationDTO
    d = ChannelsConfigurationDTO()
    assert d.backend == "none"
    assert d.topics == []


def test_channels_config_load():
    from fast_channels.config_loader import ChannelsConfiguration
    ChannelsConfiguration._instance = None
    data = {"backend": "redis", "topics": ["alerts"]}
    with patch("fast_channels.config_loader.open", mock_open(read_data=json.dumps(data))):
        with patch("fast_channels.config_loader.os.getenv", return_value=None):
            cfg = ChannelsConfiguration()
    dto = cfg.get_config()
    assert dto.backend == "redis"
    assert dto.topics == ["alerts"]


def test_channels_config_file_not_found():
    from fast_channels.config_loader import ChannelsConfiguration
    ChannelsConfiguration._instance = None
    with patch("fast_channels.config_loader.open", side_effect=FileNotFoundError()):
        with patch("fast_channels.config_loader.os.getenv", return_value=None):
            cfg = ChannelsConfiguration()
    dto = cfg.get_config()
    assert dto.backend == "none"
    assert dto.topics == []
