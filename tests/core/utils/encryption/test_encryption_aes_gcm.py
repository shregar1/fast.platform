from __future__ import annotations
"""Tests for :class:`utils.encryption.AesGcmEncryption`."""
from tests.core.utils.encryption.abstraction import IEncryptionUtilsTests



import pytest

from utils.encryption import AesGcmEncryption


class TestAesGcmEncryption(IEncryptionUtilsTests):
    def test_aes_gcm_roundtrip(self) -> None:
        key = AesGcmEncryption.generate_key(256)
        aes = AesGcmEncryption(key)
        plain = b"payload"
        assert aes.decrypt(aes.encrypt(plain)) == plain

    def test_aes_gcm_aad(self) -> None:
        key = AesGcmEncryption.generate_key(256)
        aes = AesGcmEncryption(key)
        aad = b"context"
        ct = aes.encrypt(b"data", associated_data=aad)
        assert aes.decrypt(ct, associated_data=aad) == b"data"
        with pytest.raises(Exception):
            aes.decrypt(ct, associated_data=b"wrong")

    def test_aes_gcm_bad_key_len(self) -> None:
        with pytest.raises(ValueError, match="16, 24, or 32"):
            AesGcmEncryption(b"short")
