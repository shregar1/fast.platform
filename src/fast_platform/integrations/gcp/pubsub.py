"""Google Cloud Pub/Sub integration."""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass


@dataclass
class PubSubMessage:
    """Pub/Sub message."""

    data: str
    message_id: str
    publish_time: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    ordering_key: str = ""


class PubSubClient:
    """Google Cloud Pub/Sub client."""

    def __init__(self, project: Optional[str] = None, credentials_path: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            project: The project parameter.
            credentials_path: The credentials_path parameter.
        """
        self.project = project
        self.credentials_path = credentials_path
        self._publisher = None
        self._subscriber = None

    def _get_publisher(self):
        """Execute _get_publisher operation.

        Returns:
            The result of the operation.
        """
        if self._publisher is None:
            try:
                from google.cloud import pubsub_v1

                if self.credentials_path:
                    self._publisher = pubsub_v1.PublisherClient.from_service_account_file(
                        self.credentials_path
                    )
                else:
                    self._publisher = pubsub_v1.PublisherClient()

            except ImportError:
                raise ImportError("google-cloud-pubsub required for PubSubClient")

        return self._publisher

    def _get_subscriber(self):
        """Execute _get_subscriber operation.

        Returns:
            The result of the operation.
        """
        if self._subscriber is None:
            try:
                from google.cloud import pubsub_v1

                if self.credentials_path:
                    self._subscriber = pubsub_v1.SubscriberClient.from_service_account_file(
                        self.credentials_path
                    )
                else:
                    self._subscriber = pubsub_v1.SubscriberClient()

            except ImportError:
                raise ImportError("google-cloud-pubsub required for PubSubClient")

        return self._subscriber

    def _topic_path(self, topic: str) -> str:
        """Get full topic path."""
        from google.cloud import pubsub_v1

        publisher = self._get_publisher()
        project = self.project or publisher.project
        return publisher.topic_path(project, topic)

    def _subscription_path(self, subscription: str) -> str:
        """Get full subscription path."""
        from google.cloud import pubsub_v1

        subscriber = self._get_subscriber()
        project = self.project or subscriber.project
        return subscriber.subscription_path(project, subscription)

    async def publish(
        self,
        topic: str,
        data: str,
        attributes: Optional[Dict[str, str]] = None,
        ordering_key: str = "",
    ) -> str:
        """Publish a message to a topic."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        publisher = self._get_publisher()
        topic_path = self._topic_path(topic)

        data_bytes = data.encode("utf-8")

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            future = await loop.run_in_executor(
                pool,
                lambda: publisher.publish(
                    topic_path, data_bytes, **(attributes or {}), ordering_key=ordering_key
                ),
            )

            # Wait for result
            message_id = await loop.run_in_executor(pool, future.result)

        return message_id

    async def subscribe(
        self, subscription: str, callback: Callable[[PubSubMessage], None], max_messages: int = 100
    ) -> Any:
        """Subscribe to a subscription.

        Args:
            subscription: Subscription name
            callback: Message handler function
            max_messages: Max messages to pull

        Returns:
            Streaming pull future

        """
        from google.cloud import pubsub_v1

        subscriber = self._get_subscriber()
        subscription_path = self._subscription_path(subscription)

        def wrapper(message):
            """Execute wrapper operation.

            Args:
                message: The message parameter.

            Returns:
                The result of the operation.
            """
            pubsub_message = PubSubMessage(
                data=message.data.decode("utf-8"),
                message_id=message.message_id,
                publish_time=str(message.publish_time),
                attributes=dict(message.attributes),
                ordering_key=message.ordering_key,
            )

            callback(pubsub_message)
            message.ack()

        streaming_pull_future = subscriber.subscribe(
            subscription_path,
            callback=wrapper,
            flow_control=pubsub_v1.types.FlowControl(max_messages=max_messages),
        )

        return streaming_pull_future

    async def pull_messages(self, subscription: str, max_messages: int = 10) -> List[PubSubMessage]:
        """Pull messages from a subscription."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        subscriber = self._get_subscriber()
        subscription_path = self._subscription_path(subscription)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: subscriber.pull(subscription=subscription_path, max_messages=max_messages),
            )

        messages = []
        for received_message in response.received_messages:
            msg = received_message.message
            messages.append(
                PubSubMessage(
                    data=msg.data.decode("utf-8"),
                    message_id=msg.message_id,
                    publish_time=str(msg.publish_time),
                    attributes=dict(msg.attributes),
                    ordering_key=msg.ordering_key,
                )
            )

        return messages

    async def acknowledge(self, subscription: str, ack_ids: List[str]) -> bool:
        """Acknowledge messages."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        subscriber = self._get_subscriber()
        subscription_path = self._subscription_path(subscription)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: subscriber.acknowledge(subscription=subscription_path, ack_ids=ack_ids),
            )

        return True

    async def create_topic(self, topic: str) -> str:
        """Create a new topic."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        publisher = self._get_publisher()
        topic_path = self._topic_path(topic)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, lambda: publisher.create_topic(name=topic_path))

        return topic_path

    async def delete_topic(self, topic: str) -> bool:
        """Delete a topic."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        publisher = self._get_publisher()
        topic_path = self._topic_path(topic)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, lambda: publisher.delete_topic(topic=topic_path))

        return True

    async def create_subscription(self, topic: str, subscription: str) -> str:
        """Create a new subscription."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        subscriber = self._get_subscriber()
        topic_path = self._topic_path(topic)
        subscription_path = self._subscription_path(subscription)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: subscriber.create_subscription(name=subscription_path, topic=topic_path),
            )

        return subscription_path

    async def delete_subscription(self, subscription: str) -> bool:
        """Delete a subscription."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        subscriber = self._get_subscriber()
        subscription_path = self._subscription_path(subscription)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool, lambda: subscriber.delete_subscription(subscription=subscription_path)
            )

        return True
