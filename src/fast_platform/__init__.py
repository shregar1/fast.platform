"""Public ``fast_platform`` namespace (re-exports ``configuration`` + ``dtos`` for flat ``src`` layout)."""

from configuration import *  # noqa: F403
from dtos import *  # noqa: F403

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
