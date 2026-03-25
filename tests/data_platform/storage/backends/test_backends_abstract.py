from __future__ import annotations

"""Tests for :class:`data.storage.base.IStorageBackend` defaults and abstract methods."""
from typing import BinaryIO, Optional

import pytest

from data.storage.base import IStorageBackend
from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsAbstract(IStorageTests):
    def test_is_storage_backend_abstract_methods_and_presigned_url(self) -> None:
        class DummyBackend(IStorageBackend):
            name = "dummy"

            def upload(
                self,
                key: str,
                body: bytes | BinaryIO,
                *,
                content_type: Optional[str] = None,
                metadata: Optional[dict[str, str]] = None,
            ) -> str:
                return super().upload(key, body, content_type=content_type, metadata=metadata)

            def download(self, key: str) -> bytes:
                return super().download(key)

            def delete(self, key: str) -> None:
                return super().delete(key)

            def exists(self, key: str) -> bool:
                return super().exists(key)

            def head(self, key: str):
                return super().head(key)

        b = DummyBackend()
        assert b.presigned_url("k") is None
        with pytest.raises(NotImplementedError):
            b.upload("k", b"v")
        with pytest.raises(NotImplementedError):
            b.download("k")
        with pytest.raises(NotImplementedError):
            b.delete("k")
        with pytest.raises(NotImplementedError):
            b.exists("k")
        with pytest.raises(NotImplementedError):
            b.head("k")
