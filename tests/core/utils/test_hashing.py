"""Module test_hashing.py."""

from __future__ import annotations

"""Tests for :mod:`utils.hashing`."""
import hashlib
import tempfile
from pathlib import Path

from tests.core.utils.abstraction import IUtilsTests
from fast_platform.core.utils.hashing import HashingUtility


class TestHashingUtility(IUtilsTests):
    """Represents the TestHashingUtility class."""

    def test_sha256_hex_matches_hashlib(self) -> None:
        """Execute test_sha256_hex_matches_hashlib operation.

        Returns:
            The result of the operation.
        """
        data = b"hello"
        assert HashingUtility.sha256_hex(data) == hashlib.sha256(data).hexdigest()

    def test_sha512_hex_matches_hashlib(self) -> None:
        """Execute test_sha512_hex_matches_hashlib operation.

        Returns:
            The result of the operation.
        """
        data = b"hello"
        assert HashingUtility.sha512_hex(data) == hashlib.sha512(data).hexdigest()

    def test_blake2b_hex(self) -> None:
        """Execute test_blake2b_hex operation.

        Returns:
            The result of the operation.
        """
        data = b"x"
        assert HashingUtility.blake2b_hex(data) == hashlib.blake2b(data, digest_size=32).hexdigest()

    def test_hmac_sha256_hex(self) -> None:
        """Execute test_hmac_sha256_hex operation.

        Returns:
            The result of the operation.
        """
        k, d = b"key", b"data"
        assert (
            HashingUtility.hmac_sha256_hex(k, d)
            == __import__("hmac").new(k, d, hashlib.sha256).hexdigest()
        )

    def test_hash_file_streams(self) -> None:
        """Execute test_hash_file_streams operation.

        Returns:
            The result of the operation.
        """
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"abc" * 10000)
            path = Path(f.name)
        try:
            assert HashingUtility.hash_file(path) == hashlib.sha256(b"abc" * 10000).hexdigest()
        finally:
            path.unlink()
