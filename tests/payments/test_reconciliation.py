"""Tests for reconciliation DTOs and CSV export."""

from datetime import date

from fast_payments.reconciliation import (
    ReconciliationLineItem,
    ReconciliationMismatchKind,
    ReconciliationReport,
    reconciliation_report_to_csv,
)


def test_reconciliation_report_csv_roundtrip_shape():
    r = ReconciliationReport(
        report_date=date(2026, 3, 21),
        currency="usd",
        matched_count=10,
        mismatch_count=1,
        gateway_total_smallest_unit=5000,
        ledger_total_smallest_unit=4900,
        items=[
            ReconciliationLineItem(
                id="row-1",
                currency="usd",
                amount_smallest_unit=100,
                mismatch_kind=ReconciliationMismatchKind.AMOUNT_MISMATCH,
                ledger_amount_smallest_unit=100,
                gateway_amount_smallest_unit=50,
            )
        ],
    )
    csv_text = reconciliation_report_to_csv(r)
    assert "2026-03-21" in csv_text
    assert "5000" in csv_text
    assert "amount_mismatch" in csv_text
    assert "row-1" in csv_text
