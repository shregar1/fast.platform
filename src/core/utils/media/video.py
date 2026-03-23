"""
Video container sniffing from magic bytes (no codec decode).

These helpers inspect only a short prefix of a file or buffer. They are useful
for logging, upload validation, and choosing a MIME type before spawning
transcoding tools. They **do not** demux streams, verify moov placement, or
distinguish all Matroska variants—EBML-based containers are reported as
``webm`` for this heuristic (see :meth:`VideoUtility.detect_container`).
"""

from __future__ import annotations

from typing import Optional

from .abstraction import IMedia

__all__ = ["VideoUtility"]


class VideoUtility(IMedia):
    """
    Heuristic video container detection from leading bytes.

    Supports common web and desktop wrappers: ISO BMFF (``ftyp``) for MP4/MOV,
    EBML header for WebM-style detection, and RIFF/AVI. Unknown or too-short
    buffers return ``None``. For production transcoding, still validate with
    ffprobe or your media pipeline.
    """

    @staticmethod
    def detect_container(data: bytes) -> Optional[str]:
        """
        Guess a container label from the first bytes of *data*.

        **ISO BMFF:** If bytes 4–7 are ``ftyp``, treats the file as MP4-like;
        if the brand at 8–11 starts with ``qt``, returns ``mov``, otherwise
        ``mp4``.

        **EBML:** If the classic EBML header prefix is present (byte ``0x1A``
        followed by ``0x45 0xDF 0xA3``), returns ``webm``. Matroska (``.mkv``)
        shares EBML; this implementation does not parse the DocType element, so
        MKV may be labeled ``webm`` here—use a full parser if you must separate
        them.

        **RIFF:** If the RIFF fourcc at offset 8 is ``AVI `` returns ``avi``.

        Parameters
        ----------
        data:
            At least ~12 bytes recommended; shorter buffers may yield ``None``.

        Returns
        -------
        str or None
            One of ``mp4``, ``mov``, ``webm``, ``avi``, or ``None``.
        """
        if len(data) < 12:
            return None
        # ISO BMFF (mp4, mov, part of mkv family): size + 'ftyp' at offset 4
        if len(data) >= 8 and data[4:8] == b"ftyp":
            # minor brands often include mp41, isom, M4V ...
            brand = data[8:12] if len(data) >= 12 else b""
            if brand.startswith(b"qt"):
                return "mov"
            return "mp4"
        # EBML (Matroska / WebM)
        if len(data) >= 4 and data[0] == 0x1A and data[1:4] == b"\x45\xdf\xa3":
            return "webm"
        if data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"AVI ":
            return "avi"
        return None

    @staticmethod
    def mime_from_magic(data: bytes) -> Optional[str]:
        """
        Map :meth:`detect_container` output to a common ``video/*`` MIME type.

        Parameters
        ----------
        data:
            Same prefix buffer as :meth:`detect_container`.

        Returns
        -------
        str or None
            e.g. ``video/mp4``, or ``None`` if the container is unknown.
        """
        c = VideoUtility.detect_container(data)
        if c is None:
            return None
        return {
            "mp4": "video/mp4",
            "webm": "video/webm",
            "avi": "video/x-msvideo",
            "mov": "video/quicktime",
        }.get(c)
