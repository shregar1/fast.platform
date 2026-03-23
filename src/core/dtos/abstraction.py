"""Base types for Pydantic DTOs in the ``dtos`` package."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class IDTO(BaseModel):
    """Base model for configuration and API DTOs (consistent ``extra`` policy)."""

    model_config = ConfigDict(extra="ignore")


__all__ = ["IDTO"]
