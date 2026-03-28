"""Public re-exports for :mod:`utils` — shared helpers used across fast-platform.

This package aggregates small, stateless **utility** types (hashing, media sniffing,
archives, time, metrics, etc.). Prefer importing concrete classes from their
submodules when you only need one area; import from :mod:`utils` when you want a
stable barrel of names for application code or tests.

**Optional dependencies:** several utilities (e.g. :class:`~utils.media.pdf.PdfUtility`,
:class:`~utils.media.image.ImageUtility` dimensions) require extras—see
``pyproject.toml`` optional dependency groups such as ``utils-pdf`` and ``pillow``.
"""

from .abstraction import IUtility
from .archive import ArchiveUtility, IArchiveUtility
from .clock import Clock, ClockRegistry, FrozenClock, IClockUtility, SystemClock
from .crowdfunding import CrowdfundingUtility, ICrowdfundingUtility
from .currency import CurrencyUtility, ICurrencyUtility
from .datatype import BooleanUtility, IDatatype, IntegerUtility, StringUtility
from .decimal import DecimalUtility, IDecimalUtility
from .digests import Digests, IDigestsUtility
from .geo import GeoUtility, IGeoUtility
from .hashing import HashingUtility, IHashingUtility
from .html import HtmlUtility, IHtmlUtility
from .idempotency import Idempotency, IIdempotencyUtility
from .jwt import JWTUtility
from .media.audio import AudioUtility
from .media.image import ImageUtility
from .media.pdf import PdfUtility
from .media.text import TextUtility
from .media.video import VideoUtility
from .metrics import Counter, Histogram, IMetricsUtility, MetricsRegistry
from .network import INetworkUtility, NetworkUtility
from .nutrition import INutritionUtility, NutritionUtility
from .optional_imports import IOptionalImportsUtility, OptionalImports
from .phone import IPhoneUtility, PhoneUtility
from .qr import IQRUtility, QRUtility
from .request_id_context import IRequestIdContextUtility, RequestIdContext
from .retry import AsyncRetry, IAsyncRetryUtility
from .sanitization import ISanitization, SanitizationJsonUtility
from .structured_log import (
    IStructuredLogUtility,
    StructuredLog,
    StructuredLogFields,
    StructuredLogSink,
)
from .system import ISystemUtility, SystemUtility
from .temperature import ITemperatureUtility, TemperatureUtility
from .time import ITimeUtility, TimeUtility
from .uuid import IUUIDUtility, UUIDUtility
from .validation import (
    ValidationError,
    RuleEngine,
    rules,
    parse_rule,
    validate,
    validate_json,
    validate_data,
    validate_field,
    quick_validate,
    ValidationUtility,
)

__all__ = [
    "IUtility",
    "IArchiveUtility",
    "IAsyncRetryUtility",
    "IClockUtility",
    "ICrowdfundingUtility",
    "ICurrencyUtility",
    "IDatatype",
    "IDecimalUtility",
    "IDigestsUtility",
    "IGeoUtility",
    "IHashingUtility",
    "IHtmlUtility",
    "IIdempotencyUtility",
    "IMetricsUtility",
    "INetworkUtility",
    "INutritionUtility",
    "IOptionalImportsUtility",
    "IPhoneUtility",
    "IQRUtility",
    "IRequestIdContextUtility",
    "IStructuredLogUtility",
    "ISystemUtility",
    "ITemperatureUtility",
    "ITimeUtility",
    "IUUIDUtility",
    "BooleanUtility",
    "CurrencyUtility",
    "IntegerUtility",
    "StringUtility",
    "ArchiveUtility",
    "AsyncRetry",
    "AudioUtility",
    "Digests",
    "DecimalUtility",
    "GeoUtility",
    "HashingUtility",
    "HtmlUtility",
    "Idempotency",
    "ImageUtility",
    "NetworkUtility",
    "OptionalImports",
    "PdfUtility",
    "PhoneUtility",
    "QRUtility",
    "RequestIdContext",
    "SanitizationJsonUtility",
    "SystemUtility",
    "TemperatureUtility",
    "UUIDUtility",
    "Clock",
    "ClockRegistry",
    "CrowdfundingUtility",
    "FrozenClock",
    "SystemClock",
    "Counter",
    "Histogram",
    "MetricsRegistry",
    "NutritionUtility",
    "TextUtility",
    "TimeUtility",
    "VideoUtility",
    "StructuredLog",
    "StructuredLogFields",
    "StructuredLogSink",
    "ValidationError",
    "RuleEngine",
    "rules",
    "parse_rule",
    "validate",
    "validate_json",
    "validate_data",
    "validate_field",
    "quick_validate",
    "ValidationUtility",
    "JWTUtility",
]
