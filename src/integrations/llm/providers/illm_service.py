"""Structural typing contract for LLM backends."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ILLMService(Protocol):
    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        """Run a single user-message completion and return assistant text."""


__all__ = ["ILLMService"]
