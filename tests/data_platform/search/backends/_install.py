"""Helpers for injecting fake client modules into ``sys.modules``."""

from __future__ import annotations

import sys
import types


def install_module(name: str, module_obj: types.ModuleType) -> None:
    sys.modules[name] = module_obj
