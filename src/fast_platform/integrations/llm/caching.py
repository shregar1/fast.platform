"""Prompt-cache control helpers for OpenAI and Anthropic APIs.

Both providers support ``cache_control`` on **content blocks** (e.g. long static prompts).
Pass the returned dicts through unchanged in your ``messages`` / ``system`` payloads.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional, Union

CacheControl = Dict[str, str]


def ephemeral_cache_control() -> CacheControl:
    """Anthropic / OpenAI prompt-cache: mark a block as eligible for ephemeral caching."""
    return {"type": "ephemeral"}


def openai_content_part_text(
    text: str,
    *,
    cache_control: Optional[Union[CacheControl, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """OpenAI Responses / Chat **content part** with optional ``cache_control``.

    When using providers that support prompt caching, attach ``cache_control`` to large
    static segments (system prompt, tool definitions, RAG context).
    """
    part: Dict[str, Any] = {"type": "text", "text": text}
    if cache_control is not None:
        part["cache_control"] = cache_control
    return part


def anthropic_text_block(
    text: str,
    *,
    cache_control: Optional[Union[CacheControl, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Anthropic message **content** block (``type: text``) with optional ``cache_control``."""
    block: Dict[str, Any] = {"type": "text", "text": text}
    if cache_control is not None:
        block["cache_control"] = cache_control
    return block


def anthropic_cached_text(
    text: str,
    *,
    ttl: Literal["5m", "1h"] = "5m",
) -> Dict[str, Any]:
    """Anthropic prompt cache with explicit TTL (``cache_control`` ``type: ephemeral`` + ``ttl``).

    Older SDKs may only support ``{"type": "ephemeral"}``; use :func:`ephemeral_cache_control` then.
    """
    cc: Dict[str, Any] = {"type": "ephemeral", "ttl": ttl}
    return anthropic_text_block(text, cache_control=cc)


def openai_system_message_cached(
    text: str,
    *,
    use_ephemeral_cache: bool = True,
) -> Dict[str, Any]:
    """Build a **system** message whose content uses cache control (OpenAI-compatible structure).

    Shape: ``{"role": "system", "content": [ openai_content_part_text(...) ] }``
    """
    cc = ephemeral_cache_control() if use_ephemeral_cache else None
    return {
        "role": "system",
        "content": [openai_content_part_text(text, cache_control=cc)],
    }
