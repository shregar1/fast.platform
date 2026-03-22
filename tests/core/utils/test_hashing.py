from __future__ import annotations
"""Tests for :mod:`utils.hashing`."""
from tests.core.utils.abstraction import IUtilsTests



import hashlib
import tempfile
from pathlib import Path

from utils.hashing import HashingUtility


class TestHashingUtility(IUtilsTests):
    def test_sha256_hex_matches_hashlib(self) -> None:
        data = b"hello"
        assert HashingUtility.sha256_hex(data) == hashlib.sha256(data).hexdigest()

    def test_sha512_hex_matches_hashlib(self) -> None:
        data = b"hello"
        assert HashingUtility.sha512_hex(data) == hashlib.sha512(data).hexdigest()

    def test_blake2b_hex(self) -> None:
        data = b"x"
        assert HashingUtility.blake2b_hex(data) == hashlib.blake2b(data, digest_size=32).hexdigest()

    def test_hmac_sha256_hex(self) -> None:
        k, d = b"key", b"data"
        assert HashingUtility.hmac_sha256_hex(k, d) == __import__("hmac").new(k, d, hashlib.sha256).hexdigest()

    def test_hash_file_streams(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"abc" * 10000)
            path = Path(f.name)
        try:
            assert HashingUtility.hash_file(path) == hashlib.sha256(b"abc" * 10000).hexdigest()
        finally:
            path.unlink()
