"""Tests for media."""

import pytest


def test_imports():
    from media import (
        IMediaStore,
        UploadResult,
        read_upload_as_bytes,
        generate_image_variant,
        validate_content_type,
        ImageVariantPipeline,
        noop_virus_scan,
    )
    assert validate_content_type("image/jpeg", ["image/jpeg"]) is True
    assert validate_content_type("image/svg+xml", ["image/jpeg"]) is False
    assert ImageVariantPipeline is not None
    noop_virus_scan(b"")
