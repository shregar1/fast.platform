from __future__ import annotations
"""Tests for :mod:`utils.media.pdf`."""
from tests.core.utils.media.abstraction import IMediaUtilsTests



from io import BytesIO

import pytest

from utils.media.pdf import PdfUtility


class TestPdfUtility(IMediaUtilsTests):
    @pytest.fixture
    def one_page_pdf(self) -> bytes:
        pytest.importorskip("pypdf")
        from pypdf import PdfWriter

        w = PdfWriter()
        w.add_blank_page(width=72, height=72)
        buf = BytesIO()
        w.write(buf)
        return buf.getvalue()

    def test_without_pypdf_returns_none_for_page_count(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import utils.media.pdf as pu

        monkeypatch.setattr(pu.OptionalImports, "optional_import", lambda m, a=None: (None, None))
        assert PdfUtility.page_count(b"%PDF") is None

    def test_page_count_and_extract(self, one_page_pdf: bytes) -> None:
        assert PdfUtility.page_count(one_page_pdf) == 1
        text = PdfUtility.extract_text(one_page_pdf)
        assert text is not None
