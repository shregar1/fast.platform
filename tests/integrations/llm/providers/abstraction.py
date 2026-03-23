from __future__ import annotations

"""Test-suite markers for ``llm/providers`` (mirrors ``src/llm/providers/``)."""

from abc import ABC

from tests.integrations.llm.abstraction import ILLMTests


class ILLMProvidersTests(ILLMTests, ABC):
    """Marker base for test classes covering :mod:`integrations.llm.providers`."""

    __slots__ = ()


__all__ = ["ILLMProvidersTests"]
