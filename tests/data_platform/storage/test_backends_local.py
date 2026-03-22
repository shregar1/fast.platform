from __future__ import annotations

"""Tests for :class:`storage.local_backend.LocalStorageBackend`."""
import pytest

from storage.local_backend import LocalStorageBackend
from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsLocal(IStorageTests):
    def test_local_storage_backend_upload_download_delete(self, tmp_path) -> None:
        backend = LocalStorageBackend(
            base_dir=str(tmp_path / "storage"), base_url="https://example.com/files"
        )
        url = backend.upload("a/b.txt", b"hello", content_type="text/plain")
        assert url == "https://example.com/files/a/b.txt"
        data = backend.download("a/b.txt")
        assert data == b"hello"
        backend.delete("a/b.txt")
        assert (tmp_path / "storage" / "a" / "b.txt").exists() is False

    def test_local_storage_exists_head(self, tmp_path) -> None:
        backend = LocalStorageBackend(base_dir=str(tmp_path / "storage"))
        assert backend.exists("missing") is False
        with pytest.raises(FileNotFoundError):
            backend.head("missing")
        backend.upload("a/b.txt", b"hello", content_type="text/plain")
        assert backend.exists("a/b.txt") is True
        h = backend.head("a/b.txt")
        assert h.size == 5
        assert h.last_modified is not None
