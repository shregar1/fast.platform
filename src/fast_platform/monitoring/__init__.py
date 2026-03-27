"""FastMVC Monitoring Module.

Synthetic monitoring, SLA tracking, and alerting.
"""

from .synthetic import (
    synthetic_check,
    SyntheticMonitor,
    CheckResult,
)
from .sla import (
    track_sla,
    SLA,
)

__all__ = [
    "synthetic_check",
    "SyntheticMonitor",
    "CheckResult",
    "track_sla",
    "SLA",
]
