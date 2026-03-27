"""AWS SNS integration."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class SNSMessage:
    """SNS message."""

    message_id: str
    body: str
    subject: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None


class SNSClient:
    """AWS SNS client."""

    def __init__(
        self,
        topic_arn: Optional[str] = None,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """Execute __init__ operation.

        Args:
            topic_arn: The topic_arn parameter.
            region: The region parameter.
            access_key: The access_key parameter.
            secret_key: The secret_key parameter.
        """
        self.topic_arn = topic_arn
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                import boto3

                session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
                self._client = session.client("sns")

            except ImportError:
                raise ImportError("boto3 required for SNSClient")

        return self._client

    async def publish(
        self,
        message: str,
        topic_arn: Optional[str] = None,
        subject: Optional[str] = None,
        message_attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Publish a message to a topic."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        arn = topic_arn or self.topic_arn

        if not arn:
            raise ValueError("topic_arn required")

        params = {"TopicArn": arn, "Message": message}

        if subject:
            params["Subject"] = subject

        if message_attributes:
            params["MessageAttributes"] = {
                k: {"DataType": "String", "StringValue": str(v)}
                for k, v in message_attributes.items()
            }

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(pool, lambda: client.publish(**params))

        return response["MessageId"]

    async def subscribe(self, protocol: str, endpoint: str, topic_arn: Optional[str] = None) -> str:
        """Subscribe an endpoint to a topic.

        Args:
            protocol: http, https, email, email-json, sms, sqs, application, lambda
            endpoint: Endpoint URL/ARN
            topic_arn: Topic ARN

        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        arn = topic_arn or self.topic_arn

        if not arn:
            raise ValueError("topic_arn required")

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool, lambda: client.subscribe(TopicArn=arn, Protocol=protocol, Endpoint=endpoint)
            )

        return response["SubscriptionArn"]

    async def unsubscribe(self, subscription_arn: str) -> bool:
        """Unsubscribe an endpoint."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool, lambda: client.unsubscribe(SubscriptionArn=subscription_arn)
            )

        return True

    async def list_subscriptions(self, topic_arn: Optional[str] = None) -> List[Dict[str, Any]]:
        """List subscriptions."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            if topic_arn:
                response = await loop.run_in_executor(
                    pool, lambda: client.list_subscriptions_by_topic(TopicArn=topic_arn)
                )
            else:
                response = await loop.run_in_executor(pool, lambda: client.list_subscriptions())

        return response.get("Subscriptions", [])

    async def create_topic(self, name: str) -> str:
        """Create a new topic."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(pool, lambda: client.create_topic(Name=name))

        return response["TopicArn"]

    async def delete_topic(self, topic_arn: Optional[str] = None) -> bool:
        """Delete a topic."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        arn = topic_arn or self.topic_arn

        if not arn:
            raise ValueError("topic_arn required")

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, lambda: client.delete_topic(TopicArn=arn))

        return True

    async def list_topics(self) -> List[Dict[str, Any]]:
        """List all topics."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(pool, lambda: client.list_topics())

        return response.get("Topics", [])
