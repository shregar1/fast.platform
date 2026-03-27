"""Google Cloud Storage integration."""

from typing import Optional, BinaryIO, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GCSObject:
    """GCS object."""

    name: str
    bucket: str
    size: int
    time_created: datetime
    etag: str
    content_type: str


class GCSClient:
    """Google Cloud Storage client."""

    def __init__(
        self,
        bucket: Optional[str] = None,
        project: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ):
        """Execute __init__ operation.

        Args:
            bucket: The bucket parameter.
            project: The project parameter.
            credentials_path: The credentials_path parameter.
        """
        self.bucket = bucket
        self.project = project
        self.credentials_path = credentials_path
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                from google.cloud import storage

                if self.credentials_path:
                    self._client = storage.Client.from_service_account_json(
                        self.credentials_path, project=self.project
                    )
                else:
                    self._client = storage.Client(project=self.project)
            except ImportError:
                raise ImportError("google-cloud-storage required for GCSClient")
        return self._client

    async def upload_file(
        self,
        name: str,
        file: BinaryIO,
        bucket: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> GCSObject:
        """Upload a file to GCS."""
        client = self._get_client()
        bucket_name = bucket or self.bucket

        if not bucket_name:
            raise ValueError("bucket required")

        bucket_obj = client.bucket(bucket_name)
        blob = bucket_obj.blob(name)

        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool, lambda: blob.upload_from_file(file, content_type=content_type)
            )

        return GCSObject(
            name=blob.name,
            bucket=bucket_name,
            size=blob.size or 0,
            time_created=blob.time_created or datetime.utcnow(),
            etag=blob.etag or "",
            content_type=blob.content_type or "application/octet-stream",
        )

    async def download_file(self, name: str, bucket: Optional[str] = None) -> bytes:
        """Download a file from GCS."""
        client = self._get_client()
        bucket_name = bucket or self.bucket

        if not bucket_name:
            raise ValueError("bucket required")

        bucket_obj = client.bucket(bucket_name)
        blob = bucket_obj.blob(name)

        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, blob.download_as_bytes)

    async def delete_file(self, name: str, bucket: Optional[str] = None) -> bool:
        """Delete a file from GCS."""
        client = self._get_client()
        bucket_name = bucket or self.bucket

        if not bucket_name:
            raise ValueError("bucket required")

        bucket_obj = client.bucket(bucket_name)
        blob = bucket_obj.blob(name)
        blob.delete()

        return True

    async def generate_signed_url(
        self, name: str, expiration: int = 3600, bucket: Optional[str] = None
    ) -> str:
        """Generate a signed URL."""
        client = self._get_client()
        bucket_name = bucket or self.bucket

        if not bucket_name:
            raise ValueError("bucket required")

        bucket_obj = client.bucket(bucket_name)
        blob = bucket_obj.blob(name)

        url = blob.generate_signed_url(version="v4", expiration=expiration, method="GET")

        return url
