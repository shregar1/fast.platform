"""Module test_backends_abstract.py."""

from __future__ import annotations

"""Tests for :class:`data.storage.base.IStorageBackend` defaults and abstract methods."""
from typing import BinaryIO, Optional

import pytest

from data.storage.base import IStorageBackend
from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsAbstract(IStorageTests):
    """Represents the TestBackendsAbstract class."""

    def test_is_storage_backend_abstract_methods_and_presigned_url(self) -> None:
        """Execute test_is_storage_backend_abstract_methods_and_presigned_url operation.

        Returns:
            The result of the operation.
        """

        class DummyBackend(IStorageBackend):
            """Represents the DummyBackend class."""

            name = "dummy"

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
                return super().upload(key, body, content_type=content_type, metadata=metadata)

            def download(self, key: str) -> bytes:
                """Execute download operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
                return super().download(key)

            def delete(self, key: str) -> None:
                """Execute delete operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
                return super().delete(key)

            def exists(self, key: str) -> bool:
                """Execute exists operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
                return super().exists(key)

            def head(self, key: str):
                """Execute head operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
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
