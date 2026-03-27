"""Module test_digests.py."""

from __future__ import annotations

"""Tests for :mod:`utils.digests`."""
from tests.core.utils.abstraction import IUtilsTests
from core.utils.digests import Digests


class TestDigests(IUtilsTests):
    """Represents the TestDigests class."""

    def test_sha256_hex_utf8_matches_hashlib(self) -> None:
        """Execute test_sha256_hex_utf8_matches_hashlib operation.

        Returns:
            The result of the operation.
        """
        assert Digests.sha256_hex_utf8("a") == Digests.sha256_hex_bytes(b"a")

    def test_fernet_key_bytes_from_utf8_secret_stable(self) -> None:
        """Execute test_fernet_key_bytes_from_utf8_secret_stable operation.

        Returns:
            The result of the operation.
        """
        k = Digests.fernet_key_bytes_from_utf8_secret("same-secret")
        assert len(k) == 44
        assert Digests.fernet_key_bytes_from_utf8_secret("same-secret") == k
