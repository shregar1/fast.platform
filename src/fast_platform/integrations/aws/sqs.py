"""
AWS SQS integration
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class SQSMessage:
    """SQS message"""
    message_id: str
    body: str
    receipt_handle: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    message_attributes: Optional[Dict[str, Any]] = None


class SQSClient:
    """
    AWS SQS client
    """
    
    def __init__(
        self,
        queue_url: Optional[str] = None,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        self.queue_url = queue_url
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
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
                self._client = session.client("sqs")
                
            except ImportError:
                raise ImportError("boto3 required for SQSClient")
        
        return self._client
    
    async def send_message(
        self,
        message_body: str,
        queue_url: Optional[str] = None,
        message_attributes: Optional[Dict[str, Any]] = None,
        delay_seconds: int = 0
    ) -> str:
        """Send a message to the queue"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        url = queue_url or self.queue_url
        
        if not url:
            raise ValueError("queue_url required")
        
        params = {
            "QueueUrl": url,
            "MessageBody": message_body,
            "DelaySeconds": delay_seconds
        }
        
        if message_attributes:
            params["MessageAttributes"] = {
                k: {"DataType": "String", "StringValue": str(v)}
                for k, v in message_attributes.items()
            }
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: client.send_message(**params)
            )
        
        return response["MessageId"]
    
    async def send_message_batch(
        self,
        messages: List[Dict[str, Any]],
        queue_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send multiple messages"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        url = queue_url or self.queue_url
        
        if not url:
            raise ValueError("queue_url required")
        
        entries = [
            {
                "Id": str(i),
                "MessageBody": msg["body"],
                **({"DelaySeconds": msg["delay_seconds"]} if "delay_seconds" in msg else {})
            }
            for i, msg in enumerate(messages)
        ]
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: client.send_message_batch(
                    QueueUrl=url,
                    Entries=entries
                )
            )
        
        return response
    
    async def receive_messages(
        self,
        queue_url: Optional[str] = None,
        max_messages: int = 10,
        wait_time_seconds: int = 0,
        visibility_timeout: int = 30
    ) -> List[SQSMessage]:
        """Receive messages from the queue"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        url = queue_url or self.queue_url
        
        if not url:
            raise ValueError("queue_url required")
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: client.receive_message(
                    QueueUrl=url,
                    MaxNumberOfMessages=max_messages,
                    WaitTimeSeconds=wait_time_seconds,
                    VisibilityTimeout=visibility_timeout,
                    AttributeNames=["All"],
                    MessageAttributeNames=["All"]
                )
            )
        
        messages = []
        for msg in response.get("Messages", []):
            messages.append(SQSMessage(
                message_id=msg["MessageId"],
                body=msg["Body"],
                receipt_handle=msg["ReceiptHandle"],
                attributes=msg.get("Attributes"),
                message_attributes=msg.get("MessageAttributes")
            ))
        
        return messages
    
    async def delete_message(
        self,
        receipt_handle: str,
        queue_url: Optional[str] = None
    ) -> bool:
        """Delete a message from the queue"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        url = queue_url or self.queue_url
        
        if not url:
            raise ValueError("queue_url required")
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.delete_message(
                    QueueUrl=url,
                    ReceiptHandle=receipt_handle
                )
            )
        
        return True
    
    async def change_visibility(
        self,
        receipt_handle: str,
        visibility_timeout: int,
        queue_url: Optional[str] = None
    ) -> bool:
        """Change message visibility timeout"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        url = queue_url or self.queue_url
        
        if not url:
            raise ValueError("queue_url required")
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.change_message_visibility(
                    QueueUrl=url,
                    ReceiptHandle=receipt_handle,
                    VisibilityTimeout=visibility_timeout
                )
            )
        
        return True
    
    async def get_queue_attributes(
        self, queue_url: Optional[str] = None
    ) -> Dict[str, str]:
        """Get queue attributes"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        url = queue_url or self.queue_url
        
        if not url:
            raise ValueError("queue_url required")
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: client.get_queue_attributes(
                    QueueUrl=url,
                    AttributeNames=["All"]
                )
            )
        
        return response.get("Attributes", {})
