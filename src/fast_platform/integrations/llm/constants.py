"""Default URLs and other LLM provider constants."""

from __future__ import annotations

from typing import Final

GROQ_DEFAULT_BASE_URL: Final[str] = "https://api.groq.com/openai/v1"
MISTRAL_DEFAULT_BASE_URL: Final[str] = "https://api.mistral.ai/v1"
OPENAI_PROVIDER: Final[str] = "openai"
ANTHROPIC_PROVIDER: Final[str] = "anthropic"
GEMINI_PROVIDER: Final[str] = "gemini"
GROQ_PROVIDER: Final[str] = "groq"
MISTRAL_PROVIDER: Final[str] = "mistral"
OLLAMA_PROVIDER: Final[str] = "ollama"
OLLAMA_DEFAULT_BASE_URL: Final[str] = "http://localhost:11434"

__all__ = [
    "GROQ_DEFAULT_BASE_URL",
    "MISTRAL_DEFAULT_BASE_URL",
    "OPENAI_PROVIDER",
    "ANTHROPIC_PROVIDER",
    "GEMINI_PROVIDER",
    "GROQ_PROVIDER",
    "MISTRAL_PROVIDER",
    "OLLAMA_PROVIDER",
    "OLLAMA_DEFAULT_BASE_URL",
]
