"""
Optional image variant generation (resize, format) using Pillow.
"""

from typing import Optional


def generate_image_variant(
    source_data: bytes,
    output_format: Optional[str] = "webp",
    *,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    quality: int = 85,
) -> bytes:
    """
    Resize/convert image to variant. Returns new image bytes.

    Requires Pillow: pip install fast_media[pillow]
    """
    try:
        from PIL import Image
        import io
    except ImportError as e:
        raise RuntimeError("Pillow required for image variants. Install: pip install fast_media[pillow]") from e

    img = Image.open(io.BytesIO(source_data))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if max_width or max_height:
        w, h = img.size
        if max_width and w > max_width:
            ratio = max_width / w
            h = int(h * ratio)
            w = max_width
        if max_height and h > max_height:
            ratio = max_height / h
            w = int(w * ratio)
            h = max_height
        img = img.resize((w, h), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    fmt = output_format or "webp"
    if fmt.lower() == "jpeg":
        img.save(buf, "JPEG", quality=quality, optimize=True)
    elif fmt.lower() == "webp":
        img.save(buf, "WEBP", quality=quality)
    elif fmt.lower() == "png":
        img.save(buf, "PNG", optimize=True)
    else:
        img.save(buf, fmt.upper(), quality=quality)
    return buf.getvalue()
