"""Tests for push configuration loader."""

import json
from unittest.mock import mock_open, patch

from tests.messaging.notifications.abstraction import INotificationTests


class TestConfigLoader(INotificationTests):
    """Represents the TestConfigLoader class."""

    def test_push_config_load_from_file(self):
        """Execute test_push_config_load_from_file operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.notifications import NotificationsConfiguration

        NotificationsConfiguration._instance = None
        data = {"apns": {"enabled": True, "key_id": "k"}, "fcm": {"enabled": False}}
        m = mock_open(read_data=json.dumps(data))
        with patch("core.configuration.notifications.open", m):
            with patch.dict("os.environ", {}, clear=False):
                cfg = NotificationsConfiguration()
        dto = cfg.get_config()
        assert dto.apns.enabled is True
        assert dto.apns.key_id == "k"

    def test_push_config_file_not_found(self):
        """Execute test_push_config_file_not_found operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.notifications import NotificationsConfiguration

        NotificationsConfiguration._instance = None
        with patch("core.configuration.notifications.open", side_effect=FileNotFoundError()):
            cfg = NotificationsConfiguration()
        dto = cfg.get_config()
        assert dto.apns.enabled is False

    def test_push_config_json_error(self):
        """Execute test_push_config_json_error operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.notifications import NotificationsConfiguration

        NotificationsConfiguration._instance = None
        with patch("core.configuration.notifications.open", mock_open(read_data="not-json")):
            with patch(
                "core.configuration.notifications.json.load",
                side_effect=json.JSONDecodeError("bad", "doc", 0),
            ):
                cfg = NotificationsConfiguration()
        dto = cfg.get_config()
        assert dto.fcm.enabled is False

    def test_push_config_env_overrides(self):
        """Execute test_push_config_env_overrides operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.notifications import NotificationsConfiguration

        NotificationsConfiguration._instance = None
        env = {
            "APNS_ENABLED": "true",
            "APNS_KEY_ID": "kid",
            "FCM_ENABLED": "1",
            "FCM_SERVER_KEY": "sk",
        }
        with patch("core.configuration.notifications.open", side_effect=FileNotFoundError()):
            with patch.dict("os.environ", env, clear=False):
                cfg = NotificationsConfiguration()
        dto = cfg.get_config()
        assert dto.apns.enabled is True
        assert dto.apns.key_id == "kid"
        assert dto.fcm.enabled is True
        assert dto.fcm.server_key == "sk"

    def test_push_config_singleton(self):
        """Execute test_push_config_singleton operation.

        Returns:
            The result of the operation.
        """
        from core.configuration.notifications import NotificationsConfiguration

        NotificationsConfiguration._instance = None
        with patch("core.configuration.notifications.open", side_effect=FileNotFoundError()):
            a = NotificationsConfiguration()
            b = NotificationsConfiguration()
        assert a is b
