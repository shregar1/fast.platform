"""
Public re-exports for :mod:`utils` — shared helpers used across fast-platform.

This package aggregates small, stateless **utility** types (hashing, media sniffing,
archives, time, metrics, etc.). Prefer importing concrete classes from their
submodules when you only need one area; import from :mod:`utils` when you want a
stable barrel of names for application code or tests.

**Optional dependencies:** several utilities (e.g. :class:`~utils.media.pdf.PdfUtility`,
:class:`~utils.media.image.ImageUtility` dimensions) require extras—see
``pyproject.toml`` optional dependency groups such as ``utils-pdf`` and ``pillow``.
"""

from .abstraction import IUtility
from .archive import ArchiveUtility
from .clock import Clock, ClockRegistry, FrozenClock, SystemClock
from .currency import CurrencyUtility
from .datatype import BooleanUtility, IDatatype, IntegerUtility, StringUtility
from .decimal import DecimalUtility
from .digests import Digests
from .hashing import HashingUtility
from .html import HtmlUtility
from .idempotency import Idempotency
from .media.audio import AudioUtility
from .media.image import ImageUtility
from .media.pdf import PdfUtility
from .media.text import TextUtility
from .media.video import VideoUtility
from .metrics import Counter, Histogram, MetricsRegistry
from .nutrition import NutritionUtility
from .optional_imports import OptionalImports
from .request_id_context import RequestIdContext
from .retry import AsyncRetry
from .structured_log import StructuredLog, StructuredLogFields, StructuredLogSink
from .time import TimeUtility

__all__ = [
    "IUtility",
    "BooleanUtility",
    "CurrencyUtility",
    "IDatatype",
    "IntegerUtility",
    "StringUtility",
    "ArchiveUtility",
    "AudioUtility",
    "Digests",
    "HashingUtility",
    "HtmlUtility",
    "Idempotency",
    "ImageUtility",
    "OptionalImports",
    "PdfUtility",
    "RequestIdContext",
    "Clock",
    "ClockRegistry",
    "FrozenClock",
    "SystemClock",
    "Counter",
    "Histogram",
    "MetricsRegistry",
    "DecimalUtility",
    "NutritionUtility",
    "AsyncRetry",
    "TextUtility",
    "TimeUtility",
    "VideoUtility",
    "StructuredLog",
    "StructuredLogFields",
    "StructuredLogSink",
]
