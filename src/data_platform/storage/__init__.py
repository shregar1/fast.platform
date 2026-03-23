"""
fast_storage – Object storage (S3, GCS, Azure Blob, local) for FastMVC.
"""

from fast_platform import StorageConfiguration, StorageConfigurationDTO

from .base import IStorageBackend, StorageObjectHead, build_storage_backend
from .local_backend import LocalStorageBackend
from .multipart import multipart_upload_large_file

__version__ = "0.2.0"

__all__ = [
    "IStorageBackend",
    "LocalStorageBackend",
    "StorageObjectHead",
    "StorageConfiguration",
    "StorageConfigurationDTO",
    "build_storage_backend",
    "multipart_upload_large_file",
]
