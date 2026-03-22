"""Tests for analytics."""

from tests.integrations.analytics.abstraction import IAnalyticsTests


class TestInit(IAnalyticsTests):
    def test_imports(self) -> None:
        from analytics import (
            AnalyticsConfiguration,
            AnalyticsConfigurationDTO,
            AnalyticsSamplingMiddleware,
            BufferedAnalyticsBackend,
            EventSchemaRegistry,
            IAnalyticsBackend,
            RateLimitedAnalyticsBackend,
            ScrubbingAnalyticsBackend,
            ValidatingAnalyticsBackend,
            build_analytics_client,
            default_analytics_user_key,
            parse_versioned_event_name,
            scrub_pii_properties,
        )

        assert AnalyticsConfiguration is not None
        assert AnalyticsConfigurationDTO is not None
        assert IAnalyticsBackend is not None
        assert build_analytics_client is not None
        assert scrub_pii_properties is not None
        assert ScrubbingAnalyticsBackend is not None
        assert RateLimitedAnalyticsBackend is not None
        assert AnalyticsSamplingMiddleware is not None
        assert default_analytics_user_key is not None
        assert BufferedAnalyticsBackend is not None
        assert EventSchemaRegistry is not None
        assert ValidatingAnalyticsBackend is not None
        assert parse_versioned_event_name is not None
