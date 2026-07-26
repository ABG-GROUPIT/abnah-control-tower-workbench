#!/usr/bin/env python3
"""Build a privacy-minimized Control Tower audit evidence contract.

The compiler reads local-only deterministic audit output, verifies every observed
CSV header against the corresponding Schema Workbench structure variant, and
emits only aggregate findings plus narrowly scoped issue-row excerpts.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


CONTRACT_VERSION = "2.0.0"
SOURCE_REPORT_MAP = {
    "RAWN_CT_gross_net_margin": "p2.gross_net_margin.item",
    "RAWN_CT_item_recipe_report": "p1.item_recipe.detail",
    "RAWN_CT_enterprise_variance_normal": "p4.enterprise_variance.normal",
    "RAWN_CT_closing_stock": "p4.closing_stock.item",
    "RAWN_CT_enterprise_purchase_order": "p4.enterprise_purchase_order.item",
    "RAWN_CT_enterprise_entry": "p4.enterprise_entry.item",
    "RAWN_CT_enterprise_transfer_from": "p4.enterprise_transfer.from_item",
    "RAWN_CT_enterprise_transfer_to": "p4.enterprise_transfer.to_item",
    "RAWN_CT_enterprise_wastage_normal": "p4.enterprise_wastage.normal",
    "RAWN_CT_enterprise_stock_return": "p4.enterprise_stock_return.item",
    "RAWN_CT_bill_item_detail": "p2.bill_item_detail.item",
    "RAWN_CT_purchase_detail": "p4.purchase_detail.po_enabled",
    "RAWN_CT_recipe_consumption": "p4.recipe_consumption.item",
    "RAWN_CT_enterprise_consumption_detail": "p4.enterprise_consumption.detail",
    "RAWN_CT_enterprise_physical": "p4.enterprise_physical.item",
    "RAWN_CT_enterprise_reorder": "p4.enterprise_reorder.item",
}
ALTERNATIVE_ROLES = {
    "p4.enterprise_stock_return.item": {
        "role": "evaluated_unavailable",
        "pages": ["P2", "P3", "P4"],
        "reason": "Header-only evidence; excluded from the active model and vendor return rate.",
    },
    "p4.enterprise_reorder.item": {
        "role": "evaluated_unavailable",
        "pages": ["P1", "P4"],
        "reason": "Header-only evidence; excluded from active calculations and replaced by forecast-driven projected shortage.",
    },
    "p4.bulk_return.item": {
        "role": "evaluated_fallback",
        "pages": ["P2", "P3", "P4"],
        "reason": "Retained only as a fallback to Enterprise Stock Return.",
    },
    "p4.enterprise_opening.item": {
        "role": "evaluated_reconciliation",
        "pages": ["P3", "P4"],
        "reason": "Useful for inventory bridge checks; not a minimum dashboard source.",
    },
    "p4.enterprise_variance.master": {
        "role": "evaluated_reconciliation",
        "pages": ["P3", "P4"],
        "reason": "Retained as a master-level comparison to the selected normal variance report.",
    },
    "p4.stock_in_stock_out.item": {
        "role": "evaluated_fallback",
        "pages": ["P1", "P3", "P4"],
        "reason": "Retained as a movement fallback when paired transfer reports are incomplete.",
    },
}
RULE_TITLES = {
    "observed_ideal_closing_formula": "Ideal closing does not reconcile to the observed movement formula",
    "entry_base_from_qty_price": "Entry base amount differs from quantity multiplied by unit price",
    "entry_total_tax_bridge": "Entry total tax differs from exported tax components",
    "physical_amount_from_qty_price": "Physical-stock amount differs from quantity multiplied by unit price",
    "transfer_amount_from_qty_price": "Transfer amount differs from quantity multiplied by unit price",
    "wastage_amount_from_qty_price": "Wastage amount differs from quantity multiplied by unit price",
    "parent_subtotal_from_qty_price": "Recipe parent subtotal differs from quantity multiplied by unit price",
    "bill_item_net_bridge": "Bill-item net amount does not reconcile to the exported bridge",
    "closing_amount_from_qty_price": "Closing-stock amount differs from quantity multiplied by average price",
    "gross_margin_formula": "Reported gross margin differs from the conventional exported-value formula",
    "net_margin_formula": "Reported net margin differs from the conventional exported-value formula",
    "stock_in_subtotal_from_qty_price": "Stock-in subtotal differs from quantity multiplied by unit price",
    "stock_out_subtotal_from_qty_price": "Stock-out subtotal differs from quantity multiplied by unit price",
}
RULE_ACTIONS = {
    "observed_ideal_closing_formula": "Retain the source value and investigate any row outside the verified movement bridge and export tolerance.",
    "entry_base_from_qty_price": "Retain the raw amount and review only differences outside the uncertainty created by displayed quantity and price precision.",
    "entry_total_tax_bridge": "Retain exported tax and components separately; publish a canonical tax only after the missing component or rounding rule is confirmed.",
    "physical_amount_from_qty_price": "Retain the exported valuation when it is compatible with the displayed quantity and price precision; investigate only out-of-envelope rows.",
    "transfer_amount_from_qty_price": "Reconcile both transfer directions and investigate only valuation differences outside displayed precision.",
    "wastage_amount_from_qty_price": "Retain the exported valuation when compatible with displayed precision and preserve any genuine exceptions for audit.",
    "parent_subtotal_from_qty_price": "Retain source subtotals that reconcile within displayed precision and review only genuine outliers.",
    "bill_item_net_bridge": "Use the corrected taxable-base and tax-value semantics, then retain any remaining row as a genuine reconciliation exception.",
    "closing_amount_from_qty_price": "Retain closing value when compatible with displayed precision; review genuine outliers before capital KPIs are published.",
    "gross_margin_formula": "Recompute canonical gross margin from approved revenue and cost fields; retain the reported percentage only as a source comparison.",
    "net_margin_formula": "Recompute canonical net margin from approved net sales and cost; retain the reported percentage only as a source comparison.",
    "stock_in_subtotal_from_qty_price": "Accept values compatible with displayed precision and investigate only out-of-envelope stock-in rows.",
    "stock_out_subtotal_from_qty_price": "Accept values compatible with displayed precision and investigate only out-of-envelope stock-out rows.",
}
SEMANTIC_RULE_REVIEWS = {
    "observed_ideal_closing_formula": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "The corrected movement equation includes Purchase and Stock In separately and subtracts both Stock Out and Consumption. A future finding means the row is outside that verified bridge and tolerance, not that the earlier incomplete equation should be restored.",
        "businessQuestion": "Does the exceptional row contain a movement type, reuse, yield-wastage, or cut-off treatment not represented in the current populated sample?",
    },
    "entry_base_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "The rule already allows the complete uncertainty implied by displayed quantity, price, and amount precision. A remaining finding is incompatible with those visible fields and requires a valuation or UOM explanation.",
        "businessQuestion": "Which UOM conversion or valuation basis explains the out-of-envelope amount?",
    },
    "entry_total_tax_bridge": {
        "classification": "formula_definition_gate",
        "confidence": "medium",
        "assessment": "Item rows are checked against exported tax components. Document-charge rows are excluded because Restroworks exports their Total Tax but leaves component and rate columns blank.",
        "businessQuestion": "Which additional item-level tax component explains the remaining difference?",
    },
    "physical_amount_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "Displayed-precision uncertainty is already allowed. A remaining finding requires a valuation-date, UOM, or hidden-price explanation.",
        "businessQuestion": "Which approved valuation basis explains the out-of-envelope Physical Amount?",
    },
    "transfer_amount_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "Displayed rounding is already allowed. A remaining transfer difference requires UOM or source-outlet valuation review.",
        "businessQuestion": "Is the exceptional transfer valued using a different UOM or source-outlet cost?",
    },
    "wastage_amount_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "Displayed rounding is already allowed. A remaining wastage difference requires valuation or UOM review.",
        "businessQuestion": "Which valuation price or UOM conversion explains the out-of-envelope Wastage Amount?",
    },
    "parent_subtotal_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "Displayed rounding is already allowed. A remaining parent subtotal requires recipe-grain, allocation, or UOM review.",
        "businessQuestion": "Is the exceptional Parent Subtotal allocated or converted at another recipe grain?",
    },
    "bill_item_net_bridge": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "The bridge now distinguishes each GST taxable base from its tax value. A remaining finding indicates an additional charge, allocation, or rounding treatment.",
        "businessQuestion": "Which additional bill-item component explains the corrected bridge exception?",
    },
    "closing_amount_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "Displayed quantity and price precision is already allowed. A remaining closing difference requires valuation or UOM review.",
        "businessQuestion": "Which valuation basis explains the out-of-envelope Closing Amount?",
    },
    "gross_margin_formula": {
        "classification": "formula_definition_gate",
        "confidence": "high",
        "assessment": "Zero-cost rows are excluded from formula validation and hidden cost precision is allowed. A remaining finding indicates a genuine source-formula or revenue-basis exception.",
        "businessQuestion": "Which revenue or cost basis explains the remaining Gross Margin Percent exception?",
    },
    "net_margin_formula": {
        "classification": "formula_definition_gate",
        "confidence": "high",
        "assessment": "Zero-cost rows are excluded from formula validation and hidden cost precision is allowed. A remaining finding indicates a genuine source-formula or net-sales-basis exception.",
        "businessQuestion": "Which net-sales or cost basis explains the remaining Net Margin Percent exception?",
    },
    "stock_in_subtotal_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "Displayed precision is already allowed. A remaining stock-in difference requires UOM or valuation review.",
        "businessQuestion": "Which UOM or valuation basis explains the out-of-envelope Stock In Subtotal?",
    },
    "stock_out_subtotal_from_qty_price": {
        "classification": "reconciliation_exception",
        "confidence": "high",
        "assessment": "Displayed precision is already allowed. A remaining stock-out difference requires UOM or valuation review.",
        "businessQuestion": "Which UOM or valuation basis explains the out-of-envelope Stock Out Subtotal?",
    },
}
SEMANTIC_CATEGORY_REVIEWS = {
    "coverage": {
        "classification": "coverage_blocker",
        "confidence": "high",
        "assessment": "The export contains no usable rows for one or more captured periods. This is a confirmed evidence-coverage gap, regardless of whether the underlying operational system contains data elsewhere.",
        "businessQuestion": "Is the report genuinely unused, filtered incorrectly, permission-restricted, or populated in another module?",
    },
    "duplication": {
        "classification": "deduplication_risk",
        "confidence": "medium",
        "assessment": "Exact repeated exported rows create an aggregation risk, but they may represent legitimate repeated events when the report omits a transaction-line key. Do not delete them until the business grain is approved.",
        "businessQuestion": "Which transaction and line identifiers distinguish legitimate repeated rows from duplicate exports?",
    },
    "sign_review": {
        "classification": "operational_exception",
        "confidence": "high",
        "assessment": "Negative quantities, values, or margins can be valid returns, reversals, corrections, oversold stock, or loss-making sales. They are operational exceptions, not automatic data errors.",
        "businessQuestion": "Which transaction types and status values define the approved sign convention for each negative field?",
    },
    "cost_coverage": {
        "classification": "cost_coverage_gap",
        "confidence": "high",
        "assessment": "Zero exported cost is a source-coverage state, not proof that an item was free and not a margin-formula defect. The period concentration must be resolved before source-reported margin is used.",
        "businessQuestion": "Why does purchase-cost coverage fall sharply in the affected period, and which approved recipe or valuation source should fill the gap?",
    },
}
REPORT_DECISIONS = {
    "p2.gross_net_margin.item": "Schema-ready; reported margins reconcile where cost is present, but the period-specific zero-cost coverage gap blocks source-margin completeness.",
    "p1.item_recipe.detail": "Schema-ready and populated; recipe identifiers, effective dates, and UOM conversion still require master-data approval.",
    "p4.enterprise_variance.normal": "Schema-ready; negative inventory and consumption signs require business treatment before KPI publication.",
    "p4.closing_stock.item": "Schema-ready; quantity-price-value rows reconcile within displayed precision, while negative stock remains an operational exception.",
    "p4.enterprise_purchase_order.item": "Populated and schema-ready; receipt linkage, status semantics, and eligible closed-line rules remain production gates.",
    "p4.enterprise_entry.item": "Schema-ready; item amounts reconcile within displayed precision. Charge rows carry total tax without component columns, while PO and batch coverage remain production gates.",
    "p4.enterprise_transfer.from_item": "Schema-ready; values reconcile within displayed precision and must still pair against Transfer To by transaction.",
    "p4.enterprise_transfer.to_item": "Schema-ready; values reconcile within displayed precision and must still pair against Transfer From by transaction.",
    "p4.enterprise_wastage.normal": "Schema-ready; exported wastage values reconcile within displayed precision.",
    "p4.enterprise_stock_return.item": "Header-only export; exclude it from the active model and keep vendor return rate unavailable.",
    "p2.bill_item_detail.item": "Schema-ready; GST taxable bases and tax values are now distinguished, and every populated row reconciles to exported net amount.",
    "p4.purchase_detail.po_enabled": "Schema-ready but PO coverage is sparse; use only as a fallback and reconciliation source.",
    "p4.recipe_consumption.item": "Schema-ready; subtotals reconcile within displayed precision, while two periods are empty and exact duplicate-looking rows remain a grain risk.",
    "p4.enterprise_consumption.detail": "Schema-ready; the ideal-closing movement bridge is verified across all 812 populated rows within export tolerance.",
    "p4.enterprise_physical.item": "Schema-ready; exported physical values reconcile within displayed precision and approved month-end checkpoints are still required.",
    "p4.enterprise_reorder.item": "Header-only export; exclude it from the active model and do not describe projected shortage as a POSIST reorder breach.",
    "p4.bulk_return.item": "Schema-ready and populated, but retained only as a fallback return source.",
    "p4.enterprise_opening.item": "Schema-ready with only three rows and zero valuation price/amount throughout; retain for quantity reconciliation only.",
    "p4.enterprise_variance.master": "Schema-ready; sign conventions require review and normal variance remains the selected source.",
    "p4.stock_in_stock_out.item": "Schema-ready; stock-in and stock-out subtotals reconcile within displayed precision, while paired enterprise transfers remain the preferred authority.",
}
KEY_FIELDS = {
    "p4.enterprise_purchase_order.item": [
        "po_number",
        "po_date",
        "expected_delivery_date",
        "po_status",
        "ordered_qty",
        "processed_qty",
        "remaining_balance_qty",
        "po_close_or_partial_receive_date",
    ],
    "p4.enterprise_entry.item": [
        "transaction_number",
        "po_number",
        "batch_number",
        "entry_qty",
        "unit_price",
        "total_amt",
    ],
    "p4.purchase_detail.po_enabled": [
        "po_number",
        "po_date",
        "po_qty",
        "po_unit_price",
        "purchase_qty",
        "purchase_amount",
    ],
    "p4.recipe_consumption.item": [
        "item_code",
        "parent_item_qty",
        "consumed_item_code",
        "consumed_qty",
        "consumed_subtotal",
    ],
    "p4.enterprise_stock_return.item": ["transaction_number", "return_date", "return_qty", "return_amt"],
    "p4.enterprise_reorder.item": ["item_code", "reorder_level_qty", "minimum_order_level_qty"],
}
NEGATIVE_EVIDENCE_REPORTS = {
    "p4.enterprise_variance.normal",
    "p4.enterprise_variance.master",
    "p4.closing_stock.item",
    "p2.gross_net_margin.item",
}
MANUAL_REVIEW_REPORTS = {
    "p4.enterprise_purchase_order.item",
    "p4.purchase_detail.po_enabled",
}
SENSITIVE_NAME_PATTERN = re.compile(
    r"(?i)(customer|mobile|phone|email|address|contact|whatsapp|card_number|user_name|waiter)"
)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def normalize_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\ufeff", "").strip()).casefold()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "source"


def column_leaves(nodes: list[dict[str, Any]]) -> list[str]:
    leaves: list[str] = []
    for node in nodes:
        children = node.get("children") or []
        if children:
            leaves.extend(column_leaves(children))
        else:
            leaves.append(str(node.get("label", "")))
    return leaves


def column_leaf_keys(nodes: list[dict[str, Any]]) -> list[str]:
    leaves: list[str] = []
    for node in nodes:
        children = node.get("children") or []
        if children:
            leaves.extend(column_leaf_keys(children))
        else:
            leaves.append(str(node.get("key") or slug(str(node.get("label", "")))))
    return leaves


def block_header(block: dict[str, Any]) -> list[str]:
    if block.get("columns"):
        return column_leaves(block["columns"])
    if block.get("value_columns"):
        return [str(value) for value in block.get("row_headers") or []] + column_leaves(
            block["value_columns"]
        )
    return []


def block_keys(block: dict[str, Any]) -> list[str]:
    if block.get("columns"):
        return column_leaf_keys(block["columns"])
    if block.get("value_columns"):
        return [
            slug(str(value)) for value in block.get("row_headers") or []
        ] + column_leaf_keys(block["value_columns"])
    return []


def verify_workbench_variant(
    profile: dict[str, Any],
    atlas_root: Path,
    contract: dict[str, Any],
) -> dict[str, Any]:
    blueprint_path = atlas_root / profile["workbench"]["blueprint_path"]
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    observed = [normalize_label(value) for value in profile["schema"]["observed_header"]]
    canonical = [column["name"] for column in contract.get("row_columns") or []]
    matches = []
    candidates = []
    for block in blueprint.get("blocks") or []:
        header = block_header(block)
        keys = block_keys(block)
        if not header:
            continue
        candidates.append({"id": block.get("id", ""), "columnCount": len(header)})
        if (
            [normalize_label(value) for value in header] == observed
            or (canonical and keys == canonical)
        ):
            matches.append(block)
    if not matches:
        raise ValueError(
            f"{profile['report_id']} has no exact Workbench block match; "
            f"observed {len(observed)} columns, candidates {candidates}"
        )
    return {
        "status": "exact",
        "workbenchReportId": blueprint["report_id"],
        "matchedVariantId": matches[0].get("id", ""),
        "matchedVariantName": matches[0].get("name", ""),
        "columnCount": len(observed),
        "statement": "Observed CSV header matches its contract exactly; canonical column positions match the captured Workbench variant, including grouped quantity and amount headings.",
    }


def format_period(dates: list[str], export_number: int) -> str:
    if not dates:
        return f"Export {export_number}"
    parsed = [date.fromisoformat(value) for value in dates]
    if len(parsed) == 1 or parsed[0] == parsed[-1]:
        return f"Snapshot {parsed[0].strftime('%d %b %Y')}"
    return f"{parsed[0].strftime('%d %b')} - {parsed[-1].strftime('%d %b %Y')}"


def rule_fields(rule: dict[str, Any]) -> list[str]:
    fields = []
    for key in ("target", "left", "right", "field", "revenue", "cost", "earlier", "later"):
        if rule.get(key):
            fields.append(rule[key])
    fields.extend(term["field"] for term in rule.get("terms") or [])
    return list(dict.fromkeys(fields))


def read_normalized_row(
    normalized_dir: Path,
    profile: dict[str, Any],
    source_row_number: int,
) -> dict[str, str]:
    source_stem = Path(profile["file"]).stem
    path = normalized_dir / f"{source_stem}__normalized.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    index = source_row_number - int(profile["schema"].get("header_row_number", 1)) - 1
    return rows[index] if 0 <= index < len(rows) else {}


def decimal_cell(row: dict[str, str], field: str) -> Decimal | None:
    raw = (row.get(field) or "").strip()
    if not raw:
        return None
    try:
        return Decimal(raw)
    except InvalidOperation:
        return None


def zero_cost_coverage(
    normalized_dir: Path,
    profiles: list[dict[str, Any]],
    export_labels: dict[str, str],
) -> dict[str, Any]:
    eligible = 0
    zero_cost = 0
    periods = []
    for profile in profiles:
        path = normalized_dir / f"{Path(profile['file']).stem}__normalized.csv"
        period_eligible = 0
        period_zero_cost = 0
        if path.exists():
            with path.open(encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    net_sales = decimal_cell(row, "net_sale_value")
                    purchase_value = decimal_cell(row, "purchase_value")
                    if net_sales in (None, 0):
                        continue
                    period_eligible += 1
                    if purchase_value == 0:
                        period_zero_cost += 1
        eligible += period_eligible
        zero_cost += period_zero_cost
        periods.append(
            {
                "label": export_labels[profile["file"]],
                "eligibleRows": period_eligible,
                "zeroCostRows": period_zero_cost,
                "coverageGapPercent": (
                    round(period_zero_cost / period_eligible * 100, 1)
                    if period_eligible
                    else 0
                ),
            }
        )
    return {
        "eligibleRows": eligible,
        "zeroCostRows": zero_cost,
        "coverageGapPercent": (
            round(zero_cost / eligible * 100, 1) if eligible else 0
        ),
        "periods": periods,
    }


def field_lookup(contracts: dict[str, dict[str, Any]], report_id: str) -> dict[str, dict[str, Any]]:
    return {
        column["name"]: column
        for column in contracts.get(report_id, {}).get("row_columns") or []
    }


def safe_excerpt_values(
    row: dict[str, str],
    fields: list[str],
    contract_fields: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    values = []
    for field in fields:
        metadata = contract_fields.get(field, {})
        if metadata.get("sensitive") or SENSITIVE_NAME_PATTERN.search(field):
            continue
        raw = row.get(field, "")
        values.append(
            {
                "field": field,
                "label": str(metadata.get("source_label") or metadata.get("label") or field).replace("_", " "),
                "value": raw,
            }
        )
    return values


def aggregate_fields(profiles: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    fields: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        for source in profile.get("fields") or []:
            if source.get("sensitive") or SENSITIVE_NAME_PATTERN.search(source["field"]):
                continue
            target = fields.setdefault(
                source["field"],
                {
                    "field": source["field"],
                    "label": source["field"].replace("_", " "),
                    "declaredType": source.get("declared_type", "text"),
                    "totalCount": 0,
                    "nonNullCount": 0,
                    "nullCount": 0,
                    "zeroCount": 0,
                    "negativeCount": 0,
                    "parseErrorCount": 0,
                },
            )
            for source_key, target_key in (
                ("total_count", "totalCount"),
                ("non_null_count", "nonNullCount"),
                ("null_count", "nullCount"),
                ("zero_count", "zeroCount"),
                ("negative_count", "negativeCount"),
                ("parse_error_count", "parseErrorCount"),
            ):
                target[target_key] += int(source.get(source_key, 0))
    return fields


def coverage_status(field: dict[str, Any]) -> str:
    total = field["totalCount"]
    non_null = field["nonNullCount"]
    if total == 0 or non_null == 0:
        return "missing"
    ratio = non_null / total
    if ratio < 0.5:
        return "weak"
    if ratio < 0.95:
        return "partial"
    return "complete"


def semantic_review(rule_id: str, category: str) -> dict[str, str]:
    review = SEMANTIC_RULE_REVIEWS.get(rule_id) or SEMANTIC_CATEGORY_REVIEWS.get(category)
    if review:
        return dict(review)
    return {
        "classification": "review_required",
        "confidence": "medium",
        "assessment": "The deterministic observation is real, but its business meaning has not been proven from the exported fields alone.",
        "businessQuestion": "What source-system definition and business rule should govern this observation?",
    }


def business_finding_to_evidence(finding: dict[str, Any]) -> dict[str, Any]:
    issue_class = finding["issue_class"]
    state = finding["state"]
    if state == "operational_exception":
        classification = "operational_exception"
        assessment = (
            "The exported condition is real and decision-relevant, but it may be a valid "
            "business event rather than a data defect."
        )
    elif issue_class == "grain":
        classification = "deduplication_risk"
        assessment = (
            "The repeated evidence is real, but the export grain is insufficient to prove "
            "that equal rows represent duplicate business events."
        )
    elif issue_class in {"coverage", "freshness"}:
        classification = (
            "coverage_blocker"
            if finding["severity"] == "critical"
            else "cost_coverage_gap"
        )
        assessment = (
            "The exported evidence directly proves a coverage or freshness gap. "
            "Dependent production KPIs remain gated."
        )
    else:
        classification = "review_required"
        assessment = (
            "The exported condition is confirmed, but the standardization or business "
            "treatment must be approved before production use."
        )
    return {
        "id": finding["id"],
        "category": issue_class,
        "issueClass": issue_class,
        "state": state,
        "severity": finding["severity"],
        "title": finding["title"],
        "affectedRowCount": finding["affected_row_count"],
        "fields": finding["fields"],
        "observation": finding["observation"],
        "productionTreatment": finding["production_treatment"],
        "metrics": finding.get("metrics") or {},
        "semanticReview": {
            "classification": classification,
            "confidence": finding["confidence"],
            "assessment": assessment,
            "businessQuestion": finding["business_question"],
        },
    }


def issue_density(
    profile: dict[str, Any],
    profile_issues: list[dict[str, str]],
    bucket_count: int = 36,
) -> list[int]:
    row_count = int(profile["rows"]["source_count"])
    buckets = [0] * bucket_count
    if row_count <= 0:
        return buckets
    header_row = int(profile["schema"].get("header_row_number", 1))
    for issue in profile_issues:
        if not issue.get("row_number"):
            continue
        data_index = max(0, int(issue["row_number"]) - header_row - 1)
        bucket = min(bucket_count - 1, int(data_index / row_count * bucket_count))
        buckets[bucket] += 1
    return buckets


def report_review_summary(
    row_count: int,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    classifications = Counter(
        finding["semanticReview"]["classification"] for finding in findings
    )
    if row_count == 0:
        status = "coverage_blocked"
        headline = "No structural mismatch; populated evidence is missing."
        next_decision = "Obtain a populated export or approve an alternate source before enabling dependent KPIs."
    elif classifications["coverage_blocker"] or classifications["cost_coverage_gap"]:
        status = "coverage_review"
        headline = "Schema is sound; critical value coverage remains incomplete."
        next_decision = "Resolve the identified period or field coverage gap before enabling dependent production KPIs."
    elif classifications["formula_definition_gate"] or classifications["reconciliation_exception"]:
        status = "definition_review"
        headline = "Schema is sound; a bounded reconciliation definition remains unresolved."
        next_decision = "Confirm the exceptional UOM, valuation, tax, or movement treatment before classifying the source value as incorrect."
    elif classifications["deduplication_risk"] or classifications["operational_exception"]:
        status = "business_review"
        headline = "Schema is sound; observed rows need business-grain and sign treatment."
        next_decision = "Approve transaction grain and sign conventions before aggregation."
    else:
        status = "no_encoded_exception"
        headline = "No encoded structural or value exception was detected."
        next_decision = "Continue period reconciliation and business sign-off before production publication."
    return {
        "status": status,
        "headline": headline,
        "assessment": (
            "Codex independently reviewed the deterministic rule semantics. "
            "No confirmed structural error was found in this report's captured CSV contract."
        ),
        "confirmedStructuralErrorCount": 0,
        "classificationCounts": dict(sorted(classifications.items())),
        "nextDecision": next_decision,
    }


def model_role_group(role: str) -> str:
    if role in {"primary", "primary_production_gate", "primary_quality_gated"}:
        return "primary"
    if role.startswith("required_") or role in {
        "validation_reference",
        "conditional_feature",
        "derived_dimension",
    }:
        return "auxiliary"
    return "control"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-run", type=Path, required=True)
    parser.add_argument("--atlas-root", type=Path, required=True)
    parser.add_argument("--source-matrix", type=Path, required=True)
    parser.add_argument("--contracts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    local_dir = args.audit_run / "LOCAL_EVIDENCE_DO_NOT_UPLOAD"
    profiles = json.loads(
        (local_dir / "full_profiles_with_local_samples.json").read_text(encoding="utf-8")
    )
    with (local_dir / "deterministic_audit" / "issues.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        issues = list(csv.DictReader(handle))
    with args.source_matrix.open(encoding="utf-8-sig", newline="") as handle:
        source_matrix = list(csv.DictReader(handle))
    public_business_review_path = local_dir / "public_business_review.json"
    public_business_review = (
        json.loads(public_business_review_path.read_text(encoding="utf-8"))
        if public_business_review_path.exists()
        else {"summary": {}, "findings": [], "controls": []}
    )
    business_findings_by_report: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in public_business_review.get("findings") or []:
        business_findings_by_report[finding["report_id"]].append(finding)

    contracts = {}
    for path in args.contracts.glob("*.json"):
        contract = json.loads(path.read_text(encoding="utf-8"))
        contracts[contract["report_id"]] = contract

    grouped_profiles: dict[str, list[dict[str, Any]]] = defaultdict(list)
    profile_by_file: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        grouped_profiles[profile["report_id"]].append(profile)
        profile_by_file[profile["file"]] = profile

    visual_matches = {
        report_id: verify_workbench_variant(
            report_profiles[0],
            args.atlas_root,
            contracts[report_id],
        )
        for report_id, report_profiles in grouped_profiles.items()
    }

    gated_roles = {"blocked_feature", "unavailable_header_only"}
    selected_by_report = {
        SOURCE_REPORT_MAP[row["source_table"]]: row
        for row in source_matrix
        if row["source_table"] in SOURCE_REPORT_MAP
        and row["model_role"] not in gated_roles
    }
    source_register = []
    for row in source_matrix:
        report_id = SOURCE_REPORT_MAP.get(row["source_table"], "")
        report_profiles = grouped_profiles.get(report_id, [])
        row_count = sum(int(profile["rows"]["source_count"]) for profile in report_profiles)
        source_register.append(
            {
                "id": f"source:{slug(row['source_table'])}",
                "sourceName": row["source_name"],
                "sourceTable": row["source_table"],
                "modelRole": row["model_role"],
                "roleGroup": model_role_group(row["model_role"]),
                "pages": row["pages"].split("|"),
                "requiredFields": [value.strip() for value in row["required_fields"].split(",") if value.strip()],
                "productionDecision": row["production_decision"],
                "fallbackOrReconciliation": row["fallback_or_reconciliation"],
                "auditReportId": report_id,
                "workbenchReportId": (
                    visual_matches[report_id]["workbenchReportId"] if report_id else ""
                ),
                "auditStatus": (
                    "historical_schema_with_documented_quality_gate"
                    if row["source_table"] == "RAWN_CT_vendor_report"
                    else (
                        "not_in_local_export_set"
                        if not report_id
                        else ("populated" if row_count else "header_only")
                    )
                ),
                "rowCount": row_count,
            }
        )

    report_entries = []
    total_business_issues = 0
    for report_id, report_profiles in sorted(
        grouped_profiles.items(), key=lambda item: item[1][0]["display_name"]
    ):
        report_profiles.sort(key=lambda item: (item.get("filename_dates") or [], item["file_name"]))
        export_labels = {
            profile["file"]: format_period(profile.get("filename_dates") or [], index)
            for index, profile in enumerate(report_profiles, start=1)
        }
        report_issues = [
            issue
            for issue in issues
            if issue["report_id"] == report_id
            and issue["phase"] == "business"
            and issue["row_number"]
        ]
        total_business_issues += len(report_issues)
        grouped_issues: dict[str, list[dict[str, str]]] = defaultdict(list)
        for issue in report_issues:
            grouped_issues[issue["rule_id"]].append(issue)

        contract = contracts.get(report_id, {})
        contract_fields = field_lookup(contracts, report_id)
        rules = {rule["id"]: rule for rule in contract.get("rules") or []}
        findings = []
        evidence_rows = []
        for rule_id, rule_issues in sorted(grouped_issues.items()):
            first = rule_issues[0]
            rule = rules.get(rule_id, {})
            finding_id = f"{report_id}:{rule_id}"
            findings.append(
                {
                    "id": finding_id,
                    "category": "business_rule",
                    "severity": first["severity"],
                    "title": RULE_TITLES.get(rule_id, first["message"]),
                    "affectedRowCount": len(rule_issues),
                    "fields": rule_fields(rule) or [first["field"]],
                    "observation": first["message"],
                    "productionTreatment": RULE_ACTIONS.get(
                        rule_id,
                        "Preserve the source value in raw, calculate the standardized value, and retain a row-level exception flag.",
                    ),
                    "semanticReview": semantic_review(rule_id, "business_rule"),
                }
            )
            profile = profile_by_file[first["file"]]
            row_number = int(first["row_number"])
            normalized_row = read_normalized_row(
                local_dir / "deterministic_audit" / "normalized",
                profile,
                row_number,
            )
            evidence_rows.append(
                {
                    "id": f"evidence:{slug(report_id)}:{slug(rule_id)}",
                    "findingId": finding_id,
                    "exportLabel": export_labels[first["file"]],
                    "sourceRowNumber": row_number,
                    "values": safe_excerpt_values(
                        normalized_row,
                        rule_fields(rule) or [first["field"]],
                        contract_fields,
                    ),
                    "expected": first["expected"],
                    "observed": first["observed"],
                    "privacy": "Only issue-relevant non-sensitive cells are included.",
                }
            )

        field_health = aggregate_fields(report_profiles)
        key_fields = KEY_FIELDS.get(report_id)
        if key_fields is None:
            selected = selected_by_report.get(report_id)
            key_fields = [
                field
                for field in ((selected or {}).get("required_fields") or "").split(",")
                if field.strip()
            ]
        key_field_coverage = []
        for field_name in key_fields:
            field_name = field_name.strip()
            if field_name not in field_health:
                continue
            field = dict(field_health[field_name])
            field["label"] = str(
                contract_fields.get(field_name, {}).get("source_label")
                or contract_fields.get(field_name, {}).get("label")
                or field_name.replace("_", " ")
            )
            field["coverageStatus"] = coverage_status(field)
            field["coveragePercent"] = (
                round(field["nonNullCount"] / field["totalCount"] * 100, 1)
                if field["totalCount"]
                else 0
            )
            key_field_coverage.append(field)

        if report_id == "p2.gross_net_margin.item":
            cost_coverage = zero_cost_coverage(
                local_dir / "deterministic_audit" / "normalized",
                report_profiles,
                export_labels,
            )
            if cost_coverage["zeroCostRows"]:
                period_summary = "; ".join(
                    f"{item['label']}: {item['coverageGapPercent']:.1f}%"
                    for item in cost_coverage["periods"]
                )
                findings.append(
                    {
                        "id": f"{report_id}:zero_cost_coverage",
                        "category": "cost_coverage",
                        "severity": "warning",
                        "title": "Exported purchase-cost coverage changes sharply by period",
                        "affectedRowCount": cost_coverage["zeroCostRows"],
                        "fields": ["purchase_value", "net_sale_value"],
                        "observation": (
                            f"{cost_coverage['zeroCostRows']:,} of "
                            f"{cost_coverage['eligibleRows']:,} rows with non-zero net sales "
                            f"have zero exported purchase value "
                            f"({cost_coverage['coverageGapPercent']:.1f}%). "
                            f"Period gap rates: {period_summary}."
                        ),
                        "productionTreatment": (
                            "Do not interpret zero exported purchase value as free cost. "
                            "Use the approved recipe and ingredient valuation route only after "
                            "cost coverage and effective dates pass validation."
                        ),
                        "semanticReview": semantic_review("", "cost_coverage"),
                    }
                )

        if report_id == "p4.enterprise_opening.item":
            opening_price = field_health.get("unit_price", {})
            if (
                opening_price.get("nonNullCount")
                and opening_price.get("zeroCount")
                == opening_price.get("nonNullCount")
            ):
                findings.append(
                    {
                        "id": f"{report_id}:zero_valuation_coverage",
                        "category": "cost_coverage",
                        "severity": "warning",
                        "title": "Opening-stock valuation is unavailable in the captured rows",
                        "affectedRowCount": opening_price["zeroCount"],
                        "fields": ["unit_price", "opening_subtotal"],
                        "observation": (
                            "Every populated opening-stock row exports zero unit price and "
                            "zero subtotal. Quantity remains usable, but value does not."
                        ),
                        "productionTreatment": (
                            "Use this report only for opening quantity reconciliation until "
                            "an approved valuation source is joined."
                        ),
                        "semanticReview": semantic_review("", "cost_coverage"),
                    }
                )

        duplicate_count = sum(
            int(profile["rows"].get("duplicate_row_count", 0)) for profile in report_profiles
        )
        empty_file_count = sum(
            1 for profile in report_profiles if int(profile["rows"]["source_count"]) == 0
        )
        if empty_file_count:
            all_empty = empty_file_count == len(report_profiles)
            findings.append(
                {
                    "id": f"{report_id}:row_coverage",
                    "category": "coverage",
                    "severity": "blocker" if all_empty else "warning",
                    "title": (
                        "Export is header-only"
                        if all_empty
                        else "Some captured periods are header-only"
                    ),
                    "affectedRowCount": 0,
                    "fields": [],
                    "observation": (
                        f"{empty_file_count} of {len(report_profiles)} exports contain no data rows."
                    ),
                    "productionTreatment": (
                        "Keep dependent KPIs blocked until a populated export or approved alternate source is available."
                        if all_empty
                        else "Keep period completeness visible and exclude empty periods from trend conclusions."
                    ),
                    "semanticReview": semantic_review("", "coverage"),
                }
            )
        if duplicate_count:
            findings.append(
                {
                    "id": f"{report_id}:duplicate_rows",
                    "category": "duplication",
                    "severity": "warning",
                    "title": "Duplicate source rows were observed",
                    "affectedRowCount": duplicate_count,
                    "fields": [],
                    "observation": f"{duplicate_count:,} duplicate rows were observed across the captured exports.",
                    "productionTreatment": "Deduplicate on the approved business grain before aggregation and preserve duplicate counts as a data-quality measure.",
                    "semanticReview": semantic_review("", "duplication"),
                }
            )

        negative_fields = [
            field
            for field in field_health.values()
            if field["negativeCount"] and field["declaredType"] == "decimal"
        ]
        if report_id in NEGATIVE_EVIDENCE_REPORTS and negative_fields:
            negative_fields.sort(key=lambda item: item["negativeCount"], reverse=True)
            finding_id = f"{report_id}:negative_values"
            findings.append(
                {
                    "id": finding_id,
                    "category": "sign_review",
                    "severity": "review",
                    "title": "Negative values require signed-off business treatment",
                    "affectedRowCount": sum(item["negativeCount"] for item in negative_fields),
                    "fields": [item["field"] for item in negative_fields[:8]],
                    "observation": "Negative observations can represent returns, adjustments, or stock corrections; they are not classified as errors automatically.",
                    "productionTreatment": "Confirm sign conventions by transaction type and apply them consistently in standardized facts and KPI formulas.",
                    "semanticReview": semantic_review("", "sign_review"),
                }
            )
            for profile in report_profiles:
                anomaly = next(
                    (
                        row
                        for row in profile.get("local_only_anomaly_rows") or []
                        if "negative_value_review" in row.get("reasons", [])
                    ),
                    None,
                )
                if not anomaly:
                    continue
                values = [
                    {
                        "field": field,
                        "label": str(
                            contract_fields.get(field, {}).get("source_label")
                            or contract_fields.get(field, {}).get("label")
                            or field.replace("_", " ")
                        ),
                        "value": value,
                    }
                    for field, value in anomaly["values"].items()
                    if not SENSITIVE_NAME_PATTERN.search(field)
                ]
                evidence_rows.append(
                    {
                        "id": f"evidence:{slug(report_id)}:negative",
                        "findingId": finding_id,
                        "exportLabel": export_labels[profile["file"]],
                        "sourceRowNumber": int(anomaly["row_number"]),
                        "values": values,
                        "expected": "Business-approved sign convention",
                        "observed": "One or more exported values are negative",
                        "privacy": "Only issue-relevant non-sensitive cells are included.",
                    }
                )
                break

        reviewed_findings = business_findings_by_report.get(report_id)
        if reviewed_findings is not None and public_business_review_path.exists():
            findings = [
                business_finding_to_evidence(finding)
                for finding in reviewed_findings
            ]
            finding_ids = {finding["id"] for finding in findings}
            if evidence_rows and finding_ids:
                operational_id = next(
                    (
                        finding["id"]
                        for finding in findings
                        if finding["state"] == "operational_exception"
                    ),
                    "",
                )
                evidence_rows = [
                    {
                        **row,
                        "findingId": (
                            row["findingId"]
                            if row["findingId"] in finding_ids
                            else operational_id
                        ),
                    }
                    for row in evidence_rows
                    if row["findingId"] in finding_ids or operational_id
                ]
            else:
                evidence_rows = []

        row_count = sum(int(profile["rows"]["source_count"]) for profile in report_profiles)
        profile_issues = {
            profile["file"]: [
                issue
                for issue in report_issues
                if issue["file"] == profile["file"]
            ]
            for profile in report_profiles
        }
        for evidence_row in evidence_rows:
            profile = next(
                (
                    candidate
                    for candidate in report_profiles
                    if export_labels[candidate["file"]] == evidence_row["exportLabel"]
                ),
                None,
            )
            if profile:
                profile_issues[profile["file"]].append(
                    {"row_number": str(evidence_row["sourceRowNumber"])}
                )
        report_columns = [
            {
                "field": column["name"],
                "label": str(
                    column.get("source_label")
                    or column.get("label")
                    or column["name"].replace("_", " ")
                ),
                "sensitive": bool(
                    column.get("sensitive")
                    or SENSITIVE_NAME_PATTERN.search(column["name"])
                ),
            }
            for column in contract.get("row_columns") or []
        ]
        context_windows = []
        for evidence_row in evidence_rows:
            profile = next(
                (
                    candidate
                    for candidate in report_profiles
                    if export_labels[candidate["file"]] == evidence_row["exportLabel"]
                ),
                None,
            )
            if not profile:
                continue
            header_row = int(profile["schema"].get("header_row_number", 1))
            first_data_row = header_row + 1
            last_data_row = header_row + int(profile["rows"]["source_count"])
            context_windows.append(
                {
                    "id": f"context:{evidence_row['id']}",
                    "findingId": evidence_row["findingId"],
                    "exportLabel": evidence_row["exportLabel"],
                    "focusSourceRowNumber": evidence_row["sourceRowNumber"],
                    "rows": [
                        {
                            "sourceRowNumber": source_row,
                            "state": (
                                "issue"
                                if source_row == evidence_row["sourceRowNumber"]
                                else "context"
                            ),
                            "values": (
                                evidence_row["values"]
                                if source_row == evidence_row["sourceRowNumber"]
                                else []
                            ),
                        }
                        for source_row in range(
                            max(first_data_row, evidence_row["sourceRowNumber"] - 2),
                            min(last_data_row, evidence_row["sourceRowNumber"] + 2) + 1,
                        )
                    ],
                }
            )
        report_context = {
            "mode": "hosted_structure_local_values",
            "statement": (
                "The hosted review shows the complete report schema, every captured export, "
                "row-level issue density, and redacted context windows. Full operational rows "
                "remain available only in the localhost reviewer."
            ),
            "columns": report_columns,
            "exports": [
                {
                    "label": export_labels[profile["file"]],
                    "rowCount": int(profile["rows"]["source_count"]),
                    "headerRowNumber": int(
                        profile["schema"].get("header_row_number", 1)
                    ),
                    "issueObservationCount": len(profile_issues[profile["file"]]),
                    "issueDensity": issue_density(
                        profile, profile_issues[profile["file"]]
                    ),
                }
                for profile in report_profiles
            ],
            "contextWindows": context_windows,
            "localViewerUrl": (
                "http://127.0.0.1:8765/?report_id="
                + report_id
            ),
        }
        matrix_row = selected_by_report.get(report_id)
        alternative = ALTERNATIVE_ROLES.get(report_id)
        selection = (
            {
                "status": "selected",
                "modelRole": matrix_row["model_role"],
                "roleGroup": model_role_group(matrix_row["model_role"]),
                "pages": matrix_row["pages"].split("|"),
                "sourceTable": matrix_row["source_table"],
                "reason": matrix_row["production_decision"],
            }
            if matrix_row
            else {
                "status": "evaluated_not_selected",
                "modelRole": (alternative or {}).get("role", "evaluated"),
                "roleGroup": "evaluated",
                "pages": (alternative or {}).get("pages", []),
                "sourceTable": "",
                "reason": (alternative or {}).get(
                    "reason", "Audited for discovery but not selected for the minimum production source set."
                ),
            }
        )
        report_entries.append(
            {
                "reportId": report_id,
                "displayName": report_profiles[0]["display_name"],
                "selection": selection,
                "filesAudited": len(report_profiles),
                "rowsAudited": row_count,
                "emptyFileCount": empty_file_count,
                "duplicateRowCount": duplicate_count,
                "periods": list(dict.fromkeys(export_labels.values())),
                "schema": {
                    "contractMatch": "exact"
                    if all(profile["schema"]["matches_contract"] for profile in report_profiles)
                    else "difference_detected",
                    "contractVariantCount": len(
                        {
                            tuple(profile["schema"]["observed_header"])
                            for profile in report_profiles
                        }
                    ),
                    **visual_matches[report_id],
                },
                "readiness": (
                    "blocked_header_only"
                    if row_count == 0
                    else (
                        "review_required"
                        if findings
                        or report_id in MANUAL_REVIEW_REPORTS
                        or any(
                            field["coverageStatus"] in {"partial", "weak", "missing"}
                            for field in key_field_coverage
                        )
                        else "schema_ready_value_checks_passed"
                    )
                ),
                "decision": REPORT_DECISIONS.get(
                    report_id,
                    "Schema and deterministic value evidence reviewed; production use follows the selected-source register.",
                ),
                "codexReview": report_review_summary(row_count, findings),
                "keyFieldCoverage": key_field_coverage,
                "findings": findings,
                "evidenceRows": evidence_rows,
                "reportContext": report_context,
            }
        )

    contract = {
        "contractVersion": CONTRACT_VERSION,
        "status": "semantic_evidence_compiled",
        "asOfDate": "2026-07-23",
        "sourcePolicy": (
            "Hosted evidence contains report schemas, export coverage, issue density, "
            "semantic review and redacted context only. Screenshots, full operational rows, "
            "local paths, file names, hashes, credentials, and sensitive values are excluded."
        ),
        "privacy": {
            "rawFilesRemainLocal": True,
            "fullRowsIncluded": False,
            "sensitiveValuesIncluded": False,
            "issueExcerptPolicy": "At most one non-sensitive issue-row excerpt per finding type; surrounding hosted rows are structurally represented but remain redacted.",
        },
        "decision": {
            "headline": "Schemas and encoded arithmetic align; remaining risks are coverage and business treatment.",
            "reason": "Synthetic data remains appropriate for the demonstrator because the actual exports cover one operating scope with uneven periods, two evaluated reports are header-only, PO linkage is sparse, and expiry data is not enabled.",
            "productionRule": "Raw exports remain authoritative evidence. Item and outlet references may use only observed source fields. Vendor identity uses the locally repaired historical Vendor Report with PO and Entry names as transaction-only fallbacks. Unsupported attributes and KPIs remain null or unavailable until an exact source is validated.",
        },
        "zohoReadiness": {
            "demoBuild": "ready",
            "productionModelBuild": "ready_with_gates",
            "productionPublication": "blocked_pending_signoff",
            "requiredLandingTableCount": 14,
            "queryTableCount": 38,
            "dashboardTabCount": 4,
            "migrationRule": "Build v2 in parallel. Do not delete old raw tables before reconciliation, dashboard acceptance, and rollback approval.",
            "nextSequence": [
                "Back up or duplicate the current Zoho workspace.",
                "Import the 10 active RAWN_CT tables and 4 approved model/reference tables with exact names.",
                "Keep Enterprise Stock Return and Enterprise Stock Re-Order outside active landing dependencies; keep expiry visibly synthetic until a batch source exists.",
                "Build the 38 active Query Tables in manifest dependency order.",
                "Validate facts and summaries before building the four pages of saved views.",
                "Train Ask Zia only after dashboard calculations pass.",
            ],
        },
        "summary": {
            "selectedSourceCount": sum(
                1 for item in source_matrix if item["model_role"] not in gated_roles
            ),
            "primarySourceCount": sum(
                1
                for item in source_register
                if item["roleGroup"] == "primary"
                and item["modelRole"] not in gated_roles
            ),
            "auxiliarySourceCount": sum(
                1
                for item in source_register
                if item["roleGroup"] == "auxiliary"
                and item["modelRole"] not in gated_roles
            ),
            "controlSourceCount": sum(
                1
                for item in source_register
                if item["roleGroup"] == "control"
                and item["modelRole"] not in gated_roles
            ),
            "auditedReportCount": len(grouped_profiles),
            "auditedFileCount": len(profiles),
            "auditedRowCount": sum(
                int(profile["rows"]["source_count"]) for profile in profiles
            ),
            "schemaContractMatches": sum(
                1 for profile in profiles if profile["schema"]["matches_contract"]
            ),
            "schemaVisualMatches": len(visual_matches),
            "headerOnlyReportCount": sum(
                1
                for report_profiles in grouped_profiles.values()
                if sum(int(profile["rows"]["source_count"]) for profile in report_profiles) == 0
            ),
            "deterministicIssueRowCount": total_business_issues,
            "semanticFindingCount": sum(len(report["findings"]) for report in report_entries),
            "criticalFindingCount": sum(
                finding["severity"] == "critical"
                for report in report_entries
                for finding in report["findings"]
            ),
            "majorFindingCount": sum(
                finding["severity"] == "major"
                for report in report_entries
                for finding in report["findings"]
            ),
            "minorFindingCount": sum(
                finding["severity"] == "minor"
                for report in report_entries
                for finding in report["findings"]
            ),
            "passedControlCount": int(
                public_business_review.get("summary", {}).get(
                    "passed_control_count", 0
                )
            ),
            "failedControlCount": int(
                public_business_review.get("summary", {}).get(
                    "failed_control_count", 0
                )
            ),
        },
        "businessReview": {
            "contractVersion": public_business_review.get("contract_version", ""),
            "asOfDate": public_business_review.get("as_of_date", ""),
            "summary": public_business_review.get("summary", {}),
            "severityLegend": public_business_review.get("severity_legend", {}),
            "stateLegend": public_business_review.get("state_legend", {}),
            "controls": public_business_review.get("controls", []),
        },
        "sourceRegister": source_register,
        "reportEvidence": report_entries,
    }
    write_json(args.output, contract)
    print(
        f"Wrote {args.output}: {contract['summary']['selectedSourceCount']} active sources, "
        f"{len(report_entries)} audited reports, {total_business_issues} issue rows."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
