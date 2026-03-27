"""FastMVC Storage Module.

Object storage integrations (S3, GCS, Azure Blob).
"""

from .s3 import S3Client
from .gcs import GCSClient
from .azure import AzureBlobClient

__all__ = [
    "S3Client",
    "GCSClient",
    "AzureBlobClient",
]
