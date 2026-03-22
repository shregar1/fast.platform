"""Google Cloud Storage backend."""

from __future__ import annotations

from typing import BinaryIO, Optional

from .base import IStorageBackend, StorageObjectHead


class GCSStorageBackend(IStorageBackend):
    """Google Cloud Storage backend."""

    name = "gcs"

    def __init__(
        self,
        bucket: str,
        credentials_path: Optional[str] = None,
        base_path: str = "",
    ):
        try:
            from google.cloud import storage
        except ImportError as e:
            raise RuntimeError("google-cloud-storage is required for GCS. Install: pip install fast_storage[gcs]") from e
        if credentials_path:
            self._client = storage.Client.from_service_account_json(credentials_path)
        else:
            self._client = storage.Client()
        self._bucket_name = bucket
        self._base = (base_path.rstrip("/") + "/") if base_path else ""

    def _key(self, key: str) -> str:
        return self._base + key.lstrip("/")

    def upload(
        self,
        key: str,
        body: bytes | BinaryIO,
        *,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(self._key(key))
        if isinstance(body, bytes):
            blob.upload_from_string(body, content_type=content_type)
        else:
            blob.upload_from_file(body, content_type=content_type)
        return f"gs://{self._bucket_name}/{self._key(key)}"

    def download(self, key: str) -> bytes:
        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(self._key(key))
        return blob.download_as_bytes()

    def delete(self, key: str) -> None:
        bucket = self._client.bucket(self._bucket_name)
        bucket.blob(self._key(key)).delete()

    def exists(self, key: str) -> bool:
        bucket = self._client.bucket(self._bucket_name)
        return bucket.blob(self._key(key)).exists()

    def head(self, key: str) -> StorageObjectHead:
        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(self._key(key))
        if not blob.exists():
            raise FileNotFoundError(self._key(key))
        blob.reload()
        lm = blob.updated
        return StorageObjectHead(
            size=int(blob.size or 0),
            content_type=blob.content_type,
            etag=blob.etag,
            last_modified=lm,
        )

    def presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        from datetime import timedelta
        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(self._key(key))
        return blob.generate_signed_url(expiration=timedelta(seconds=expires_in))
