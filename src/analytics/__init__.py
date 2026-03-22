"""
fast_analytics – Analytics and event tracking for FastMVC.
"""

from fast_core import AnalyticsConfiguration, AnalyticsConfigurationDTO

from .base import IAnalyticsBackend, build_analytics_client
from .buffer import BufferedAnalyticsBackend
from .middleware import AnalyticsSamplingMiddleware, default_analytics_user_key
from .pii import ScrubbingAnalyticsBackend, scrub_pii_properties
from .rate_limit import RateLimitedAnalyticsBackend
from .schema_registry import EventSchemaRegistry, parse_versioned_event_name
from .validating_backend import ValidatingAnalyticsBackend

__version__ = "0.3.0"

__all__ = [
    "AnalyticsSamplingMiddleware",
    "BufferedAnalyticsBackend",
    "EventSchemaRegistry",
    "IAnalyticsBackend",
    "RateLimitedAnalyticsBackend",
    "ScrubbingAnalyticsBackend",
    "ValidatingAnalyticsBackend",
    "AnalyticsConfiguration",
    "AnalyticsConfigurationDTO",
    "build_analytics_client",
    "default_analytics_user_key",
    "parse_versioned_event_name",
    "scrub_pii_properties",
]
