from __future__ import annotations

"""Ensure :mod:`fast_platform.taxonomy` matches the ``src/`` package tree."""

from tests.core.fast_platform.abstraction import IFastPlatformTests

from fast_platform.taxonomy import (
    PACKAGE_TO_SECTION,
    SECTION_TEST_FOLDER,
    PackageSection,
    all_taxonomy_packages,
    discover_src_packages,
)


class TestTaxonomySync(IFastPlatformTests):
    def test_every_src_package_is_mapped(self) -> None:
        src = discover_src_packages()
        registered = all_taxonomy_packages()
        missing = src - registered
        extra = registered - src
        assert not missing, f"Add missing packages to PACKAGE_TO_SECTION: {missing}"
        assert not extra, f"Remove stale taxonomy entries (no src dir): {extra}"

    def test_section_test_folder_covers_all_sections(self) -> None:
        assert set(SECTION_TEST_FOLDER.keys()) == set(PackageSection)

    def test_package_section_maps_to_test_folder(self) -> None:
        for pkg, sec in PACKAGE_TO_SECTION.items():
            folder = SECTION_TEST_FOLDER[sec]
            assert folder and folder.isidentifier()
