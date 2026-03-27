"""Tests for Pusher client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fast_platform.notifications.providers.pusher import PusherClient, PusherChannel


class TestPusherClient:
    """Test Pusher client."""

    @pytest.fixture
    def client(self):
        """Create Pusher client."""
        return PusherClient(app_id="12345", key="test-key", secret="test-secret", cluster="mt1")

    @pytest.mark.asyncio
    async def test_trigger(self, client):
        """Test triggering event."""
        with patch.dict("sys.modules", {"pusher": MagicMock()}):
            import sys

            mock_pusher = sys.modules["pusher"]
            mock_client = Mock()
            mock_client.trigger.return_value = None
            mock_pusher.Pusher.return_value = mock_client

            client._client = None

            result = await client.trigger(
                channels=["my-channel"], event="my-event", data={"message": "Hello"}
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_trigger_batch(self, client):
        """Test batch trigger."""
        with patch.dict("sys.modules", {"pusher": MagicMock()}):
            import sys

            mock_pusher = sys.modules["pusher"]
            mock_client = Mock()
            mock_client.trigger_batch.return_value = None
            mock_pusher.Pusher.return_value = mock_client

            client._client = None

            events = [
                {"channel": "channel-1", "name": "event-1", "data": {"msg": "Hello"}},
                {"channel": "channel-2", "name": "event-2", "data": {"msg": "World"}},
            ]

            result = await client.trigger_batch(events)

            assert result is True

    @pytest.mark.asyncio
    async def test_authenticate_private_channel(self, client):
        """Test private channel auth."""
        mock_auth = {"auth": "test-key:signature123"}

        with patch.dict("sys.modules", {"pusher": MagicMock()}):
            import sys

            mock_pusher = sys.modules["pusher"]
            mock_client = Mock()
            mock_client.authenticate.return_value = mock_auth
            mock_pusher.Pusher.return_value = mock_client

            client._client = None

            auth = await client.authenticate_private_channel(
                socket_id="123.456", channel_name="private-my-channel"
            )

            assert auth["auth"] == "test-key:signature123"

    @pytest.mark.asyncio
    async def test_authenticate_presence_channel(self, client):
        """Test presence channel auth."""
        mock_auth = {"auth": "test-key:signature456", "channel_data": "{}"}

        with patch.dict("sys.modules", {"pusher": MagicMock()}):
            import sys

            mock_pusher = sys.modules["pusher"]
            mock_client = Mock()
            mock_client.authenticate.return_value = mock_auth
            mock_pusher.Pusher.return_value = mock_client

            client._client = None

            auth = await client.authenticate_presence_channel(
                socket_id="123.456",
                channel_name="presence-room",
                user_id="user-123",
                user_info={"name": "John"},
            )

            assert auth["auth"] == "test-key:signature456"

    @pytest.mark.asyncio
    async def test_get_channel_info(self, client):
        """Test getting channel info."""
        mock_info = {"occupied": True, "user_count": 5, "subscription_count": 10}

        with patch.dict("sys.modules", {"pusher": MagicMock()}):
            import sys

            mock_pusher = sys.modules["pusher"]
            mock_client = Mock()
            mock_client.channel_info.return_value = mock_info
            mock_pusher.Pusher.return_value = mock_client

            client._client = None

            info = await client.get_channel_info("my-channel")

            assert info["occupied"] is True
            assert info["user_count"] == 5

    @pytest.mark.asyncio
    async def test_get_channels(self, client):
        """Test getting all channels."""
        mock_channels = {
            "channels": {"channel-1": {"user_count": 2}, "channel-2": {"user_count": 5}}
        }

        with patch.dict("sys.modules", {"pusher": MagicMock()}):
            import sys

            mock_pusher = sys.modules["pusher"]
            mock_client = Mock()
            mock_client.channels_info.return_value = mock_channels
            mock_pusher.Pusher.return_value = mock_client

            client._client = None

            channels = await client.get_channels()

            assert "channels" in channels
            assert len(channels["channels"]) == 2

    @pytest.mark.asyncio
    async def test_get_users_in_channel(self, client):
        """Test getting users in presence channel."""
        mock_users = {"users": [{"id": "user-1"}, {"id": "user-2"}]}

        with patch.dict("sys.modules", {"pusher": MagicMock()}):
            import sys

            mock_pusher = sys.modules["pusher"]
            mock_client = Mock()
            mock_client.users_info.return_value = mock_users
            mock_pusher.Pusher.return_value = mock_client

            client._client = None

            users = await client.get_users_in_channel("presence-room")

            assert len(users) == 2
            assert users[0]["id"] == "user-1"


class TestPusherChannel:
    """Test Pusher channel."""

    def test_channel_creation(self):
        """Test channel creation."""
        channel = PusherChannel(name="my-channel")
        assert channel.name == "my-channel"
        assert channel.is_private is False
        assert channel.is_presence is False

    def test_private_channel(self):
        """Test private channel."""
        channel = PusherChannel(name="private-my-channel", is_private=True)
        assert channel.is_private is True

    def test_presence_channel(self):
        """Test presence channel."""
        channel = PusherChannel(name="presence-room", is_private=True, is_presence=True)
        assert channel.is_private is True
        assert channel.is_presence is True


class TestPusherError:
    """Test Pusher error handling."""

    @pytest.mark.asyncio
    async def test_missing_pusher(self):
        """Test error when pusher not installed."""
        with patch.dict("sys.modules", {"pusher": None}):
            client = PusherClient(app_id="123", key="key", secret="secret")

            with pytest.raises(ImportError) as exc_info:
                await client.trigger(channels=["test"], event="test", data={})

            assert "pusher" in str(exc_info.value)
