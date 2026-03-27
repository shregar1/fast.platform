"""Tests for Amazon SES client."""

import pytest
from fast_platform.notifications.providers.ses import SESClient


class TestSESClient:
    """Test Amazon SES client."""

    @pytest.fixture
    def client(self):
        """Create SES client."""
        return SESClient(
            region_name="us-east-1",
            aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
            aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        )

    def test_client_init(self, client):
        """Test client initializes with correct attributes."""
        assert client.aws_access_key_id == "AKIAIOSFODNN7EXAMPLE"
        assert client.aws_secret_access_key == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        assert client.region_name == "us-east-1"

    def test_client_defaults(self):
        """Test client default values."""
        client = SESClient()
        assert client.aws_access_key_id is None
        assert client.aws_secret_access_key is None
        assert client.region_name == "us-east-1"

    @pytest.mark.asyncio
    async def test_send_email_raises(self, client):
        """Test send_email raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="boto3"):
            await client.send_email(
                to=["recipient@example.com"],
                subject="Test Subject",
                text="Hello World",
                html="<p>Hello World</p>",
            )

    @pytest.mark.asyncio
    async def test_send_template_raises(self, client):
        """Test send_template raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="boto3"):
            await client.send_template(
                to=["user@example.com"],
                template="WelcomeTemplate",
                subject="Welcome",
                template_data={"name": "John"},
            )

    @pytest.mark.asyncio
    async def test_create_template_raises(self, client):
        """Test create_template raises NotImplementedError (stub)."""
        with pytest.raises(NotImplementedError, match="boto3"):
            await client.create_template(
                name="WelcomeTemplate",
                subject="Welcome to {{company}}",
                html="<h1>Welcome {{name}}!</h1>",
                text="Welcome {{name}}!",
            )
