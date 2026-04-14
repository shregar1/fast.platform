"""Multipart file upload helpers for FastAPI."""

from fast_platform.core.utils.media.constants import MIME_IMAGE_JPEG, MIME_IMAGE_PNG, MIME_IMAGE_WEBP, MIME_IMAGE_GIF
from typing import Optional

from fastapi import UploadFile


async def read_upload_as_bytes(upload: UploadFile, max_size: Optional[int] = None) -> bytes:
    """Read UploadFile to bytes. Optionally enforce max_size (raises ValueError if exceeded)."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if max_size is not None and total > max_size:
            raise ValueError(f"File size exceeds {max_size} bytes")
        chunks.append(chunk)
    return b"".join(chunks)


def allowed_content_types(
    allow: Optional[list[str]] = None,
    default: list[str] = [
        MIME_IMAGE_JPEG,
        MIME_IMAGE_PNG,
        MIME_IMAGE_GIF,
        MIME_IMAGE_WEBP,
        "application/pdf",
    ],
) -> list[str]:
    """Return list of allowed content types for upload validation."""
    return allow if allow is not None else default


def validate_content_type(
    content_type: Optional[str],
    allowed: list[str],
) -> bool:
    """Return True if content_type is in allowed or is a subtype (e.g. image/*)."""
    if not content_type:
        return False
    if content_type in allowed:
        return True
    for a in allowed:
        if a.endswith("/*") and content_type.startswith(a[:-1]):
            return True
    return False
