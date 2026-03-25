from __future__ import annotations

"""Tests for :class:`data.storage.gcs_backend.GCSStorageBackend`."""
import builtins
import io
import sys
import types
from typing import BinaryIO, Optional

import pytest

from data.storage.gcs_backend import GCSStorageBackend
from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsGcs(IStorageTests):
    def test_gcs_backend_upload_download_delete_and_presigned_url(self, monkeypatch) -> None:
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
            def from_service_account_json(credentials_path: str) -> FakeClient:
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

    def test_gcs_backend_dependency_missing_raises_runtime_error(self, monkeypatch) -> None:
        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            if name in {"google.cloud", "google"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            GCSStorageBackend(bucket="bucket", credentials_path=None, base_path="")
