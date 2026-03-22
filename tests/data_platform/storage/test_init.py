from __future__ import annotations

"""Smoke tests for ``storage`` package exports."""
from tests.data_platform.storage.abstraction import IStorageTests


class TestInit(IStorageTests):
    def test_imports(self) -> None:
        from storage import (
            IStorageBackend,
            LocalStorageBackend,
            StorageConfiguration,
            StorageConfigurationDTO,
            StorageObjectHead,
            build_storage_backend,
            multipart_upload_large_file,
        )

        assert LocalStorageBackend is not None
        assert build_storage_backend is not None
        assert StorageObjectHead is not None
        assert multipart_upload_large_file is not None
        assert IStorageBackend is not None
        assert StorageConfiguration is not None
        assert StorageConfigurationDTO is not None
