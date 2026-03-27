"""Module test_multipart_gcs.py."""

from __future__ import annotations

"""Multipart upload: GCS path."""
import io
import sys
import types

from fast_platform.data.storage.multipart import multipart_upload_large_file
from tests.data_platform.storage.abstraction import IStorageTests


class TestMultipartGcs(IStorageTests):
    """Represents the TestMultipartGcs class."""

    def test_multipart_upload_gcs(self) -> None:
        """Execute test_multipart_upload_gcs operation.

        Returns:
            The result of the operation.
        """
        from data.storage.gcs_backend import GCSStorageBackend

        class FakeBlob:
            """Represents the FakeBlob class."""

            def __init__(self, key: str) -> None:
                """Execute __init__ operation.

                Args:
                    key: The key parameter.
                """
                self.key = key
                self.uploaded_from_file = False

            def upload_from_file(self, fileobj, content_type=None, rewind=True):
                """Execute upload_from_file operation.

                Args:
                    fileobj: The fileobj parameter.
                    content_type: The content_type parameter.
                    rewind: The rewind parameter.

                Returns:
                    The result of the operation.
                """
                assert fileobj.read() == b"abc"
                self.uploaded_from_file = True

        class FakeBucket:
            """Represents the FakeBucket class."""

            def blob(self, key: str) -> FakeBlob:
                """Execute blob operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
                return FakeBlob(key)

        class FakeClient:
            """Represents the FakeClient class."""

            def bucket(self, name: str) -> FakeBucket:
                """Execute bucket operation.

                Args:
                    name: The name parameter.

                Returns:
                    The result of the operation.
                """
                return FakeBucket()

        fake_storage = types.ModuleType("google.cloud.storage")
        fake_storage.Client = lambda: FakeClient()
        sys.modules["google"] = types.ModuleType("google")
        sys.modules["google.cloud"] = types.ModuleType("google.cloud")
        sys.modules["google.cloud.storage"] = fake_storage
        backend = GCSStorageBackend(bucket="bucket", credentials_path=None, base_path="")
        url = multipart_upload_large_file(backend, "k", io.BytesIO(b"abc"))
        assert url == "gs://bucket/k"
