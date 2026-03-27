"""Tests for virus scan hooks."""

from unittest.mock import MagicMock

import pytest

from integrations.media import (
    ImageVariantPipeline,
    InMemoryMediaStore,
    VirusDetectedError,
    clamscan_bytes,
    noop_virus_scan,
)
from integrations.media.virus_scan import ClamdScanner
from tests.integrations.media.abstraction import IFastMediaTests


class TestVirusScan(IFastMediaTests):
    """Represents the TestVirusScan class."""

    def test_noop(self):
        """Execute test_noop operation.

        Returns:
            The result of the operation.
        """
        noop_virus_scan(b"hello")

    def test_pipeline_rejects_when_scan_raises(self):
        """Execute test_pipeline_rejects_when_scan_raises operation.

        Returns:
            The result of the operation.
        """
        store = InMemoryMediaStore()

        def boom(data: bytes) -> None:
            """Execute boom operation.

            Args:
                data: The data parameter.

            Returns:
                The result of the operation.
            """
            raise VirusDetectedError("bad", engine="test")

        pipe = ImageVariantPipeline(store)
        with pytest.raises(VirusDetectedError):
            pipe.process(base_key="a.png", source_bytes=b"x", virus_scan=boom)

    def test_clamscan_clean(self, monkeypatch):
        """Execute test_clamscan_clean operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        proc = MagicMock()
        proc.returncode = 0
        proc.stdout = b""
        proc.stderr = b""
        monkeypatch.setattr("integrations.media.virus_scan.subprocess.run", lambda *a, **k: proc)
        clamscan_bytes(b"ok")

    def test_clamscan_infected(self, monkeypatch):
        """Execute test_clamscan_infected operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        proc = MagicMock()
        proc.returncode = 1
        proc.stdout = b"stdin: Eicar-Test-Signature FOUND"
        proc.stderr = b""
        monkeypatch.setattr("integrations.media.virus_scan.subprocess.run", lambda *a, **k: proc)
        with pytest.raises(VirusDetectedError):
            clamscan_bytes(b"infected")

    def test_clamd_found(self, monkeypatch):
        """Execute test_clamd_found operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        scanner = ClamdScanner(host="127.0.0.1", port=65530, timeout=0.1)

        class FakeSock:
            """Represents the FakeSock class."""

            def sendall(self, data: bytes) -> None:
                """Execute sendall operation.

                Args:
                    data: The data parameter.

                Returns:
                    The result of the operation.
                """
                pass

            def recv(self, n: int) -> bytes:
                """Execute recv operation.

                Args:
                    n: The n parameter.

                Returns:
                    The result of the operation.
                """
                return b"stream: Eicar-Signature FOUND"

            def close(self) -> None:
                """Execute close operation.

                Returns:
                    The result of the operation.
                """
                pass

        monkeypatch.setattr(
            "integrations.media.virus_scan.socket.create_connection", lambda *a, **k: FakeSock()
        )
        with pytest.raises(VirusDetectedError):
            scanner(b"data")

    def test_clamd_ok(self, monkeypatch):
        """Execute test_clamd_ok operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        scanner = ClamdScanner(host="127.0.0.1", port=65530, timeout=0.1)

        class FakeSock:
            """Represents the FakeSock class."""

            def sendall(self, data: bytes) -> None:
                """Execute sendall operation.

                Args:
                    data: The data parameter.

                Returns:
                    The result of the operation.
                """
                pass

            def recv(self, n: int) -> bytes:
                """Execute recv operation.

                Args:
                    n: The n parameter.

                Returns:
                    The result of the operation.
                """
                return b"stream: OK"

            def close(self) -> None:
                """Execute close operation.

                Returns:
                    The result of the operation.
                """
                pass

        monkeypatch.setattr(
            "integrations.media.virus_scan.socket.create_connection", lambda *a, **k: FakeSock()
        )
        scanner(b"clean")
