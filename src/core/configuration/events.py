"""Singleton accessor for events configuration."""

from __future__ import annotations

from typing import Optional, Type

from core.dtos import EventsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class EventsConfiguration(ConfigurationSingletonBase[EventsConfigurationDTO]):
    _instance: Optional["EventsConfiguration"] = None
    _section: str = "events"
    _env_key: str = "EVENTS"
    _dto: Type[EventsConfigurationDTO] = EventsConfigurationDTO
