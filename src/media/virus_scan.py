"""
Optional virus scanning hooks (ClamAV) for uploaded bytes.

Uses **ClamAV** only when configured; no extra PyPI dependency beyond the stdlib
(``subprocess`` / ``socket``).
"""

from __future__ import annotations

import os
import socket
import struct
import subprocess
import tempfile
from typing import Protocol


class VirusDetectedError(Exception):
    """Raised when a scanner reports malware."""

    def __init__(self, message: str, *, engine: str = "unknown") -> None:
        super().__init__(message)
        self.engine = engine


class VirusScanHook(Protocol):
    def __call__(self, data: bytes) -> None: ...


def noop_virus_scan(_data: bytes) -> None:
    """No-op scanner (tests or disabled scanning)."""
    return None


def clamscan_bytes(
    data: bytes,
    *,
    clamscan_bin: str = "clamscan",
    timeout: float = 120.0,
) -> None:
    """
    Scan **data** with the ``clamscan`` CLI (writes a temp file).

    Return codes: 0 = clean, 1 = infected, 2 = error (raises).
    """
    if not data:
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        proc = subprocess.run(
            [clamscan_bin, "--no-summary", path],
            capture_output=True,
            timeout=timeout,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    if proc.returncode == 0:
        return
    if proc.returncode == 1:
        msg = proc.stdout.decode(errors="replace") or "infected"
        raise VirusDetectedError(msg.strip(), engine="clamscan")
    err = proc.stderr.decode(errors="replace") or proc.stdout.decode(errors="replace")
    raise RuntimeError(f"clamscan failed ({proc.returncode}): {err.strip()}")


class ClamdScanner:
    """
    Talk to **clamd** over TCP using the INSTREAM protocol (default ``127.0.0.1:3310``).

    Suitable when ``clamd`` is running locally or reachable on the network.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 3310, *, timeout: float = 30.0) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout

    def __call__(self, data: bytes) -> None:
        if not data:
            return
        sock = socket.create_connection((self._host, self._port), timeout=self._timeout)
        try:
            sock.sendall(b"zINSTREAM\0")
            chunk_size = 2048
            offset = 0
            while offset < len(data):
                chunk = data[offset : offset + chunk_size]
                sock.sendall(struct.pack("!I", len(chunk)) + chunk)
                offset += len(chunk)
            sock.sendall(struct.pack("!I", 0))
            response = b""
            while True:
                part = sock.recv(4096)
                if not part:
                    break
                response += part
                if len(response) > 65536:
                    break
        finally:
            sock.close()

        text = response.decode(errors="replace").strip()
        if "FOUND" in text:
            raise VirusDetectedError(text, engine="clamd")
        if "ERROR" in text.upper():
            raise RuntimeError(f"clamd: {text}")
        if "OK" in text or not text:
            return


__all__ = [
    "VirusDetectedError",
    "VirusScanHook",
    "noop_virus_scan",
    "clamscan_bytes",
    "ClamdScanner",
]
