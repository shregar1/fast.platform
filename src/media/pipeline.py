"""
Image variant pipeline: thumb + WebP (and custom specs) uploaded via :class:`~fast_media.abstractions.IMediaStore`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .abstractions import IMediaStore, UploadResult
from .variants import generate_image_variant


def variant_storage_key(base_key: str, variant_name: str, ext: str) -> str:
    """
    Derive a sibling key: ``dir/a.jpg`` → ``dir/a_thumb.webp`` (extension from variant).
    """
    ext = ext.lstrip(".")
    if "/" in base_key:
        directory, name = base_key.rsplit("/", 1)
    else:
        directory, name = "", base_key
    if "." in name:
        stem, _orig = name.rsplit(".", 1)
        leaf = f"{stem}_{variant_name}.{ext}"
    else:
        leaf = f"{name}_{variant_name}.{ext}"
    return f"{directory}/{leaf}" if directory else leaf


@dataclass(frozen=True)
class VariantSpec:
    """One derivative to generate and store."""

    name: str
    max_width: Optional[int]
    max_height: Optional[int]
    format: str = "webp"
    quality: int = 85


# Sensible defaults: bounded thumbnail + full-size WebP transcode.
DEFAULT_THUMB_WEBP_VARIANTS: tuple[VariantSpec, ...] = (
    VariantSpec("thumb", 200, 200, "webp", 85),
    VariantSpec("webp", None, None, "webp", 90),
)


class ImageVariantPipeline:
    """
    Generate image variants with Pillow and upload each to an :class:`IMediaStore`.

    Pass an optional **virus_scan** callable (see :mod:`fast_media.virus_scan`)
    to reject payloads before decoding images.
    """

    def __init__(
        self,
        store: IMediaStore,
        *,
        variants: tuple[VariantSpec, ...] | list[VariantSpec] | None = None,
    ) -> None:
        self._store = store
        self._variants: tuple[VariantSpec, ...] = tuple(variants) if variants else DEFAULT_THUMB_WEBP_VARIANTS

    def process(
        self,
        *,
        base_key: str,
        source_bytes: bytes,
        virus_scan: Optional[Callable[[bytes], None]] = None,
    ) -> dict[str, UploadResult]:
        """
        Optionally scan **source_bytes**, then for each variant resize/transcode and upload.

        Keys are produced with :func:`variant_storage_key` (``thumb`` → ``*_thumb.webp``, etc.).
        """
        if virus_scan is not None:
            virus_scan(source_bytes)

        results: dict[str, UploadResult] = {}
        for spec in self._variants:
            out = generate_image_variant(
                source_bytes,
                output_format=spec.format,
                max_width=spec.max_width,
                max_height=spec.max_height,
                quality=spec.quality,
            )
            ext = spec.format.lower()
            key = variant_storage_key(base_key, spec.name, ext)
            content_type = _mime_for_format(ext)
            results[spec.name] = self._store.upload(key, out, content_type=content_type)
        return results


def _mime_for_format(fmt: str) -> str:
    f = fmt.lower()
    if f == "webp":
        return "image/webp"
    if f in ("jpeg", "jpg"):
        return "image/jpeg"
    if f == "png":
        return "image/png"
    return f"image/{f}"


__all__ = [
    "VariantSpec",
    "DEFAULT_THUMB_WEBP_VARIANTS",
    "variant_storage_key",
    "ImageVariantPipeline",
]
