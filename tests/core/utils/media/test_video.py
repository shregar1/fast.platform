"""Module test_video.py."""

from __future__ import annotations

"""Tests for :mod:`utils.media.video`."""
from tests.core.utils.media.abstraction import IMediaUtilsTests
from fast_platform.core.utils.media.video import VideoUtility


class TestVideoUtility(IMediaUtilsTests):
    """Represents the TestVideoUtility class."""

    def test_mp4_ftyp(self) -> None:
        """Execute test_mp4_ftyp operation.

        Returns:
            The result of the operation.
        """
        # ISO BMFF: 4-byte size + ftyp + brand
        data = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2"
        assert VideoUtility.detect_container(data) == "mp4"
        assert VideoUtility.mime_from_magic(data) == "video/mp4"

    def test_mov_qt_brand(self) -> None:
        """Execute test_mov_qt_brand operation.

        Returns:
            The result of the operation.
        """
        data = b"\x00\x00\x00\x20ftypqt  \x00\x00\x02\x00qt  "
        assert VideoUtility.detect_container(data) == "mov"

    def test_avi(self) -> None:
        """Execute test_avi operation.

        Returns:
            The result of the operation.
        """
        data = b"RIFF\x00\x00\x00\x00AVI LIST"
        assert VideoUtility.detect_container(data) == "avi"

    def test_ebml_webm(self) -> None:
        """Execute test_ebml_webm operation.

        Returns:
            The result of the operation.
        """
        data = bytes([0x1A, 0x45, 0xDF, 0xA3]) + b"\x00" * 20
        assert VideoUtility.detect_container(data) == "webm"
