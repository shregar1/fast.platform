"""LLM Provider integrations."""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class LLMResponse:
    """Standardized LLM response."""

    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(
        self, messages: List[Dict[str, str]], tools: Optional[List] = None, stream: bool = False
    ) -> LLMResponse:
        """Complete a conversation."""
        pass

    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        """Stream response chunks."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            model: The model parameter.
        """
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required for OpenAIProvider")
        return self._client

    async def complete(
        self, messages: List[Dict[str, str]], tools: Optional[List] = None, stream: bool = False
    ) -> LLMResponse:
        """Execute complete operation.

        Args:
            messages: The messages parameter.
            tools: The tools parameter.
            stream: The stream parameter.

        Returns:
            The result of the operation.
        """
        client = self._get_client()

        kwargs = {"model": self.model, "messages": messages, "stream": stream}

        if tools:
            kwargs["tools"] = [t.to_schema() for t in tools]
            kwargs["tool_choice"] = "auto"

        response = await client.chat.completions.create(**kwargs)

        choice = response.choices[0]

        # Extract tool calls
        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in choice.message.tool_calls
            ]

        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=choice.finish_reason,
            tool_calls=tool_calls,
        )

    async def stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        """Execute stream operation.

        Args:
            messages: The messages parameter.

        Returns:
            The result of the operation.
        """
        client = self._get_client()

        response = await client.chat.completions.create(
            model=self.model, messages=messages, stream=True
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            model: The model parameter.
        """
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required for AnthropicProvider")
        return self._client

    async def complete(
        self, messages: List[Dict[str, str]], tools: Optional[List] = None, stream: bool = False
    ) -> LLMResponse:
        """Execute complete operation.

        Args:
            messages: The messages parameter.
            tools: The tools parameter.
            stream: The stream parameter.

        Returns:
            The result of the operation.
        """
        client = self._get_client()

        # Convert messages to Anthropic format
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs = {"model": self.model, "messages": chat_messages, "max_tokens": 4096}

        if system_message:
            kwargs["system"] = system_message

        if tools:
            kwargs["tools"] = [t.to_schema() for t in tools]

        response = await client.messages.create(**kwargs)

        content = ""
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    {
                        "id": block.id,
                        "function": {"name": block.name, "arguments": json.dumps(block.input)},
                    }
                )

        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            tool_calls=tool_calls,
        )

    async def stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        """Execute stream operation.

        Args:
            messages: The messages parameter.

        Returns:
            The result of the operation.
        """
        # Implementation similar to complete but with streaming
        pass


class OllamaProvider(LLMProvider):
    """Local Ollama provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """Execute __init__ operation.

        Args:
            base_url: The base_url parameter.
            model: The model parameter.
        """
        self.base_url = base_url
        self.model = model

    async def complete(
        self, messages: List[Dict[str, str]], tools: Optional[List] = None, stream: bool = False
    ) -> LLMResponse:
        """Execute complete operation.

        Args:
            messages: The messages parameter.
            tools: The tools parameter.
            stream: The stream parameter.

        Returns:
            The result of the operation.
        """
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
            ) as response:
                data = await response.json()

                return LLMResponse(
                    content=data["message"]["content"],
                    model=self.model,
                    usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                )

    async def stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        """Execute stream operation.

        Args:
            messages: The messages parameter.

        Returns:
            The result of the operation.
        """
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True},
            ) as response:
                async for line in response.content:
                    if line:
                        data = json.loads(line)
                        if "message" in data:
                            yield data["message"]["content"]


# Import json for AnthropicProvider
import json
