"""Google Gemini (Google AI Studio)."""

from __future__ import annotations

from typing import Any, Optional

from core.errors.llm_dependency_error import LLMDependencyError


class GeminiLLMService:
    """Google Gemini via ``google-generativeai`` (Google AI Studio key)."""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None) -> None:
        try:
            import google.generativeai as genai
        except ImportError as e:  # pragma: no cover
            raise LLMDependencyError(
                provider="gemini",
                pip_extra="fast_llm[gemini]",
                cause=e,
            ) from e
        genai.configure(api_key=api_key)
        self._genai = genai
        self._gemini_model = genai.GenerativeModel(model)
        self._model_name = model
        _ = base_url

    async def _generate_response(self, prompt: str, *, max_tokens: int) -> Any:
        gc = self._genai.GenerationConfig(max_output_tokens=max_tokens)
        return await self._gemini_model.generate_content_async(prompt, generation_config=gc)

    @staticmethod
    def _extract_text(resp: Any) -> str:
        t = getattr(resp, "text", None)
        if t:
            return str(t)
        for c in getattr(resp, "candidates", None) or []:
            content = getattr(c, "content", None)
            if not content:
                continue
            for p in getattr(content, "parts", []) or []:
                tx = getattr(p, "text", None)
                if tx:
                    return str(tx)
        return ""

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        resp = await self._generate_response(prompt, max_tokens=max_tokens)
        return self._extract_text(resp)


__all__ = ["GeminiLLMService"]
