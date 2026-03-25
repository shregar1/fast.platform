"""Public ``fast_platform`` namespace (re-exports ``core.configuration`` + ``core.dtos``)."""

from .abstraction import IPlatform

from core.configuration import *  # noqa: F403,F401
from core.dtos import *  # noqa: F403,F401

from .taxonomy import (  # noqa: F401
    PACKAGE_TO_SECTION,
    SECTION_TEST_FOLDER,
    SECTION_TO_PACKAGES,
    PackageSection,
    all_taxonomy_packages,
    discover_src_packages,
    packages_in_section,
    section_of,
)
