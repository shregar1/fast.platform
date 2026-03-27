"""
Twilio SMS integration
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class SMSMessage:
    """SMS message"""
    to: str
    body: str
    from_number: Optional[str] = None
    media_urls: Optional[list] = None


@dataclass
class SMSResult:
    """SMS send result"""
    sid: str
    status: str
    to: str
    from_number: str
    body: str
    price: Optional[str] = None


class TwilioClient:
    """
    Twilio SMS client
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                raise ImportError("twilio package required for TwilioClient")
        return self._client
    
    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None,
        media_urls: Optional[list] = None
    ) -> SMSResult:
        """
        Send an SMS
        
        Args:
            to: Recipient phone number
            body: Message body
            from_number: Sender number (uses default if not provided)
            media_urls: Optional media URLs (MMS)
        """
        client = self._get_client()
        
        from_num = from_number or self.from_number
        if not from_num:
            raise ValueError("from_number required")
        
        params = {
            "to": to,
            "from_": from_num,
            "body": body
        }
        
        if media_urls:
            params["media_url"] = media_urls
        
        message = client.messages.create(**params)
        
        return SMSResult(
            sid=message.sid,
            status=message.status,
            to=message.to,
            from_number=message.from_,
            body=message.body,
            price=message.price
        )
    
    async def send_bulk_sms(
        self,
        messages: list[SMSMessage]
    ) -> list[SMSResult]:
        """Send multiple SMS messages"""
        results = []
        for msg in messages:
            result = await self.send_sms(
                to=msg.to,
                body=msg.body,
                from_number=msg.from_number,
                media_urls=msg.media_urls
            )
            results.append(result)
        return results
