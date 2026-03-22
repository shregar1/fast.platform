import builtins
import io
import sys
import types
from typing import Any, BinaryIO, Optional

import pytest

from tests.data_platform.storage.abstraction import IStorageTests


class TestBackends(IStorageTests):
    def test_is_storage_backend_abstract_methods_and_presigned_url(self):
        from storage.base import IStorageBackend

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

    def test_local_storage_backend_upload_download_delete(self, tmp_path):
        from storage.local_backend import LocalStorageBackend

        backend = LocalStorageBackend(
            base_dir=str(tmp_path / "storage"), base_url="https://example.com/files"
        )
        url = backend.upload("a/b.txt", b"hello", content_type="text/plain")
        assert url == "https://example.com/files/a/b.txt"
        data = backend.download("a/b.txt")
        assert data == b"hello"
        backend.delete("a/b.txt")
        assert (tmp_path / "storage" / "a" / "b.txt").exists() is False

    def test_local_storage_exists_head(self, tmp_path):
        from storage.local_backend import LocalStorageBackend

        backend = LocalStorageBackend(base_dir=str(tmp_path / "storage"))
        assert backend.exists("missing") is False
        with pytest.raises(FileNotFoundError):
            backend.head("missing")
        backend.upload("a/b.txt", b"hello", content_type="text/plain")
        assert backend.exists("a/b.txt") is True
        h = backend.head("a/b.txt")
        assert h.size == 5
        assert h.last_modified is not None

    def test_storage_factory_selects_local_backend(self, monkeypatch, tmp_path):
        from storage import base as storage_base

        class FakeCfg:
            def __init__(self):
                self.s3 = types.SimpleNamespace(enabled=False, bucket=None)
                self.gcs = types.SimpleNamespace(enabled=False, bucket=None)
                self.azure_blob = types.SimpleNamespace(enabled=False, container=None)
                self.local = types.SimpleNamespace(
                    enabled=True, base_dir=str(tmp_path / "storage"), base_url=None
                )

        monkeypatch.setattr(
            storage_base,
            "StorageConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        backend = storage_base.build_storage_backend("local")
        assert backend is not None
        assert backend.name == "local"

    def test_build_storage_backend_import_error_returns_none(self, monkeypatch):
        from storage import base as storage_base

        class FakeCfg:
            def __init__(self):
                self.s3 = types.SimpleNamespace(
                    enabled=True,
                    bucket="b",
                    region="us-east-1",
                    endpoint_url=None,
                    access_key_id=None,
                    secret_access_key=None,
                    base_path="",
                )
                self.gcs = types.SimpleNamespace(
                    enabled=True, bucket="g", credentials_json_path=None, base_path=""
                )
                self.azure_blob = types.SimpleNamespace(
                    enabled=True,
                    container="c",
                    connection_string=None,
                    account_url="http://acc",
                    base_path="",
                )
                self.local = types.SimpleNamespace(enabled=False, base_dir="x", base_url=None)

        monkeypatch.setattr(
            storage_base,
            "StorageConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        real_import = builtins.__import__

        def _fail_backend_import(name, *args, **kwargs):
            if "s3_backend" in name or "gcs_backend" in name or "azure_backend" in name:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fail_backend_import)
        sys.modules.pop("storage.s3_backend", None)
        sys.modules.pop("storage.gcs_backend", None)
        sys.modules.pop("storage.azure_backend", None)
        assert storage_base.build_storage_backend("s3") is None
        assert storage_base.build_storage_backend("gcs") is None
        assert storage_base.build_storage_backend("azure_blob") is None

    def test_storage_factory_success_builds_s3_gcs_and_azure(self, monkeypatch, tmp_path):
        from storage import base as storage_base
        from storage.azure_backend import AzureBlobStorageBackend
        from storage.gcs_backend import GCSStorageBackend
        from storage.s3_backend import S3StorageBackend

        fake_botocore_config = types.ModuleType("botocore.config")

        class FakeConfig:
            def __init__(self, signature_version: str):
                self.signature_version = signature_version

        fake_botocore_config.Config = FakeConfig
        sys.modules["botocore.config"] = fake_botocore_config
        sys.modules["botocore"] = types.ModuleType("botocore")
        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda service_name, config=None, **kwargs: object()
        sys.modules["boto3"] = fake_boto3
        fake_storage_mod = types.ModuleType("google.cloud.storage")

        class FakeStorageClient:
            def __init__(self):
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
            def __init__(self):
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

    def test_s3_backend_upload_download_delete_and_presigned_url(self, monkeypatch):
        from storage.s3_backend import S3StorageBackend

        class FakeBody:
            def __init__(self, data: bytes):
                self._data = data

            def read(self):
                return self._data

        class FakeS3Client:
            def __init__(self):
                self.put_calls: list[dict[str, Any]] = []
                self.upload_fileobj_calls: list[dict[str, Any]] = []
                self.deleted: list[dict[str, Any]] = []
                self.last_get_key: Optional[str] = None

            def put_object(self, *, Bucket: str, Key: str, Body: bytes, **extra):
                self.put_calls.append({"Bucket": Bucket, "Key": Key, "Body": Body, "extra": extra})

            def upload_fileobj(self, fileobj: BinaryIO, Bucket: str, Key: str, ExtraArgs=None):
                self.upload_fileobj_calls.append(
                    {"Bucket": Bucket, "Key": Key, "ExtraArgs": ExtraArgs}
                )

            def get_object(self, *, Bucket: str, Key: str):
                self.last_get_key = Key
                return {"Body": FakeBody(b"payload")}

            def delete_object(self, *, Bucket: str, Key: str):
                self.deleted.append({"Bucket": Bucket, "Key": Key})

            def head_object(self, *, Bucket: str, Key: str):
                return {
                    "ContentLength": 42,
                    "ContentType": "text/plain",
                    "ETag": '"abc"',
                    "LastModified": None,
                }

            def create_multipart_upload(self, *, Bucket: str, Key: str, **extra):
                return {"UploadId": "up-1"}

            def upload_part(
                self, *, Bucket: str, Key: str, PartNumber: int, UploadId: str, Body: bytes
            ):
                return {"ETag": f"etag-{PartNumber}"}

            def complete_multipart_upload(
                self, *, Bucket: str, Key: str, UploadId: str, MultipartUpload: dict
            ):
                self.completed = {
                    "Bucket": Bucket,
                    "Key": Key,
                    "UploadId": UploadId,
                    "Parts": MultipartUpload["Parts"],
                }

            def abort_multipart_upload(self, *, Bucket: str, Key: str, UploadId: str):
                self.aborted = True

            def generate_presigned_url(
                self, method: str, *, Params: dict[str, Any], ExpiresIn: int
            ):
                return f"presigned://{Params['Key']}?exp={ExpiresIn}"

        class FakeConfig:
            def __init__(self, signature_version: str):
                self.signature_version = signature_version

        fake_botocore = types.ModuleType("botocore")
        fake_botocore_config = types.ModuleType("botocore.config")
        fake_botocore_config.Config = FakeConfig
        fake_botocore_exceptions = types.ModuleType("botocore.exceptions")

        class FakeClientError(Exception):
            def __init__(self, response: dict | None = None, operation_name: str = ""):
                self.response = response or {}

        fake_botocore_exceptions.ClientError = FakeClientError
        sys.modules["botocore"] = fake_botocore
        sys.modules["botocore.config"] = fake_botocore_config
        sys.modules["botocore.exceptions"] = fake_botocore_exceptions
        fake_boto3 = types.ModuleType("boto3")
        captured_kwargs: dict[str, Any] = {}

        def _fake_client(service_name, config=None, **kwargs):
            captured_kwargs.update(kwargs)
            return FakeS3Client()

        fake_boto3.client = _fake_client
        sys.modules["boto3"] = fake_boto3
        backend = S3StorageBackend(
            bucket="bucket",
            base_path="base",
            region="us-east-1",
            endpoint_url="http://endpoint",
            access_key_id="ak",
            secret_access_key="sk",
        )
        url1 = backend.upload("k1", b"v1", content_type="text/plain", metadata={"x": "y"})
        assert url1 == "s3://bucket/base/k1"
        backend.upload("k2", io.BytesIO(b"v2"))
        assert backend._client.put_calls
        assert backend._client.upload_fileobj_calls
        assert backend.download("k1") == b"payload"
        backend.delete("k1")
        assert backend._client.deleted[-1]["Key"] == "base/k1"
        assert backend.presigned_url("k1", expires_in=10).startswith("presigned://base/k1")
        assert "endpoint_url" in captured_kwargs
        assert captured_kwargs.get("aws_access_key_id") == "ak"
        assert captured_kwargs.get("aws_secret_access_key") == "sk"
        assert backend.exists("k1") is True
        h = backend.head("k1")
        assert h.size == 42
        assert h.content_type == "text/plain"

    def test_s3_backend_dependency_missing_raises_runtime_error(self, monkeypatch):
        from storage.s3_backend import S3StorageBackend

        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            if name in {"boto3"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            S3StorageBackend(bucket="b")

    def test_gcs_backend_upload_download_delete_and_presigned_url(self, monkeypatch):
        from storage.gcs_backend import GCSStorageBackend

        class FakeBlob:
            def __init__(self, key: str):
                self.key = key
                self.deleted = False
                self._exists = False
                self.size = 0
                self.content_type: Optional[str] = None
                self.etag: Optional[str] = "fake-etag"
                self.updated = None

            def upload_from_string(self, body: bytes, content_type: Optional[str] = None):
                self._exists = True
                self.uploaded = ("string", body, content_type)
                self.size = len(body)
                self.content_type = content_type

            def upload_from_file(self, fileobj: BinaryIO, content_type: Optional[str] = None):
                data = fileobj.read()
                self._exists = True
                self.uploaded = ("file", data, content_type)
                self.size = len(data)
                self.content_type = content_type

            def exists(self) -> bool:
                return self._exists

            def reload(self) -> None:
                pass

            def download_as_bytes(self) -> bytes:
                return b"gcs-bytes"

            def delete(self):
                self.deleted = True

            def generate_signed_url(self, expiration):
                return f"gcs-presigned://{self.key}"

        class FakeBucket:
            def __init__(self, name: str):
                self.name = name
                self._blobs: dict[str, FakeBlob] = {}

            def blob(self, key: str) -> FakeBlob:
                if key not in self._blobs:
                    self._blobs[key] = FakeBlob(key)
                return self._blobs[key]

        class FakeClient:
            def __init__(self):
                self.buckets: dict[str, FakeBucket] = {}

            @staticmethod
            def from_service_account_json(credentials_path: str) -> "FakeClient":
                return FakeClient()

            def bucket(self, name: str) -> FakeBucket:
                if name not in self.buckets:
                    self.buckets[name] = FakeBucket(name)
                return self.buckets[name]

        fake_storage = types.ModuleType("google.cloud.storage")
        fake_storage.Client = FakeClient
        fake_google = types.ModuleType("google")
        fake_google_cloud = types.ModuleType("google.cloud")
        fake_google_cloud.storage = fake_storage
        sys.modules["google"] = fake_google
        sys.modules["google.cloud"] = fake_google_cloud
        sys.modules["google.cloud.storage"] = fake_storage
        backend = GCSStorageBackend(
            bucket="bucket", credentials_path="creds.json", base_path="base"
        )
        url = backend.upload("k1", b"v1", content_type="text/plain")
        assert url == "gs://bucket/base/k1"
        backend.upload("k2", io.BytesIO(b"v2"))
        assert backend.download("k1") == b"gcs-bytes"
        backend.delete("k1")
        assert backend.presigned_url("k1", expires_in=20).startswith("gcs-presigned://base/k1")
        backend.upload("k3", b"xyz")
        assert backend.exists("k3") is True
        gh = backend.head("k3")
        assert gh.size == 3

    def test_gcs_backend_dependency_missing_raises_runtime_error(self, monkeypatch):
        from storage.gcs_backend import GCSStorageBackend

        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            if name in {"google.cloud", "google"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            GCSStorageBackend(bucket="bucket", credentials_path=None, base_path="")

    def test_azure_blob_backend_upload_download_delete(self, monkeypatch, tmp_path):
        from storage.azure_backend import AzureBlobStorageBackend

        class FakeBlobClient:
            def __init__(self, key: str):
                self.key = key
                self.url = f"https://blob/{key}"
                self._uploaded = False

            def upload_blob(self, data: bytes | BinaryIO, content_settings: Any = None):
                self.uploaded = True
                self._uploaded = True

            def exists(self) -> bool:
                return self._uploaded

            def get_blob_properties(self):
                cs = types.SimpleNamespace(content_type="text/plain")
                return types.SimpleNamespace(
                    size=2, content_settings=cs, etag="e1", last_modified=None
                )

            def download_blob(self):
                return types.SimpleNamespace(readall=lambda: b"azure-bytes")

        class FakeContainerClient:
            def __init__(self):
                self._blobs: dict[str, FakeBlobClient] = {}
                self.deleted: list[str] = []

            def get_blob_client(self, key: str) -> FakeBlobClient:
                if key not in self._blobs:
                    self._blobs[key] = FakeBlobClient(key)
                return self._blobs[key]

            def delete_blob(self, key: str):
                self.deleted.append(key)

        class FakeBlobServiceClient:
            def __init__(self, *args, **kwargs):
                self._container = FakeContainerClient()
                self.init_args = args
                self.init_kwargs = kwargs

            @staticmethod
            def from_connection_string(connection_string: str) -> "FakeBlobServiceClient":
                return FakeBlobServiceClient()

            def get_container_client(self, container: str) -> FakeContainerClient:
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

    def test_azure_blob_backend_account_url_branch_and_missing_args(self, monkeypatch):
        from storage.azure_backend import AzureBlobStorageBackend

        class FakeBlobServiceClient:
            def __init__(self, *args, **kwargs):
                self._container = types.SimpleNamespace(
                    get_blob_client=lambda key: types.SimpleNamespace(
                        upload_blob=lambda *a, **k: None,
                        url="https://blob/url",
                        download_blob=lambda: types.SimpleNamespace(readall=lambda: b""),
                    ),
                    delete_blob=lambda key: None,
                )

            @staticmethod
            def from_connection_string(connection_string: str) -> "FakeBlobServiceClient":
                return FakeBlobServiceClient()

            def get_container_client(self, container: str):
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

    def test_azure_blob_backend_dependency_missing_raises_runtime_error(self, monkeypatch):
        from storage.azure_backend import AzureBlobStorageBackend

        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            if name in {"azure.storage.blob", "azure.storage"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            AzureBlobStorageBackend(
                container="c", connection_string="cs", account_url=None, base_path=""
            )
