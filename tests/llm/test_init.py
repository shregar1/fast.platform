"""Tests for llm."""

import pytest


def test_imports():
    from llm import (
        ILLMService,
        InstrumentedOpenAILLMService,
        StreamChunk,
        TokenUsage,
        build_llm_service,
        iter_llm_stream,
        LLMConfiguration,
        LLMConfigurationDTO,
    )
    assert build_llm_service is not None
    assert TokenUsage is not None
    assert StreamChunk is not None
    assert iter_llm_stream is not None
    assert InstrumentedOpenAILLMService is not None
