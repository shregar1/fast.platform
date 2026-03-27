"""
Amazon SES client
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class SESAttachment:
    """SES email attachment"""
    filename: str
    content: bytes
    content_type: str


class SESClient:
    """
    Amazon Simple Email Service client
    """
    
    def __init__(
        self,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        configuration_set: Optional[str] = None
    ):
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.configuration_set = configuration_set
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                
                session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region
                )
                self._client = session.client("ses")
                
            except ImportError:
                raise ImportError("boto3 required for SESClient")
        
        return self._client
    
    async def send_email(
        self,
        source: str,
        to_addresses: List[str],
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
        reply_to: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Send an email via SES
        
        Args:
            source: From email address
            to_addresses: List of recipient addresses
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body
            tags: Message tags for analytics
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        # Build message
        message = {}
        
        if body_text:
            message["Text"] = {"Data": body_text}
        if body_html:
            message["Html"] = {"Data": body_html}
        
        destination = {"ToAddresses": to_addresses}
        if cc_addresses:
            destination["CcAddresses"] = cc_addresses
        if bcc_addresses:
            destination["BccAddresses"] = bcc_addresses
        
        params = {
            "Source": source,
            "Destination": destination,
            "Message": {
                "Subject": {"Data": subject},
                "Body": message
            }
        }
        
        if reply_to:
            params["ReplyToAddresses"] = reply_to
        
        if self.configuration_set:
            params["ConfigurationSetName"] = self.configuration_set
        
        if tags:
            params["Tags"] = [{"Name": k, "Value": v} for k, v in tags.items()]
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: client.send_email(**params)
            )
        
        return response["MessageId"]
    
    async def send_templated_email(
        self,
        source: str,
        template: str,
        template_data: Dict[str, Any],
        to_addresses: List[str]
    ) -> str:
        """Send using an SES template"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        import json
        
        client = self._get_client()
        
        params = {
            "Source": source,
            "Template": template,
            "Destination": {"ToAddresses": to_addresses},
            "TemplateData": json.dumps(template_data)
        }
        
        if self.configuration_set:
            params["ConfigurationSetName"] = self.configuration_set
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: client.send_templated_email(**params)
            )
        
        return response["MessageId"]
    
    async def send_bulk_templated_email(
        self,
        source: str,
        template: str,
        destinations: List[Dict[str, Any]],
        default_template_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send bulk emails using a template"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        import json
        
        client = self._get_client()
        
        params = {
            "Source": source,
            "Template": template,
            "Destinations": destinations
        }
        
        if default_template_data:
            params["DefaultTemplateData"] = json.dumps(default_template_data)
        
        if self.configuration_set:
            params["ConfigurationSetName"] = self.configuration_set
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: client.send_bulk_templated_email(**params)
            )
        
        return response
    
    async def create_template(
        self,
        name: str,
        subject: str,
        text_part: Optional[str] = None,
        html_part: Optional[str] = None
    ) -> bool:
        """Create an email template"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        template = {
            "TemplateName": name,
            "SubjectPart": subject
        }
        
        if text_part:
            template["TextPart"] = text_part
        if html_part:
            template["HtmlPart"] = html_part
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.create_template(Template=template)
            )
        
        return True
    
    async def verify_email_identity(self, email: str) -> bool:
        """Verify an email address"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.verify_email_identity(EmailAddress=email)
            )
        
        return True
    
    async def get_send_quota(self) -> Dict[str, Any]:
        """Get sending quota"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                client.get_send_quota
            )
        
        return response
    
    async def get_send_statistics(self) -> List[Dict[str, Any]]:
        """Get sending statistics"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                client.get_send_statistics
            )
        
        return response.get("SendDataPoints", [])
