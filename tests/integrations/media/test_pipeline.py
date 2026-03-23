"""Tests for image variant pipeline and default generator."""

import io

from PIL import Image

from integrations.media import (
    DefaultImageVariantGenerator,
    ImageVariantPipeline,
    InMemoryMediaStore,
    VariantSpec,
    variant_storage_key,
)
from tests.integrations.media.abstraction import IFastMediaTests


def _rgb_png_bytes() -> bytes:
    img = Image.new("RGB", (400, 300), color=(10, 20, 30))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestPipeline(IFastMediaTests):
    def test_variant_storage_key(self):
        assert variant_storage_key("a/b/c.jpg", "thumb", "webp") == "a/b/c_thumb.webp"
        assert variant_storage_key("photo.png", "webp", "webp") == "photo_webp.webp"

    def test_pipeline_uploads_thumb_and_webp(self):
        store = InMemoryMediaStore()
        pipe = ImageVariantPipeline(store)
        png = _rgb_png_bytes()
        out = pipe.process(base_key="uploads/x.png", source_bytes=png)
        assert set(out.keys()) == {"thumb", "webp"}
        assert out["thumb"].key == "uploads/x_thumb.webp"
        assert out["webp"].key == "uploads/x_webp.webp"
        assert store.get_bytes(out["thumb"].key)[:4] == b"RIFF"
        assert store.get_bytes(out["webp"].key)[:4] == b"RIFF"

    def test_pipeline_custom_variants(self):
        store = InMemoryMediaStore()
        pipe = ImageVariantPipeline(store, variants=(VariantSpec("small", 50, 50, "webp", 80),))
        png = _rgb_png_bytes()
        out = pipe.process(base_key="z.jpg", source_bytes=png)
        assert list(out.keys()) == ["small"]
        assert len(store.get_bytes(out["small"].key)) > 0

    def test_default_generator_roundtrip(self):
        store = InMemoryMediaStore()
        png = _rgb_png_bytes()
        store.upload("orig/x.png", png, content_type="image/png")
        gen = DefaultImageVariantGenerator(store, fetch_bytes=store.get_bytes)
        k = gen.generate("orig/x.png", "thumb")
        assert k == "orig/x_thumb.webp"
        assert store.get_bytes(k)[:4] == b"RIFF"
