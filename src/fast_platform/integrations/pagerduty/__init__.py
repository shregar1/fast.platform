"""PagerDuty Integration.

Incident management.
"""

from .client import PagerDutyClient, trigger_incident

__all__ = [
    "PagerDutyClient",
    "trigger_incident",
]
