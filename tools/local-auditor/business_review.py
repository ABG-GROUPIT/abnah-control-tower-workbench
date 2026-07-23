#!/usr/bin/env python3
"""Run deterministic cross-report and business-semantic checks locally.

The full result and browser packet remain under LOCAL_EVIDENCE_DO_NOT_UPLOAD.
Only the aggregate public summary is suitable for the hosted workbench.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

from issue_taxonomy import SEVERITY_ORDER, highest_severity


ROOT = Path(__file__).resolve().parent
DEFAULT_RUN = ROOT / "output" / "real_dump_semantic_20260723"
BUSINESS_REVIEW_VERSION = "2.0.0"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def stable_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def decimal_value(value: Any) -> Decimal | None:
    if value in ("", None):
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None


def date_value(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            continue
    return None


def canonical_identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", (value or "").upper()).removeprefix("PO").removeprefix("SE")


def unit_basis(value: str) -> tuple[str, Decimal] | None:
    text = re.sub(r"\s+", " ", (value or "").strip().upper())
    if not text:
        return None
    aliases = {
        "GRAM": "GM",
        "GRAMS": "GM",
        "G": "GM",
        "KILOGRAM": "GM",
        "KG": "GM",
        "LITRE": "ML",
        "LITER": "ML",
        "LTR": "ML",
        "PIECE": "PIECE",
        "PIECES": "PIECE",
        "PCS": "PIECE",
        "NOS": "PIECE",
        "NO": "PIECE",
    }
    direct = aliases.get(text, text)
    if direct == "GM" and text in {"KG", "KILOGRAM"}:
        return "GM", Decimal("1000")
    if direct == "ML" and text in {"LITRE", "LITER", "LTR"}:
        return "ML", Decimal("1000")
    if direct in {"GM", "ML", "PIECE"}:
        return direct, Decimal("1")
    match = re.search(r"\(([\d,.]+)\s*([A-Z]+)", text)
    if not match:
        return None
    factor = decimal_value(match.group(1))
    base = aliases.get(match.group(2), match.group(2))
    if factor is None or base not in {"GM", "ML", "PIECE"}:
        return None
    return base, factor


def magnitude_severity(amount: Decimal | None, quantity: Decimal | None = None) -> str:
    amount_abs = abs(amount or Decimal("0"))
    quantity_abs = abs(quantity or Decimal("0"))
    if amount_abs >= Decimal("5000") or quantity_abs >= Decimal("100"):
        return "critical"
    if amount_abs >= Decimal("500") or quantity_abs >= Decimal("1"):
        return "major"
    return "minor"


@dataclass
class ExportData:
    profile: dict[str, Any]
    path: Path | None
    columns: list[str]
    rows: list[dict[str, str]]

    @property
    def report_id(self) -> str:
        return self.profile["report_id"]

    @property
    def label(self) -> str:
        return self.profile["file_name"]

    def source_row_number(self, index: int) -> int:
        return int(self.profile["schema"].get("header_row_number", 1)) + index + 1


class ReviewBuilder:
    def __init__(self, exports: list[ExportData], as_of: datetime) -> None:
        self.exports = exports
        self.as_of = as_of
        self.row_issues: list[dict[str, Any]] = []
        self.findings: list[dict[str, Any]] = []
        self.controls: list[dict[str, Any]] = []
        self.exports_by_report: dict[str, list[ExportData]] = defaultdict(list)
        for export in exports:
            self.exports_by_report[export.report_id].append(export)

    def issue(
        self,
        export: ExportData,
        row_index: int,
        finding_id: str,
        *,
        severity: str,
        issue_class: str,
        state: str,
        title: str,
        message: str,
        fields: list[str],
        expected: str = "",
        observed: str = "",
        confidence: str = "high",
        production_treatment: str = "",
        impact_abs: str = "",
        impact_pct: str = "",
    ) -> None:
        self.row_issues.append(
            {
                "id": f"row:{stable_id(f'{export.profile['file']}:{row_index}:{finding_id}')}",
                "finding_id": finding_id,
                "report_id": export.report_id,
                "file": export.profile["file"],
                "export_label": export.label,
                "row_number": export.source_row_number(row_index),
                "severity": severity,
                "issue_class": issue_class,
                "state": state,
                "confidence": confidence,
                "title": title,
                "message": message,
                "fields": fields,
                "expected": expected,
                "observed": observed,
                "impact_abs": impact_abs,
                "impact_pct": impact_pct,
                "production_treatment": production_treatment,
            }
        )

    def finding(
        self,
        report_id: str,
        finding_id: str,
        *,
        severity: str,
        issue_class: str,
        state: str,
        title: str,
        observation: str,
        fields: list[str],
        affected_rows: int,
        production_treatment: str,
        business_question: str,
        confidence: str = "high",
        metrics: dict[str, Any] | None = None,
    ) -> None:
        self.findings.append(
            {
                "id": finding_id,
                "report_id": report_id,
                "severity": severity,
                "issue_class": issue_class,
                "state": state,
                "confidence": confidence,
                "title": title,
                "observation": observation,
                "fields": fields,
                "affected_row_count": affected_rows,
                "production_treatment": production_treatment,
                "business_question": business_question,
                "metrics": metrics or {},
            }
        )

    def control(
        self,
        control_id: str,
        *,
        status: str,
        title: str,
        observation: str,
        reports: list[str],
        fields: list[str],
        severity: str = "info",
    ) -> None:
        self.controls.append(
            {
                "id": control_id,
                "status": status,
                "severity": severity,
                "title": title,
                "observation": observation,
                "reports": reports,
                "fields": fields,
            }
        )

    def rows(self, report_id: str) -> Iterable[tuple[ExportData, int, dict[str, str]]]:
        for export in self.exports_by_report.get(report_id, []):
            for index, row in enumerate(export.rows):
                yield export, index, row


def load_exports(audit_run: Path) -> tuple[Path, list[ExportData]]:
    local_dir = audit_run / "LOCAL_EVIDENCE_DO_NOT_UPLOAD"
    profiles = json.loads(
        (local_dir / "full_profiles_with_local_samples.json").read_text(encoding="utf-8")
    )
    normalized_dir = local_dir / "deterministic_audit" / "normalized"
    exports = []
    for profile in profiles:
        path = normalized_dir / f"{Path(profile['file']).stem}__normalized.csv"
        if path.exists():
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                columns = list(reader.fieldnames or [])
        else:
            path = None
            rows = []
            columns = [field["field"] for field in profile.get("fields") or []]
        exports.append(ExportData(profile, path, columns, rows))
    return local_dir, exports


def profile_controls(builder: ReviewBuilder) -> None:
    for report_id, exports in sorted(builder.exports_by_report.items()):
        display_name = exports[0].profile["display_name"]
        schema_ok = all(export.profile["schema"].get("matches_contract") for export in exports)
        malformed = sum(
            int(export.profile["rows"].get("malformed_width_count", 0)) for export in exports
        )
        parse_errors = sum(
            int(field.get("parse_error_count", 0))
            for export in exports
            for field in export.profile.get("fields") or []
        )
        row_count = sum(len(export.rows) for export in exports)
        if schema_ok and not malformed and not parse_errors:
            builder.control(
                f"{report_id}:schema_and_type_integrity",
                status="passed",
                title=f"{display_name} schema and declared types align",
                observation=(
                    f"{len(exports)} export(s), {row_count:,} rows: exact contract headers, "
                    "no malformed-width rows, and no declared-type parse failures."
                ),
                reports=[report_id],
                fields=[],
            )
        else:
            builder.finding(
                report_id,
                f"{report_id}:structural_integrity",
                severity="critical",
                issue_class="structure",
                state="confirmed_issue",
                title="Structural or declared-type integrity failed",
                observation=(
                    f"Contract match={schema_ok}; malformed rows={malformed}; "
                    f"declared-type parse errors={parse_errors}."
                ),
                fields=[],
                affected_rows=malformed + parse_errors,
                production_treatment="Block ingestion until the export contract and malformed rows are corrected.",
                business_question="Did the source export layout or field type change?",
            )
        if row_count == 0:
            builder.finding(
                report_id,
                f"{report_id}:header_only",
                severity="critical",
                issue_class="coverage",
                state="confirmed_issue",
                title="Captured report is header-only",
                observation="The captured export contains a valid schema but no data rows.",
                fields=[],
                affected_rows=0,
                production_treatment="Exclude this report from active KPI dependencies until a populated export exists.",
                business_question="Is this report unused, filtered incorrectly, permission-restricted, or stored in another module?",
            )


def closing_stock_checks(builder: ReviewBuilder) -> None:
    report_id = "p4.closing_stock.item"
    negatives = []
    stale_rows = []
    for export, index, row in builder.rows(report_id):
        quantity = decimal_value(row.get("total_qty"))
        amount = decimal_value(row.get("total_amt"))
        fields = [
            field
            for field, value in (("total_qty", quantity), ("total_amt", amount))
            if value is not None and value < 0
        ]
        if fields:
            severity = magnitude_severity(amount, quantity)
            negatives.append(severity)
            builder.issue(
                export,
                index,
                f"{report_id}:negative_closing_stock",
                severity=severity,
                issue_class="operational_exception",
                state="operational_exception",
                title="Negative closing stock",
                message="Closing quantity or valuation is below zero. This is operationally important but is not a parser/type error.",
                fields=fields,
                expected="Non-negative stock after approved adjustments",
                observed=f"qty={quantity}; amount={amount}",
                production_treatment="Retain the source row, raise a stock exception, and investigate transactions/UOM before correction.",
                impact_abs=f"{abs(amount or Decimal('0')):f}",
            )
        stock_date = date_value(row.get("stock_date", ""))
        generation_date = date_value(row.get("generation_date", ""))
        if stock_date and generation_date and (generation_date.date() - stock_date.date()).days > 1:
            stale_rows.append((export, index, (generation_date.date() - stock_date.date()).days))
    if negatives:
        builder.finding(
            report_id,
            f"{report_id}:negative_closing_stock",
            severity=highest_severity(negatives),
            issue_class="operational_exception",
            state="operational_exception",
            title="Negative closing stock requires action",
            observation=f"{len(negatives):,} rows contain a negative closing quantity or value.",
            fields=["total_qty", "total_amt"],
            affected_rows=len(negatives),
            production_treatment="Expose as a stock-integrity exception; do not silently clamp to zero.",
            business_question="Which backdated movement, UOM conversion, or count adjustment caused each negative balance?",
        )
    if stale_rows:
        max_days = max(days for _, _, days in stale_rows)
        for export, index, days in stale_rows:
            builder.issue(
                export,
                index,
                f"{report_id}:stale_snapshot",
                severity="critical",
                issue_class="freshness",
                state="confirmed_issue",
                title="Closing-stock snapshot is stale",
                message=f"The stock date is {days} days behind the report generation date.",
                fields=["stock_date", "generation_date"],
                expected="Current approved stock snapshot",
                observed=f"{days} day lag",
                production_treatment="Do not use this extract as current stock until a fresh snapshot is exported.",
            )
        builder.finding(
            report_id,
            f"{report_id}:stale_snapshot",
            severity="critical",
            issue_class="freshness",
            state="confirmed_issue",
            title="Closing-stock extract is not current",
            observation=(
                f"All {len(stale_rows):,} rows carry a stock snapshot up to {max_days} days "
                "behind the generation date."
            ),
            fields=["stock_date", "generation_date"],
            affected_rows=len(stale_rows),
            production_treatment="Refresh the Closing Stock export before stockout, cover, or working-capital publication.",
            business_question="Was the older stock date intentionally selected, or did the export ignore the requested snapshot?",
        )


def variance_checks(builder: ReviewBuilder) -> None:
    report_fields = {
        "p4.enterprise_variance.normal": [
            "closing_qty",
            "closing_amt",
            "actual_consumption_qty",
            "actual_consumption_amt",
            "ideal_closing_qty",
            "ideal_closing_amt",
        ],
        "p4.enterprise_variance.master": [
            "closing_qty",
            "closing_amt",
            "actual_consumption_qty",
            "actual_consumption_amt",
        ],
    }
    for report_id, fields in report_fields.items():
        severities = []
        affected = 0
        field_counts: Counter[str] = Counter()
        for export, index, row in builder.rows(report_id):
            negative_fields = [field for field in fields if (decimal_value(row.get(field)) or 0) < 0]
            if not negative_fields:
                continue
            affected += 1
            field_counts.update(negative_fields)
            amount = max(
                (
                    abs(decimal_value(row.get(field)) or Decimal("0"))
                    for field in negative_fields
                    if field.endswith("_amt")
                ),
                default=Decimal("0"),
            )
            quantity = max(
                (
                    abs(decimal_value(row.get(field)) or Decimal("0"))
                    for field in negative_fields
                    if field.endswith("_qty")
                ),
                default=Decimal("0"),
            )
            severity = magnitude_severity(amount, quantity)
            severities.append(severity)
            builder.issue(
                export,
                index,
                f"{report_id}:negative_inventory_or_consumption",
                severity=severity,
                issue_class="operational_exception",
                state="needs_business_definition",
                title="Negative inventory or consumption state",
                message="One or more inventory/consumption measures are negative; valid reversals must be separated from unexplained balances.",
                fields=negative_fields,
                expected="Approved sign convention by movement type",
                observed=", ".join(f"{field}={row.get(field)}" for field in negative_fields),
                production_treatment="Preserve signs in raw, classify transaction meaning, and publish separate exception flags.",
                impact_abs=f"{amount:f}",
                confidence="medium",
            )
        if affected:
            builder.finding(
                report_id,
                f"{report_id}:negative_inventory_or_consumption",
                severity=highest_severity(severities),
                issue_class="operational_exception",
                state="needs_business_definition",
                title="Negative inventory and consumption states need sign rules",
                observation=(
                    f"{affected:,} rows contain at least one negative monitored field. "
                    + "; ".join(f"{field}={count:,}" for field, count in field_counts.most_common())
                    + "."
                ),
                fields=fields,
                affected_rows=affected,
                production_treatment="Separate valid returns/reversals from stock and consumption exceptions before KPI aggregation.",
                business_question="Which transaction types authorize each negative sign, and which should trigger an operational alert?",
                confidence="medium",
            )


def gross_margin_checks(builder: ReviewBuilder) -> None:
    report_id = "p2.gross_net_margin.item"
    period_stats: dict[str, Counter[str]] = defaultdict(Counter)
    zero_cost_rows = 0
    negative_margin_rows = 0
    negative_severities = []
    for export, index, row in builder.rows(report_id):
        net_sales = decimal_value(row.get("net_sale_value")) or Decimal("0")
        cost = decimal_value(row.get("purchase_value")) or Decimal("0")
        net_margin = decimal_value(row.get("net_margin_percent"))
        period_stats[export.label]["eligible"] += int(net_sales != 0)
        if net_sales != 0 and cost == 0:
            period_stats[export.label]["zero_cost"] += 1
            zero_cost_rows += 1
            builder.issue(
                export,
                index,
                f"{report_id}:zero_cost_coverage",
                severity="major",
                issue_class="coverage",
                state="confirmed_issue",
                title="Sale has no exported purchase cost",
                message="The row has non-zero sales but zero purchase value, so source-reported margin is incomplete.",
                fields=["net_sale_value", "purchase_value", "net_margin_percent", "gross_margin_percent"],
                expected="Approved non-zero cost or an explicit no-cost classification",
                observed=f"net sales={net_sales}; purchase value={cost}",
                production_treatment="Do not treat zero as free cost; use approved recipe valuation only after effective-date and UOM controls pass.",
                impact_abs=f"{net_sales:f}",
            )
        if net_margin is not None and net_margin < 0 and net_sales > 0:
            loss = max(Decimal("0"), cost - net_sales)
            severity = (
                "critical"
                if net_margin <= -500 or loss >= Decimal("1000")
                else "major"
                if net_margin <= -100 or loss >= Decimal("100")
                else "minor"
            )
            negative_severities.append(severity)
            negative_margin_rows += 1
            builder.issue(
                export,
                index,
                f"{report_id}:negative_margin",
                severity=severity,
                issue_class="operational_exception",
                state="operational_exception",
                title="Loss-making sale",
                message="Purchase value exceeds net sales for this line. The arithmetic is valid; the commercial outcome needs review.",
                fields=["net_sale_value", "purchase_value", "net_margin_percent"],
                expected="Non-negative contribution unless an approved promotion/exception applies",
                observed=f"net sales={net_sales}; cost={cost}; margin={net_margin}%",
                production_treatment="Retain the row and classify promotions, recipe cost, and pricing exceptions before escalation.",
                impact_abs=f"{loss:f}",
            )
    if zero_cost_rows:
        period_text = []
        max_gap = Decimal("0")
        for label, stats in period_stats.items():
            gap = (
                Decimal(stats["zero_cost"]) / Decimal(stats["eligible"]) * Decimal("100")
                if stats["eligible"]
                else Decimal("0")
            )
            max_gap = max(max_gap, gap)
            period_text.append(f"{stats['zero_cost']:,}/{stats['eligible']:,} ({gap:.1f}%)")
        builder.finding(
            report_id,
            f"{report_id}:zero_cost_coverage",
            severity="critical" if max_gap >= 25 else "major",
            issue_class="coverage",
            state="confirmed_issue",
            title="Source margin is blocked by period-specific cost gaps",
            observation=(
                f"{zero_cost_rows:,} non-zero-sales rows have zero exported purchase value. "
                f"Export-period gaps: {'; '.join(period_text)}."
            ),
            fields=["net_sale_value", "purchase_value", "net_margin_percent", "gross_margin_percent"],
            affected_rows=zero_cost_rows,
            production_treatment="Block source-margin publication for affected periods; do not impute zero cost as free inventory.",
            business_question="Why is purchase-cost coverage concentrated in one period, and which approved cost source should fill the gap?",
            metrics={"maximum_period_gap_percent": float(max_gap)},
        )
    if negative_margin_rows:
        builder.finding(
            report_id,
            f"{report_id}:negative_margin",
            severity=highest_severity(negative_severities),
            issue_class="operational_exception",
            state="operational_exception",
            title="Loss-making sales are arithmetically valid but commercially material",
            observation=f"{negative_margin_rows:,} rows have a negative net and gross margin with positive sales.",
            fields=["net_sale_value", "purchase_value", "net_margin_percent", "gross_margin_percent"],
            affected_rows=negative_margin_rows,
            production_treatment="Show as a margin exception; distinguish promotions and approved loss leaders from recipe/cost defects.",
            business_question="Which negative-margin items are approved promotions versus pricing or recipe-cost issues?",
        )


def opening_and_entry_checks(builder: ReviewBuilder) -> None:
    opening_id = "p4.enterprise_opening.item"
    zero_rows = 0
    for export, index, row in builder.rows(opening_id):
        if (
            decimal_value(row.get("unit_price")) == 0
            and decimal_value(row.get("opening_subtotal")) == 0
        ):
            zero_rows += 1
            builder.issue(
                export,
                index,
                f"{opening_id}:zero_valuation",
                severity="major",
                issue_class="coverage",
                state="confirmed_issue",
                title="Opening stock has quantity but no valuation",
                message="The captured opening row carries zero unit price and zero subtotal.",
                fields=["opening_qty", "unit_price", "opening_subtotal"],
                expected="Approved opening valuation",
                observed="unit price=0; subtotal=0",
                production_treatment="Use for quantity reconciliation only; exclude from value and working-capital metrics.",
            )
    if zero_rows:
        builder.finding(
            opening_id,
            f"{opening_id}:zero_valuation",
            severity="major",
            issue_class="coverage",
            state="confirmed_issue",
            title="Opening-stock valuation is unavailable",
            observation=f"All {zero_rows:,} captured opening rows have zero unit price and subtotal.",
            fields=["opening_qty", "unit_price", "opening_subtotal"],
            affected_rows=zero_rows,
            production_treatment="Retain quantities, but source value from an approved valuation method before monetary KPIs.",
            business_question="Which opening valuation basis should be used for these items?",
        )

    entry_id = "p4.enterprise_entry.item"
    entry_rows = list(builder.rows(entry_id))
    for field, title, treatment, severity in (
        (
            "batch_number",
            "Batch traceability is absent",
            "Keep expiry and batch-level traceability unavailable until batch capture is enabled.",
            "major",
        ),
        (
            "pr_number",
            "Purchase-request lineage is absent",
            "Do not publish PR-to-PO cycle-time or approval metrics from this extract.",
            "major",
        ),
    ):
        if entry_rows and not any((row.get(field) or "").strip() for _, _, row in entry_rows):
            builder.finding(
                entry_id,
                f"{entry_id}:missing_{field}",
                severity=severity,
                issue_class="coverage",
                state="confirmed_issue",
                title=title,
                observation=f"{field.replace('_', ' ').title()} is blank across all {len(entry_rows):,} captured entry rows.",
                fields=[field],
                affected_rows=len(entry_rows),
                production_treatment=treatment,
                business_question=f"Is {field.replace('_', ' ')} disabled, stored elsewhere, or unavailable for this outlet?",
            )


def po_checks(builder: ReviewBuilder) -> None:
    report_id = "p4.enterprise_purchase_order.item"
    overdue_rows = []
    delayed_closed_rows = []
    for export, index, row in builder.rows(report_id):
        expected = date_value(row.get("expected_delivery_date", ""))
        closed = date_value(row.get("po_close_or_partial_receive_date", ""))
        status = (row.get("po_status") or "").strip().casefold()
        if expected and status != "closed" and expected.date() < builder.as_of.date():
            days = (builder.as_of.date() - expected.date()).days
            severity = "critical" if days >= 15 else "major" if days >= 4 else "minor"
            overdue_rows.append((severity, days, decimal_value(row.get("total_item_cost")) or Decimal("0")))
            builder.issue(
                export,
                index,
                f"{report_id}:overdue_open_po",
                severity=severity,
                issue_class="business_logic",
                state="operational_exception",
                title="Open PO is overdue",
                message=f"The expected delivery date has passed by {days} day(s) while the PO remains requested.",
                fields=["po_number", "expected_delivery_date", "po_status", "remaining_balance_qty", "total_item_cost"],
                expected="Closed/received by expected delivery date or approved revised date",
                observed=f"{days} days overdue",
                production_treatment="Surface in procurement action queue and calculate exposure from remaining quantity/value.",
                impact_abs=str(row.get("total_item_cost") or ""),
            )
        if expected and closed and closed.date() > expected.date():
            days = (closed.date() - expected.date()).days
            severity = "major" if days >= 4 else "minor"
            delayed_closed_rows.append((severity, days))
            builder.issue(
                export,
                index,
                f"{report_id}:closed_po_delay",
                severity=severity,
                issue_class="business_logic",
                state="operational_exception",
                title="Closed PO was received after expected date",
                message=f"The close/partial-receive date is {days} day(s) after expected delivery.",
                fields=["po_number", "expected_delivery_date", "po_close_or_partial_receive_date", "po_status"],
                expected="Receipt on or before expected delivery date",
                observed=f"{days} day delay",
                production_treatment="Include in vendor delivery reliability after receipt identity is reconciled.",
            )
    if overdue_rows:
        po_rows = list(builder.rows(report_id))
        overdue_numbers = {
            row["po_number"]
            for export, index, row in po_rows
            if any(
                issue["file"] == export.profile["file"]
                and issue["row_number"] == export.source_row_number(index)
                and issue["finding_id"] == f"{report_id}:overdue_open_po"
                for issue in builder.row_issues
            )
        }
        exposure = sum(item[2] for item in overdue_rows)
        builder.finding(
            report_id,
            f"{report_id}:overdue_open_po",
            severity=highest_severity([item[0] for item in overdue_rows]),
            issue_class="business_logic",
            state="operational_exception",
            title="Overdue open purchase orders require procurement action",
            observation=(
                f"{len(overdue_numbers):,} PO documents ({len(overdue_rows):,} lines) were overdue "
                f"as of {builder.as_of.date().isoformat()}, with line-value exposure of {exposure:.2f}."
            ),
            fields=["po_number", "expected_delivery_date", "po_status", "remaining_balance_qty", "total_item_cost"],
            affected_rows=len(overdue_rows),
            production_treatment="Publish as an action queue only after owner and revised-date semantics are approved.",
            business_question="Which overdue POs have an approved revised date or cancellation not represented in the report?",
        )
    if delayed_closed_rows:
        builder.finding(
            report_id,
            f"{report_id}:closed_po_delay",
            severity=highest_severity([item[0] for item in delayed_closed_rows]),
            issue_class="business_logic",
            state="operational_exception",
            title="A closed PO missed its expected date",
            observation=f"{len(delayed_closed_rows):,} closed PO lines were received after expected delivery.",
            fields=["po_number", "expected_delivery_date", "po_close_or_partial_receive_date"],
            affected_rows=len(delayed_closed_rows),
            production_treatment="Use only after PO/receipt identity and partial-receipt definitions are approved.",
            business_question="Does close date represent full receipt, first partial receipt, or administrative closure?",
        )


def po_entry_lineage(builder: ReviewBuilder) -> None:
    po_id = "p4.enterprise_purchase_order.item"
    entry_id = "p4.enterprise_entry.item"
    po_values = {
        (row.get("po_number") or "").strip()
        for _, _, row in builder.rows(po_id)
        if (row.get("po_number") or "").strip()
    }
    po_canonical = {canonical_identifier(value): value for value in po_values}
    entry_links = []
    exact = 0
    canonical = 0
    for export, index, row in builder.rows(entry_id):
        value = (row.get("po_number") or "").strip()
        if not value:
            continue
        if value in po_values:
            exact += 1
        elif canonical_identifier(value) in po_canonical:
            canonical += 1
            entry_links.append((export, index, row, po_canonical[canonical_identifier(value)]))
    if canonical and not exact:
        for export, index, row, expected_po in entry_links:
            builder.issue(
                export,
                index,
                f"{entry_id}:po_identifier_normalization",
                severity="major",
                issue_class="identifier_standardization",
                state="confirmed_issue",
                title="PO identifier requires canonicalization",
                message="The entry PO matches the purchase-order report only after removing source prefixes.",
                fields=["po_number", "transaction_number", "item_code"],
                expected=f"Canonical PO {expected_po}",
                observed=row.get("po_number", ""),
                production_treatment="Create canonical PO and receipt identifiers in standardization; preserve raw identifiers for audit.",
            )
        builder.finding(
            entry_id,
            f"{entry_id}:po_identifier_normalization",
            severity="critical",
            issue_class="identifier_standardization",
            state="confirmed_issue",
            title="Exact PO-to-receipt joins fail without identifier standardization",
            observation=(
                f"Exact PO identifier intersection is zero; {canonical:,} entry rows link after "
                "canonical prefix normalization."
            ),
            fields=["po_number", "transaction_number", "item_code"],
            affected_rows=canonical,
            production_treatment="Normalize PO and stock-entry identifiers before any PO status, delay, or receipt KPI join.",
            business_question="Is prefix removal the approved enterprise identifier rule for every outlet and deployment?",
        )
    builder.control(
        "po_entry_identifier_check",
        status="definition_gate" if canonical and not exact else "passed",
        severity="critical" if canonical and not exact else "info",
        title="PO-to-entry identifier compatibility",
        observation=(
            f"Exact linked entry rows={exact:,}; canonical-prefix linked rows={canonical:,}. "
            "Only one closed PO is currently evidenced in the Entry export."
        ),
        reports=[po_id, entry_id, "p4.purchase_detail.po_enabled"],
        fields=["po_number", "transaction_number", "item_code"],
    )


def recipe_and_sales_checks(builder: ReviewBuilder) -> None:
    recipe_id = "p1.item_recipe.detail"
    closing_id = "p4.closing_stock.item"
    sales_id = "p2.gross_net_margin.item"
    stock_units: dict[str, str] = {}
    for _, _, row in builder.rows(closing_id):
        code = (row.get("item_code") or "").strip()
        if code:
            stock_units[code] = row.get("unit_name", "")
    conversions = 0
    missing = 0
    conversion_severities = []
    seen_recipe_rows: dict[tuple[str, ...], tuple[ExportData, int]] = {}
    duplicate_rows = 0
    menu_codes: set[str] = set()
    for export, index, row in builder.rows(recipe_id):
        menu_code = (row.get("menu_item_number") or "").strip()
        ingredient_code = (row.get("ingredient_code") or "").strip()
        if menu_code:
            menu_codes.add(menu_code)
        signature = tuple(row.get(column, "") for column in export.columns)
        if signature in seen_recipe_rows:
            duplicate_rows += 1
            builder.issue(
                export,
                index,
                f"{recipe_id}:exact_duplicate",
                severity="minor",
                issue_class="grain",
                state="needs_business_definition",
                title="Exact recipe row repeats",
                message="An identical menu-item/ingredient recipe row is present more than once.",
                fields=["menu_item_number", "ingredient_code", "recipe_qty_per_menu_unit", "recipe_unit"],
                expected="One effective recipe line per approved recipe grain",
                observed="Exact repeated row",
                production_treatment="Do not delete automatically; confirm effective-date and recipe-line grain.",
                confidence="medium",
            )
        else:
            seen_recipe_rows[signature] = (export, index)
        if not ingredient_code:
            continue
        stock_unit = stock_units.get(ingredient_code)
        if stock_unit is None:
            missing += 1
            builder.issue(
                export,
                index,
                f"{recipe_id}:ingredient_not_in_stock_snapshot",
                severity="major",
                issue_class="coverage",
                state="confirmed_issue",
                title="Recipe ingredient is absent from the stock snapshot",
                message="The ingredient code cannot be found in the captured Closing Stock item set.",
                fields=["ingredient_code", "ingredient_name", "recipe_unit"],
                expected="Ingredient code represented in an approved inventory master/snapshot",
                observed="No matching closing-stock item code",
                production_treatment="Resolve item master coverage before theoretical consumption is published.",
            )
            continue
        recipe_unit = row.get("recipe_unit", "")
        if recipe_unit.strip().casefold() == stock_unit.strip().casefold():
            continue
        recipe_basis = unit_basis(recipe_unit)
        stock_basis = unit_basis(stock_unit)
        if recipe_basis and stock_basis and recipe_basis[0] == stock_basis[0]:
            conversions += 1
            severity = "major"
            conversion_severities.append(severity)
            builder.issue(
                export,
                index,
                f"{recipe_id}:uom_conversion_required",
                severity=severity,
                issue_class="identifier_standardization",
                state="confirmed_issue",
                title="Recipe-to-stock UOM conversion is required",
                message=(
                    f"Recipe unit {recipe_unit} and inventory unit {stock_unit} share base "
                    f"{recipe_basis[0]} but use different factors."
                ),
                fields=["ingredient_code", "recipe_qty_per_menu_unit", "recipe_unit"],
                expected=f"{stock_basis[0]} factor {stock_basis[1]}",
                observed=f"{recipe_basis[0]} factor {recipe_basis[1]}",
                production_treatment="Apply a governed conversion factor; an exact UOM text join is invalid.",
            )
        else:
            conversions += 1
            conversion_severities.append("critical")
            builder.issue(
                export,
                index,
                f"{recipe_id}:uom_conversion_required",
                severity="critical",
                issue_class="identifier_standardization",
                state="needs_business_definition",
                title="Recipe and inventory UOMs are not directly compatible",
                message=f"Recipe unit {recipe_unit} does not map safely to inventory unit {stock_unit}.",
                fields=["ingredient_code", "recipe_qty_per_menu_unit", "recipe_unit"],
                expected=stock_unit,
                observed=recipe_unit,
                production_treatment="Obtain an approved UOM conversion mapping before recipe costing.",
                confidence="medium",
            )
    matched = max(0, len(list(builder.rows(recipe_id))) - missing)
    if conversions:
        builder.finding(
            recipe_id,
            f"{recipe_id}:uom_conversion_required",
            severity="critical",
            issue_class="identifier_standardization",
            state="confirmed_issue",
            title="Exact UOM joins would break most recipe lineage",
            observation=(
                f"{conversions:,} recipe rows require UOM conversion among {matched:,} rows "
                "whose ingredient code exists in Closing Stock."
            ),
            fields=["ingredient_code", "recipe_qty_per_menu_unit", "recipe_unit"],
            affected_rows=conversions,
            production_treatment="Replace exact unit equality with a governed base-unit and conversion-factor dimension.",
            business_question="Which POSIST master or approved mapping owns pack, case, piece, gram, and millilitre conversion factors?",
        )
    if missing:
        builder.finding(
            recipe_id,
            f"{recipe_id}:ingredient_not_in_stock_snapshot",
            severity="major",
            issue_class="coverage",
            state="confirmed_issue",
            title="Some recipe ingredients are absent from the stock snapshot",
            observation=f"{missing:,} recipe rows reference ingredient codes not present in the captured Closing Stock report.",
            fields=["ingredient_code", "ingredient_name"],
            affected_rows=missing,
            production_treatment="Resolve the item-master/snapshot scope before theoretical consumption publication.",
            business_question="Are these ingredients inactive, outlet-excluded, or stored outside the selected stock location?",
        )
    if duplicate_rows:
        builder.finding(
            recipe_id,
            f"{recipe_id}:exact_duplicate",
            severity="minor",
            issue_class="grain",
            state="needs_business_definition",
            title="One exact recipe line repeats",
            observation=f"{duplicate_rows:,} additional exact recipe row is present.",
            fields=["menu_item_number", "ingredient_code", "recipe_qty_per_menu_unit", "recipe_unit"],
            affected_rows=duplicate_rows,
            production_treatment="Confirm effective recipe grain before deduplication.",
            business_question="Does the report omit an effective date or recipe-line identifier that distinguishes the rows?",
            confidence="medium",
        )

    missing_sales_rows = 0
    missing_sales_value = Decimal("0")
    eligible_sales_rows = 0
    eligible_sales_value = Decimal("0")
    missing_items: set[str] = set()
    for export, index, row in builder.rows(sales_id):
        net_sales = decimal_value(row.get("net_sale_value")) or Decimal("0")
        code = (row.get("item_code") or "").strip()
        if net_sales <= 0 or not code:
            continue
        eligible_sales_rows += 1
        eligible_sales_value += net_sales
        if code in menu_codes:
            continue
        missing_sales_rows += 1
        missing_sales_value += net_sales
        missing_items.add(code)
        builder.issue(
            export,
            index,
            f"{sales_id}:missing_recipe",
            severity="major",
            issue_class="coverage",
            state="confirmed_issue",
            title="Sold menu item has no captured recipe",
            message="The sold item code is absent from the Item Recipe report.",
            fields=["item_code", "item_name", "net_sale_value", "purchase_value"],
            expected="Captured effective recipe or approved direct-cost classification",
            observed="No recipe match",
            production_treatment="Exclude from theoretical consumption or classify as approved direct-cost item.",
            impact_abs=f"{net_sales:f}",
        )
    if missing_sales_rows:
        sales_gap = (
            missing_sales_value / eligible_sales_value * Decimal("100")
            if eligible_sales_value
            else Decimal("0")
        )
        builder.finding(
            sales_id,
            f"{sales_id}:missing_recipe",
            severity="major",
            issue_class="coverage",
            state="confirmed_issue",
            title="A small sold-item set lacks recipe coverage",
            observation=(
                f"{len(missing_items):,} sold item codes across {missing_sales_rows:,} rows lack a "
                f"captured recipe, representing {sales_gap:.2f}% of eligible net sales."
            ),
            fields=["item_code", "net_sale_value"],
            affected_rows=missing_sales_rows,
            production_treatment="Keep these rows out of theoretical-consumption variance until recipes or direct-cost rules are approved.",
            business_question="Are the missing items packaged/direct-cost products or genuinely missing recipes?",
            metrics={"net_sales_gap_percent": float(sales_gap)},
        )


def recipe_consumption_duplicates(builder: ReviewBuilder) -> None:
    report_id = "p4.recipe_consumption.item"
    prior: dict[tuple[str, ...], tuple[ExportData, int]] = {}
    duplicates = 0
    involved: set[tuple[str, int]] = set()
    exports = builder.exports_by_report.get(report_id, [])
    for export in exports:
        for index, row in enumerate(export.rows):
            signature = tuple(row.get(column, "") for column in export.columns)
            if signature in prior:
                duplicates += 1
                involved.add((export.profile["file"], index))
                builder.issue(
                    export,
                    index,
                    f"{report_id}:cross_export_duplicate",
                    severity="major",
                    issue_class="grain",
                    state="needs_business_definition",
                    title="Exact row repeats across aggregate-period exports",
                    message="The report has no transaction/date key, so this repeated aggregate row may be overlap or a legitimate equal total.",
                    fields=[
                        "item_type",
                        "item_code",
                        "parent_item_qty",
                        "consumed_qty",
                        "consumed_unit",
                        "consumed_subtotal",
                    ],
                    expected="Non-overlapping period grain or a transaction/date key",
                    observed="Exact row already present in another export",
                    production_treatment="Do not append aggregate windows blindly; use non-overlapping periods or approved replacement logic.",
                    confidence="medium",
                )
            else:
                prior[signature] = (export, index)
    if duplicates:
        builder.finding(
            report_id,
            f"{report_id}:cross_export_duplicate",
            severity="major",
            issue_class="grain",
            state="needs_business_definition",
            title="Aggregate recipe-consumption exports cannot be safely appended",
            observation=(
                f"{duplicates:,} additional exact rows repeat across populated exports. "
                "Because the report omits event date/transaction keys, equality is not proof of duplicate events."
            ),
            fields=["item_code", "parent_item_qty", "consumed_qty", "consumed_unit", "consumed_subtotal"],
            affected_rows=len(involved),
            production_treatment="Use non-overlapping exports or snapshot-replacement logic; never deduplicate solely by value equality.",
            business_question="Does each export represent a period aggregate, and are date endpoints inclusive?",
            confidence="medium",
        )


def transfer_control(builder: ReviewBuilder) -> None:
    from_id = "p4.enterprise_transfer.from_item"
    to_id = "p4.enterprise_transfer.to_item"
    from_rows = {
        (row.get("transaction_number"), row.get("item_code"), row.get("transfer_date")): row
        for _, _, row in builder.rows(from_id)
    }
    to_rows = {
        (row.get("transaction_number"), row.get("item_code"), row.get("transfer_date")): row
        for _, _, row in builder.rows(to_id)
    }
    common = set(from_rows) & set(to_rows)
    quantity_mismatch = sum(
        1
        for key in common
        if decimal_value(from_rows[key].get("transfer_qty"))
        != decimal_value(to_rows[key].get("transfer_qty"))
    )
    amount_mismatch = sum(
        1
        for key in common
        if decimal_value(from_rows[key].get("transfer_amt"))
        != decimal_value(to_rows[key].get("transfer_amt"))
    )
    passed = (
        len(from_rows) == len(to_rows) == len(common)
        and quantity_mismatch == 0
        and amount_mismatch == 0
    )
    builder.control(
        "transfer_pair_reconciliation",
        status="passed" if passed else "failed",
        severity="info" if passed else "critical",
        title="Transfer From and Transfer To pair reconciliation",
        observation=(
            f"From rows={len(from_rows):,}; To rows={len(to_rows):,}; paired={len(common):,}; "
            f"quantity mismatches={quantity_mismatch:,}; amount mismatches={amount_mismatch:,}."
        ),
        reports=[from_id, to_id],
        fields=["transaction_number", "item_code", "transfer_date", "transfer_qty", "transfer_amt"],
    )


def consumption_variance_control(builder: ReviewBuilder) -> None:
    consumption_id = "p4.enterprise_consumption.detail"
    variance_id = "p4.enterprise_variance.normal"
    consumption = {
        (row.get("deployment_name"), row.get("store_kitchen_name"), row.get("item_code")): row
        for _, _, row in builder.rows(consumption_id)
    }
    variance = {
        (row.get("deployment_name"), row.get("store_kitchen_name"), row.get("item_code")): row
        for _, _, row in builder.rows(variance_id)
    }
    common = set(consumption) & set(variance)
    fields = [
        "opening_qty",
        "purchase_qty",
        "stock_in_qty",
        "consumption_qty",
        "stock_out_qty",
        "wastage_qty",
        "return_qty",
        "closing_qty",
        "ideal_closing_qty",
    ]
    mismatches = 0
    for key in common:
        if any(
            decimal_value(consumption[key].get(field)) != decimal_value(variance[key].get(field))
            for field in fields
        ):
            mismatches += 1
    passed = len(consumption) == len(variance) == len(common) and mismatches == 0
    builder.control(
        "consumption_variance_reconciliation",
        status="passed" if passed else "failed",
        severity="info" if passed else "critical",
        title="Consumption and Normal Variance cross-report reconciliation",
        observation=(
            f"Consumption rows={len(consumption):,}; variance rows={len(variance):,}; "
            f"paired={len(common):,}; movement-field mismatches={mismatches:,}."
        ),
        reports=[consumption_id, variance_id],
        fields=fields,
    )


def bill_margin_control(builder: ReviewBuilder) -> None:
    bill_id = "p2.bill_item_detail.item"
    margin_id = "p2.gross_net_margin.item"

    def period_key(export: ExportData) -> str:
        dates = export.profile.get("filename_dates") or []
        if dates:
            return dates[0][:7]
        match = re.search(r"(20\d{2})[.-](\d{2})[.-]\d{2}", export.label)
        return f"{match.group(1)}-{match.group(2)}" if match else export.label

    bill_periods: dict[str, list[dict[str, str]]] = defaultdict(list)
    margin_periods: dict[str, list[dict[str, str]]] = defaultdict(list)
    for export in builder.exports_by_report.get(bill_id, []):
        bill_periods[period_key(export)].extend(export.rows)
    for export in builder.exports_by_report.get(margin_id, []):
        margin_periods[period_key(export)].extend(export.rows)
    observations = []
    passed = True
    for period in sorted(set(bill_periods) & set(margin_periods)):
        bill_rows = bill_periods[period]
        margin_rows = margin_periods[period]
        bill_gross = sum(decimal_value(row.get("net_amt")) or 0 for row in bill_rows)
        margin_gross = sum(decimal_value(row.get("gross_sale_value")) or 0 for row in margin_rows)
        difference = abs(bill_gross - margin_gross)
        tolerance = max(Decimal("1"), abs(margin_gross) * Decimal("0.00001"))
        if difference > tolerance or len(bill_rows) != len(margin_rows):
            passed = False
        observations.append(
            f"{period}: rows {len(bill_rows):,}/{len(margin_rows):,}, gross difference {difference:.2f}"
        )
    builder.control(
        "bill_margin_aggregate_reconciliation",
        status="passed" if passed else "failed",
        severity="info" if passed else "major",
        title="Bill Item Detail and Gross/Net Margin aggregate reconciliation",
        observation="; ".join(observations) or "No comparable periods were available.",
        reports=[bill_id, margin_id],
        fields=["net_amt", "gross_sale_value", "item_qty", "item_subtotal", "total_discount_amt", "tax_amt"],
    )


def report_packet(builder: ReviewBuilder) -> dict[str, Any]:
    issues_by_file_row: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for issue in builder.row_issues:
        issues_by_file_row[(issue["file"], issue["row_number"])].append(
            {key: value for key, value in issue.items() if key != "file"}
        )
    reports = []
    for report_id, exports in sorted(builder.exports_by_report.items()):
        report_findings = [item for item in builder.findings if item["report_id"] == report_id]
        report_controls = [
            item for item in builder.controls if report_id in item.get("reports", [])
        ]
        report_exports = []
        for export in exports:
            column_types = {
                field["field"]: field.get("declared_type", "text")
                for field in export.profile.get("fields") or []
            }
            rows = []
            for index, values in enumerate(export.rows):
                row_number = export.source_row_number(index)
                rows.append(
                    {
                        "source_row_number": row_number,
                        "values": values,
                        "issues": issues_by_file_row.get(
                            (export.profile["file"], row_number), []
                        ),
                    }
                )
            report_exports.append(
                {
                    "id": stable_id(export.profile["file"]),
                    "label": export.label,
                    "columns": export.columns,
                    "column_types": column_types,
                    "rows": rows,
                }
            )
        reports.append(
            {
                "report_id": report_id,
                "display_name": exports[0].profile["display_name"],
                "findings": report_findings,
                "controls": report_controls,
                "exports": report_exports,
            }
        )
    return {
        "packet_version": BUSINESS_REVIEW_VERSION,
        "privacy": "Local browser packet. Contains operational rows; never upload or commit.",
        "as_of_date": builder.as_of.date().isoformat(),
        "reports": reports,
    }


def public_summary(builder: ReviewBuilder, report_count: int, row_count: int) -> dict[str, Any]:
    severity_counts = Counter(item["severity"] for item in builder.findings)
    state_counts = Counter(item["state"] for item in builder.findings)
    row_severity_counts = Counter(item["severity"] for item in builder.row_issues)
    controls = [
        {key: value for key, value in item.items() if key not in {"file", "row_number"}}
        for item in builder.controls
    ]
    findings = [
        {key: value for key, value in item.items() if key not in {"file", "row_number"}}
        for item in builder.findings
    ]
    return {
        "contract_version": BUSINESS_REVIEW_VERSION,
        "as_of_date": builder.as_of.date().isoformat(),
        "privacy": (
            "Aggregate business findings and cross-report controls only. "
            "No source paths, file names, operational rows, item/vendor names, or sensitive values."
        ),
        "summary": {
            "reviewed_report_count": report_count,
            "reviewed_row_count": row_count,
            "finding_count": len(findings),
            "row_observation_count": len(builder.row_issues),
            "severity_counts": dict(sorted(severity_counts.items())),
            "row_severity_counts": dict(sorted(row_severity_counts.items())),
            "state_counts": dict(sorted(state_counts.items())),
            "passed_control_count": sum(item["status"] == "passed" for item in controls),
            "failed_control_count": sum(item["status"] == "failed" for item in controls),
            "definition_gate_count": sum(item["status"] == "definition_gate" for item in controls),
        },
        "severity_legend": {
            "critical": "Blocks a dependent production KPI or represents a high-impact exception.",
            "major": "Material coverage, logic, or operational issue requiring action.",
            "minor": "Bounded discrepancy or low-materiality exception retained for review.",
            "info": "Passed control or context; no defect is asserted.",
        },
        "state_legend": {
            "confirmed_issue": "The exported evidence directly proves the condition.",
            "operational_exception": "The value may be valid but requires operational action.",
            "needs_business_definition": "The observation is real; its treatment depends on an approved definition.",
        },
        "findings": findings,
        "controls": controls,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--as-of", default="2026-07-23")
    args = parser.parse_args()
    as_of = datetime.strptime(args.as_of, "%Y-%m-%d")
    local_dir, exports = load_exports(args.audit_run)
    builder = ReviewBuilder(exports, as_of)

    profile_controls(builder)
    closing_stock_checks(builder)
    variance_checks(builder)
    gross_margin_checks(builder)
    opening_and_entry_checks(builder)
    po_checks(builder)
    po_entry_lineage(builder)
    recipe_and_sales_checks(builder)
    recipe_consumption_duplicates(builder)
    transfer_control(builder)
    consumption_variance_control(builder)
    bill_margin_control(builder)

    row_count = sum(len(export.rows) for export in exports)
    private_review = {
        "contract_version": BUSINESS_REVIEW_VERSION,
        "as_of_date": as_of.date().isoformat(),
        "findings": builder.findings,
        "controls": builder.controls,
        "row_issues": builder.row_issues,
    }
    write_json(local_dir / "business_review.json", private_review)
    write_json(local_dir / "local_review_packet.json", report_packet(builder))
    safe = public_summary(builder, len(builder.exports_by_report), row_count)
    write_json(local_dir / "public_business_review.json", safe)
    print(
        f"Reviewed {len(builder.exports_by_report)} reports / {row_count:,} rows: "
        f"{len(builder.findings)} finding types, {len(builder.row_issues):,} row observations, "
        f"{safe['summary']['passed_control_count']} passed controls."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
