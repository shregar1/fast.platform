"""
In-memory :class:`~fast_media.abstractions.IMediaStore` for tests and local dev.
"""

from __future__ import annotations

from typing import BinaryIO, Optional

from .abstraction import IMediaStore, UploadResult


class InMemoryMediaStore(IMediaStore):
    """Simple dict-backed store; URLs are synthetic ``memory://`` URIs."""

    def __init__(self, base_url: str = "memory://") -> None:
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
        if key not in self._blobs:
            raise KeyError(key)
        return self._blobs[key]

    def get_url(self, key: str) -> str:
        return f"{self._base}{key}"

    def presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.get_url(key)

    def delete(self, key: str) -> None:
        self._blobs.pop(key, None)
        self._content_type.pop(key, None)
        self._metadata.pop(key, None)


__all__ = ["InMemoryMediaStore"]
