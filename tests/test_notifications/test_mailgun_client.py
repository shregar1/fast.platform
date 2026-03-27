"""Tests for Mailgun client."""

import pytest
from fast_platform.notifications.providers.mailgun import MailgunClient


class TestMailgunClient:
    """Test Mailgun client."""

    @pytest.fixture
    def client(self):
        """Create Mailgun client."""
        return MailgunClient(
            api_key="key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            domain="mg.example.com",
            region="us",
        )

    def test_client_init(self, client):
        """Test client initializes correctly."""
        assert client.api_key == "key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        assert client.domain == "mg.example.com"
        assert client.region == "us"
        assert "api.mailgun.net" in client.base_url

    def test_client_eu_region(self):
        """Test EU region URL."""
        client = MailgunClient(api_key="k", domain="d", region="eu")
        assert "api.eu.mailgun.net" in client.base_url

    @pytest.mark.asyncio
    async def test_send_email_raises(self, client):
        """Test send_email raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="aiohttp"):
            await client.send_email(
                to=["recipient@example.com"],
                subject="Test",
                text="Hello",
            )

    @pytest.mark.asyncio
    async def test_send_template_raises(self, client):
        """Test send_template raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="aiohttp"):
            await client.send_template(
                to=["user@example.com"],
                template="welcome",
                subject="Welcome",
                template_vars={"name": "John"},
            )

    @pytest.mark.asyncio
    async def test_create_template_raises(self, client):
        """Test create_template raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="aiohttp"):
            await client.create_template(
                name="welcome",
                description="Welcome template",
                template="<h1>Hi {{name}}</h1>",
            )

    @pytest.mark.asyncio
    async def test_get_events_raises(self, client):
        """Test get_events raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="aiohttp"):
            await client.get_events(limit=10)

    @pytest.mark.asyncio
    async def test_validate_email_raises(self, client):
        """Test validate_email raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="aiohttp"):
            await client.validate_email("test@example.com")
