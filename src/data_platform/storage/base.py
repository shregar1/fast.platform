"""
Storage backend interface and factory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, BinaryIO, Optional

from fast_platform import StorageConfiguration

from .abstraction import IStorage

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class StorageObjectHead:
    """Metadata from a HEAD/stat on an object."""

    size: int
    content_type: Optional[str] = None
    etag: Optional[str] = None
    last_modified: Optional[datetime] = None


class IStorageBackend(IStorage, ABC):
    """Interface for object storage backends (S3, GCS, Azure Blob, local)."""

    name: str

    @abstractmethod
    def upload(
        self,
        key: str,
        body: bytes | BinaryIO,
        *,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        """Upload object; return URL or path."""
        raise NotImplementedError

    @abstractmethod
    def download(self, key: str) -> bytes:
        """Download object as bytes."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete object."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Return whether the object exists."""
        raise NotImplementedError

    @abstractmethod
    def head(self, key: str) -> StorageObjectHead:
        """Return object metadata. Raise ``FileNotFoundError`` if missing."""
        raise NotImplementedError

    def presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Return presigned GET URL if supported, else None."""
        return None


def build_storage_backend(backend: str = "s3") -> Optional[IStorageBackend]:
    """
    Build a storage backend from StorageConfiguration (config/storage/config.json).

    backend: "s3" | "gcs" | "azure_blob" | "local"
    """
    cfg = StorageConfiguration().get_config()

    # Imports are inside the factory to avoid circular imports (backends import this module).
    if backend == "s3" and getattr(cfg.s3, "enabled", False) and cfg.s3.bucket:
        try:
            from .s3_backend import S3StorageBackend
        except ImportError:  # pragma: no cover - optional boto
            return None
        return S3StorageBackend(
            bucket=cfg.s3.bucket,
            region=cfg.s3.region,
            endpoint_url=cfg.s3.endpoint_url,
            access_key_id=cfg.s3.access_key_id,
            secret_access_key=cfg.s3.secret_access_key,
            base_path=cfg.s3.base_path or "",
        )

    if backend == "gcs" and getattr(cfg.gcs, "enabled", False) and cfg.gcs.bucket:
        try:
            from .gcs_backend import GCSStorageBackend
        except ImportError:  # pragma: no cover
            return None
        return GCSStorageBackend(
            bucket=cfg.gcs.bucket,
            credentials_path=cfg.gcs.credentials_json_path,
            base_path=cfg.gcs.base_path or "",
        )

    if (
        backend == "azure_blob"
        and getattr(cfg.azure_blob, "enabled", False)
        and cfg.azure_blob.container
    ):
        try:
            from .azure_backend import AzureBlobStorageBackend
        except ImportError:  # pragma: no cover
            return None
        return AzureBlobStorageBackend(
            container=cfg.azure_blob.container,
            connection_string=cfg.azure_blob.connection_string,
            account_url=cfg.azure_blob.account_url,
            base_path=cfg.azure_blob.base_path or "",
        )

    if backend == "local" and getattr(cfg.local, "enabled", False):
        from .local_backend import LocalStorageBackend

        return LocalStorageBackend(
            base_dir=cfg.local.base_dir,
            base_url=cfg.local.base_url,
        )

    return None
