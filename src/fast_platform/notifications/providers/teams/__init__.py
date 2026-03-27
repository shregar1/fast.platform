"""Microsoft Teams Integration.

Send notifications to Microsoft Teams via webhooks.
"""

from .client import TeamsClient, TeamsCard

__all__ = ["TeamsClient", "TeamsCard"]
