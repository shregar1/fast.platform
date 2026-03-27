"""Module test_backends_s3.py."""

from __future__ import annotations

"""Tests for :class:`data.storage.s3_backend.S3StorageBackend`."""
import builtins
import io
import sys
import types
from typing import Any, BinaryIO, Optional

import pytest

from fast_platform.data.storage.s3_backend import S3StorageBackend
from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsS3(IStorageTests):
    """Represents the TestBackendsS3 class."""

    def test_s3_backend_upload_download_delete_and_presigned_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Execute test_s3_backend_upload_download_delete_and_presigned_url operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """

        class FakeBody:
            """Represents the FakeBody class."""

            def __init__(self, data: bytes) -> None:
                """Execute __init__ operation.

                Args:
                    data: The data parameter.
                """
                self._data = data

            def read(self):
                """Execute read operation.

                Returns:
                    The result of the operation.
                """
                return self._data

        class FakeS3Client:
            """Represents the FakeS3Client class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.put_calls: list[dict[str, Any]] = []
                self.upload_fileobj_calls: list[dict[str, Any]] = []
                self.deleted: list[dict[str, Any]] = []
                self.last_get_key: Optional[str] = None

            def put_object(self, *, Bucket: str, Key: str, Body: bytes, **extra):
                """Execute put_object operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.
                    Body: The Body parameter.

                Returns:
                    The result of the operation.
                """
                self.put_calls.append({"Bucket": Bucket, "Key": Key, "Body": Body, "extra": extra})

            def upload_fileobj(self, fileobj: BinaryIO, Bucket: str, Key: str, ExtraArgs=None):
                """Execute upload_fileobj operation.

                Args:
                    fileobj: The fileobj parameter.
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.
                    ExtraArgs: The ExtraArgs parameter.

                Returns:
                    The result of the operation.
                """
                self.upload_fileobj_calls.append(
                    {"Bucket": Bucket, "Key": Key, "ExtraArgs": ExtraArgs}
                )

            def get_object(self, *, Bucket: str, Key: str):
                """Execute get_object operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.

                Returns:
                    The result of the operation.
                """
                self.last_get_key = Key
                return {"Body": FakeBody(b"payload")}

            def delete_object(self, *, Bucket: str, Key: str):
                """Execute delete_object operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.

                Returns:
                    The result of the operation.
                """
                self.deleted.append({"Bucket": Bucket, "Key": Key})

            def head_object(self, *, Bucket: str, Key: str):
                """Execute head_object operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.

                Returns:
                    The result of the operation.
                """
                return {
                    "ContentLength": 42,
                    "ContentType": "text/plain",
                    "ETag": '"abc"',
                    "LastModified": None,
                }

            def create_multipart_upload(self, *, Bucket: str, Key: str, **extra):
                """Execute create_multipart_upload operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.

                Returns:
                    The result of the operation.
                """
                return {"UploadId": "up-1"}

            def upload_part(
                self, *, Bucket: str, Key: str, PartNumber: int, UploadId: str, Body: bytes
            ):
                """Execute upload_part operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.
                    PartNumber: The PartNumber parameter.
                    UploadId: The UploadId parameter.
                    Body: The Body parameter.

                Returns:
                    The result of the operation.
                """
                return {"ETag": f"etag-{PartNumber}"}

            def complete_multipart_upload(
                self, *, Bucket: str, Key: str, UploadId: str, MultipartUpload: dict
            ):
                """Execute complete_multipart_upload operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.
                    UploadId: The UploadId parameter.
                    MultipartUpload: The MultipartUpload parameter.

                Returns:
                    The result of the operation.
                """
                self.completed = {
                    "Bucket": Bucket,
                    "Key": Key,
                    "UploadId": UploadId,
                    "Parts": MultipartUpload["Parts"],
                }

            def abort_multipart_upload(self, *, Bucket: str, Key: str, UploadId: str):
                """Execute abort_multipart_upload operation.

                Args:
                    Bucket: The Bucket parameter.
                    Key: The Key parameter.
                    UploadId: The UploadId parameter.

                Returns:
                    The result of the operation.
                """
                self.aborted = True

            def generate_presigned_url(
                self, method: str, *, Params: dict[str, Any], ExpiresIn: int
            ):
                """Execute generate_presigned_url operation.

                Args:
                    method: The method parameter.
                    Params: The Params parameter.
                    ExpiresIn: The ExpiresIn parameter.

                Returns:
                    The result of the operation.
                """
                return f"presigned://{Params['Key']}?exp={ExpiresIn}"

        class FakeConfig:
            """Represents the FakeConfig class."""

            def __init__(self, signature_version: str) -> None:
                """Execute __init__ operation.

                Args:
                    signature_version: The signature_version parameter.
                """
                self.signature_version = signature_version

        fake_botocore = types.ModuleType("botocore")
        fake_botocore_config = types.ModuleType("botocore.config")
        fake_botocore_config.Config = FakeConfig
        fake_botocore_exceptions = types.ModuleType("botocore.exceptions")

        class FakeClientError(Exception):
            """Represents the FakeClientError class."""

            def __init__(self, response: dict | None = None, operation_name: str = "") -> None:
                """Execute __init__ operation.

                Args:
                    response: The response parameter.
                    operation_name: The operation_name parameter.
                """
                self.response = response or {}

        fake_botocore_exceptions.ClientError = FakeClientError
        sys.modules["botocore"] = fake_botocore
        sys.modules["botocore.config"] = fake_botocore_config
        sys.modules["botocore.exceptions"] = fake_botocore_exceptions
        fake_boto3 = types.ModuleType("boto3")
        captured_kwargs: dict[str, Any] = {}

        def _fake_client(service_name, config=None, **kwargs):
            """Execute _fake_client operation.

            Args:
                service_name: The service_name parameter.
                config: The config parameter.

            Returns:
                The result of the operation.
            """
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
        """Execute test_s3_backend_dependency_missing_raises_runtime_error operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        real_import = builtins.__import__

        def _deny_import(name: str, *args: object, **kwargs: object):
            """Execute _deny_import operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if name in {"boto3"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            S3StorageBackend(bucket="b")
