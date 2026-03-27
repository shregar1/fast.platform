"""Conversation memory for AI agents."""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime


class ConversationMemory(ABC):
    """Abstract base class for conversation memory."""

    @abstractmethod
    async def get_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get messages for a conversation."""
        pass

    @abstractmethod
    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to a conversation."""
        pass

    @abstractmethod
    async def clear(self, conversation_id: str) -> None:
        """Clear a conversation."""
        pass


class InMemoryConversationMemory(ConversationMemory):
    """In-memory conversation memory (development/testing)."""

    def __init__(self, max_messages: int = 100):
        """Execute __init__ operation.

        Args:
            max_messages: The max_messages parameter.
        """
        self._conversations: Dict[str, List[Dict[str, str]]] = {}
        self._max_messages = max_messages

    async def get_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """Execute get_messages operation.

        Args:
            conversation_id: The conversation_id parameter.

        Returns:
            The result of the operation.
        """
        return self._conversations.get(conversation_id, []).copy()

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Execute add_message operation.

        Args:
            conversation_id: The conversation_id parameter.
            role: The role parameter.
            content: The content parameter.

        Returns:
            The result of the operation.
        """
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        self._conversations[conversation_id].append(
            {"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()}
        )

        # Trim if too long
        if len(self._conversations[conversation_id]) > self._max_messages:
            self._conversations[conversation_id] = self._conversations[conversation_id][
                -self._max_messages :
            ]

    async def clear(self, conversation_id: str) -> None:
        """Execute clear operation.

        Args:
            conversation_id: The conversation_id parameter.

        Returns:
            The result of the operation.
        """
        self._conversations.pop(conversation_id, None)


class RedisConversationMemory(ConversationMemory):
    """Redis-backed conversation memory (production)."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        ttl: int = 86400 * 7,  # 7 days
        max_messages: int = 100,
    ):
        """Execute __init__ operation.

        Args:
            redis_url: The redis_url parameter.
            ttl: The ttl parameter.
            max_messages: The max_messages parameter.
        """
        self.redis_url = redis_url
        self.ttl = ttl
        self.max_messages = max_messages
        self._redis = None

    def _get_redis(self):
        """Execute _get_redis operation.

        Returns:
            The result of the operation.
        """
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(self.redis_url)
            except ImportError:
                raise ImportError("redis package required for RedisConversationMemory")
        return self._redis

    async def get_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """Execute get_messages operation.

        Args:
            conversation_id: The conversation_id parameter.

        Returns:
            The result of the operation.
        """
        redis = self._get_redis()
        key = f"conversation:{conversation_id}"

        messages_json = await redis.lrange(key, 0, -1)
        import json

        return [json.loads(m) for m in messages_json]

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Execute add_message operation.

        Args:
            conversation_id: The conversation_id parameter.
            role: The role parameter.
            content: The content parameter.

        Returns:
            The result of the operation.
        """
        redis = self._get_redis()
        key = f"conversation:{conversation_id}"

        message = {"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()}

        import json

        await redis.rpush(key, json.dumps(message))
        await redis.expire(key, self.ttl)

        # Trim to max_messages
        await redis.ltrim(key, -self.max_messages, -1)

    async def clear(self, conversation_id: str) -> None:
        """Execute clear operation.

        Args:
            conversation_id: The conversation_id parameter.

        Returns:
            The result of the operation.
        """
        redis = self._get_redis()
        key = f"conversation:{conversation_id}"
        await redis.delete(key)


class SummarizingMemory(ConversationMemory):
    """Memory that summarizes old messages to stay within token limits."""

    def __init__(
        self,
        base_memory: ConversationMemory,
        max_messages_before_summary: int = 20,
        summarization_model: Optional[Any] = None,
    ):
        """Execute __init__ operation.

        Args:
            base_memory: The base_memory parameter.
            max_messages_before_summary: The max_messages_before_summary parameter.
            summarization_model: The summarization_model parameter.
        """
        self.base_memory = base_memory
        self.max_messages_before_summary = max_messages_before_summary
        self.summarization_model = summarization_model

    async def get_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """Execute get_messages operation.

        Args:
            conversation_id: The conversation_id parameter.

        Returns:
            The result of the operation.
        """
        messages = await self.base_memory.get_messages(conversation_id)

        if len(messages) <= self.max_messages_before_summary:
            return messages

        # Need to summarize older messages
        # This is a simplified version - real implementation would use LLM
        to_summarize = messages[: -self.max_messages_before_summary]
        recent = messages[-self.max_messages_before_summary :]

        summary = await self._summarize(to_summarize)

        return [{"role": "system", "content": f"Previous conversation summary: {summary}"}, *recent]

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Execute add_message operation.

        Args:
            conversation_id: The conversation_id parameter.
            role: The role parameter.
            content: The content parameter.

        Returns:
            The result of the operation.
        """
        await self.base_memory.add_message(conversation_id, role, content)

    async def clear(self, conversation_id: str) -> None:
        """Execute clear operation.

        Args:
            conversation_id: The conversation_id parameter.

        Returns:
            The result of the operation.
        """
        await self.base_memory.clear(conversation_id)

    async def _summarize(self, messages: List[Dict[str, str]]) -> str:
        """Summarize a list of messages."""
        if not self.summarization_model:
            # Simple summary - just note the message count
            return f"{len(messages)} previous messages"

        # Use LLM to create summary
        # Implementation would call the summarization model
        return "Summary of previous conversation"
