"""Tests for storage."""

import pytest


def test_imports():
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
