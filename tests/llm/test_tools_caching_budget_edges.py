"""Edge cases for tools, caching, budget, token_usage."""

from __future__ import annotations

import pytest

from llm.budget import estimate_tokens_from_text
from llm.caching import anthropic_cached_text, anthropic_text_block, openai_system_message_cached
from llm.token_usage import TokenUsage
from llm.tools import normalize_tools_to_anthropic, normalize_tools_to_openai, tool_definition_from_openai


def test_estimate_tokens_empty() -> None:
    assert estimate_tokens_from_text("") == 0


def test_tool_definition_from_openai_plain_function_dict() -> None:
    t = tool_definition_from_openai({"name": "n", "description": "d", "parameters": "bad"})
    assert t.parameters["type"] == "object"


def test_normalize_tools_mixed_else_branch() -> None:
    # neither openai wrapper nor input_schema — falls through to from_openai
    raw = {"name": "x", "description": "y", "parameters": {"type": "object"}}
    oa = normalize_tools_to_openai([raw])
    assert oa[0]["function"]["name"] == "x"
    an = normalize_tools_to_anthropic([raw])
    assert an[0]["name"] == "x"


def test_anthropic_cached_text_and_blocks() -> None:
    b = anthropic_cached_text("long", ttl="1h")
    assert b["cache_control"]["ttl"] == "1h"
    plain = anthropic_text_block("t", cache_control=None)
    assert "cache_control" not in plain


def test_openai_system_no_cache() -> None:
    m = openai_system_message_cached("sys", use_ephemeral_cache=False)
    part = m["content"][0]
    assert "cache_control" not in part


def test_token_usage_openai_no_usage() -> None:
    resp = type("R", (), {"usage": None})()
    u = TokenUsage.from_openai_completion(resp, model="m")
    assert u.total_tokens == 0


def test_token_usage_anthropic_no_usage() -> None:
    resp = type("R", (), {"usage": None})()
    u = TokenUsage.from_anthropic_message(resp, model="m")
    assert u.total_tokens == 0


def test_tool_definition_from_anthropic_non_dict_schema() -> None:
    from llm.tools import tool_definition_from_anthropic

    t = tool_definition_from_anthropic(
        {"name": "n", "description": "d", "input_schema": "not-a-dict"}
    )
    assert t.parameters.get("type") == "object"
