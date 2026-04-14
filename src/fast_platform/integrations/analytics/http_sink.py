from __future__ import annotations
"""HTTP sink analytics backend (generic event forwarding)."""

from ...core.constants import HEADER_AUTHORIZATION
from ...core.constants import CONTENT_TYPE_APPLICATION_JSON, DEFAULT_TIMEOUT_SECONDS, HEADER_CONTENT_TYPE

from typing import Any, Optional

from .base import IAnalyticsBackend


class HttpSinkAnalyticsBackend(IAnalyticsBackend):
    """Send events to an HTTP endpoint (e.g. webhook, custom collector)."""

    def __init__(self, endpoint: str, api_key: Optional[str] = None) -> None:
        """Execute __init__ operation.

        Args:
            endpoint: The endpoint parameter.
            api_key: The api_key parameter.
        """
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key

    def track(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        """Execute track operation.

        Args:
            distinct_id: The distinct_id parameter.
            event_name: The event_name parameter.
            properties: The properties parameter.

        Returns:
            The result of the operation.
        """
        try:
            import json
            import urllib.request

            data = json.dumps(
                {
                    "distinct_id": distinct_id,
                    "event": event_name,
                    "properties": properties or {},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                self._endpoint,
                data=data,
                headers={
                    HEADER_CONTENT_TYPE: CONTENT_TYPE_APPLICATION_JSON,
                    **({HEADER_AUTHORIZATION: f"Bearer {self._api_key}"} if self._api_key else {}),
                },
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass  # best-effort

    def identify(self, distinct_id: str, traits: Optional[dict[str, Any]] = None) -> None:
        """Execute identify operation.

        Args:
            distinct_id: The distinct_id parameter.
            traits: The traits parameter.

        Returns:
            The result of the operation.
        """
        try:
            import json
            import urllib.request

            data = json.dumps(
                {
                    "distinct_id": distinct_id,
                    "traits": traits or {},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                self._endpoint + "/identify" if self._endpoint else self._endpoint,
                data=data,
                headers={
                    HEADER_CONTENT_TYPE: CONTENT_TYPE_APPLICATION_JSON,
                    **({HEADER_AUTHORIZATION: f"Bearer {self._api_key}"} if self._api_key else {}),
                },
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass

    def delete_user(self, distinct_id: str) -> None:
        """POST ``/forget`` with ``distinct_id`` (extend your collector to forward to vendors)."""
        try:
            import json
            import urllib.request

            data = json.dumps({"distinct_id": distinct_id}).encode("utf-8")
            req = urllib.request.Request(
                f"{self._endpoint}/forget",
                data=data,
                headers={
                    HEADER_CONTENT_TYPE: CONTENT_TYPE_APPLICATION_JSON,
                    **({HEADER_AUTHORIZATION: f"Bearer {self._api_key}"} if self._api_key else {}),
                },
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass
