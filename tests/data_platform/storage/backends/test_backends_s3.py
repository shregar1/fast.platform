from __future__ import annotations

"""Tests for :class:`data.storage.s3_backend.S3StorageBackend`."""
import builtins
import io
import sys
import types
from typing import Any, BinaryIO, Optional

import pytest

from data.storage.s3_backend import S3StorageBackend
from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsS3(IStorageTests):
    def test_s3_backend_upload_download_delete_and_presigned_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class FakeBody:
            def __init__(self, data: bytes) -> None:
                self._data = data

            def read(self):
                return self._data

        class FakeS3Client:
            def __init__(self) -> None:
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
            def __init__(self, signature_version: str) -> None:
                self.signature_version = signature_version

        fake_botocore = types.ModuleType("botocore")
        fake_botocore_config = types.ModuleType("botocore.config")
        fake_botocore_config.Config = FakeConfig
        fake_botocore_exceptions = types.ModuleType("botocore.exceptions")

        class FakeClientError(Exception):
            def __init__(self, response: dict | None = None, operation_name: str = "") -> None:
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

    def test_s3_backend_dependency_missing_raises_runtime_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        real_import = builtins.__import__

        def _deny_import(name: str, *args: object, **kwargs: object):
            if name in {"boto3"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            S3StorageBackend(bucket="b")
