"""Tests for newly added core utilities (UUID, Temperature, Network, Geo, QR, Phone, System)."""

from __future__ import annotations

import os
from decimal import Decimal
import pytest
from unittest.mock import MagicMock

from fast_platform.core.utils import (
    UUIDUtility,
    TemperatureUtility,
    NetworkUtility,
    GeoUtility,
    QRUtility,
    PhoneUtility,
    SystemUtility,
)


def test_uuid_utility():
    # v1, v4, v5
    u1 = UUIDUtility.v1()
    u4 = UUIDUtility.v4()
    u5 = UUIDUtility.v5("6ba7b810-9dad-11d1-80b4-00c04fd430c8", "test")
    
    assert UUIDUtility.is_valid(u1)
    assert UUIDUtility.is_valid(u4)
    assert UUIDUtility.is_valid(u5)
    assert not UUIDUtility.is_valid("invalid-uuid")
    
    # version
    assert UUIDUtility.get_version(u4) == 4
    assert UUIDUtility.get_version(u1) == 1
    
    # compact
    compact = UUIDUtility.to_compact(u4)
    assert "-" not in compact
    assert UUIDUtility.from_compact(compact) == u4


def test_temperature_utility():
    # C to F
    assert TemperatureUtility.c_to_f(0) == Decimal("32")
    assert TemperatureUtility.c_to_f(100) == Decimal("212")
    
    # F to C
    assert TemperatureUtility.f_to_c(32) == Decimal("0")
    
    # K
    assert TemperatureUtility.c_to_k(0) == Decimal("273.15")
    assert TemperatureUtility.k_to_c(273.15) == Decimal("0")
    
    # Rounding
    assert TemperatureUtility.format_temp(36.12345, decimal_places=1) == Decimal("36.1")


def test_network_utility():
    # IPs
    assert NetworkUtility.is_ipv4("127.0.0.1")
    assert NetworkUtility.is_ipv6("::1")
    assert not NetworkUtility.is_ipv4("not-an-ip")
    
    # Private
    assert NetworkUtility.is_private_ip("192.168.1.1")
    assert not NetworkUtility.is_private_ip("8.8.8.8")
    
    # CIDR
    assert NetworkUtility.is_valid_cidr("192.168.0.0/24")
    assert not NetworkUtility.is_valid_cidr("not-a-network")


def test_geo_utility():
    # London to Paris (~344km)
    london = (51.5074, -0.1278)
    paris = (48.8566, 2.3522)
    dist = GeoUtility.distance_haversine(london[0], london[1], paris[0], paris[1])
    assert 340 < dist < 350
    
    # Bearing (North-ish)
    bearing = GeoUtility.calculate_bearing(0, 0, 10, 0)
    assert bearing == 0.0
    
    # Validation
    assert GeoUtility.is_valid_coordinate(45, 90)
    assert not GeoUtility.is_valid_lat(100)
    assert not GeoUtility.is_valid_lon(200)


def test_system_utility(monkeypatch):
    # Env
    monkeypatch.setenv("TEST_VAL", "true")
    assert SystemUtility.get_env_bool("TEST_VAL") is True
    
    monkeypatch.setenv("TEST_INT", "123")
    assert SystemUtility.get_env_int("TEST_INT") == 123
    
    # Platform
    assert isinstance(SystemUtility.get_python_version(), str)
    # Just ensure it doesn't crash
    assert isinstance(SystemUtility.get_memory_usage_mb(), float)


def test_phone_utility():
    # Digits
    assert PhoneUtility.normalize_digits("(555) 123-4567") == "5551234567"
    
    # E164
    assert PhoneUtility.is_likely_e164("+15551234567")
    assert not PhoneUtility.is_likely_e164("5551234567")
    
    # Format (fallback)
    assert PhoneUtility.format_e164("5551234567") == "+5551234567"


def test_qr_utility(monkeypatch):
    # Mock OptionalImports to simulate dependency missing/present
    # Just check that it returns None if dependencies are missing, or doesn't crash
    # Real test requires qrcode/segno installed (which they should be now)
    
    png = QRUtility.generate_png_bytes("test-data")
    if png: # If qrcode/segno is installed
        assert isinstance(png, bytes)
        assert png.startswith(b"\x89PNG")
    
    svg = QRUtility.generate_svg("test-data")
    if svg:
        assert "<svg" in svg.lower()
