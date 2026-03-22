"""Load configuration JSON and singleton configuration accessors."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Type

from loguru import logger

from config.dto import (
    AnalyticsConfigurationDTO,
    CacheConfigurationDTO,
    DBConfigurationDTO,
    DatadogConfigurationDTO,
    EventsConfigurationDTO,
    IdentityProvidersConfigurationDTO,
    LLMConfigurationDTO,
    QueuesConfigurationDTO,
    SearchConfigurationDTO,
    SecretsConfigurationDTO,
    StorageConfigurationDTO,
    StreamsConfigurationDTO,
    TelemetryConfigurationDTO,
    VectorsConfigurationDTO,
)
from config.dto_extras import JobsConfigurationDTO, RealtimeConfigurationDTO


def load_config_json(section: str, env_key: str) -> Optional[Dict[str, Any]]:
    """
    Load ``config/<section>/config.json`` (or ``FASTMVC_CONFIG_BASE/<section>/config.json``).

    ``env_key`` is used for ``FASTMVC_{env_key}_CONFIG_PATH`` override.
    """
    path = os.getenv(f"FASTMVC_{env_key}_CONFIG_PATH")
    if not path:
        base = os.getenv("FASTMVC_CONFIG_BASE")
        path = os.path.join(base, section, "config.json") if base else f"config/{section}/config.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug("Config file not found: %s", path)
        return None
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in %s: %s", path, exc)
        return None


def _validate(dto_cls: Type[Any], raw: Optional[Dict[str, Any]]) -> Any:
    return dto_cls.model_validate(raw or {})


class DBConfiguration:
    _instance: Optional["DBConfiguration"] = None

    def __new__(cls) -> "DBConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(DBConfigurationDTO, load_config_json("db", "DB"))
        return cls._instance

    def get_config(self) -> DBConfigurationDTO:
        return self._dto


class SecretsConfiguration:
    _instance: Optional["SecretsConfiguration"] = None

    def __new__(cls) -> "SecretsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(SecretsConfigurationDTO, load_config_json("secrets", "SECRETS"))
        return cls._instance

    def get_config(self) -> SecretsConfigurationDTO:
        return self._dto


class CacheConfiguration:
    _instance: Optional["CacheConfiguration"] = None

    def __new__(cls) -> "CacheConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(CacheConfigurationDTO, load_config_json("cache", "CACHE"))
        return cls._instance

    def get_config(self) -> CacheConfigurationDTO:
        return self._dto


class LLMConfiguration:
    _instance: Optional["LLMConfiguration"] = None

    def __new__(cls) -> "LLMConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(LLMConfigurationDTO, load_config_json("llm", "LLM"))
        return cls._instance

    def get_config(self) -> LLMConfigurationDTO:
        return self._dto


class IdentityProvidersConfiguration:
    _instance: Optional["IdentityProvidersConfiguration"] = None

    def __new__(cls) -> "IdentityProvidersConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(
                IdentityProvidersConfigurationDTO, load_config_json("identity", "IDENTITY")
            )
        return cls._instance

    def get_config(self) -> IdentityProvidersConfigurationDTO:
        return self._dto


class VectorsConfiguration:
    _instance: Optional["VectorsConfiguration"] = None

    def __new__(cls) -> "VectorsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(VectorsConfigurationDTO, load_config_json("vectors", "VECTORS"))
        return cls._instance

    def get_config(self) -> VectorsConfigurationDTO:
        return self._dto


class StorageConfiguration:
    _instance: Optional["StorageConfiguration"] = None

    def __new__(cls) -> "StorageConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(StorageConfigurationDTO, load_config_json("storage", "STORAGE"))
        return cls._instance

    def get_config(self) -> StorageConfigurationDTO:
        return self._dto


class SearchConfiguration:
    _instance: Optional["SearchConfiguration"] = None

    def __new__(cls) -> "SearchConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(SearchConfigurationDTO, load_config_json("search", "SEARCH"))
        return cls._instance

    def get_config(self) -> SearchConfigurationDTO:
        return self._dto


class QueuesConfiguration:
    _instance: Optional["QueuesConfiguration"] = None

    def __new__(cls) -> "QueuesConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(QueuesConfigurationDTO, load_config_json("queues", "QUEUES"))
        return cls._instance

    def get_config(self) -> QueuesConfigurationDTO:
        return self._dto


class JobsConfiguration:
    _instance: Optional["JobsConfiguration"] = None

    def __new__(cls) -> "JobsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(JobsConfigurationDTO, load_config_json("jobs", "JOBS"))
        return cls._instance

    def get_config(self) -> JobsConfigurationDTO:
        return self._dto


class AnalyticsConfiguration:
    _instance: Optional["AnalyticsConfiguration"] = None

    def __new__(cls) -> "AnalyticsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(
                AnalyticsConfigurationDTO, load_config_json("analytics", "ANALYTICS")
            )
        return cls._instance

    def get_config(self) -> AnalyticsConfigurationDTO:
        return self._dto


class EventsConfiguration:
    _instance: Optional["EventsConfiguration"] = None

    def __new__(cls) -> "EventsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(EventsConfigurationDTO, load_config_json("events", "EVENTS"))
        return cls._instance

    @classmethod
    def instance(cls) -> "EventsConfiguration":
        return cls()

    def get_config(self) -> EventsConfigurationDTO:
        return self._dto


class StreamsConfiguration:
    _instance: Optional["StreamsConfiguration"] = None

    def __new__(cls) -> "StreamsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(StreamsConfigurationDTO, load_config_json("streams", "STREAMS"))
        return cls._instance

    @classmethod
    def instance(cls) -> "StreamsConfiguration":
        return cls()

    def get_config(self) -> StreamsConfigurationDTO:
        return self._dto


class TelemetryConfiguration:
    _instance: Optional["TelemetryConfiguration"] = None

    def __new__(cls) -> "TelemetryConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(
                TelemetryConfigurationDTO, load_config_json("telemetry", "TELEMETRY")
            )
        return cls._instance

    def get_config(self) -> TelemetryConfigurationDTO:
        return self._dto


class DatadogConfiguration:
    _instance: Optional["DatadogConfiguration"] = None

    def __new__(cls) -> "DatadogConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(
                DatadogConfigurationDTO, load_config_json("datadog", "DATADOG")
            )
        return cls._instance

    def get_config(self) -> DatadogConfigurationDTO:
        return self._dto


class RealtimeConfiguration:
    _instance: Optional["RealtimeConfiguration"] = None

    def __new__(cls) -> "RealtimeConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = _validate(
                RealtimeConfigurationDTO, load_config_json("realtime", "REALTIME")
            )
        return cls._instance

    def get_config(self) -> RealtimeConfigurationDTO:
        return self._dto


__all__ = [
    "AnalyticsConfiguration",
    "CacheConfiguration",
    "DBConfiguration",
    "DatadogConfiguration",
    "EventsConfiguration",
    "IdentityProvidersConfiguration",
    "JobsConfiguration",
    "LLMConfiguration",
    "QueuesConfiguration",
    "RealtimeConfiguration",
    "SearchConfiguration",
    "SecretsConfiguration",
    "StorageConfiguration",
    "StreamsConfiguration",
    "TelemetryConfiguration",
    "VectorsConfiguration",
    "load_config_json",
]
