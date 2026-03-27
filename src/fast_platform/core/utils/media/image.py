"""Image format sniffing and optional Pillow-based decoding.

**Sniffing** inspects only leading magic bytes and is cheap and dependency-free.
**Dimensions** and **opening** images require Pillow (``pip install Pillow`` or
``fast-platform[pillow]``). Sniffing can disagree with a corrupt file that has
valid magic bytes; for strict validation, decode with Pillow or another library.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Optional, Tuple

from ..optional_imports import OptionalImports

from .abstraction import IMedia

__all__ = ["ImageUtility"]


class ImageUtility(IMedia):
    """Image container detection from magic bytes, plus optional Pillow helpers.

    Typical uses: pick a validator or transcoder after upload, set ``Content-Type``
    from a buffer, or read width/height for layout without shelling out to
    ``file(1)``. Methods are stateless and safe to call from request handlers.

    Dependencies
    ------------
    :meth:`detect_format` and :meth:`mime_from_magic` use only the stdlib.
    :meth:`dimensions` and :meth:`open_image` require Pillow at runtime.
    """

    @staticmethod
    def detect_format(data: bytes) -> Optional[str]:
        """Infer a short format label from the first bytes of *data*.

        Examines roughly the first 12–16 bytes only; does not scan the full
        blob or verify checksums. Returns ``None`` if the buffer is too short or
        unrecognized.

        Recognized labels
        -----------------
        ``png``, ``jpeg``, ``gif``, ``webp``, ``bmp``, ``tiff``, or ``None``.

        Parameters
        ----------
        data:
            Beginning of a file or memory buffer (larger buffers are fine; only
            the prefix is read).

        Returns
        -------
        str or None
            A short label for known magic bytes, else ``None``.

        """
        if len(data) < 4:
            return None
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return "png"
        if data[:3] == b"\xff\xd8\xff":
            return "jpeg"
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return "gif"
        if data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"WEBP":
            return "webp"
        if data[:2] == b"BM":
            return "bmp"
        if data[:4] in (b"II*\x00", b"MM\x00*"):
            return "tiff"
        return None

    @staticmethod
    def mime_from_magic(data: bytes) -> Optional[str]:
        """Map detected format to a common ``image/*`` MIME type string.

        Parameters
        ----------
        data:
            Same as :meth:`detect_format` — prefix bytes of the image.

        Returns
        -------
        str or None
            e.g. ``image/png``, or ``None`` if :meth:`detect_format` returns ``None``.

        """
        fmt = ImageUtility.detect_format(data)
        if fmt is None:
            return None
        return {
            "png": "image/png",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
            "bmp": "image/bmp",
            "tiff": "image/tiff",
        }.get(fmt)

    @staticmethod
    def dimensions(data: bytes) -> Optional[Tuple[int, int]]:
        """Decode *data* with Pillow and return ``(width, height)`` in pixels.

        Opens the image long enough to read :attr:`~PIL.Image.Image.size`, then
        closes it. If Pillow is not installed, or the payload is not a decodable
        image, returns ``None`` (failures are swallowed—see also :meth:`open_image`
        if you need error details).

        Parameters
        ----------
        data:
            Full image bytes (not only a prefix).

        Returns
        -------
        tuple[int, int] or None
            ``(width, height)`` if successful, else ``None``.

        """
        _, open_fn = OptionalImports.optional_import("PIL.Image", "open")
        if open_fn is None:
            return None

        try:
            im = open_fn(BytesIO(data))
            try:
                w, h = im.size
                return (int(w), int(h))
            finally:
                im.close()
        except Exception:
            return None

    @staticmethod
    def open_image(data: bytes) -> Any:
        """Open *data* as a Pillow :class:`~PIL.Image.Image` and return it.

        Prefer :meth:`dimensions` when you only need size. This method returns a
        live image object; the caller **must** close it (context manager or
        ``.close()``) to release decoder resources.

        Parameters
        ----------
        data:
            Full image bytes.

        Returns
        -------
        PIL.Image.Image or None
            An opened image, or ``None`` if Pillow is unavailable or opening fails.

        """
        _, open_fn = OptionalImports.optional_import("PIL.Image", "open")
        if open_fn is None:
            return None

        try:
            return open_fn(BytesIO(data))
        except Exception:
            return None
