"""Ensure ``core.utils`` concrete utilities inherit subfolder markers → :class:`IUtility`."""

from __future__ import annotations

from tests.core.utils.abstraction import IUtilsTests


class TestUtilsAbstractionChain(IUtilsTests):
    """Represents the TestUtilsAbstractionChain class."""

    def test_subfolder_markers_subclass_iutility(self) -> None:
        """Execute test_subfolder_markers_subclass_iutility operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.core.utils.abstraction import IUtility
        from fast_platform.core.utils.archive import IArchiveUtility
        from fast_platform.core.utils.clock import IClockUtility
        from fast_platform.core.utils.crowdfunding import ICrowdfundingUtility
        from fast_platform.core.utils.currency import ICurrencyUtility
        from fast_platform.core.utils.datatype import IDatatype
        from fast_platform.core.utils.decimal import IDecimalUtility
        from fast_platform.core.utils.digests import IDigestsUtility
        from fast_platform.core.utils.encryption.abstraction import IEncryptionUtility
        from fast_platform.core.utils.hashing import IHashingUtility
        from fast_platform.core.utils.html import IHtmlUtility
        from fast_platform.core.utils.idempotency import IIdempotencyUtility
        from fast_platform.core.utils.media.abstraction import IMedia
        from fast_platform.core.utils.metrics import IMetricsUtility
        from fast_platform.core.utils.nutrition import INutritionUtility
        from fast_platform.core.utils.optional_imports import IOptionalImportsUtility
        from fast_platform.core.utils.request_id_context import IRequestIdContextUtility
        from fast_platform.core.utils.retry import IAsyncRetryUtility
        from fast_platform.core.utils.sanitization import SanitizationJsonUtility
        from fast_platform.core.utils.sanitization.abstraction import ISanitization
        from fast_platform.core.utils.structured_log import IStructuredLogUtility
        from fast_platform.core.utils.time import ITimeUtility

        markers = (
            IArchiveUtility,
            IAsyncRetryUtility,
            IClockUtility,
            ICrowdfundingUtility,
            ICurrencyUtility,
            IDatatype,
            IDecimalUtility,
            IDigestsUtility,
            IEncryptionUtility,
            IHashingUtility,
            IHtmlUtility,
            IIdempotencyUtility,
            IMedia,
            IMetricsUtility,
            INutritionUtility,
            IOptionalImportsUtility,
            IRequestIdContextUtility,
            ISanitization,
            IStructuredLogUtility,
            SanitizationJsonUtility,
            ITimeUtility,
        )
        for m in markers:
            assert issubclass(m, IUtility), m

    def test_concrete_classes_use_subfolder_base(self) -> None:
        """Execute test_concrete_classes_use_subfolder_base operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.core.utils.archive import ArchiveUtility, IArchiveUtility
        from fast_platform.core.utils.crowdfunding import CrowdfundingUtility, ICrowdfundingUtility
        from fast_platform.core.utils.decimal import DecimalUtility, IDecimalUtility
        from fast_platform.core.utils.digests import Digests, IDigestsUtility
        from fast_platform.core.utils.hashing import HashingUtility, IHashingUtility
        from fast_platform.core.utils.optional_imports import OptionalImports, IOptionalImportsUtility
        from fast_platform.core.utils.sanitization import SanitizationJsonUtility
        from fast_platform.core.utils.sanitization.abstraction import ISanitization

        assert issubclass(ArchiveUtility, IArchiveUtility)
        assert issubclass(CrowdfundingUtility, ICrowdfundingUtility)
        assert issubclass(DecimalUtility, IDecimalUtility)
        assert issubclass(Digests, IDigestsUtility)
        assert issubclass(HashingUtility, IHashingUtility)
        assert issubclass(OptionalImports, IOptionalImportsUtility)
        assert issubclass(SanitizationJsonUtility, ISanitization)
