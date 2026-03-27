"""
Tests for Mailgun client
"""

import pytest
from unittest.mock import AsyncMock, patch
from fast_platform.notifications.providers.mailgun import MailgunClient


class TestMailgunClient:
    """Test Mailgun client"""
    
    @pytest.fixture
    def client(self):
        """Create Mailgun client"""
        return MailgunClient(
            api_key="test-api-key",
            domain="mg.example.com",
            region="us"
        )
    
    @pytest.mark.asyncio
    async def test_send_email(self, client):
        """Test sending email"""
        mock_response = {
            "id": "<20240101000000.12345@test.mailgun.org>",
            "message": "Queued. Thank you."
        }
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)
            
            result = await client.send_email(
                to=["recipient@example.com"],
                subject="Test Subject",
                text="Hello World",
                html="<p>Hello World</p>",
                from_email="sender@example.com"
            )
            
            assert result["message"] == "Queued. Thank you."
    
    @pytest.mark.asyncio
    async def test_send_template(self, client):
        """Test sending with template"""
        mock_response = {"message": "Queued"}
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)
            
            result = await client.send_template(
                to=["user@example.com"],
                template="welcome",
                subject="Welcome",
                template_vars={"name": "John", "company": "Acme"}
            )
            
            assert result["message"] == "Queued"
    
    @pytest.mark.asyncio
    async def test_create_template(self, client):
        """Test creating template"""
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.status = 200
            mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_context)
            
            result = await client.create_template(
                name="welcome",
                description="Welcome email template",
                template="<h1>Welcome {{name}}!</h1>"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_events(self, client):
        """Test getting events"""
        mock_response = {
            "items": [
                {
                    "event": "delivered",
                    "timestamp": 1640995200,
                    "recipient": "user@example.com"
                }
            ]
        }
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_context)
            
            events = await client.get_events(limit=10)
            
            assert len(events) == 1
            assert events[0]["event"] == "delivered"
    
    @pytest.mark.asyncio
    async def test_validate_email(self, client):
        """Test email validation"""
        mock_response = {
            "address": "test@example.com",
            "is_valid": True,
            "parts": {"local_part": "test", "domain": "example.com"}
        }
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_context = AsyncMock()
            mock_context.json.return_value = mock_response
            mock_context.status = 200
            mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_context)
            
            result = await client.validate_email("test@example.com")
            
            assert result["is_valid"] is True
            assert result["address"] == "test@example.com"
    
    def test_eu_region(self):
        """Test EU region URL"""
        client = MailgunClient(
            api_key="test",
            domain="mg.example.com",
            region="eu"
        )
        
        assert client.base_url == "https://api.eu.mailgun.net/v3"
