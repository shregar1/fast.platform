from __future__ import annotations

"""Tests for :class:`utils.encryption.FernetEncryption`."""
from tests.core.utils.encryption.abstraction import IEncryptionUtilsTests
from core.utils.encryption import FernetEncryption


class TestFernetEncryption(IEncryptionUtilsTests):
    def test_fernet_roundtrip(self) -> None:
        key = FernetEncryption.generate_key()
        f = FernetEncryption(key)
        plain = b"secret-bytes"
        assert f.decrypt(f.encrypt(plain)) == plain

    def test_fernet_string_key(self) -> None:
        key = FernetEncryption.random_key_string()
        f = FernetEncryption(key)
        assert f.decrypt(f.encrypt(b"x")) == b"x"

    def test_fernet_decrypt_optional_invalid(self) -> None:
        f = FernetEncryption(FernetEncryption.generate_key())
        assert f.decrypt_optional(b"not-a-token") is None
