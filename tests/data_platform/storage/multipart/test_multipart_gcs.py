from __future__ import annotations

"""Multipart upload: GCS path."""
import io
import sys
import types

from storage.multipart import multipart_upload_large_file
from tests.data_platform.storage.abstraction import IStorageTests


class TestMultipartGcs(IStorageTests):
    def test_multipart_upload_gcs(self) -> None:
        from storage.gcs_backend import GCSStorageBackend

        class FakeBlob:
            def __init__(self, key: str) -> None:
                self.key = key
                self.uploaded_from_file = False

            def upload_from_file(self, fileobj, content_type=None, rewind=True):
                assert fileobj.read() == b"abc"
                self.uploaded_from_file = True

        class FakeBucket:
            def blob(self, key: str) -> FakeBlob:
                return FakeBlob(key)

        class FakeClient:
            def bucket(self, name: str) -> FakeBucket:
                return FakeBucket()

        fake_storage = types.ModuleType("google.cloud.storage")
        fake_storage.Client = lambda: FakeClient()
        sys.modules["google"] = types.ModuleType("google")
        sys.modules["google.cloud"] = types.ModuleType("google.cloud")
        sys.modules["google.cloud.storage"] = fake_storage
        backend = GCSStorageBackend(bucket="bucket", credentials_path=None, base_path="")
        url = multipart_upload_large_file(backend, "k", io.BytesIO(b"abc"))
        assert url == "gs://bucket/k"
