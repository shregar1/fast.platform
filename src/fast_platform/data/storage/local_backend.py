"""Local filesystem storage backend."""

from __future__ import annotations

from .constants import LOCAL_BACKEND
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Optional

from .base import IStorageBackend, StorageObjectHead


class LocalStorageBackend(IStorageBackend):
    """Store objects on local disk."""

    name = LOCAL_BACKEND

    def __init__(self, base_dir: str = "storage", base_url: Optional[str] = None) -> None:
        """Execute __init__ operation.

        Args:
            base_dir: The base_dir parameter.
            base_url: The base_url parameter.
        """
        self._base = Path(base_dir)
        self._base_url = base_url or ""

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
        path = self._base / key
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            path.write_bytes(body)
        else:
            path.write_bytes(body.read())
        return self._base_url.rstrip("/") + "/" + key if self._base_url else str(path)

    def download(self, key: str) -> bytes:
        """Execute download operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        path = self._base / key
        return path.read_bytes()

    def delete(self, key: str) -> None:
        """Execute delete operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        path = self._base / key
        if path.exists():
            path.unlink()

    def exists(self, key: str) -> bool:
        """Execute exists operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        path = self._base / key
        return path.is_file()

    def head(self, key: str) -> StorageObjectHead:
        """Execute head operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        path = self._base / key
        if not path.is_file():
            raise FileNotFoundError(str(path))
        st = path.stat()
        ct, _ = mimetypes.guess_type(path.name)
        lm = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
        return StorageObjectHead(
            size=st.st_size,
            content_type=ct,
            etag=None,
            last_modified=lm,
        )
