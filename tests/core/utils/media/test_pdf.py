"""Module test_pdf.py."""

from __future__ import annotations

"""Tests for :mod:`utils.media.pdf`."""
from io import BytesIO

import pytest

from tests.core.utils.media.abstraction import IMediaUtilsTests
from core.utils.media.pdf import PdfUtility


class TestPdfUtility(IMediaUtilsTests):
    """Represents the TestPdfUtility class."""

    @pytest.fixture
    def one_page_pdf(self) -> bytes:
        """Execute one_page_pdf operation.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("pypdf")
        from pypdf import PdfWriter

        w = PdfWriter()
        w.add_blank_page(width=72, height=72)
        buf = BytesIO()
        w.write(buf)
        return buf.getvalue()

    def test_without_pypdf_returns_none_for_page_count(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Execute test_without_pypdf_returns_none_for_page_count operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        import core.utils.media.pdf as pu

        monkeypatch.setattr(pu.OptionalImports, "optional_import", lambda m, a=None: (None, None))
        assert PdfUtility.page_count(b"%PDF") is None

    def test_page_count_and_extract(self, one_page_pdf: bytes) -> None:
        """Execute test_page_count_and_extract operation.

        Args:
            one_page_pdf: The one_page_pdf parameter.

        Returns:
            The result of the operation.
        """
        assert PdfUtility.page_count(one_page_pdf) == 1
        text = PdfUtility.extract_text(one_page_pdf)
        assert text is not None
