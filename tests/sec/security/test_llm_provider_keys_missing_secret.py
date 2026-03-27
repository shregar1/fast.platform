"""Module test_llm_provider_keys_missing_secret.py."""

from __future__ import annotations

"""Tests for missing secret behavior (``sec.security.llm_provider_keys``)."""
import pytest

from tests.sec.security._llm_provider_keys_load import encrypt_api_key
from tests.sec.security.abstraction import ISecurityTests


class TestLlmProviderKeysMissingSecret(ISecurityTests):
    """Represents the TestLlmProviderKeysMissingSecret class."""

    def test_missing_secret_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Execute test_missing_secret_raises operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        monkeypatch.delenv("LLM_PROVIDER_KEYS_SECRET", raising=False)
        monkeypatch.delenv("SECRET_KEY", raising=False)
        with pytest.raises(RuntimeError):
            encrypt_api_key("x")
