from __future__ import annotations

"""Multipart upload: S3 path and rejection of local backend."""
import sys
import types
from pathlib import Path
from typing import Any

import pytest

from storage.multipart import multipart_upload_large_file
from tests.data_platform.storage.abstraction import IStorageTests


class TestMultipartS3Local(IStorageTests):
    def test_multipart_upload_s3_and_rejects_local(self, tmp_path: Path) -> None:
        from storage.local_backend import LocalStorageBackend
        from storage.s3_backend import S3StorageBackend

        class FakeS3Client:
            def __init__(self) -> None:
                self.parts: list[dict[str, Any]] = []

            def create_multipart_upload(self, *, Bucket: str, Key: str, **extra):
                return {"UploadId": "u1"}

            def upload_part(
                self, *, Bucket: str, Key: str, PartNumber: int, UploadId: str, Body: bytes
            ):
                self.parts.append({"PartNumber": PartNumber, "len": len(Body)})
                return {"ETag": f"e{PartNumber}"}

            def complete_multipart_upload(
                self, *, Bucket: str, Key: str, UploadId: str, MultipartUpload: dict
            ):
                self.completed = MultipartUpload["Parts"]

            def abort_multipart_upload(self, *, Bucket: str, Key: str, UploadId: str) -> None:
                pass

        fake_botocore_config = types.ModuleType("botocore.config")

        class FakeConfig:
            def __init__(self, signature_version: str) -> None:
                self.signature_version = signature_version

        fake_botocore_config.Config = FakeConfig
        fake_botocore_exceptions = types.ModuleType("botocore.exceptions")

        class FakeClientError(Exception):
            def __init__(self, response: dict | None = None, operation_name: str = "") -> None:
                self.response = response or {}

        fake_botocore_exceptions.ClientError = FakeClientError
        sys.modules["botocore.config"] = fake_botocore_config
        sys.modules["botocore.exceptions"] = fake_botocore_exceptions
        sys.modules["botocore"] = types.ModuleType("botocore")
        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda service_name, config=None, **kwargs: FakeS3Client()
        sys.modules["boto3"] = fake_boto3
        backend = S3StorageBackend(bucket="bucket", base_path="", region="us-east-1")
        p = tmp_path / "f.bin"
        p.write_bytes(b"x" * 5000)
        url = multipart_upload_large_file(backend, "big", p, part_size=2000)
        assert url == "s3://bucket/big"
        client = backend._client
        assert len(client.parts) >= 2
        with pytest.raises(ValueError, match="S3 and GCS"):
            multipart_upload_large_file(LocalStorageBackend(base_dir=str(tmp_path / "s")), "k", p)
