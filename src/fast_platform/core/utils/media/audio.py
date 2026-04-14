from __future__ import annotations
"""Audio format sniffing from magic bytes (no decode).

Inspects only a small prefix to classify common containers and sync patterns.
Does not parse full frames, validate CRCs, or detect every proprietary variant.
Use for routing, logging, and ``Content-Type`` hints; use a decoder for
authoritative format validation.
"""

from .constants import DEFAULT_ENCODING

from typing import Optional

from .abstraction import IMedia

__all__ = ["AudioUtility"]


class AudioUtility(IMedia):
    """Heuristic audio container / framing detection.

    Covers RIFF/WAVE, FLAC, MP3 (ID3 or MPEG sync), Ogg, ADTS AAC, and AIFF
    (``FORM`` … ``AIFF``). Edge cases (e.g. MP3 without ID3 in the first bytes)
    may still match MPEG sync bits—treat labels as hints.
    """

    @staticmethod
    def detect_format(data: bytes) -> Optional[str]:
        """Infer a short audio format label from the beginning of *data*.

        Rules (first match wins where applicable):

        - **wav:** ``RIFF`` and ``WAVE`` at offsets 0 and 8.
        - **flac:** Magic ``fLaC``.
        - **mp3:** ``ID3`` prefix or MPEG audio sync (``0xFF`` and high bits of next byte).
        - **ogg:** ``OggS`` page header.
        - **aac_adts:** ADTS sync words ``0xFFF1`` / ``0xFFF9``.
        - **aiff:** ``FORM`` and ``AIFF`` at offset 8.

        Parameters
        ----------
        data:
            At least 4 bytes; more bytes improve reliability for RIFF/AIFF.

        Returns
        -------
        str or None
            One of ``wav``, ``flac``, ``mp3``, ``ogg``, ``aac_adts``, ``aiff``, or ``None``.

        """
        if len(data) < 4:
            return None
        if data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"WAVE":
            return "wav"
        if data[:4] == b"fLaC":
            return "flac"
        if data[:3] == b"ID3" or (data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
            return "mp3"
        if data[:4] == b"OggS":
            return "ogg"
        if data[:2] == b"\xff\xf1" or data[:2] == b"\xff\xf9":
            return "aac_adts"
        if data[:4] in (b"FORM",) and len(data) >= 12 and data[8:12] == b"AIFF":
            return "aiff"
        return None

    @staticmethod
    def mime_from_magic(data: bytes) -> Optional[str]:
        """Map :meth:`detect_format` to a conventional ``audio/*`` MIME type.

        Parameters
        ----------
        data:
            Prefix bytes of the audio blob.

        Returns
        -------
        str or None
            e.g. ``audio/mpeg`` for MP3, or ``None`` if unknown.

        """
        fmt = AudioUtility.detect_format(data)
        if fmt is None:
            return None
        return {
            "wav": "audio/wav",
            "flac": "audio/flac",
            "mp3": "audio/mpeg",
            "ogg": "audio/ogg",
            "aac_adts": "audio/aac",
            "aiff": "audio/aiff",
        }.get(fmt)
