"""Tests for OneSignal client."""

import pytest
from fast_platform.notifications.providers.onesignal import (
    DeviceType,
    OneSignalClient,
    OneSignalError,
    OneSignalNotification,
)


class TestDeviceType:
    """Test OneSignal DeviceType enum."""

    def test_device_types(self):
        """Test device type enumeration values."""
        assert DeviceType.IOS.value == 0
        assert DeviceType.ANDROID.value == 1
        assert DeviceType.AMAZON.value == 2
        assert DeviceType.WINDOWS_PHONE.value == 3
        assert DeviceType.CHROME_APP.value == 4
        assert DeviceType.CHROME_WEB.value == 5
        assert DeviceType.SAFARI.value == 7
        assert DeviceType.FIREFOX.value == 8
        assert DeviceType.MACOS.value == 9


class TestOneSignalNotification:
    """Test OneSignalNotification data class."""

    def test_notification_creation(self):
        """Test notification creation."""
        notification = OneSignalNotification(
            title="Test Title",
            message="Test Message",
            data={"key": "value"},
        )
        assert notification.title == "Test Title"
        assert notification.message == "Test Message"
        assert notification.data == {"key": "value"}
        assert notification.included_segments is None
        assert notification.include_player_ids is None

    def test_notification_with_segments(self):
        """Test notification with segments."""
        notification = OneSignalNotification(
            title="Alert",
            message="Hello",
            included_segments=["Active Users"],
        )
        assert notification.included_segments == ["Active Users"]

    def test_notification_with_player_ids(self):
        """Test notification with player ids."""
        notification = OneSignalNotification(
            title="DM",
            message="Private message",
            include_player_ids=["player-1", "player-2"],
        )
        assert notification.include_player_ids == ["player-1", "player-2"]


class TestOneSignalClient:
    """Test OneSignal client."""

    @pytest.fixture
    def client(self):
        """Create OneSignal client."""
        return OneSignalClient(
            app_id="test-app-id",
            api_key="test-api-key",
        )

    def test_client_init(self, client):
        """Test client initializes correctly."""
        assert client.app_id == "test-app-id"
        assert client.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_send_push_raises(self, client):
        """Test send_push raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="aiohttp"):
            await client.send_push(
                player_ids=["player-1"],
                title="Test",
                message="Hello",
            )

    @pytest.mark.asyncio
    async def test_send_to_segments_raises(self, client):
        """Test send_to_segments raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="aiohttp"):
            await client.send_to_segments(
                segments=["Active Users"],
                title="Test",
                message="Hello",
            )


class TestOneSignalError:
    """Test OneSignalError exception."""

    def test_error_is_exception(self):
        """Test error inherits from Exception."""
        err = OneSignalError("test error")
        assert isinstance(err, Exception)
        assert str(err) == "test error"
