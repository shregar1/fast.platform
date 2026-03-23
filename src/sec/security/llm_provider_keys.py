"""
Fernet encryption for user LLM provider API keys at rest.

Uses ``LLM_PROVIDER_KEYS_SECRET`` (preferred) or falls back to ``SECRET_KEY``
from the environment. The derived key is stable for the lifetime of those env vars.

Do not log plaintext keys.
"""

from __future__ import annotations

import os

from cryptography.fernet import Fernet, InvalidToken

from core.utils.digests import Digests


def _fernet() -> Fernet:
    raw = (os.getenv("LLM_PROVIDER_KEYS_SECRET") or os.getenv("SECRET_KEY") or "").strip()
    if not raw:
        raise RuntimeError(
            "Set LLM_PROVIDER_KEYS_SECRET (preferred) or SECRET_KEY for LLM provider key encryption."
        )
    return Fernet(Digests.fernet_key_bytes_from_utf8_secret(raw))


def encrypt_api_key(plaintext: str) -> str:
    """Return URL-safe base64 Fernet token (string) for storage in ``secret_ciphertext``."""

    return _fernet().encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt_api_key(ciphertext: str) -> str:
    """Decrypt a server-encrypted ``secret_ciphertext`` row."""

    return _fernet().decrypt(ciphertext.encode("ascii")).decode("utf-8")


def safe_decrypt(ciphertext: str) -> str | None:
    """Decrypt or return None if token is invalid (wrong key / corrupt data)."""

    try:
        return decrypt_api_key(ciphertext)
    except (InvalidToken, ValueError, RuntimeError):
        return None


def last_four(plaintext: str) -> str | None:
    """Last four characters for display (e.g. ``…sk-12ab``)."""

    s = (plaintext or "").strip()
    if len(s) < 4:
        return None
    return s[-4:]
