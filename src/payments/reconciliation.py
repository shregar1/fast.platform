"""
Daily reconciliation: compare payment gateway totals vs internal ledger (DTO + CSV hook).
"""

from __future__ import annotations

import csv
import io
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from datetime import date


class ReconciliationMismatchKind(str, Enum):
    """Why a row appears in a reconciliation diff."""

    MISSING_IN_GATEWAY = "missing_in_gateway"
    MISSING_IN_LEDGER = "missing_in_ledger"
    AMOUNT_MISMATCH = "amount_mismatch"
    STATUS_MISMATCH = "status_mismatch"


class ReconciliationLineItem(BaseModel):
    """One row in a gateway-vs-ledger diff."""

    id: str
    currency: str
    amount_smallest_unit: int
    ledger_ref: Optional[str] = None
    gateway_ref: Optional[str] = None
    ledger_amount_smallest_unit: Optional[int] = None
    gateway_amount_smallest_unit: Optional[int] = None
    mismatch_kind: Optional[ReconciliationMismatchKind] = None
    notes: Optional[str] = None


class ReconciliationReport(BaseModel):
    """
    Aggregated daily (or windowed) reconciliation result.

    *amounts* are in the smallest currency unit (cents, paisa, …).
    """

    report_date: date
    currency: str
    gateway_label: str = "gateway"
    ledger_label: str = "ledger"
    matched_count: int = 0
    mismatch_count: int = 0
    gateway_total_smallest_unit: int = 0
    ledger_total_smallest_unit: int = 0
    items: list[ReconciliationLineItem] = Field(default_factory=list)


def reconciliation_report_to_csv(report: ReconciliationReport) -> str:
    """
    Serialize *report* to CSV for exports, BI tools, or email attachments.

    First block: summary columns; second block: one row per :class:`ReconciliationLineItem`.
    """
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "report_date",
            "currency",
            "gateway_label",
            "ledger_label",
            "matched_count",
            "mismatch_count",
            "gateway_total_smallest_unit",
            "ledger_total_smallest_unit",
        ]
    )
    w.writerow(
        [
            report.report_date.isoformat(),
            report.currency,
            report.gateway_label,
            report.ledger_label,
            report.matched_count,
            report.mismatch_count,
            report.gateway_total_smallest_unit,
            report.ledger_total_smallest_unit,
        ]
    )
    w.writerow([])
    w.writerow(
        [
            "id",
            "currency",
            "amount_smallest_unit",
            "ledger_ref",
            "gateway_ref",
            "ledger_amount_smallest_unit",
            "gateway_amount_smallest_unit",
            "mismatch_kind",
            "notes",
        ]
    )
    for it in report.items:
        w.writerow(
            [
                it.id,
                it.currency,
                it.amount_smallest_unit,
                it.ledger_ref or "",
                it.gateway_ref or "",
                (
                    it.ledger_amount_smallest_unit
                    if it.ledger_amount_smallest_unit is not None
                    else ""
                ),
                (
                    it.gateway_amount_smallest_unit
                    if it.gateway_amount_smallest_unit is not None
                    else ""
                ),
                it.mismatch_kind.value if it.mismatch_kind else "",
                it.notes or "",
            ]
        )
    return buf.getvalue()
