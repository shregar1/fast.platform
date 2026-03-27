"""Module abstraction.py."""

from __future__ import annotations

from tests.integrations.abstraction import IIntegrationsSuite

"""Test-suite markers for ``llm`` (mirrors ``src/llm/``)."""


from abc import ABC


class ILLMTests(IIntegrationsSuite, ABC):
    """Marker base for test classes covering :mod:`llm`."""

    __slots__ = ()


__all__ = ["ILLMTests"]
