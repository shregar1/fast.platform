"""Module test_archive.py."""

from __future__ import annotations

"""Tests for :mod:`utils.archive`."""
import io
import tarfile
import zipfile

from tests.core.utils.abstraction import IUtilsTests
from fast_platform.core.utils.archive import ArchiveUtility


class TestArchiveUtility(IUtilsTests):
    """Represents the TestArchiveUtility class."""

    def test_zip_roundtrip(self) -> None:
        """Execute test_zip_roundtrip operation.

        Returns:
            The result of the operation.
        """
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("a.txt", b"hello")
        data = buf.getvalue()
        assert ArchiveUtility.is_zip(data)
        assert "a.txt" in ArchiveUtility.zip_namelist(data)
        assert ArchiveUtility.zip_read_member(data, "a.txt") == b"hello"

    def test_tar_uncompressed(self) -> None:
        """Execute test_tar_uncompressed operation.

        Returns:
            The result of the operation.
        """
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            ti = tarfile.TarInfo(name="b.txt")
            ti.size = 3
            tf.addfile(ti, io.BytesIO(b"foo"))
        data = buf.getvalue()
        assert "b.txt" in ArchiveUtility.tar_member_names(data)

    def test_tar_gzip(self) -> None:
        """Execute test_tar_gzip operation.

        Returns:
            The result of the operation.
        """
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode="w:gz") as tf:
            ti = tarfile.TarInfo(name="c.txt")
            ti.size = 1
            tf.addfile(ti, io.BytesIO(b"x"))
        data = raw.getvalue()
        assert ArchiveUtility.is_gzip(data)
        assert "c.txt" in ArchiveUtility.tar_member_names(data)
