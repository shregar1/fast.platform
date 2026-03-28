"""UUID generation and validation utilities."""

from __future__ import annotations

import uuid
from typing import Optional, Union

from .abstraction import IUUIDUtility


class UUIDUtility(IUUIDUtility):
    """Standardized UUID operations using the stdlib :mod:`uuid` module."""

    @staticmethod
    def v1() -> str:
        """Generate a time-based UUID (Version 1)."""
        return str(uuid.uuid1())

    @staticmethod
    def v4() -> str:
        """Generate a random UUID (Version 4)."""
        return str(uuid.uuid4())

    @staticmethod
    def v4_bytes() -> bytes:
        """Generate a random UUID and return as 16-byte buffer."""
        return uuid.uuid4().bytes

    @staticmethod
    def v5(namespace: Union[str, uuid.UUID], name: str) -> str:
        """Generate a name-based UUID using SHA-1 (Version 5)."""
        if isinstance(namespace, str):
            ns = uuid.UUID(namespace)
        else:
            ns = namespace
        return str(uuid.uuid5(ns, name))

    @staticmethod
    def is_valid(value: Optional[str]) -> bool:
        """True if *value* is a valid UUID string (any version)."""
        if not value:
            return False
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_version(value: str) -> Optional[int]:
        """Return the UUID version integer, or None if invalid string."""
        try:
            return uuid.UUID(value).version
        except ValueError:
            return None

    @staticmethod
    def to_compact(value: str) -> Optional[str]:
        """Remove hyphens from a UUID string."""
        try:
            return uuid.UUID(value).hex
        except ValueError:
            return None

    @staticmethod
    def from_compact(compact_value: str) -> Optional[str]:
        """Restore hyphens to a 32-character hex UUID string."""
        try:
            return str(uuid.UUID(compact_value))
        except ValueError:
            return None


__all__ = ["UUIDUtility", "IUUIDUtility"]
