"""Geographic coordinate (WGS84) distance and bearing utilities."""

from __future__ import annotations

import math
from typing import Tuple, Union

from .abstraction import IGeoUtility


class GeoUtility(IGeoUtility):
    """Pure-math geodesic distance (Haversine) and bearing helpers.

    Operates in decimal degrees (EPSG:4326/WGS84). Standard for mobile/web GPS.
    """

    EARTH_RADIUS_KM = 6371.0
    EARTH_RADIUS_MILES = 3958.8

    @staticmethod
    def distance_haversine(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        *,
        miles: bool = False,
    ) -> float:
        """Return the great-circle distance between two points in km (default)."""
        # Convert to radians
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        # Haversine formula
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        r = GeoUtility.EARTH_RADIUS_MILES if miles else GeoUtility.EARTH_RADIUS_KM
        return r * c

    @staticmethod
    def calculate_bearing(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Return the initial bearing from point 1 to point 2 in degrees [0, 360)."""
        lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
        diff_lon = math.radians(lon2 - lon1)

        x = math.sin(diff_lon) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - (
            math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(diff_lon)
        )

        initial_bearing = math.atan2(x, y)
        # Normalize to 0-360
        return (math.degrees(initial_bearing) + 360) % 360

    @staticmethod
    def is_valid_lat(lat: Union[float, int]) -> bool:
        """True if *lat* is in range [-90, 90]."""
        return -90 <= float(lat) <= 90

    @staticmethod
    def is_valid_lon(lon: Union[float, int]) -> bool:
        """True if *lon* is in range [-180, 180]."""
        return -180 <= float(lon) <= 180

    @staticmethod
    def is_valid_coordinate(lat: float, lon: float) -> bool:
        """True if both latitude and longitude are valid."""
        return GeoUtility.is_valid_lat(lat) and GeoUtility.is_valid_lon(lon)


__all__ = ["GeoUtility", "IGeoUtility"]
