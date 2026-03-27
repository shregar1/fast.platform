"""AWS S3 storage backend."""

from __future__ import annotations

from typing import Any, BinaryIO, Optional

from .base import IStorageBackend, StorageObjectHead


class S3StorageBackend(IStorageBackend):
    """S3-compatible object storage."""

    name = "s3"

    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        base_path: str = "",
    ) -> None:
        """Execute __init__ operation.

        Args:
            bucket: The bucket parameter.
            region: The region parameter.
            endpoint_url: The endpoint_url parameter.
            access_key_id: The access_key_id parameter.
            secret_access_key: The secret_access_key parameter.
            base_path: The base_path parameter.
        """
        try:
            import boto3
            from botocore.config import Config
        except ImportError as e:
            raise RuntimeError(
                "boto3 is required for S3 backend. Install: pip install fast_storage[s3]"
            ) from e
        kwargs: dict[str, Any] = {"region_name": region}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        if access_key_id and secret_access_key:
            kwargs["aws_access_key_id"] = access_key_id
            kwargs["aws_secret_access_key"] = secret_access_key
        self._client = boto3.client("s3", config=Config(signature_version="s3v4"), **kwargs)
        self._bucket = bucket
        self._base = (base_path.rstrip("/") + "/") if base_path else ""

    def _key(self, key: str) -> str:
        """Execute _key operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        return self._base + key.lstrip("/")

    def upload(
        self,
        key: str,
        body: bytes | BinaryIO,
        *,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        """Execute upload operation.

        Args:
            key: The key parameter.
            body: The body parameter.
            content_type: The content_type parameter.
            metadata: The metadata parameter.

        Returns:
            The result of the operation.
        """
        k = self._key(key)
        extra: dict[str, Any] = {}
        if content_type:
            extra["ContentType"] = content_type
        if isinstance(body, bytes):
            self._client.put_object(Bucket=self._bucket, Key=k, Body=body, **extra)
        else:
            self._client.upload_fileobj(body, self._bucket, k, ExtraArgs=extra or None)
        return f"s3://{self._bucket}/{k}"

    def download(self, key: str) -> bytes:
        """Execute download operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        resp = self._client.get_object(Bucket=self._bucket, Key=self._key(key))
        return resp["Body"].read()

    def delete(self, key: str) -> None:
        """Execute delete operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        self._client.delete_object(Bucket=self._bucket, Key=self._key(key))

    def exists(self, key: str) -> bool:
        """Execute exists operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        from botocore.exceptions import ClientError

        k = self._key(key)
        try:
            self._client.head_object(Bucket=self._bucket, Key=k)
            return True
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("404", "NotFound", "NoSuchKey"):
                return False
            raise

    def head(self, key: str) -> StorageObjectHead:
        """Execute head operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        from botocore.exceptions import ClientError

        k = self._key(key)
        try:
            r = self._client.head_object(Bucket=self._bucket, Key=k)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("404", "NotFound", "NoSuchKey"):
                raise FileNotFoundError(k) from e
            raise
        etag = r.get("ETag")
        if isinstance(etag, str):
            etag = etag.strip('"')
        return StorageObjectHead(
            size=int(r["ContentLength"]),
            content_type=r.get("ContentType"),
            etag=etag,
            last_modified=r.get("LastModified"),
        )

    def presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Execute presigned_url operation.

        Args:
            key: The key parameter.
            expires_in: The expires_in parameter.

        Returns:
            The result of the operation.
        """
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": self._key(key)},
            ExpiresIn=expires_in,
        )
