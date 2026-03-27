"""Tests for Pusher client."""

import pytest
from fast_platform.notifications.providers.pusher import PusherChannel, PusherClient


class TestPusherClient:
    """Test Pusher client."""

    @pytest.fixture
    def client(self):
        """Create Pusher client."""
        return PusherClient(
            app_id="123456",
            key="abc123key",
            secret="supersecret",
            cluster="mt1",
        )

    def test_client_init(self, client):
        """Test client initializes correctly."""
        assert client.app_id == "123456"
        assert client.key == "abc123key"
        assert client.secret == "supersecret"
        assert client.cluster == "mt1"

    @pytest.mark.asyncio
    async def test_trigger_raises(self, client):
        """Test trigger raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="pusher"):
            await client.trigger(
                channel="test-channel",
                event="test-event",
                data={"message": "hello"},
            )

    def test_bind_raises(self, client):
        """Test bind raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="pusher"):
            client.bind("test-event", lambda x: x)


class TestPusherChannel:
    """Test PusherChannel model."""

    def test_channel_creation(self):
        """Test basic channel creation."""
        channel = PusherChannel(name="my-channel")
        assert channel.name == "my-channel"

    def test_private_channel(self):
        """Test private channel naming convention."""
        channel = PusherChannel(name="private-my-channel")
        assert channel.name.startswith("private-")

    def test_presence_channel(self):
        """Test presence channel naming convention."""
        channel = PusherChannel(name="presence-room")
        assert channel.name.startswith("presence-")
