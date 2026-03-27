"""
Azure Service Bus integration
"""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass


@dataclass
class ServiceBusMessage:
    """Service Bus message"""
    body: str
    message_id: Optional[str] = None
    content_type: Optional[str] = None
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    application_properties: Optional[Dict[str, Any]] = None


class ServiceBusClient:
    """
    Azure Service Bus client
    """
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        fully_qualified_namespace: Optional[str] = None,
        credential: Optional[Any] = None
    ):
        self.connection_string = connection_string
        self.fully_qualified_namespace = fully_qualified_namespace
        self.credential = credential
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from azure.servicebus import ServiceBusClient as AzureServiceBusClient
                
                if self.connection_string:
                    self._client = AzureServiceBusClient.from_connection_string(
                        conn_str=self.connection_string
                    )
                else:
                    self._client = AzureServiceBusClient(
                        fully_qualified_namespace=self.fully_qualified_namespace,
                        credential=self.credential
                    )
                    
            except ImportError:
                raise ImportError("azure-servicebus required for ServiceBusClient")
        
        return self._client
    
    async def send_message(
        self,
        queue_or_topic: str,
        body: str,
        message_id: Optional[str] = None,
        content_type: Optional[str] = None,
        application_properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send a message to a queue or topic"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            sender = await loop.run_in_executor(
                pool,
                lambda: client.get_queue_sender(queue_name=queue_or_topic)
            )
            
            try:
                from azure.servicebus import ServiceBusMessage
                
                message = ServiceBusMessage(body)
                
                if message_id:
                    message.message_id = message_id
                if content_type:
                    message.content_type = content_type
                if application_properties:
                    message.application_properties = application_properties
                
                await loop.run_in_executor(pool, sender.send_messages, message)
            finally:
                await loop.run_in_executor(pool, sender.close)
    
    async def send_messages_batch(
        self,
        queue_or_topic: str,
        messages: List[ServiceBusMessage]
    ) -> None:
        """Send multiple messages"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        from azure.servicebus import ServiceBusMessage
        
        batch_messages = []
        for msg in messages:
            sb_msg = ServiceBusMessage(msg.body)
            if msg.message_id:
                sb_msg.message_id = msg.message_id
            if msg.content_type:
                sb_msg.content_type = msg.content_type
            if msg.application_properties:
                sb_msg.application_properties = msg.application_properties
            batch_messages.append(sb_msg)
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            sender = await loop.run_in_executor(
                pool,
                lambda: client.get_queue_sender(queue_name=queue_or_topic)
            )
            
            try:
                await loop.run_in_executor(pool, sender.send_messages, batch_messages)
            finally:
                await loop.run_in_executor(pool, sender.close)
    
    async def receive_messages(
        self,
        queue_or_subscription: str,
        max_messages: int = 10,
        max_wait_time: int = 5,
        topic: Optional[str] = None
    ) -> List[ServiceBusMessage]:
        """Receive messages from a queue or subscription"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            if topic:
                receiver = await loop.run_in_executor(
                    pool,
                    lambda: client.get_subscription_receiver(
                        topic_name=topic,
                        subscription_name=queue_or_subscription
                    )
                )
            else:
                receiver = await loop.run_in_executor(
                    pool,
                    lambda: client.get_queue_receiver(queue_name=queue_or_subscription)
                )
            
            try:
                received = await loop.run_in_executor(
                    pool,
                    lambda: receiver.receive_messages(
                        max_message_count=max_messages,
                        max_wait_time=max_wait_time
                    )
                )
                
                messages = []
                for msg in received:
                    messages.append(ServiceBusMessage(
                        body=str(msg),
                        message_id=msg.message_id,
                        content_type=msg.content_type,
                        correlation_id=msg.correlation_id,
                        session_id=msg.session_id,
                        application_properties=msg.application_properties
                    ))
                
                return messages
            finally:
                await loop.run_in_executor(pool, receiver.close)
    
    async def complete_message(
        self,
        queue_or_subscription: str,
        message: ServiceBusMessage,
        topic: Optional[str] = None
    ) -> None:
        """Complete a message"""
        # This would need the actual received message object
        # Simplified implementation
        pass
    
    async def dead_letter_message(
        self,
        queue_or_subscription: str,
        message: ServiceBusMessage,
        reason: str = "",
        error_description: str = "",
        topic: Optional[str] = None
    ) -> None:
        """Dead-letter a message"""
        # This would need the actual received message object
        pass
    
    async def schedule_message(
        self,
        queue_or_topic: str,
        body: str,
        scheduled_enqueue_time_utc: Any,
        message_id: Optional[str] = None
    ) -> str:
        """Schedule a message for future delivery"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        from azure.servicebus import ServiceBusMessage
        
        message = ServiceBusMessage(body)
        if message_id:
            message.message_id = message_id
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            sender = await loop.run_in_executor(
                pool,
                lambda: client.get_queue_sender(queue_name=queue_or_topic)
            )
            
            try:
                sequence_number = await loop.run_in_executor(
                    pool,
                    lambda: sender.schedule_messages(
                        messages=[message],
                        scheduled_enqueue_time_utc=scheduled_enqueue_time_utc
                    )
                )
                return str(sequence_number[0]) if sequence_number else ""
            finally:
                await loop.run_in_executor(pool, sender.close)
    
    async def close(self):
        """Close the client"""
        if self._client:
            self._client.close()
            self._client = None
