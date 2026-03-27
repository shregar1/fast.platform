"""Install lightweight fake ``typesense`` / ``meilisearch`` / ``opensearchpy`` modules for factory tests."""

from __future__ import annotations

import sys
import types


def install_fake_typesense() -> None:
    """Execute install_fake_typesense operation.

    Returns:
        The result of the operation.
    """
    m = types.ModuleType("typesense")

    class Client:
        """Represents the Client class."""

        def __init__(self, _cfg: object) -> None:
            """Execute __init__ operation.

            Args:
                _cfg: The _cfg parameter.
            """
            pass

    m.Client = Client
    sys.modules["typesense"] = m


def install_fake_meilisearch() -> None:
    """Execute install_fake_meilisearch operation.

    Returns:
        The result of the operation.
    """
    m = types.ModuleType("meilisearch")

    class Client:
        """Represents the Client class."""

        def __init__(self, _url: str, _key: object = None) -> None:
            """Execute __init__ operation.

            Args:
                _url: The _url parameter.
                _key: The _key parameter.
            """
            pass

    m.Client = Client
    sys.modules["meilisearch"] = m


def install_fake_opensearch() -> None:
    """Execute install_fake_opensearch operation.

    Returns:
        The result of the operation.
    """
    m = types.ModuleType("opensearchpy")

    class OpenSearch:
        """Represents the OpenSearch class."""

        def __init__(self, **_kwargs: object) -> None:
            """Execute __init__ operation."""
            pass

    m.OpenSearch = OpenSearch
    sys.modules["opensearchpy"] = m


def cleanup_fake_modules(*names: str) -> None:
    """Execute cleanup_fake_modules operation.

    Returns:
        The result of the operation.
    """
    for n in names:
        sys.modules.pop(n, None)
