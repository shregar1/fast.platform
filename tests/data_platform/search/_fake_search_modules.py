"""Install lightweight fake ``typesense`` / ``meilisearch`` / ``opensearchpy`` modules for factory tests."""

from __future__ import annotations

import sys
import types


def install_fake_typesense() -> None:
    m = types.ModuleType("typesense")

    class Client:
        def __init__(self, _cfg: object) -> None:
            pass

    m.Client = Client
    sys.modules["typesense"] = m


def install_fake_meilisearch() -> None:
    m = types.ModuleType("meilisearch")

    class Client:
        def __init__(self, _url: str, _key: object = None) -> None:
            pass

    m.Client = Client
    sys.modules["meilisearch"] = m


def install_fake_opensearch() -> None:
    m = types.ModuleType("opensearchpy")

    class OpenSearch:
        def __init__(self, **_kwargs: object) -> None:
            pass

    m.OpenSearch = OpenSearch
    sys.modules["opensearchpy"] = m


def cleanup_fake_modules(*names: str) -> None:
    for n in names:
        sys.modules.pop(n, None)
