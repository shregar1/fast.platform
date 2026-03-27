"""Tests for media."""

from tests.integrations.media.abstraction import IFastMediaTests


class TestInit(IFastMediaTests):
    """Represents the TestInit class."""

    def test_imports(self) -> None:
        """Execute test_imports operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.integrations.media import (
            ImageVariantPipeline,
            IMediaStore,
            UploadResult,
            generate_image_variant,
            noop_virus_scan,
            read_upload_as_bytes,
            validate_content_type,
        )

        assert IMediaStore is not None
        assert UploadResult is not None
        assert read_upload_as_bytes is not None
        assert generate_image_variant is not None
        assert ImageVariantPipeline is not None
        assert validate_content_type("image/jpeg", ["image/jpeg"]) is True
        assert validate_content_type("image/svg+xml", ["image/jpeg"]) is False
        noop_virus_scan(b"")
