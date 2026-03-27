"""
Tests for Amazon SES client
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fast_platform.notifications.providers.ses import SESClient


class TestSESClient:
    """Test Amazon SES client"""
    
    @pytest.fixture
    def client(self):
        """Create SES client"""
        return SESClient(
            region="us-east-1",
            access_key="AKIAIOSFODNN7EXAMPLE",
            secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )
    
    @pytest.mark.asyncio
    async def test_send_email(self, client):
        """Test sending email"""
        mock_response = {"MessageId": "test-message-id-123"}
        
        with patch.dict("sys.modules", {"boto3": MagicMock()}):
            import sys
            mock_boto3 = sys.modules["boto3"]
            mock_session = Mock()
            mock_client = Mock()
            mock_client.send_email.return_value = mock_response
            mock_session.client.return_value = mock_client
            mock_boto3.Session.return_value = mock_session
            
            # Reset client cache
            client._client = None
            
            message_id = await client.send_email(
                source="sender@example.com",
                to_addresses=["recipient@example.com"],
                subject="Test Subject",
                body_text="Hello World",
                body_html="<p>Hello World</p>"
            )
            
            assert message_id == "test-message-id-123"
    
    @pytest.mark.asyncio
    async def test_send_templated_email(self, client):
        """Test sending templated email"""
        mock_response = {"MessageId": "template-msg-id"}
        
        with patch.dict("sys.modules", {"boto3": MagicMock()}):
            import sys
            mock_boto3 = sys.modules["boto3"]
            mock_session = Mock()
            mock_client = Mock()
            mock_client.send_templated_email.return_value = mock_response
            mock_session.client.return_value = mock_client
            mock_boto3.Session.return_value = mock_session
            
            client._client = None
            
            message_id = await client.send_templated_email(
                source="sender@example.com",
                template="WelcomeTemplate",
                template_data={"name": "John", "company": "Acme"},
                to_addresses=["user@example.com"]
            )
            
            assert message_id == "template-msg-id"
    
    @pytest.mark.asyncio
    async def test_create_template(self, client):
        """Test creating template"""
        with patch.dict("sys.modules", {"boto3": MagicMock()}):
            import sys
            mock_boto3 = sys.modules["boto3"]
            mock_session = Mock()
            mock_client = Mock()
            mock_session.client.return_value = mock_client
            mock_boto3.Session.return_value = mock_session
            
            client._client = None
            
            result = await client.create_template(
                name="WelcomeTemplate",
                subject="Welcome to {{company}}",
                html_part="<h1>Welcome {{name}}!</h1>"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_email_identity(self, client):
        """Test verifying email"""
        with patch.dict("sys.modules", {"boto3": MagicMock()}):
            import sys
            mock_boto3 = sys.modules["boto3"]
            mock_session = Mock()
            mock_client = Mock()
            mock_session.client.return_value = mock_client
            mock_boto3.Session.return_value = mock_session
            
            client._client = None
            
            result = await client.verify_email_identity("test@example.com")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_send_quota(self, client):
        """Test getting send quota"""
        mock_quota = {
            "Max24HourSend": 1000.0,
            "MaxSendRate": 10.0,
            "SentLast24Hours": 100.0
        }
        
        with patch.dict("sys.modules", {"boto3": MagicMock()}):
            import sys
            mock_boto3 = sys.modules["boto3"]
            mock_session = Mock()
            mock_client = Mock()
            mock_client.get_send_quota.return_value = mock_quota
            mock_session.client.return_value = mock_client
            mock_boto3.Session.return_value = mock_session
            
            client._client = None
            
            quota = await client.get_send_quota()
            
            assert quota["Max24HourSend"] == 1000.0
            assert quota["SentLast24Hours"] == 100.0


class TestSESClientError:
    """Test SES error handling"""
    
    @pytest.mark.asyncio
    async def test_missing_boto3(self):
        """Test error when boto3 not installed"""
        with patch.dict("sys.modules", {"boto3": None}):
            client = SESClient()
            
            with pytest.raises(ImportError) as exc_info:
                await client.send_email(
                    source="test@example.com",
                    to_addresses=["user@example.com"],
                    subject="Test",
                    body_text="Hello"
                )
            
            assert "boto3" in str(exc_info.value)
