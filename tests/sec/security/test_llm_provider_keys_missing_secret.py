from __future__ import annotations

"""Tests for missing secret behavior (``sec.security.llm_provider_keys``)."""
import pytest

from tests.sec.security._llm_provider_keys_load import encrypt_api_key
from tests.sec.security.abstraction import ISecurityTests


class TestLlmProviderKeysMissingSecret(ISecurityTests):
    def test_missing_secret_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("LLM_PROVIDER_KEYS_SECRET", raising=False)
        monkeypatch.delenv("SECRET_KEY", raising=False)
        with pytest.raises(RuntimeError):
            encrypt_api_key("x")
