"""
Generic webhook client with signature verification
"""

from typing import Optional, Dict, Any
import hmac
import hashlib
import json
import time


class WebhookSignature:
    """Webhook signature verification and generation"""
    
    @staticmethod
    def generate_signature(payload: str, secret: str, algorithm: str = "sha256") -> str:
        """Generate HMAC signature"""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            getattr(hashlib, algorithm)
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(
        payload: str,
        signature: str,
        secret: str,
        algorithm: str = "sha256"
    ) -> bool:
        """Verify HMAC signature"""
        expected = WebhookSignature.generate_signature(payload, secret, algorithm)
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(signature, expected)
    
    @staticmethod
    def generate_stripe_signature(payload: str, secret: str, timestamp: Optional[int] = None) -> str:
        """Generate Stripe-style signature"""
        timestamp = timestamp or int(time.time())
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"
    
    @staticmethod
    def verify_stripe_signature(payload: str, signature_header: str, secret: str) -> bool:
        """Verify Stripe-style signature"""
        elements = signature_header.split(",")
        signature_dict = {}
        
        for element in elements:
            if "=" in element:
                key, value = element.split("=", 1)
                signature_dict[key] = value
        
        timestamp = signature_dict.get("t")
        signature = signature_dict.get("v1")
        
        if not timestamp or not signature:
            return False
        
        signed_payload = f"{timestamp}.{payload}"
        expected = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)


class WebhookClient:
    """
    Generic webhook client
    """
    
    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None,
        signature_header: str = "X-Webhook-Signature"
    ):
        self.url = url
        self.headers = headers or {}
        self.secret = secret
        self.signature_header = signature_header
    
    async def send(
        self,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        sign: bool = True
    ) -> Dict[str, Any]:
        """
        Send webhook payload
        
        Args:
            payload: JSON payload
            headers: Additional headers
            sign: Whether to sign the payload
        """
        import aiohttp
        
        payload_json = json.dumps(payload, default=str)
        
        request_headers = {
            "Content-Type": "application/json",
            **self.headers
        }
        
        if headers:
            request_headers.update(headers)
        
        # Add signature if secret provided
        if sign and self.secret:
            signature = WebhookSignature.generate_signature(payload_json, self.secret)
            request_headers[self.signature_header] = signature
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                data=payload_json,
                headers=request_headers
            ) as response:
                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": await response.text()
                }
    
    async def send_with_retry(
        self,
        payload: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """Send with retry logic"""
        import asyncio
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self.send(payload)
                if result["status"] < 500:
                    return result
            except Exception as e:
                last_error = e
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
        
        raise last_error or Exception("Max retries exceeded")
    
    def create_signed_url(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Create a signed URL for webhook verification"""
        import base64
        import time
        
        payload_json = json.dumps(payload, default=str)
        timestamp = int(time.time())
        expires = timestamp + expires_in
        
        data = f"{payload_json}:{expires}"
        signature = WebhookSignature.generate_signature(data, self.secret)
        
        # Create signed payload
        signed_data = base64.urlsafe_b64encode(data.encode()).decode()
        
        return f"{self.url}?data={signed_data}&signature={signature}"
    
    @staticmethod
    def verify_incoming_request(
        payload: bytes,
        signature_header: str,
        secret: str,
        scheme: str = "hmac-sha256"
    ) -> bool:
        """
        Verify incoming webhook request
        
        Args:
            payload: Raw request body
            signature_header: Signature from header
            secret: Webhook secret
            scheme: Signature scheme (hmac-sha256, stripe)
        """
        if scheme == "stripe":
            return WebhookSignature.verify_stripe_signature(
                payload.decode(), signature_header, secret
            )
        
        return WebhookSignature.verify_signature(
            payload.decode(), signature_header, secret
        )
