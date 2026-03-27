"""Tests for OneSignal client."""

import pytest
from unittest.mock import AsyncMock, patch
from fast_platform.notifications.providers.onesignal import (
    OneSignalClient,
    OneSignalNotification,
    DeviceType,
    OneSignalError,
)


class TestOneSignalClient:
    """Test OneSignal client."""

    @pytest.fixture
    def client(self):
        """Create OneSignal client."""
        return OneSignalClient(app_id="test-app-id", rest_api_key="test-rest-api-key")

    @pytest.mark.asyncio
    async def test_send_to_all(self, client):
        """Test sending to all users."""
        mock_response = {"id": "notification-id-123", "recipients": 1000}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            notification = await client.send_to_all(
                headings={"en": "Test Title"}, contents={"en": "Test message content"}
            )

            assert notification.id == "notification-id-123"
            assert notification.recipients == 1000

    @pytest.mark.asyncio
    async def test_send_to_users(self, client):
        """Test sending to specific users."""
        mock_response = {"id": "msg-id", "recipients": 2}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            notification = await client.send_to_users(
                player_ids=["user-1", "user-2"],
                headings={"en": "Hello"},
                contents={"en": "Direct message"},
                data={"type": "welcome"},
            )

            assert notification.recipients == 2

    @pytest.mark.asyncio
    async def test_send_to_segments(self, client):
        """Test sending to segments."""
        mock_response = {"id": "segment-msg-id", "recipients": 500}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            notification = await client.send_to_segments(
                segments=["Active Users", "Subscribers"],
                headings={"en": "News"},
                contents={"en": "New update available"},
            )

            assert notification.recipients == 500

    @pytest.mark.asyncio
    async def test_send_to_tags(self, client):
        """Test sending with tag filters."""
        mock_response = {"id": "tag-msg-id", "recipients": 50}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            tags = [{"key": "role", "relation": "=", "value": "admin"}]

            notification = await client.send_to_tags(
                tags=tags,
                headings={"en": "Admin Alert"},
                contents={"en": "System maintenance scheduled"},
            )

            assert notification.recipients == 50

    @pytest.mark.asyncio
    async def test_cancel_notification(self, client):
        """Test canceling notification."""
        with patch("aiohttp.ClientSession.delete") as mock_delete:
            mock_context = AsyncMock()
            mock_context.status = 200
            mock_delete.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            result = await client.cancel_notification("notification-id-123")

            assert result is True

    @pytest.mark.asyncio
    async def test_get_notification(self, client):
        """Test getting notification details."""
        mock_response = {"id": "msg-123", "successful": 100, "failed": 0, "errored": 0}

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            details = await client.get_notification("msg-123")

            assert details["id"] == "msg-123"
            assert details["successful"] == 100

    @pytest.mark.asyncio
    async def test_get_devices(self, client):
        """Test getting devices list."""
        mock_response = {
            "players": [{"id": "device-1", "device_type": 1}, {"id": "device-2", "device_type": 0}]
        }

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            devices = await client.get_devices(limit=50)

            assert len(devices) == 2
            assert devices[0]["id"] == "device-1"

    @pytest.mark.asyncio
    async def test_send_with_buttons(self, client):
        """Test sending with action buttons."""
        mock_response = {"id": "btn-msg-id", "recipients": 100}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            buttons = [{"id": "yes", "text": "Yes"}, {"id": "no", "text": "No"}]

            notification = await client.send_to_all(
                headings={"en": "Question"},
                contents={"en": "Do you want to continue?"},
                buttons=buttons,
            )

            assert notification.id == "btn-msg-id"

    @pytest.mark.asyncio
    async def test_api_error(self, client):
        """Test API error handling."""
        mock_response = {"errors": ["Invalid player id format"]}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 400
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)

            with pytest.raises(OneSignalError) as exc_info:
                await client.send_to_all(headings={"en": "Test"}, contents={"en": "Test"})

            assert "Invalid player id format" in str(exc_info.value)


class TestDeviceType:
    """Test device type enum."""

    def test_device_types(self):
        """Test device type values."""
        assert DeviceType.IOS.value == 0
        assert DeviceType.ANDROID.value == 1
        assert DeviceType.AMAZON.value == 2
        assert DeviceType.CHROME_WEB.value == 5
        assert DeviceType.HUAWEI.value == 13


class TestOneSignalNotification:
    """Test notification data class."""

    def test_notification_creation(self):
        """Test notification creation."""
        notification = OneSignalNotification(id="test-id", recipients=100, errors=None)

        assert notification.id == "test-id"
        assert notification.recipients == 100
        assert notification.errors is None
