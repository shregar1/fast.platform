"""Module test_taxonomy_sync.py."""

from __future__ import annotations

"""Ensure :mod:`fast_platform.taxonomy` matches the ``src/`` package tree."""

from fast_platform.taxonomy import (
    PACKAGE_TO_SECTION,
    SECTION_TEST_FOLDER,
    PackageSection,
    all_taxonomy_packages,
    discover_src_packages,
)
from tests.core.fast_platform.abstraction import IFastPlatformTests


class TestTaxonomySync(IFastPlatformTests):
    """Represents the TestTaxonomySync class."""

    def test_every_src_package_is_mapped(self) -> None:
        """Execute test_every_src_package_is_mapped operation.

        Returns:
            The result of the operation.
        """
        src = discover_src_packages()
        registered = all_taxonomy_packages()
        missing = src - registered
        extra = registered - src
        assert not missing, f"Add missing packages to PACKAGE_TO_SECTION: {missing}"
        assert not extra, f"Remove stale taxonomy entries (no src dir): {extra}"

    def test_section_test_folder_covers_all_sections(self) -> None:
        """Execute test_section_test_folder_covers_all_sections operation.

        Returns:
            The result of the operation.
        """
        assert set(SECTION_TEST_FOLDER.keys()) == set(PackageSection)

    def test_package_section_maps_to_test_folder(self) -> None:
        """Execute test_package_section_maps_to_test_folder operation.

        Returns:
            The result of the operation.
        """
        for pkg, sec in PACKAGE_TO_SECTION.items():
            folder = SECTION_TEST_FOLDER[sec]
            assert folder and folder.isidentifier()

    def test_canonical_core_imports_resolve(self) -> None:
        """DTOs and configuration live under ``core.*``, not messaging shims."""
        from fast_platform.core.configuration.kafka import KafkaConfiguration
        from fast_platform.core.configuration.notifications import NotificationsConfiguration
        from fast_platform.core.dtos.kafka import KafkaConfigurationDTO, KafkaJsonEnvelope
        from fast_platform.core.dtos.notifications import NotificationFanoutRequest
        from fast_platform.core.dtos.search import SearchConfigurationDTO

        assert KafkaConfiguration is not None
        assert NotificationsConfiguration is not None
        assert KafkaConfigurationDTO is not None
        assert KafkaJsonEnvelope is not None
        assert NotificationFanoutRequest is not None
        assert SearchConfigurationDTO is not None
