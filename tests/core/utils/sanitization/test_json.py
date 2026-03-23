"""Tests for API response JSON sanitization."""

from tests.core.utils.abstraction import IUtilsTests


class TestSanitizationJsonUtility(IUtilsTests):
    def test_removes_id_fields_recursively(self) -> None:
        from core.utils.sanitization import SanitizationJsonUtility

        data = {
            "id": 1,
            "user_id": "x",
            "urn": "urn:ok",
            "nested": {"id": 2, "keep": True},
        }
        out = SanitizationJsonUtility.sanitize_for_api(data)
        assert "id" not in out
        assert "user_id" not in out
        assert out["urn"] == "urn:ok"
        assert "id" not in out["nested"]
        assert out["nested"]["keep"] is True
