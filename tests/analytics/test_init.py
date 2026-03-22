"""Tests for analytics."""


def test_imports():
    from analytics import (
        BufferedAnalyticsBackend,
        EventSchemaRegistry,
        RateLimitedAnalyticsBackend,
        ScrubbingAnalyticsBackend,
        ValidatingAnalyticsBackend,
        AnalyticsSamplingMiddleware,
        IAnalyticsBackend,
        AnalyticsConfiguration,
        AnalyticsConfigurationDTO,
        build_analytics_client,
        default_analytics_user_key,
        parse_versioned_event_name,
        scrub_pii_properties,
    )

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
