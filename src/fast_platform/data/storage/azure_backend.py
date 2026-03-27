"""Azure Blob Storage backend."""

from __future__ import annotations

from typing import BinaryIO, Optional

from .base import IStorageBackend, StorageObjectHead


class AzureBlobStorageBackend(IStorageBackend):
    """Azure Blob Storage backend."""

    name = "azure_blob"

    def __init__(
        self,
        container: str,
        connection_string: Optional[str] = None,
        account_url: Optional[str] = None,
        base_path: str = "",
    ) -> None:
        """Execute __init__ operation.

        Args:
            container: The container parameter.
            connection_string: The connection_string parameter.
            account_url: The account_url parameter.
            base_path: The base_path parameter.
        """
        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError as e:
            raise RuntimeError(
                "azure-storage-blob is required for Azure. Install: pip install fast_storage[azure]"
            ) from e
        if connection_string:
            self._client = BlobServiceClient.from_connection_string(connection_string)
        elif account_url:
            from azure.identity import DefaultAzureCredential

            self._client = BlobServiceClient(
                account_url=account_url, credential=DefaultAzureCredential()
            )
        else:
            raise ValueError("Provide connection_string or account_url")
        self._container = container
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
        container_client = self._client.get_container_client(self._container)
        blob = container_client.get_blob_client(self._key(key))
        if isinstance(body, bytes):
            blob.upload_blob(
                body, content_settings={"content_type": content_type} if content_type else None
            )
        else:
            blob.upload_blob(
                body, content_settings={"content_type": content_type} if content_type else None
            )
        return blob.url

    def download(self, key: str) -> bytes:
        """Execute download operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        container_client = self._client.get_container_client(self._container)
        blob = container_client.get_blob_client(self._key(key))
        return blob.download_blob().readall()

    def delete(self, key: str) -> None:
        """Execute delete operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        container_client = self._client.get_container_client(self._container)
        container_client.delete_blob(self._key(key))

    def exists(self, key: str) -> bool:
        """Execute exists operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        container_client = self._client.get_container_client(self._container)
        blob = container_client.get_blob_client(self._key(key))
        return blob.exists()

    def head(self, key: str) -> StorageObjectHead:
        """Execute head operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        container_client = self._client.get_container_client(self._container)
        blob = container_client.get_blob_client(self._key(key))
        if not blob.exists():
            raise FileNotFoundError(self._key(key))
        props = blob.get_blob_properties()
        lm = props.last_modified
        return StorageObjectHead(
            size=int(props.size),
            content_type=props.content_settings.content_type if props.content_settings else None,
            etag=props.etag,
            last_modified=lm,
        )
