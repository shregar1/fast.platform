"""
Default :class:`~fast_media.abstractions.IImageVariantGenerator` using a bytes fetcher + store upload.
"""

from __future__ import annotations

from typing import Callable, Optional

from .abstraction import IImageVariantGenerator, IMediaStore
from .pipeline import VariantSpec, variant_storage_key
from .variants import generate_image_variant


class DefaultImageVariantGenerator(IImageVariantGenerator):
    """
    Fetch original bytes by key, generate a variant, upload, return stored key.

    **fetch_bytes** loads the source object (e.g. from ``InMemoryMediaStore.get_bytes``,
    S3 download, or DB blob).
    """

    def __init__(
        self,
        store: IMediaStore,
        fetch_bytes: Callable[[str], bytes],
        *,
        defaults: dict[str, VariantSpec] | None = None,
    ) -> None:
        self._store = store
        self._fetch = fetch_bytes
        self._defaults = defaults or {
            "thumb": VariantSpec("thumb", 200, 200, "webp", 85),
            "webp": VariantSpec("webp", None, None, "webp", 90),
        }

    def generate(
        self,
        source_key: str,
        variant_name: str,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: Optional[str] = None,
        quality: Optional[int] = None,
    ) -> str:
        raw = self._fetch(source_key)
        spec = self._defaults.get(variant_name)
        if spec is None:
            if format is None:
                raise ValueError(
                    f"Unknown variant {variant_name!r}; register defaults or pass format= / use a known name"
                )
            spec = VariantSpec(variant_name, width, height, format, quality or 85)
        else:
            mw = width if width is not None else spec.max_width
            mh = height if height is not None else spec.max_height
            fmt = (format or spec.format).lower()
            qual = quality if quality is not None else spec.quality
            spec = VariantSpec(variant_name, mw, mh, fmt, qual)

        out = generate_image_variant(
            raw,
            output_format=spec.format,
            max_width=spec.max_width,
            max_height=spec.max_height,
            quality=spec.quality,
        )
        key = variant_storage_key(source_key, variant_name, spec.format)
        fmt = spec.format.lower()
        ct = f"image/{fmt}" if fmt in ("webp", "jpeg", "png", "jpg") else f"image/{fmt}"
        self._store.upload(key, out, content_type=ct)
        return key


__all__ = ["DefaultImageVariantGenerator"]
