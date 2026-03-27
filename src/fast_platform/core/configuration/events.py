"""Singleton accessor for events configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos import EventsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class EventsConfiguration(ConfigurationSingletonBase[EventsConfigurationDTO]):
    """Represents the EventsConfiguration class."""

    _instance: Optional["EventsConfiguration"] = None
    _section: str = "events"
    _env_key: str = "EVENTS"
    _dto: Type[EventsConfigurationDTO] = EventsConfigurationDTO
