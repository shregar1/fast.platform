"""
FastMVC Edge Functions Module

Deploy and run Python functions at the edge across 200+ global locations.
"""

from .core import (
    EdgeRuntime,
    EdgeRequest,
    EdgeResponse,
    EdgeFunction,
    edge_function,
    EdgeFunctionRegistry,
)
from .kv import EdgeKV
from .cache import EdgeCache

__all__ = [
    "EdgeRuntime",
    "EdgeRequest",
    "EdgeResponse",
    "EdgeFunction",
    "edge_function",
    "EdgeFunctionRegistry",
    "EdgeKV",
    "EdgeCache",
]
