"""Tests for llm."""

from tests.integrations.llm.abstraction import ILLMTests


class TestInit(ILLMTests):
    def test_imports(self) -> None:
        from integrations.llm import (
            ILLMService,
            InstrumentedOpenAILLMService,
            LLMConfiguration,
            LLMConfigurationDTO,
            StreamChunk,
            TokenUsage,
            build_llm_service,
            iter_llm_stream,
        )

        assert ILLMService is not None
        assert InstrumentedOpenAILLMService is not None
        assert LLMConfiguration is not None
        assert LLMConfigurationDTO is not None
        assert StreamChunk is not None
        assert TokenUsage is not None
        assert build_llm_service is not None
        assert iter_llm_stream is not None
