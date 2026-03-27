"""Module test_audio.py."""

from __future__ import annotations

"""Tests for :mod:`utils.media.audio`."""
from tests.core.utils.media.abstraction import IMediaUtilsTests
from core.utils.media.audio import AudioUtility


class TestAudioUtility(IMediaUtilsTests):
    """Represents the TestAudioUtility class."""

    def test_wav(self) -> None:
        """Execute test_wav operation.

        Returns:
            The result of the operation.
        """
        data = b"RIFF\x00\x00\x00\x00WAVEfmt "
        assert AudioUtility.detect_format(data) == "wav"
        assert AudioUtility.mime_from_magic(data) == "audio/wav"

    def test_flac(self) -> None:
        """Execute test_flac operation.

        Returns:
            The result of the operation.
        """
        assert AudioUtility.detect_format(b"fLaC\x00") == "flac"

    def test_mp3_sync(self) -> None:
        """Execute test_mp3_sync operation.

        Returns:
            The result of the operation.
        """
        assert AudioUtility.detect_format(b"\xff\xfb\x90\x00") == "mp3"

    def test_aiff(self) -> None:
        """Execute test_aiff operation.

        Returns:
            The result of the operation.
        """
        data = b"FORM\x00\x00\x00\x00AIFF"
        assert AudioUtility.detect_format(data) == "aiff"
