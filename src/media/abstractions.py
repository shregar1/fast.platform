"""
Media upload and URL abstractions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, BinaryIO, Optional


@dataclass
class UploadResult:
    """Result of an upload."""

    key: str
    url: str
    size: int
    content_type: Optional[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class IMediaStore(ABC):
    """
    Interface for media storage: upload, download URL / presigned URL, delete.
    Can be backed by fast_storage or custom S3/GCS.
    """

    @abstractmethod
    def upload(
        self,
        key: str,
        body: bytes | BinaryIO,
        *,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> UploadResult:
        """Upload file; return key and URL (or path)."""
        raise NotImplementedError

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Return public or permanent URL for the key."""
        raise NotImplementedError

    @abstractmethod
    def presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Return a temporary URL for GET."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete object at key."""
        raise NotImplementedError


class IImageVariantGenerator(ABC):
    """Generate image variants (resize, format) from an uploaded file."""

    @abstractmethod
    def generate(
        self,
        source_key: str,
        variant_name: str,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: Optional[str] = None,
        quality: Optional[int] = None,
    ) -> str:
        """
        Generate variant; store and return new key (e.g. thumbs/abc_200x200.webp).
        """
        raise NotImplementedError
