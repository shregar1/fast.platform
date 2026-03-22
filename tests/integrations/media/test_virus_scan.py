"""Tests for virus scan hooks."""

from unittest.mock import MagicMock

import pytest

from media import (
    ImageVariantPipeline,
    InMemoryMediaStore,
    VirusDetectedError,
    clamscan_bytes,
    noop_virus_scan,
)
from media.virus_scan import ClamdScanner
from tests.integrations.media.abstraction import IFastMediaTests


class TestVirusScan(IFastMediaTests):
    def test_noop(self):
        noop_virus_scan(b"hello")

    def test_pipeline_rejects_when_scan_raises(self):
        store = InMemoryMediaStore()

        def boom(data: bytes) -> None:
            raise VirusDetectedError("bad", engine="test")

        pipe = ImageVariantPipeline(store)
        with pytest.raises(VirusDetectedError):
            pipe.process(base_key="a.png", source_bytes=b"x", virus_scan=boom)

    def test_clamscan_clean(self, monkeypatch):
        proc = MagicMock()
        proc.returncode = 0
        proc.stdout = b""
        proc.stderr = b""
        monkeypatch.setattr("media.virus_scan.subprocess.run", lambda *a, **k: proc)
        clamscan_bytes(b"ok")

    def test_clamscan_infected(self, monkeypatch):
        proc = MagicMock()
        proc.returncode = 1
        proc.stdout = b"stdin: Eicar-Test-Signature FOUND"
        proc.stderr = b""
        monkeypatch.setattr("media.virus_scan.subprocess.run", lambda *a, **k: proc)
        with pytest.raises(VirusDetectedError):
            clamscan_bytes(b"infected")

    def test_clamd_found(self, monkeypatch):
        scanner = ClamdScanner(host="127.0.0.1", port=65530, timeout=0.1)

        class FakeSock:
            def sendall(self, data: bytes) -> None:
                pass

            def recv(self, n: int) -> bytes:
                return b"stream: Eicar-Signature FOUND"

            def close(self) -> None:
                pass

        monkeypatch.setattr("media.virus_scan.socket.create_connection", lambda *a, **k: FakeSock())
        with pytest.raises(VirusDetectedError):
            scanner(b"data")

    def test_clamd_ok(self, monkeypatch):
        scanner = ClamdScanner(host="127.0.0.1", port=65530, timeout=0.1)

        class FakeSock:
            def sendall(self, data: bytes) -> None:
                pass

            def recv(self, n: int) -> bytes:
                return b"stream: OK"

            def close(self) -> None:
                pass

        monkeypatch.setattr("media.virus_scan.socket.create_connection", lambda *a, **k: FakeSock())
        scanner(b"clean")
