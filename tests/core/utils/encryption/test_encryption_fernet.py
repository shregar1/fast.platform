"""Module test_encryption_fernet.py."""

from __future__ import annotations

"""Tests for :class:`utils.encryption.FernetEncryption`."""
from tests.core.utils.encryption.abstraction import IEncryptionUtilsTests
from fast_platform.core.utils.encryption import FernetEncryption


class TestFernetEncryption(IEncryptionUtilsTests):
    """Represents the TestFernetEncryption class."""

    def test_fernet_roundtrip(self) -> None:
        """Execute test_fernet_roundtrip operation.

        Returns:
            The result of the operation.
        """
        key = FernetEncryption.generate_key()
        f = FernetEncryption(key)
        plain = b"secret-bytes"
        assert f.decrypt(f.encrypt(plain)) == plain

    def test_fernet_string_key(self) -> None:
        """Execute test_fernet_string_key operation.

        Returns:
            The result of the operation.
        """
        key = FernetEncryption.random_key_string()
        f = FernetEncryption(key)
        assert f.decrypt(f.encrypt(b"x")) == b"x"

    def test_fernet_decrypt_optional_invalid(self) -> None:
        """Execute test_fernet_decrypt_optional_invalid operation.

        Returns:
            The result of the operation.
        """
        f = FernetEncryption(FernetEncryption.generate_key())
        assert f.decrypt_optional(b"not-a-token") is None
