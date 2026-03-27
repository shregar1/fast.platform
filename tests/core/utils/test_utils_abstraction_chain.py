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
        from core.utils.abstraction import IUtility
        from core.utils.archive import IArchiveUtility
        from core.utils.clock import IClockUtility
        from core.utils.crowdfunding import ICrowdfundingUtility
        from core.utils.currency import ICurrencyUtility
        from core.utils.datatype import IDatatype
        from core.utils.decimal import IDecimalUtility
        from core.utils.digests import IDigestsUtility
        from core.utils.encryption.abstraction import IEncryptionUtility
        from core.utils.hashing import IHashingUtility
        from core.utils.html import IHtmlUtility
        from core.utils.idempotency import IIdempotencyUtility
        from core.utils.media.abstraction import IMedia
        from core.utils.metrics import IMetricsUtility
        from core.utils.nutrition import INutritionUtility
        from core.utils.optional_imports import IOptionalImportsUtility
        from core.utils.request_id_context import IRequestIdContextUtility
        from core.utils.retry import IAsyncRetryUtility
        from core.utils.sanitization import SanitizationJsonUtility
        from core.utils.sanitization.abstraction import ISanitization
        from core.utils.structured_log import IStructuredLogUtility
        from core.utils.time import ITimeUtility

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
        from core.utils.archive import ArchiveUtility, IArchiveUtility
        from core.utils.crowdfunding import CrowdfundingUtility, ICrowdfundingUtility
        from core.utils.decimal import DecimalUtility, IDecimalUtility
        from core.utils.digests import Digests, IDigestsUtility
        from core.utils.hashing import HashingUtility, IHashingUtility
        from core.utils.optional_imports import OptionalImports, IOptionalImportsUtility
        from core.utils.sanitization import SanitizationJsonUtility
        from core.utils.sanitization.abstraction import ISanitization

        assert issubclass(ArchiveUtility, IArchiveUtility)
        assert issubclass(CrowdfundingUtility, ICrowdfundingUtility)
        assert issubclass(DecimalUtility, IDecimalUtility)
        assert issubclass(Digests, IDigestsUtility)
        assert issubclass(HashingUtility, IHashingUtility)
        assert issubclass(OptionalImports, IOptionalImportsUtility)
        assert issubclass(SanitizationJsonUtility, ISanitization)
