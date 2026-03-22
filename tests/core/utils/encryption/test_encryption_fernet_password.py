from __future__ import annotations
"""Tests for Fernet password-based helpers on :class:`utils.encryption.FernetEncryption`."""
from tests.core.utils.encryption.abstraction import IEncryptionUtilsTests



import pytest

from utils.encryption import FernetEncryption


class TestFernetPasswordBased(IEncryptionUtilsTests):
    def test_password_based_roundtrip(self) -> None:
        salt, ct = FernetEncryption.encrypt_with_password("user-password", b"hello")
        assert FernetEncryption.decrypt_with_password("user-password", salt, ct) == b"hello"

    def test_password_based_wrong_password(self) -> None:
        salt, ct = FernetEncryption.encrypt_with_password("a", b"data")
        with pytest.raises(Exception):
            FernetEncryption.decrypt_with_password("b", salt, ct)
