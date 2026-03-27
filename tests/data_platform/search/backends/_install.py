"""Helpers for injecting fake client modules into ``sys.modules``."""

from __future__ import annotations

import sys
import types


def install_module(name: str, module_obj: types.ModuleType) -> None:
    """Execute install_module operation.

    Args:
        name: The name parameter.
        module_obj: The module_obj parameter.

    Returns:
        The result of the operation.
    """
    sys.modules[name] = module_obj
