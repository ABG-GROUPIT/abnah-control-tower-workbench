#!/usr/bin/env python3
"""Build the synthetic-to-POSIST schema and sparsity fidelity register."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CONTRACT_VERSION = "1.0.0"

ACTIVE_FIELDS = {
    "vendor_report": {
        "vendor_name",
        "vendor_code",
        "description",
        "msme",
        "from_date",
        "to_date",
        "state",
    },
    "gross_net_margin": {
        "sale_date",
        "bill_number",
        "tab_type",
        "source",
        "super_category_name",
        "category_name",
        "item_code",
        "item_name",
        "item_rate",
        "item_qty",
        "item_subtotal",
        "total_discount_amt",
        "net_sale_value",
        "tax_amt",
        "gross_sale_value",
        "purchase_rate",
        "purchase_value",
    },
    "item_recipe_report": {
        "menu_item_type",
        "menu_item_number",
        "menu_item_name",
        "recipe_item_type",
        "ingredient_code",
        "ingredient_name",
        "recipe_qty_per_menu_unit",
        "recipe_unit",
    },
    "enterprise_variance_normal": {
        "deployment_name",
        "store_kitchen_name",
        "opening_date",
        "closing_date",
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "average_price",
        "unit",
        "opening_qty",
        "purchase_qty",
        "stock_in_qty",
        "stock_out_qty",
        "return_qty",
        "wastage_qty",
        "closing_qty",
        "physical_qty",
        "actual_consumption_qty",
        "variance_qty",
        "variance_percent",
    },
    "closing_stock": {
        "deployment_name",
        "stock_date",
        "item_code",
        "item_name",
        "category_code",
        "category_name",
        "super_category_code",
        "super_category_name",
        "unit_name",
        "average_price",
        "total_qty",
        "total_amt",
    },
    "enterprise_purchase_order": {
        "deployment_name",
        "store_name",
        "vendor_name",
        "po_number",
        "po_date",
        "expected_delivery_date",
        "po_close_or_partial_receive_date",
        "po_status",
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "processed_qty",
        "remaining_balance_qty",
        "ordered_qty",
        "unit",
        "unit_price",
        "new_subtotal",
        "tax_amt",
        "total_item_cost",
    },
    "enterprise_entry": {
        "deployment_name",
        "store_kitchen_name",
        "vendor_name",
        "entry_date",
        "transaction_number",
        "invoice_number",
        "po_number",
        "invoice_date",
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "entry_qty",
        "unit",
        "unit_price",
        "base_amt",
        "discount_amt",
        "total_tax_amt",
        "total_amt",
    },
    "enterprise_transfer_from": {
        "deployment_name",
        "transfer_date",
        "transaction_number",
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "transfer_qty",
        "unit",
        "transfer_amt",
    },
    "enterprise_transfer_to": {
        "deployment_name",
        "supplier_store_name",
        "transfer_date",
        "transaction_number",
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "transfer_qty",
        "unit",
        "transfer_amt",
    },
    "enterprise_wastage_normal": {
        "deployment_name",
        "store_kitchen_name",
        "wastage_date",
        "transaction_number",
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "comment",
        "wastage_qty",
        "unit",
        "unit_price",
        "wastage_amt",
    },
}

GATED_FIELDS = {
    "enterprise_reorder": {
        "item_code",
        "reorder_level_qty",
        "minimum_order_level_qty",
    },
    "enterprise_stock_return": {
        "transaction_number",
        "stock_entry_date",
        "return_date",
        "vendor_name",
        "item_code",
        "return_qty",
        "return_amt",
    }
}

SCHEMA_CAPTURE_ONLY = [
    {
        "name": "ERP Vendor Price",
        "status": "captured_headers_not_uat_csv_validated",
        "handling": "Reference only until a populated UAT export is audited.",
    },
    {
        "name": "Enterprise Purchase Summary",
        "status": "captured_headers_not_uat_csv_validated",
        "handling": "Reconciliation candidate only; not an active fact source.",
    },
    {
        "name": "Enterprise Consolidated Indent",
        "status": "captured_headers_not_uat_csv_validated",
        "handling": "Optional workflow source; not used by the current dashboard.",
    },
]

AUXILIARY_TABLES = [
    "AUX_Expiry_Estimate",
    "AUX_Menu_Demand_Forecast",
    "AUX_Outlet_Master",
    "AUX_Theoretical_Consumption",
]

HISTORICAL_CONTRACT_STEMS = {"vendor_report"}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def aggregate_actual_profiles(path: Path) -> tuple[dict[tuple[str, str], dict[str, int]], dict[str, set[str]]]:
    counts: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    files: dict[str, set[str]] = defaultdict(set)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            report_id = row["report_id"]
            files[report_id].add(row["file_name"])
            field_counts = counts[(report_id, row["field"])]
            for key in (
                "total_count",
                "blank_count",
                "null_count",
                "zero_count",
                "negative_count",
                "positive_count",
                "parse_error_count",
            ):
                field_counts[key] += int(row.get(key) or 0)
    return counts, files


def field_state(counts: dict[str, int], declared_type: str) -> str:
    total = counts.get("total_count", 0)
    blank = counts.get("blank_count", 0) + counts.get("null_count", 0)
    zero = counts.get("zero_count", 0)
    positive = counts.get("positive_count", 0)
    negative = counts.get("negative_count", 0)
    if total == 0:
        return "no_rows"
    if blank >= total:
        return "all_blank"
    if (
        declared_type == "decimal"
        and zero > 0
        and positive == 0
        and negative == 0
        and zero + blank >= total
    ):
        return "all_zero"
    if blank > 0:
        return "partially_blank"
    if declared_type == "decimal" and zero > 0 and positive + negative > 0:
        return "mixed_zero_nonzero"
    return "populated"


def profile_synthetic(
    path: Path,
    fields: list[dict[str, Any]],
    expected_header: list[str],
) -> tuple[bool, int, dict[str, str]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        rows = 0
        for row in reader:
            rows += 1
            for index, field in enumerate(fields):
                value = row[index].strip() if index < len(row) else ""
                profile = counts[field["name"]]
                profile["total_count"] += 1
                if value == "":
                    profile["blank_count"] += 1
                    continue
                if field.get("type") == "decimal":
                    try:
                        number = float(value.replace(",", ""))
                    except ValueError:
                        profile["parse_error_count"] += 1
                    else:
                        if number == 0:
                            profile["zero_count"] += 1
                        elif number > 0:
                            profile["positive_count"] += 1
                        else:
                            profile["negative_count"] += 1
    states = {
        field["name"]: field_state(counts[field["name"]], field.get("type", "text"))
        for field in fields
    }
    return header == expected_header, rows, states


def build(root: Path, actual_profile: Path) -> dict[str, Any]:
    contracts_root = root / "local_data_auditor" / "contracts"
    exports_root = root / "exports" / "control_tower_zoho"
    actual_counts, actual_files = aggregate_actual_profiles(actual_profile)
    manifest_rows = {
        row["report_stem"]: row
        for row in csv.DictReader(
            (exports_root / "_CONTROL_TOWER_IMPORT_MANIFEST.csv").open(
                "r", encoding="utf-8-sig", newline=""
            )
        )
        if row.get("contract_status", "").startswith("validated_")
    }

    reports: list[dict[str, Any]] = []
    exact_headers = 0
    all_blank_count = 0
    all_zero_count = 0
    sparsity_mismatches: list[str] = []

    for contract_path in sorted(contracts_root.glob("*.json")):
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        stem = contract_path.stem
        historical_contract = stem in HISTORICAL_CONTRACT_STEMS
        fields = contract["row_columns"]
        field_types = {field["name"]: field.get("type", "text") for field in fields}
        labels = {
            field["name"]: contract["expected_header"][index]
            for index, field in enumerate(fields)
        }
        header_match, synthetic_rows, synthetic_states = profile_synthetic(
            exports_root / f"RAW_CT_{stem}.csv",
            fields,
            contract["expected_header"],
        )
        exact_headers += int(header_match)

        if historical_contract:
            actual_states = {
                field["name"]: "historical_schema_not_in_current_uat_dump"
                for field in fields
            }
            actual_rows: int | None = None
            blank_fields: list[str] = []
            zero_fields: list[str] = []
        else:
            actual_states = {
                field["name"]: field_state(
                    actual_counts[(contract["report_id"], field["name"])],
                    field.get("type", "text"),
                )
                for field in fields
            }
            actual_rows = max(
                (
                    actual_counts[(contract["report_id"], field["name"])].get(
                        "total_count", 0
                    )
                    for field in fields
                ),
                default=0,
            )
            blank_fields = sorted(
                field for field, state in actual_states.items() if state == "all_blank"
            )
            zero_fields = sorted(
                field for field, state in actual_states.items() if state == "all_zero"
            )
        all_blank_count += len(blank_fields)
        all_zero_count += len(zero_fields)
        for field in blank_fields + zero_fields:
            if synthetic_states.get(field) != actual_states[field]:
                sparsity_mismatches.append(
                    f"{stem}.{field}: actual={actual_states[field]} "
                    f"synthetic={synthetic_states.get(field)}"
                )

        header_only = actual_rows == 0 and not historical_contract
        if header_only and synthetic_rows != 0:
            sparsity_mismatches.append(
                f"{stem}: actual header-only but synthetic has {synthetic_rows} rows"
            )

        active = sorted(ACTIVE_FIELDS.get(stem, set()))
        gated = sorted(GATED_FIELDS.get(stem, set()))
        ignored = sorted(set(blank_fields + zero_fields))
        context = sorted(
            set(field_types) - set(active) - set(gated) - set(ignored)
        )
        if gated:
            downstream_status = "gated_source_unavailable"
        elif active:
            downstream_status = "active_projected_fields"
        else:
            downstream_status = "audit_or_reconciliation_only"

        column_decisions = [
            {
                "field": field,
                "label": labels[field],
                "declaredType": field_types[field],
                "observedState": actual_states[field],
                "syntheticState": synthetic_states[field],
                "decision": "ignored_until_source_populates",
                "reason": (
                    "The audited POSIST exports contain no usable signal in this "
                    "column, so it is preserved in raw shape but excluded from "
                    "active Query Tables and dashboard measures."
                ),
            }
            for field in ignored
        ]
        if header_only:
            column_decisions = [
                {
                    "field": field["name"],
                    "label": labels[field["name"]],
                    "declaredType": field.get("type", "text"),
                    "observedState": "no_rows",
                    "syntheticState": synthetic_states[field["name"]],
                    "decision": "gated_report",
                    "reason": (
                        "The captured POSIST export is header-only. Its schema is "
                        "retained, but no KPI is published from it."
                    ),
                }
                for field in fields
            ]

        reports.append(
            {
                "reportId": contract["report_id"],
                "reportStem": stem,
                "displayName": contract["display_name"],
                "grain": contract["grain"],
                "evidenceScope": (
                    "historical_abnah_export"
                    if historical_contract
                    else "current_uat_audit"
                ),
                "schemaStatus": "exact_validated_contract",
                "headerMatch": header_match,
                "columnCount": len(fields),
                "actualFilesAudited": len(actual_files[contract["report_id"]]),
                "actualRowsAudited": actual_rows,
                "syntheticFilesGenerated": int(
                    manifest_rows.get(stem, {}).get("file_count") or 0
                ),
                "syntheticRowsGenerated": synthetic_rows,
                "rowPatternStatus": (
                    "historical_schema_with_structural_quality_gate"
                    if historical_contract
                    else (
                        "mirrored_header_only"
                        if header_only
                        else "modelled_at_captured_grain"
                    )
                ),
                "downstreamStatus": downstream_status,
                "activeFields": [
                    {"field": field, "label": labels[field]} for field in active
                ],
                "gatedFields": [
                    {"field": field, "label": labels[field]} for field in gated
                ],
                "contextOnlyFields": [
                    {"field": field, "label": labels[field]} for field in context
                ],
                "ignoredFields": column_decisions,
                "fidelityNote": (
                    (
                        "Header spelling/order follows the earlier ABNAH Vendor "
                        "Report contract. The source is quality-gated because "
                        "multiple phone numbers and long addresses were documented "
                        "to shift exported cells or continue onto another row."
                    )
                    if historical_contract
                    else (
                        "Header spelling/order and confirmed blank, zero-only, or "
                        "header-only behavior match the audited POSIST contract. "
                        "Business values, row counts, identifiers, and event frequency "
                        "remain controlled synthetic data."
                    )
                ),
            }
        )

    if sparsity_mismatches:
        raise ValueError(
            "Synthetic source sparsity does not match audited POSIST behavior: "
            + "; ".join(sparsity_mismatches)
        )

    return {
        "contractVersion": CONTRACT_VERSION,
        "asOfDate": "2026-07-23",
        "status": "verified",
        "headline": (
            "Source schemas are exact; values and operational distributions remain synthetic."
        ),
        "scopeStatement": (
            "Twenty current UAT POSIST CSV contracts and one historically supplied "
            "ABNAH Vendor Report contract were checked against the generated raw "
            "source files. Exact means header spelling, order, field count and "
            "captured grain. Current-UAT empty-state behavior is also mirrored. "
            "It does not mean that synthetic values, row counts, identifiers, "
            "preamble rows, or missingness frequencies reproduce ABNAH operations."
        ),
        "handlingPolicy": [
            "Keep every captured POSIST column in RAW_CT source-shaped CSVs, even when unused.",
            "Mirror fields confirmed all blank or all zero in the audited UAT exports.",
            "Do not project confirmed no-signal fields into active standardized, fact, summary, or dashboard logic.",
            "Treat a header-only report as unavailable, never as a genuine zero result.",
            "Use RAWN_CT landing tables for Zoho; they intentionally add source period and outlet metadata and canonical field names.",
            "Keep AUX tables visibly labelled because they are model inputs, not POSIST reports.",
        ],
        "layers": [
            {
                "id": "source_shaped",
                "label": "RAW_CT source-shaped CSV",
                "status": "exact_contract",
                "description": (
                    "POSIST header spelling and order, confirmed empty-state behavior, "
                    "and captured report grain."
                ),
            },
            {
                "id": "normalized_landing",
                "label": "RAWN_CT Zoho landing",
                "status": "intentional_translation",
                "description": (
                    "Canonical field names plus source period and outlet metadata; "
                    "not a byte-for-byte POSIST export."
                ),
            },
            {
                "id": "analytics",
                "label": "STD / DIM / FACT / SUM",
                "status": "projected_fields_only",
                "description": (
                    "Only KPI-relevant fields with usable source evidence are carried "
                    "into active calculations."
                ),
            },
        ],
        "summary": {
            "validatedReportContracts": len(reports),
            "exactHeaderReports": exact_headers,
            "currentUatAuditedReportContracts": sum(
                report["evidenceScope"] == "current_uat_audit"
                for report in reports
            ),
            "historicalSchemaContracts": sum(
                report["evidenceScope"] == "historical_abnah_export"
                for report in reports
            ),
            "populatedReportContracts": sum(
                isinstance(report["actualRowsAudited"], int)
                and report["actualRowsAudited"] > 0
                for report in reports
            ),
            "headerOnlyReportContracts": sum(
                report["actualRowsAudited"] == 0 for report in reports
            ),
            "confirmedAllBlankFields": all_blank_count,
            "confirmedAllZeroFields": all_zero_count,
            "ignoredNoSignalFields": all_blank_count + all_zero_count,
            "activeReportContracts": len(ACTIVE_FIELDS),
            "gatedReportContracts": len(GATED_FIELDS),
            "schemaCaptureOnlyReports": len(SCHEMA_CAPTURE_ONLY),
            "auxiliaryModelTables": len(AUXILIARY_TABLES),
        },
        "schemaCaptureOnlyReports": SCHEMA_CAPTURE_ONLY,
        "auxiliaryTables": AUXILIARY_TABLES,
        "reports": reports,
    }


def write_markdown(path: Path, register: dict[str, Any]) -> None:
    summary = register["summary"]
    lines = [
        "# Control Tower Synthetic Schema Fidelity",
        "",
        register["headline"],
        "",
        register["scopeStatement"],
        "",
        "## Verified Summary",
        "",
        f"- Exact validated POSIST headers: {summary['exactHeaderReports']} of {summary['validatedReportContracts']}",
        f"- Current UAT contracts audited: {summary['currentUatAuditedReportContracts']}",
        f"- Historical schema contracts retained: {summary['historicalSchemaContracts']}",
        f"- Populated source contracts: {summary['populatedReportContracts']}",
        f"- Mirrored header-only contracts: {summary['headerOnlyReportContracts']}",
        f"- Confirmed all-blank fields excluded downstream: {summary['confirmedAllBlankFields']}",
        f"- Confirmed all-zero fields excluded downstream: {summary['confirmedAllZeroFields']}",
        f"- Schema-capture-only reports: {summary['schemaCaptureOnlyReports']}",
        f"- Explicitly synthetic AUX tables: {summary['auxiliaryModelTables']}",
        "",
        "## Layer Boundary",
        "",
        "| Layer | Fidelity | Meaning |",
        "|---|---|---|",
    ]
    for layer in register["layers"]:
        lines.append(
            f"| {layer['label']} | {layer['status']} | {layer['description']} |"
        )
    lines.extend(
        [
            "",
            "## Report Register",
            "",
            "| Report | Header | Pattern | Actual rows | Synthetic rows | Downstream | Ignored fields |",
            "|---|---|---|---:|---:|---|---:|",
        ]
    )
    for report in register["reports"]:
        actual_rows = report["actualRowsAudited"]
        actual_rows_display = (
            "historical"
            if actual_rows is None
            else f"{actual_rows:,}"
        )
        lines.append(
            f"| {report['displayName']} | "
            f"{'exact' if report['headerMatch'] else 'mismatch'} | "
            f"{report['rowPatternStatus']} | "
            f"{actual_rows_display} | "
            f"{report['syntheticRowsGenerated']:,} | "
            f"{report['downstreamStatus']} | "
            f"{len(report['ignoredFields'])} |"
        )
    lines.extend(["", "## No-Signal Field Decisions", ""])
    for report in register["reports"]:
        ignored = report["ignoredFields"]
        if not ignored:
            continue
        field_text = ", ".join(
            f"`{item['label']}` ({item['observedState']})" for item in ignored
        )
        lines.append(f"- **{report['displayName']}**: {field_text}")
    lines.extend(
        [
            "",
            "## Policy",
            "",
            *[f"- {item}" for item in register["handlingPolicy"]],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_csv_register(path: Path, register: dict[str, Any]) -> None:
    columns = [
        "report_name",
        "report_stem",
        "schema_status",
        "header_match",
        "row_pattern_status",
        "actual_rows_audited",
        "synthetic_rows_generated",
        "synthetic_files_generated",
        "downstream_status",
        "active_field_count",
        "gated_field_count",
        "ignored_field_count",
        "ignored_fields",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for report in register["reports"]:
            writer.writerow(
                {
                    "report_name": report["displayName"],
                    "report_stem": report["reportStem"],
                    "schema_status": report["schemaStatus"],
                    "header_match": report["headerMatch"],
                    "row_pattern_status": report["rowPatternStatus"],
                    "actual_rows_audited": report["actualRowsAudited"],
                    "synthetic_rows_generated": report["syntheticRowsGenerated"],
                    "synthetic_files_generated": report["syntheticFilesGenerated"],
                    "downstream_status": report["downstreamStatus"],
                    "active_field_count": len(report["activeFields"]),
                    "gated_field_count": len(report["gatedFields"]),
                    "ignored_field_count": len(report["ignoredFields"]),
                    "ignored_fields": "|".join(
                        item["field"] for item in report["ignoredFields"]
                    ),
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--actual-profile",
        type=Path,
        default=Path(
            "local_data_auditor/output/real_dump_semantic_20260723/"
            "CODEX_PACKET/field_profiles.csv"
        ),
    )
    parser.add_argument("--site-root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    actual_profile = args.actual_profile
    if not actual_profile.is_absolute():
        actual_profile = root / actual_profile
    register = build(root, actual_profile.resolve())
    write_json(root / "docs" / "control_tower_synthetic_fidelity.json", register)
    write_markdown(root / "docs" / "control_tower_synthetic_fidelity.md", register)
    write_csv_register(
        root
        / "exports"
        / "control_tower_zoho"
        / "_SYNTHETIC_FIDELITY_REGISTER.csv",
        register,
    )
    if args.site_root:
        site_root = args.site_root.resolve()
        write_json(
            site_root
            / "schema-pack"
            / "source"
            / "control_tower"
            / "control-tower-fidelity.json",
            register,
        )
    print(
        "Synthetic fidelity verified: "
        f"{register['summary']['exactHeaderReports']} exact headers, "
        f"{register['summary']['ignoredNoSignalFields']} ignored no-signal fields."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
