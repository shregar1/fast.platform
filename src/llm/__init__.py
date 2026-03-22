"""
fast_llm – LLM provider abstraction (OpenAI, Anthropic, Ollama, Groq, Mistral, Gemini) for FastMVC.
"""

from errors import (
    LLMDependencyError,
    LLMFeatureNotAvailableError,
    UnsupportedLLMProviderError,
)

from fast_platform import LLMConfiguration, LLMConfigurationDTO

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
from .constants import GROQ_DEFAULT_BASE_URL, MISTRAL_DEFAULT_BASE_URL
from .instrumented import (
    InstrumentedAnthropicLLMService,
    InstrumentedGeminiLLMService,
    InstrumentedGroqLLMService,
    InstrumentedMistralLLMService,
    InstrumentedOpenAILLMService,
)
from .providers import (
    AnthropicLLMService,
    GeminiLLMService,
    GroqLLMService,
    ILLMService,
    MistralLLMService,
    OllamaLLMService,
    OpenAILLMService,
    build_llm_service,
)
from .streaming import (
    OpenAICompatibleStreamProvider,
    StreamChunk,
    iter_anthropic_message_stream,
    iter_llm_stream,
    iter_openai_chat_stream,
)
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


__version__ = "0.4.0"

__all__ = [
    "GROQ_DEFAULT_BASE_URL",
    "ILLMService",
    "LLMDependencyError",
    "LLMFeatureNotAvailableError",
    "MISTRAL_DEFAULT_BASE_URL",
    "UnsupportedLLMProviderError",
    "InstrumentedAnthropicLLMService",
    "InstrumentedGeminiLLMService",
    "InstrumentedGroqLLMService",
    "InstrumentedMistralLLMService",
    "InstrumentedOpenAILLMService",
    "OpenAILLMService",
    "AnthropicLLMService",
    "GeminiLLMService",
    "GroqLLMService",
    "MistralLLMService",
    "OllamaLLMService",
    "OpenAICompatibleStreamProvider",
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
