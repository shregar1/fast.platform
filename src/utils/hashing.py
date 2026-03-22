"""
Cryptographic hashing helpers (HMAC, streaming file digests).

This module complements :mod:`utils.digests`, which centralizes SHA-256 hex for
strings and Fernet key material. Use :class:`HashingUtility` when you need
additional algorithms, HMAC, BLAKE2b, or streaming digests over on-disk files
without loading the whole file into memory.
"""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
from typing import Union

from .abstraction import IUtility

__all__ = ["HashingUtility"]


class HashingUtility(IUtility):
    """
    General-purpose hashing beyond :class:`~utils.digests.Digests`.

    :class:`~utils.digests.Digests` is the right choice for API-key style
    SHA-256 over UTF-8 strings and Fernet key derivation shared with other
    packages. :class:`HashingUtility` adds SHA-512, BLAKE2b, HMAC variants, and
    file streaming for integrity checks, caches, and generic content addressing.

    All hex outputs use lowercase letters, consistent with :func:`bytes.hex`
    and typical REST / hex-digest conventions.
    """

    @staticmethod
    def sha256_hex(data: bytes) -> str:
        """
        Return the lowercase hexadecimal SHA-256 digest of *data*.

        Parameters
        ----------
        data:
            Arbitrary bytes to hash (entire payload in memory).

        Returns
        -------
        str
            64-character lowercase hex string (256 bits).
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512_hex(data: bytes) -> str:
        """
        Return the lowercase hexadecimal SHA-512 digest of *data*.

        Parameters
        ----------
        data:
            Arbitrary bytes to hash.

        Returns
        -------
        str
            128-character lowercase hex string (512 bits).
        """
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def blake2b_hex(data: bytes, *, digest_size: int = 32) -> str:
        """
        Return the lowercase hexadecimal BLAKE2b digest of *data*.

        BLAKE2b is often faster than SHA-256 on modern CPUs and supports a
        configurable digest length. The default matches a 32-byte (256-bit) digest.

        Parameters
        ----------
        data:
            Payload to hash.
        digest_size:
            BLAKE2b digest length in bytes (must be valid for :func:`hashlib.blake2b`).

        Returns
        -------
        str
            Lowercase hex string of length ``2 * digest_size``.
        """
        return hashlib.blake2b(data, digest_size=digest_size).hexdigest()

    @staticmethod
    def hmac_sha256_hex(key: bytes, data: bytes) -> str:
        """
        Compute HMAC-SHA256 and return the digest as lowercase hex.

        Use when you need a secret-dependent MAC (e.g. signed tokens, webhook
        signatures) rather than a plain collision-resistant hash.

        Parameters
        ----------
        key:
            Secret key material; length is not enforced here—choose per your threat model.
        data:
            Message or payload to authenticate.

        Returns
        -------
        str
            64-character lowercase hex HMAC-SHA256 digest.
        """
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def hmac_sha512_hex(key: bytes, data: bytes) -> str:
        """
        Compute HMAC-SHA512 and return the digest as lowercase hex.

        Parameters
        ----------
        key:
            Secret key material.
        data:
            Message or payload to authenticate.

        Returns
        -------
        str
            128-character lowercase hex HMAC-SHA512 digest.
        """
        return hmac.new(key, data, hashlib.sha512).hexdigest()

    @staticmethod
    def hash_file(
        path: Union[str, Path],
        *,
        algorithm: str = "sha256",
        chunk_size: int = 1024 * 1024,
    ) -> str:
        """
        Stream-hash a file and return a lowercase hex digest.

        Reads the file in chunks so large objects can be digested without
        holding them fully in memory. Raises if the path cannot be opened for
        reading (e.g. missing file or permission error).

        Parameters
        ----------
        path:
            Filesystem path to the file to hash.
        algorithm:
            Name accepted by :func:`hashlib.new`, e.g. ``"sha256"``, ``"sha512"``, ``"blake2b"``.
        chunk_size:
            Number of bytes read per iteration; larger values reduce syscall overhead.

        Returns
        -------
        str
            Lowercase hex digest string for the chosen algorithm.
        """
        p = Path(path)
        h = hashlib.new(algorithm)
        with p.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
