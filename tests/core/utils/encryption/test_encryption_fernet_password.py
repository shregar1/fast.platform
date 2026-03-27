"""Module test_encryption_fernet_password.py."""

from __future__ import annotations

"""Tests for Fernet password-based helpers on :class:`utils.encryption.FernetEncryption`."""
import pytest

from tests.core.utils.encryption.abstraction import IEncryptionUtilsTests
from core.utils.encryption import FernetEncryption


class TestFernetPasswordBased(IEncryptionUtilsTests):
    """Represents the TestFernetPasswordBased class."""

    def test_password_based_roundtrip(self) -> None:
        """Execute test_password_based_roundtrip operation.

        Returns:
            The result of the operation.
        """
        salt, ct = FernetEncryption.encrypt_with_password("user-password", b"hello")
        assert FernetEncryption.decrypt_with_password("user-password", salt, ct) == b"hello"

    def test_password_based_wrong_password(self) -> None:
        """Execute test_password_based_wrong_password operation.

        Returns:
            The result of the operation.
        """
        salt, ct = FernetEncryption.encrypt_with_password("a", b"data")
        with pytest.raises(Exception):
            FernetEncryption.decrypt_with_password("b", salt, ct)
