"""Module test_llm_provider_keys_safe_decrypt.py."""

from __future__ import annotations

"""Tests for ``safe_decrypt`` (``sec.security.llm_provider_keys``)."""
import pytest

from tests.sec.security._llm_provider_keys_load import safe_decrypt
from tests.sec.security.abstraction import ISecurityTests


class TestLlmProviderKeysSafeDecrypt(ISecurityTests):
    """Represents the TestLlmProviderKeysSafeDecrypt class."""

    def test_safe_decrypt_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Execute test_safe_decrypt_invalid operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        monkeypatch.setenv("LLM_PROVIDER_KEYS_SECRET", "a")
        assert safe_decrypt("not-a-fernet-token!!!") is None
