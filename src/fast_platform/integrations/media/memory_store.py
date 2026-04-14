from __future__ import annotations
"""In-memory :class:`~fast_media.abstractions.IMediaStore` for tests and local dev."""

from ...data.storage.constants import MEMORY_URL_PREFIX

from typing import BinaryIO, Optional

from .abstraction import IMediaStore, UploadResult


class InMemoryMediaStore(IMediaStore):
    """Simple dict-backed store; URLs are synthetic ``memory://`` URIs."""

    def __init__(self, base_url: str = MEMORY_URL_PREFIX) -> None:
        """Execute __init__ operation.

        Args:
            base_url: The base_url parameter.
        """
        self._base = base_url.rstrip("/") + "/"
        self._blobs: dict[str, bytes] = {}
        self._content_type: dict[str, Optional[str]] = {}
        self._metadata: dict[str, dict[str, str]] = {}

    def upload(
        self,
        key: str,
        body: bytes | BinaryIO,
        *,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> UploadResult:
        """Execute upload operation.

        Args:
            key: The key parameter.
            body: The body parameter.
            content_type: The content_type parameter.
            metadata: The metadata parameter.

        Returns:
            The result of the operation.
        """
        raw = body if isinstance(body, bytes) else body.read()
        self._blobs[key] = raw
        self._content_type[key] = content_type
        self._metadata[key] = dict(metadata or {})
        return UploadResult(
            key=key,
            url=self.get_url(key),
            size=len(raw),
            content_type=content_type,
            metadata=dict(metadata or {}),
        )

    def get_bytes(self, key: str) -> bytes:
        """Execute get_bytes operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        if key not in self._blobs:
            raise KeyError(key)
        return self._blobs[key]

    def get_url(self, key: str) -> str:
        """Execute get_url operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        return f"{self._base}{key}"

    def presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Execute presigned_url operation.

        Args:
            key: The key parameter.
            expires_in: The expires_in parameter.

        Returns:
            The result of the operation.
        """
        return self.get_url(key)

    def delete(self, key: str) -> None:
        """Execute delete operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        self._blobs.pop(key, None)
        self._content_type.pop(key, None)
        self._metadata.pop(key, None)


__all__ = ["InMemoryMediaStore"]
