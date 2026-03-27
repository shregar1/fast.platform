"""Singleton accessor for vectors configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos import VectorsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class VectorsConfiguration(ConfigurationSingletonBase[VectorsConfigurationDTO]):
    """Represents the VectorsConfiguration class."""

    _instance: Optional["VectorsConfiguration"] = None
    _section: str = "vectors"
    _env_key: str = "VECTORS"
    _dto: Type[VectorsConfigurationDTO] = VectorsConfigurationDTO
