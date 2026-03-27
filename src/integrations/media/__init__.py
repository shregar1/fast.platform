"""fast_media – File upload, image variants, presigned URLs for FastMVC."""

from .abstraction import IImageVariantGenerator, IMedia, IMediaStore, UploadResult
from .generator import DefaultImageVariantGenerator
from .memory_store import InMemoryMediaStore
from .pipeline import (
    DEFAULT_THUMB_WEBP_VARIANTS,
    ImageVariantPipeline,
    VariantSpec,
    variant_storage_key,
)
from .upload import allowed_content_types, read_upload_as_bytes, validate_content_type
from .variants import generate_image_variant
from .virus_scan import (
    ClamdScanner,
    VirusDetectedError,
    VirusScanHook,
    clamscan_bytes,
    noop_virus_scan,
)

__version__ = "0.1.1"

__all__ = [
    "IMedia",
    "IMediaStore",
    "IImageVariantGenerator",
    "UploadResult",
    "read_upload_as_bytes",
    "allowed_content_types",
    "validate_content_type",
    "generate_image_variant",
    "InMemoryMediaStore",
    "ImageVariantPipeline",
    "VariantSpec",
    "DEFAULT_THUMB_WEBP_VARIANTS",
    "variant_storage_key",
    "DefaultImageVariantGenerator",
    "VirusDetectedError",
    "VirusScanHook",
    "noop_virus_scan",
    "clamscan_bytes",
    "ClamdScanner",
]
