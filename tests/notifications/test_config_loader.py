"""Tests for push configuration loader."""

import json
from unittest.mock import mock_open, patch

def test_push_config_load_from_file():
    from fast_notifications.config_loader import PushConfiguration

    PushConfiguration._instance = None
    data = {
        "apns": {"enabled": True, "key_id": "k"},
        "fcm": {"enabled": False},
    }
    m = mock_open(read_data=json.dumps(data))
    with patch("fast_notifications.config_loader.open", m):
        with patch.dict("os.environ", {}, clear=False):
            cfg = PushConfiguration()
    dto = cfg.get_config()
    assert dto.apns.enabled is True
    assert dto.apns.key_id == "k"


def test_push_config_file_not_found():
    from fast_notifications.config_loader import PushConfiguration

    PushConfiguration._instance = None
    with patch("fast_notifications.config_loader.open", side_effect=FileNotFoundError()):
        cfg = PushConfiguration()
    dto = cfg.get_config()
    assert dto.apns.enabled is False


def test_push_config_json_error():
    from fast_notifications.config_loader import PushConfiguration

    PushConfiguration._instance = None
    with patch("fast_notifications.config_loader.open", mock_open(read_data="not-json")):
        with patch("fast_notifications.config_loader.json.load", side_effect=json.JSONDecodeError("bad", "doc", 0)):
            cfg = PushConfiguration()
    dto = cfg.get_config()
    assert dto.fcm.enabled is False


def test_push_config_env_overrides():
    from fast_notifications.config_loader import PushConfiguration

    PushConfiguration._instance = None
    env = {
        "APNS_ENABLED": "true",
        "APNS_KEY_ID": "kid",
        "FCM_ENABLED": "1",
        "FCM_SERVER_KEY": "sk",
    }
    with patch("fast_notifications.config_loader.open", side_effect=FileNotFoundError()):
        with patch.dict("os.environ", env, clear=False):
            cfg = PushConfiguration()
    dto = cfg.get_config()
    assert dto.apns.enabled is True
    assert dto.apns.key_id == "kid"
    assert dto.fcm.enabled is True
    assert dto.fcm.server_key == "sk"


def test_push_config_singleton():
    from fast_notifications.config_loader import PushConfiguration

    PushConfiguration._instance = None
    with patch("fast_notifications.config_loader.open", side_effect=FileNotFoundError()):
        a = PushConfiguration()
        b = PushConfiguration()
    assert a is b
