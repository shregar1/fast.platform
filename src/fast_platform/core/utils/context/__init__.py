"""Context Mixin Module.

Provides shared context attributes and logger binding for framework components
like repositories, services, controllers, and errors.

This eliminates duplication of context fields (urn, user_urn, api_name, user_id)
across the codebase.

Example:
    >>> from fast_platform.core.utils.context import ContextMixin
    >>> class MyService(ContextMixin):
    ...     def __init__(self, **kwargs):
    ...         super().__init__(**kwargs)
    ...         # Context fields are automatically initialized

"""

from __future__ import annotations

from abc import ABC
from typing import Any

from loguru import logger

from .abstraction import IContext


class ContextMixin(ABC):
    """Abstract mixin providing shared context attributes and structured logging.

    This mixin eliminates code duplication across framework components that need
    request context tracking (repositories, services, controllers, errors, etc.).

    Attributes:
        urn (str): Unique Request Number for tracing.
        user_urn (str): User's unique resource name.
        api_name (str): Name of the API endpoint.
        user_id (str): Database identifier of the user.
        logger: Structured logger bound with request context.

    Example:
        >>> class MyRepository(ContextMixin):
        ...     def __init__(self, session, **kwargs):
        ...         super().__init__(**kwargs)
        ...         self.session = session
        ...         # logger is automatically bound with context
        ...         self.logger.info("Repository initialized")

    """

    def __init__(
        self,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize context fields and structured logger.

        Args:
            urn: Unique Request Number for tracing.
            user_urn: User's unique resource name.
            api_name: Name of the API endpoint.
            user_id: Database identifier of the user (string form).
            **kwargs: Additional arguments passed to parent classes.

        """
        super().__init__(**kwargs)
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
        )

    @property
    def urn(self) -> str | None:
        """Unique Request Number for tracing."""
        return self._urn

    @urn.setter
    def urn(self, value: str | None) -> None:
        """Execute urn operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._urn = value
        self._rebind_logger()

    @property
    def user_urn(self) -> str | None:
        """User's unique resource name."""
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str | None) -> None:
        """Execute user_urn operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._user_urn = value
        self._rebind_logger()

    @property
    def api_name(self) -> str | None:
        """Name of the API endpoint."""
        return self._api_name

    @api_name.setter
    def api_name(self, value: str | None) -> None:
        """Execute api_name operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._api_name = value
        self._rebind_logger()

    @property
    def user_id(self) -> int | None:
        """Database identifier of the user."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: int | None) -> None:
        """Execute user_id operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._user_id = value
        self._rebind_logger()

    @property
    def logger(self) -> Any:
        """Structured logger bound with request context."""
        return self._logger

    @logger.setter
    def logger(self, value: Any) -> None:
        """Execute logger operation.

        Args:
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        self._logger = value

    def _rebind_logger(self) -> None:
        """Rebind logger when context fields change."""
        self._logger = logger.bind(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
        )

    def get_context_dict(self) -> dict[str, Any]:
        """Get context fields as a dictionary.

        Returns:
            Dictionary with urn, user_urn, api_name, user_id.

        Example:
            >>> context = service.get_context_dict()
            >>> new_service = AnotherService(**context)

        """
        return {
            "urn": self._urn,
            "user_urn": self._user_urn,
            "api_name": self._api_name,
            "user_id": self._user_id,
        }

    def copy_context_to(self, target: ContextMixin) -> None:
        """Copy context fields to another ContextMixin instance.

        Args:
            target: Another instance to copy context to.

        Example:
            >>> service.copy_context_to(repository)

        """
        target.urn = self._urn
        target.user_urn = self._user_urn
        target.api_name = self._api_name
        target.user_id = self._user_id


__all__ = ["ContextMixin", "IContext"]
