"""Module test_tools_caching_budget.py."""

from __future__ import annotations

"""Tool DTOs, cache helpers, token budget."""
from typing import AsyncIterator, List

import pytest

from fast_platform.integrations.llm.budget import (
    TokenBudgetExceeded,
    check_usage_against_budget,
    iter_llm_stream_with_budget,
)
from fast_platform.integrations.llm.caching import (
    ephemeral_cache_control,
    openai_content_part_text,
    openai_system_message_cached,
)
from fast_platform.integrations.llm.streaming import StreamChunk
from fast_platform.integrations.llm.token_usage import TokenUsage
from fast_platform.integrations.llm.tools import (
    ToolDefinition,
    normalize_tools_to_anthropic,
    normalize_tools_to_openai,
    tool_definition_from_anthropic,
    tool_definition_from_openai,
    tool_definitions_to_anthropic_tools,
    tool_definitions_to_openai_tools,
)
from tests.integrations.llm.abstraction import ILLMTests


async def _chunks(*items: StreamChunk) -> AsyncIterator[StreamChunk]:
    """Execute _chunks operation.

    Returns:
        The result of the operation.
    """
    for c in items:
        yield c


class TestToolsCachingBudget(ILLMTests):
    """Represents the TestToolsCachingBudget class."""

    def test_tool_definition_roundtrip_openai_anthropic(self) -> None:
        """Execute test_tool_definition_roundtrip_openai_anthropic operation.

        Returns:
            The result of the operation.
        """
        t = ToolDefinition(
            name="get_weather",
            description="Weather lookup",
            parameters={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        )
        oa = t.to_openai_tool()
        an = t.to_anthropic_tool()
        assert oa["type"] == "function"
        assert oa["function"]["name"] == "get_weather"
        assert an["name"] == "get_weather"
        assert an["input_schema"]["type"] == "object"
        assert tool_definition_from_openai(oa).name == "get_weather"
        assert tool_definition_from_anthropic(an).name == "get_weather"

    def test_normalize_mixed_tool_lists(self) -> None:
        """Execute test_normalize_mixed_tool_lists operation.

        Returns:
            The result of the operation.
        """
        openai_shape = {
            "type": "function",
            "function": {
                "name": "f",
                "description": "d",
                "parameters": {"type": "object", "properties": {}},
            },
        }
        anthropic_shape = {
            "name": "g",
            "description": "d2",
            "input_schema": {"type": "object", "properties": {}},
        }
        to_o = normalize_tools_to_openai([openai_shape, anthropic_shape])
        assert to_o[0]["function"]["name"] == "f"
        assert to_o[1]["function"]["name"] == "g"
        to_a = normalize_tools_to_anthropic([openai_shape, anthropic_shape])
        assert to_a[0]["name"] == "f"
        assert to_a[1]["name"] == "g"

    def test_tool_definitions_lists(self) -> None:
        """Execute test_tool_definitions_lists operation.

        Returns:
            The result of the operation.
        """
        tools = [
            ToolDefinition("a", "da", {"type": "object", "properties": {}}),
        ]
        assert len(tool_definitions_to_openai_tools(tools)) == 1
        assert len(tool_definitions_to_anthropic_tools(tools)) == 1

    def test_cache_helpers(self) -> None:
        """Execute test_cache_helpers operation.

        Returns:
            The result of the operation.
        """
        assert ephemeral_cache_control() == {"type": "ephemeral"}
        p = openai_content_part_text("hello", cache_control=ephemeral_cache_control())
        assert p["type"] == "text" and p["cache_control"]["type"] == "ephemeral"
        sysm = openai_system_message_cached("long system", use_ephemeral_cache=True)
        assert sysm["role"] == "system"
        assert isinstance(sysm["content"], list)

    def test_check_usage_against_budget(self) -> None:
        """Execute test_check_usage_against_budget operation.

        Returns:
            The result of the operation.
        """
        u = TokenUsage(1, 2, 3, model="m", provider="openai")
        check_usage_against_budget(u, 10)
        with pytest.raises(TokenBudgetExceeded):
            check_usage_against_budget(u, 2)

    @pytest.mark.asyncio
    async def test_iter_llm_stream_with_budget_usage(self) -> None:
        """Execute test_iter_llm_stream_with_budget_usage operation.

        Returns:
            The result of the operation.
        """
        chunks: List[StreamChunk] = [
            StreamChunk(text="a", provider="openai"),
            StreamChunk(
                text="",
                provider="openai",
                usage=TokenUsage(5, 5, 10, model="", provider="openai"),
            ),
        ]
        out: List[StreamChunk] = []
        async for c in iter_llm_stream_with_budget(
            _chunks(*chunks),
            max_total_tokens=100,
            estimate_text_until_usage=False,
        ):
            out.append(c)
        assert len(out) == 2

    @pytest.mark.asyncio
    async def test_iter_llm_stream_with_budget_raises_on_estimate(self) -> None:
        """Execute test_iter_llm_stream_with_budget_raises_on_estimate operation.

        Returns:
            The result of the operation.
        """
        big = "x" * 400
        chunks = [StreamChunk(text=big, provider="openai")]
        with pytest.raises(TokenBudgetExceeded):
            async for _ in iter_llm_stream_with_budget(
                _chunks(*chunks),
                max_total_tokens=50,
                estimate_text_until_usage=True,
                chars_per_token=4.0,
            ):
                pass
