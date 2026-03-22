"""Load JSON config files and validate into Pydantic DTOs."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Protocol, Type, TypeVar, runtime_checkable

from loguru import logger
from pydantic import BaseModel

TConfigurationDTO = TypeVar("TConfigurationDTO", bound=BaseModel, covariant=True)


@runtime_checkable
class IConfiguration(Protocol[TConfigurationDTO]):
    """
    Structural type for configuration singletons (e.g. :class:`CacheConfiguration`)
    that expose a validated Pydantic DTO via :meth:`get_config`.
    """

    def get_config(self) -> TConfigurationDTO:
        ...

    def load_config_json(cls, section: str, env_key: str) -> Optional[Dict[str, Any]]:
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


    def validate_config(cls, dto_cls: Type[Any], raw: Optional[Dict[str, Any]]) -> Any:
        """Parse *raw* JSON dict into *dto_cls* (empty dict becomes defaults)."""
        return dto_cls.model_validate(raw or {})

    def __new__(cls, *args, **kwargs) -> IConfiguration[TConfigurationDTO]:
        """Create a new instance of the configuration singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dto = cls.validate_config(
                cls._dto, cls.load_config_json(cls._section, cls._env_key)
            )
        return cls._instance

    def get_config(self) -> TConfigurationDTO:
        """Get the configuration DTO."""
        return self._dto