"""Module test_backends_azure.py."""

from __future__ import annotations

"""Tests for :class:`data.storage.azure_backend.AzureBlobStorageBackend`."""
import builtins
import io
import sys
import types
from typing import Any, BinaryIO

import pytest

from fast_platform.data.storage.azure_backend import AzureBlobStorageBackend
from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsAzure(IStorageTests):
    """Represents the TestBackendsAzure class."""

    def test_azure_blob_backend_upload_download_delete(self, monkeypatch, tmp_path) -> None:
        """Execute test_azure_blob_backend_upload_download_delete operation.

        Args:
            monkeypatch: The monkeypatch parameter.
            tmp_path: The tmp_path parameter.

        Returns:
            The result of the operation.
        """

        class FakeBlobClient:
            """Represents the FakeBlobClient class."""

            def __init__(self, key: str):
                """Execute __init__ operation.

                Args:
                    key: The key parameter.
                """
                self.key = key
                self.url = f"https://blob/{key}"
                self._uploaded = False

            def upload_blob(self, data: bytes | BinaryIO, content_settings: Any = None):
                """Execute upload_blob operation.

                Args:
                    data: The data parameter.
                    content_settings: The content_settings parameter.

                Returns:
                    The result of the operation.
                """
                self.uploaded = True
                self._uploaded = True

            def exists(self) -> bool:
                """Execute exists operation.

                Returns:
                    The result of the operation.
                """
                return self._uploaded

            def get_blob_properties(self):
                """Execute get_blob_properties operation.

                Returns:
                    The result of the operation.
                """
                cs = types.SimpleNamespace(content_type="text/plain")
                return types.SimpleNamespace(
                    size=2, content_settings=cs, etag="e1", last_modified=None
                )

            def download_blob(self):
                """Execute download_blob operation.

                Returns:
                    The result of the operation.
                """
                return types.SimpleNamespace(readall=lambda: b"azure-bytes")

        class FakeContainerClient:
            """Represents the FakeContainerClient class."""

            def __init__(self):
                """Execute __init__ operation."""
                self._blobs: dict[str, FakeBlobClient] = {}
                self.deleted: list[str] = []

            def get_blob_client(self, key: str) -> FakeBlobClient:
                """Execute get_blob_client operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
                if key not in self._blobs:
                    self._blobs[key] = FakeBlobClient(key)
                return self._blobs[key]

            def delete_blob(self, key: str):
                """Execute delete_blob operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
                self.deleted.append(key)

        class FakeBlobServiceClient:
            """Represents the FakeBlobServiceClient class."""

            def __init__(self, *args, **kwargs):
                """Execute __init__ operation."""
                self._container = FakeContainerClient()
                self.init_args = args
                self.init_kwargs = kwargs

            @staticmethod
            def from_connection_string(connection_string: str) -> FakeBlobServiceClient:
                """Execute from_connection_string operation.

                Args:
                    connection_string: The connection_string parameter.

                Returns:
                    The result of the operation.
                """
                return FakeBlobServiceClient()

            def get_container_client(self, container: str) -> FakeContainerClient:
                """Execute get_container_client operation.

                Args:
                    container: The container parameter.

                Returns:
                    The result of the operation.
                """
                return self._container

        fake_azure_blob = types.ModuleType("azure.storage.blob")
        fake_azure_blob.BlobServiceClient = FakeBlobServiceClient
        fake_azure_identity = types.ModuleType("azure.identity")
        fake_azure_identity.DefaultAzureCredential = lambda: object()
        fake_azure = types.ModuleType("azure")
        fake_azure_storage = types.ModuleType("azure.storage")
        fake_azure_storage_blob = fake_azure_blob
        sys.modules["azure"] = fake_azure
        sys.modules["azure.storage"] = fake_azure_storage
        sys.modules["azure.storage.blob"] = fake_azure_storage_blob
        sys.modules["azure.identity"] = fake_azure_identity
        backend = AzureBlobStorageBackend(
            container="c", connection_string="cs", account_url=None, base_path="base"
        )
        url = backend.upload("k1", b"v1", content_type="text/plain")
        assert url == "https://blob/base/k1"
        assert backend.download("k1") == b"azure-bytes"
        backend.delete("k1")
        backend.upload("k2", io.BytesIO(b"v2"))
        assert backend.exists("k2") is True
        ah = backend.head("k2")
        assert ah.size == 2

    def test_azure_blob_backend_account_url_branch_and_missing_args(self, monkeypatch) -> None:
        """Execute test_azure_blob_backend_account_url_branch_and_missing_args operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """

        class FakeBlobServiceClient:
            """Represents the FakeBlobServiceClient class."""

            def __init__(self, *args, **kwargs):
                """Execute __init__ operation."""
                self._container = types.SimpleNamespace(
                    get_blob_client=lambda key: types.SimpleNamespace(
                        upload_blob=lambda *a, **k: None,
                        url="https://blob/url",
                        download_blob=lambda: types.SimpleNamespace(readall=lambda: b""),
                    ),
                    delete_blob=lambda key: None,
                )

            @staticmethod
            def from_connection_string(connection_string: str) -> FakeBlobServiceClient:
                """Execute from_connection_string operation.

                Args:
                    connection_string: The connection_string parameter.

                Returns:
                    The result of the operation.
                """
                return FakeBlobServiceClient()

            def get_container_client(self, container: str):
                """Execute get_container_client operation.

                Args:
                    container: The container parameter.

                Returns:
                    The result of the operation.
                """
                return self._container

        fake_azure_blob = types.ModuleType("azure.storage.blob")
        fake_azure_blob.BlobServiceClient = FakeBlobServiceClient
        fake_azure_identity = types.ModuleType("azure.identity")
        fake_azure_identity.DefaultAzureCredential = lambda: object()
        sys.modules["azure.storage.blob"] = fake_azure_blob
        sys.modules["azure.identity"] = fake_azure_identity
        backend = AzureBlobStorageBackend(
            container="c", connection_string=None, account_url="http://acc", base_path=""
        )
        backend.upload("k1", b"v1")
        backend.delete("k1")
        with pytest.raises(ValueError):
            AzureBlobStorageBackend(
                container="c", connection_string=None, account_url=None, base_path=""
            )

    def test_azure_blob_backend_dependency_missing_raises_runtime_error(self, monkeypatch) -> None:
        """Execute test_azure_blob_backend_dependency_missing_raises_runtime_error operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            """Execute _deny_import operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if name in {"azure.storage.blob", "azure.storage"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            AzureBlobStorageBackend(
                container="c", connection_string="cs", account_url=None, base_path=""
            )
