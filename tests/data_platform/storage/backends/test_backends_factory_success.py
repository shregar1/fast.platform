from __future__ import annotations

"""Tests for :func:`storage.base.build_storage_backend` (S3, GCS, Azure)."""
import sys
import types

import pytest

from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsFactorySuccess(IStorageTests):
    def test_storage_factory_success_builds_s3_gcs_and_azure(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path
    ) -> None:
        from storage import base as storage_base
        from storage.azure_backend import AzureBlobStorageBackend
        from storage.gcs_backend import GCSStorageBackend
        from storage.s3_backend import S3StorageBackend

        fake_botocore_config = types.ModuleType("botocore.config")

        class FakeConfig:
            def __init__(self, signature_version: str) -> None:
                self.signature_version = signature_version

        fake_botocore_config.Config = FakeConfig
        sys.modules["botocore.config"] = fake_botocore_config
        sys.modules["botocore"] = types.ModuleType("botocore")
        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda service_name, config=None, **kwargs: object()
        sys.modules["boto3"] = fake_boto3
        fake_storage_mod = types.ModuleType("google.cloud.storage")

        class FakeStorageClient:
            def __init__(self) -> None:
                pass

            @staticmethod
            def from_service_account_json(credentials_path: str):
                return FakeStorageClient()

        fake_storage_mod.Client = FakeStorageClient
        sys.modules["google"] = types.ModuleType("google")
        sys.modules["google.cloud"] = types.ModuleType("google.cloud")
        sys.modules["google.cloud"].storage = fake_storage_mod
        sys.modules["google.cloud.storage"] = fake_storage_mod
        fake_blob_service_client = types.SimpleNamespace(
            from_connection_string=lambda connection_string: types.SimpleNamespace(
                get_container_client=lambda container: object()
            )
        )
        fake_azure_blob = types.ModuleType("azure.storage.blob")
        fake_azure_blob.BlobServiceClient = fake_blob_service_client
        fake_azure_identity = types.ModuleType("azure.identity")
        fake_azure_identity.DefaultAzureCredential = lambda: object()
        sys.modules["azure.storage.blob"] = fake_azure_blob
        sys.modules["azure.identity"] = fake_azure_identity

        class FakeCfg:
            def __init__(self) -> None:
                self.s3 = types.SimpleNamespace(
                    enabled=True,
                    bucket="b",
                    region="us-east-1",
                    endpoint_url=None,
                    access_key_id=None,
                    secret_access_key=None,
                    base_path="base",
                )
                self.gcs = types.SimpleNamespace(
                    enabled=True, bucket="g", credentials_json_path=None, base_path="base"
                )
                self.azure_blob = types.SimpleNamespace(
                    enabled=True,
                    container="c",
                    connection_string="cs",
                    account_url=None,
                    base_path="base",
                )
                self.local = types.SimpleNamespace(
                    enabled=False, base_dir=str(tmp_path / "x"), base_url=None
                )

        monkeypatch.setattr(
            storage_base,
            "StorageConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        s3_backend = storage_base.build_storage_backend("s3")
        gcs_backend = storage_base.build_storage_backend("gcs")
        azure_backend = storage_base.build_storage_backend("azure_blob")
        assert isinstance(s3_backend, S3StorageBackend)
        assert isinstance(gcs_backend, GCSStorageBackend)
        assert isinstance(azure_backend, AzureBlobStorageBackend)
        assert storage_base.build_storage_backend("does-not-exist") is None
