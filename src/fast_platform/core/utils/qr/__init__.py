"""QR code generation utilities via optional ``qrcode``."""

from __future__ import annotations

import io
from typing import Any, Optional, Union

from ..optional_imports import OptionalImports
from .abstraction import IQRUtility


class QRUtility(IQRUtility):
    """Stateless helpers for QR code generation.

    **Dependencies:** Requires ``qrcode`` or ``segno`` at runtime.
    If none are available, methods return ``None``.
    """

    @staticmethod
    def generate_png_bytes(
        data: str,
        *,
        box_size: int = 10,
        border: int = 4,
    ) -> Optional[bytes]:
        """Generate a QR code as PNG bytes from the given data."""
        # Try qrcode first
        _, qrcode = OptionalImports.optional_import("qrcode")
        if qrcode:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=box_size,
                    border=border,
                )
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                out = io.BytesIO()
                img.save(out, format="PNG")
                return out.getvalue()
            except Exception:
                pass

        # Try segno if qrcode failed or is missing
        _, segno = OptionalImports.optional_import("segno")
        if segno:
            try:
                qr = segno.make(data)
                out = io.BytesIO()
                qr.save(out, kind="png", scale=box_size, border=border)
                return out.getvalue()
            except Exception:
                return None

        return None

    @staticmethod
    def generate_svg(data: str) -> Optional[str]:
        """Generate a QR code as SVG string."""
        _, segno = OptionalImports.optional_import("segno")
        if segno:
            try:
                qr = segno.make(data)
                out = io.StringIO()
                qr.save(out, kind="svg")
                return out.getvalue()
            except Exception:
                return None

        # Fallback to qrcode svg
        _, qrcode = OptionalImports.optional_import("qrcode")
        if qrcode:
            from qrcode.image.svg import SvgImage

            try:
                img = qrcode.make(data, image_factory=SvgImage)
                out = io.BytesIO()
                img.save(out)
                return out.getvalue().decode("utf-8")
            except Exception:
                return None

        return None


__all__ = ["QRUtility", "IQRUtility"]
