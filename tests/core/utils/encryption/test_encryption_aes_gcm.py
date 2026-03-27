"""Module test_encryption_aes_gcm.py."""

from __future__ import annotations

"""Tests for :class:`utils.encryption.AesGcmEncryption`."""
import pytest

from tests.core.utils.encryption.abstraction import IEncryptionUtilsTests
from core.utils.encryption import AesGcmEncryption


class TestAesGcmEncryption(IEncryptionUtilsTests):
    """Represents the TestAesGcmEncryption class."""

    def test_aes_gcm_roundtrip(self) -> None:
        """Execute test_aes_gcm_roundtrip operation.

        Returns:
            The result of the operation.
        """
        key = AesGcmEncryption.generate_key(256)
        aes = AesGcmEncryption(key)
        plain = b"payload"
        assert aes.decrypt(aes.encrypt(plain)) == plain

    def test_aes_gcm_aad(self) -> None:
        """Execute test_aes_gcm_aad operation.

        Returns:
            The result of the operation.
        """
        key = AesGcmEncryption.generate_key(256)
        aes = AesGcmEncryption(key)
        aad = b"context"
        ct = aes.encrypt(b"data", associated_data=aad)
        assert aes.decrypt(ct, associated_data=aad) == b"data"
        with pytest.raises(Exception):
            aes.decrypt(ct, associated_data=b"wrong")

    def test_aes_gcm_bad_key_len(self) -> None:
        """Execute test_aes_gcm_bad_key_len operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError, match="16, 24, or 32"):
            AesGcmEncryption(b"short")
