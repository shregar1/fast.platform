"""
fast_llm – LLM provider abstraction (OpenAI, Anthropic, Ollama) for FastMVC.
"""

from from fast_platform import LLMConfiguration, LLMConfigurationDTO

from .budget import (
    TokenBudgetExceeded,
    check_usage_against_budget,
    estimate_tokens_from_text,
    iter_llm_stream_with_budget,
)
from .caching import (
    anthropic_cached_text,
    anthropic_text_block,
    ephemeral_cache_control,
    openai_content_part_text,
    openai_system_message_cached,
)
from .instrumented import InstrumentedAnthropicLLMService, InstrumentedOpenAILLMService
from .providers import (
    ILLMService,
    AnthropicLLMService,
    OllamaLLMService,
    OpenAILLMService,
    build_llm_service,
)
from .streaming import StreamChunk, iter_anthropic_message_stream, iter_llm_stream, iter_openai_chat_stream
from .token_usage import TokenUsage, TokenUsageCallback
from .tools import (
    ToolDefinition,
    normalize_tools_to_anthropic,
    normalize_tools_to_openai,
    tool_definition_from_anthropic,
    tool_definition_from_openai,
    tool_definitions_to_anthropic_tools,
    tool_definitions_to_openai_tools,
)


__version__ = "0.3.0"

__all__ = [
    "ILLMService",
    "InstrumentedAnthropicLLMService",
    "InstrumentedOpenAILLMService",
    "OpenAILLMService",
    "AnthropicLLMService",
    "OllamaLLMService",
    "StreamChunk",
    "TokenUsage",
    "TokenUsageCallback",
    "TokenBudgetExceeded",
    "ToolDefinition",
    "build_llm_service",
    "check_usage_against_budget",
    "estimate_tokens_from_text",
    "iter_llm_stream_with_budget",
    "iter_anthropic_message_stream",
    "iter_llm_stream",
    "iter_openai_chat_stream",
    "ephemeral_cache_control",
    "anthropic_text_block",
    "anthropic_cached_text",
    "openai_content_part_text",
    "openai_system_message_cached",
    "tool_definitions_to_openai_tools",
    "tool_definitions_to_anthropic_tools",
    "tool_definition_from_openai",
    "tool_definition_from_anthropic",
    "normalize_tools_to_openai",
    "normalize_tools_to_anthropic",
    "LLMConfiguration",
    "LLMConfigurationDTO",
]
