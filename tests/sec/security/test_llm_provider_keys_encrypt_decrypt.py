"""Module test_llm_provider_keys_encrypt_decrypt.py."""

from __future__ import annotations

"""Tests for encrypt/decrypt round-trip (``sec.security.llm_provider_keys``)."""
import pytest

from tests.sec.security._llm_provider_keys_load import decrypt_api_key, encrypt_api_key
from tests.sec.security.abstraction import ISecurityTests


class TestLlmProviderKeysEncryptDecrypt(ISecurityTests):
    """Represents the TestLlmProviderKeysEncryptDecrypt class."""

    def test_encrypt_decrypt_roundtrip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Execute test_encrypt_decrypt_roundtrip operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        monkeypatch.setenv("LLM_PROVIDER_KEYS_SECRET", "test-secret-for-fernet")
        plain = "sk-test-key-12345"
        ct = encrypt_api_key(plain)
        assert ct != plain
        assert decrypt_api_key(ct) == plain
