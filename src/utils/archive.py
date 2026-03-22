"""
ZIP and tar introspection using the Python standard library.

All operations are **read-only** and operate on **in-memory** ``bytes`` (the
full archive is loaded). They are
suited to listing members or reading a single small entry; for huge archives,
prefer streaming APIs or extracting to disk with appropriate security checks
(path traversal, zip bombs).
"""

from __future__ import annotations

import io
import tarfile
import zipfile

from .abstraction import IUtility

__all__ = ["ArchiveUtility"]


class ArchiveUtility(IUtility):
    """
    Read-only helpers for ZIP and tar archives in memory.

    **ZIP:** Uses :mod:`zipfile` on a :class:`io.BytesIO` wrapper—entire archive
    must fit in memory for these helpers.

    **Tar:** Supports uncompressed tar and gzip-compressed tar (detected via
    gzip magic). Other compressions (xz, bz2) are not auto-detected here.
    """

    @staticmethod
    def is_zip(data: bytes) -> bool:
        """
        Return whether *data* begins with a ZIP local file header or EOCD marker.

        True for ``PK\\x03\\x04`` (typical local header) or ``PK\\x05\\x06`` (end
        of central directory, e.g. empty zip). This is a quick sniff, not full
        structural validation.

        Parameters
        ----------
        data:
            At least 4 bytes for a meaningful check.

        Returns
        -------
        bool
            ``True`` if the prefix matches common ZIP signatures.
        """
        if len(data) < 4:
            return False
        return data[:4] == b"PK\x03\x04" or data[:4] == b"PK\x05\x06"

    @staticmethod
    def is_gzip(data: bytes) -> bool:
        """
        Return whether *data* starts with the gzip magic bytes ``0x1f 0x8b``.

        Used to choose tar open mode for :meth:`tar_member_names`.

        Parameters
        ----------
        data:
            At least 2 bytes.

        Returns
        -------
        bool
            ``True`` if gzip magic is present.
        """
        return len(data) >= 2 and data[:2] == b"\x1f\x8b"

    @staticmethod
    def zip_namelist(data: bytes) -> list[str]:
        """
        Return all member path names in a ZIP archive.

        Parameters
        ----------
        data:
            Complete ZIP file bytes.

        Returns
        -------
        list[str]
            Paths as stored in the archive (may include directories and ``..``
            segments—sanitize before use on disk).

        Raises
        ------
        zipfile.BadZipFile
            If *data* is not a valid ZIP archive.
        """
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            return zf.namelist()

    @staticmethod
    def zip_read_member(data: bytes, name: str) -> bytes:
        """
        Read the uncompressed bytes for a single named member.

        Parameters
        ----------
        data:
            Complete ZIP file bytes.
        name:
            Member name as returned by :meth:`zip_namelist`.

        Returns
        -------
        bytes
            Raw member contents.

        Raises
        ------
        KeyError
            If *name* is not present in the archive.
        zipfile.BadZipFile
            If *data* is not a valid ZIP archive.
        """
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            with zf.open(name) as f:
                return f.read()

    @staticmethod
    def tar_member_names(data: bytes) -> list[str]:
        """
        List names of **regular file** members in a tar archive.

        Opens with ``r:gz`` if :meth:`is_gzip` is true, otherwise ``r:``.
        Directories, symlinks, and special entries are skipped—only ``isfile()``
        members are included.

        Parameters
        ----------
        data:
            Complete tar (or tar.gz) file bytes.

        Returns
        -------
        list[str]
            Member paths for regular files.

        Raises
        ------
        tarfile.TarError
            If *data* is not a readable tar in the chosen mode.
        """
        bio = io.BytesIO(data)
        mode = "r:gz" if ArchiveUtility.is_gzip(data) else "r:"
        out: list[str] = []
        with tarfile.open(fileobj=bio, mode=mode) as tf:
            for m in tf.getmembers():
                if m.isfile():
                    out.append(m.name)
        return out
