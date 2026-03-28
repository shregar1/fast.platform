"""Singleton accessor for ClickHouse configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos.clickhouse import ClickHouseConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class ClickHouseConfiguration(ConfigurationSingletonBase[ClickHouseConfigurationDTO]):
    """Represents the ClickHouseConfiguration class."""

    _instance: Optional["ClickHouseConfiguration"] = None
    _section: str = "clickhouse"
    _env_key: str = "CLICKHOUSE"
    _dto: Type[ClickHouseConfigurationDTO] = ClickHouseConfigurationDTO
