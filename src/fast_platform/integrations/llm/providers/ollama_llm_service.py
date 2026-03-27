"""Local Ollama HTTP client (``/api/chat``)."""

from __future__ import annotations

from core.errors.llm_dependency_error import LLMDependencyError


class OllamaLLMService:
    """Call a local Ollama server over HTTP (``/api/chat``)."""

    def __init__(self, base_url: str, model: str) -> None:
        """Execute __init__ operation.

        Args:
            base_url: The base_url parameter.
            model: The model parameter.
        """
        try:
            import httpx
        except ImportError as e:  # pragma: no cover
            raise LLMDependencyError(
                provider="ollama",
                pip_extra="fast_llm[ollama]",
                cause=e,
            ) from e
        self._httpx = httpx
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        """Execute generate operation.

        Args:
            prompt: The prompt parameter.
            max_tokens: The max_tokens parameter.

        Returns:
            The result of the operation.
        """
        async with self._httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"num_predict": max_tokens},
                },
            )
            r.raise_for_status()
            data = r.json()
            msg = data.get("message") or {}
            return str(msg.get("content") or "")


__all__ = ["OllamaLLMService"]
