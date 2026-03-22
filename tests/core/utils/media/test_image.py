from __future__ import annotations

"""Tests for :mod:`utils.media.image`."""
import pytest

from tests.core.utils.media.abstraction import IMediaUtilsTests
from utils.media.image import ImageUtility

# Minimal 1×1 PNG (transparent)
_PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestImageUtility(IMediaUtilsTests):
    def test_detect_format_png(self) -> None:
        assert ImageUtility.detect_format(_PNG_1X1) == "png"
        assert ImageUtility.mime_from_magic(_PNG_1X1) == "image/png"

    def test_detect_format_jpeg(self) -> None:
        assert ImageUtility.detect_format(b"\xff\xd8\xff\xe0\x00\x10JFIF") == "jpeg"

    def test_dimensions_with_pillow(self) -> None:
        pytest.importorskip("PIL")
        dim = ImageUtility.dimensions(_PNG_1X1)
        assert dim == (1, 1)
