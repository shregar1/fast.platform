"""IP address, CIDR, and port validation utilities."""

from __future__ import annotations

import ipaddress
import socket
from typing import Optional, Union

from .abstraction import INetworkUtility


class NetworkUtility(INetworkUtility):
    """Network-related helpers using standard :mod:`ipaddress` and :mod:`socket`."""

    @staticmethod
    def is_ipv4(value: str) -> bool:
        """True if *value* is a valid IPv4 address."""
        try:
            ip = ipaddress.ip_address(value)
            return isinstance(ip, ipaddress.IPv4Address)
        except ValueError:
            return False

    @staticmethod
    def is_ipv6(value: str) -> bool:
        """True if *value* is a valid IPv6 address."""
        try:
            ip = ipaddress.ip_address(value)
            return isinstance(ip, ipaddress.IPv6Address)
        except ValueError:
            return False

    @staticmethod
    def is_valid_ip(value: str) -> bool:
        """True if *value* is a valid IP address (v4 or v6)."""
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_cidr(value: str) -> bool:
        """True if *value* is a valid CIDR network (e.g. "192.168.1.0/24")."""
        try:
            ipaddress.ip_network(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_private_ip(value: str) -> bool:
        """True if the IP is in a private/local range."""
        try:
            return ipaddress.ip_address(value).is_private
        except ValueError:
            return False

    @staticmethod
    def get_hostname() -> str:
        """Return the current system's hostname."""
        return socket.gethostname()

    @staticmethod
    def resolve_ip(hostname: str) -> Optional[str]:
        """Resolve a hostname to its first IP address, or None if resolution fails."""
        try:
            return socket.gethostbyname(hostname)
        except (socket.gaierror, socket.herror):
            return None

    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
        """Quickly check if a port is open on a host."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


__all__ = ["NetworkUtility", "INetworkUtility"]
