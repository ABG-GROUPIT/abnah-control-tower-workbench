#!/usr/bin/env python3
"""Validate the editable workspace contract and structural grids."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


ALLOWED_CELL_KINDS = {"group", "field", "label", "context", "blank"}
ALLOWED_WORKFLOW = {"draft", "in_review", "published"}
P1_COMPLETION_BASELINE = {
    "catalog_reports": 90,
    "active_reports": 85,
    "archived_reports": 5,
    "schema_statuses": {"captured": 76, "unavailable": 14},
    "active_schema_statuses": {"captured": 76, "unavailable": 9},
    "verification_statuses": {"reviewed": 80, "needs_review": 10},
}
P2_CAPTURE_BASELINE = {
    "catalog_reports": 155,
    "schema_statuses": {"captured": 73, "partial": 3, "pending": 79},
    "verification_statuses": {"reviewed": 76, "needs_review": 79},
    "sections": {
        "01_analytics": {
            "reports": 10,
            "schema_statuses": {"captured": 9, "partial": 1},
            "verification_statuses": {"reviewed": 10},
        },
        "02_attendance": {
            "reports": 2,
            "schema_statuses": {"pending": 2},
            "verification_statuses": {"needs_review": 2},
        },
        "03_audit": {
            "reports": 50,
            "schema_statuses": {"captured": 23, "partial": 2, "pending": 25},
            "verification_statuses": {"reviewed": 25, "needs_review": 25},
        },
        "04_category_item": {
            "reports": 18,
            "schema_statuses": {"captured": 17, "pending": 1},
            "verification_statuses": {"reviewed": 17, "needs_review": 1},
        },
        "07_sales": {
            "reports": 41,
            "schema_statuses": {"captured": 24, "pending": 17},
            "verification_statuses": {"reviewed": 24, "needs_review": 17},
        },
    },
}
P4_CAPTURE_BASELINE = {
    "catalog_reports": 74,
    "schema_statuses": {"captured": 24, "pending": 50},
    "verification_statuses": {"reviewed": 24, "needs_review": 50},
    "sections": {
        "01_enterprise_reports": {"reports": 15, "captured": 15},
        "02_transactional_reports": {"reports": 10, "captured": 6},
        "03_po_so_reports": {"reports": 6, "captured": 1},
        "05_aggregation_reports": {"reports": 7, "captured": 2},
    },
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "schema-pack" / "generated" / "workspace.json"
    workspace = json.loads(path.read_text(encoding="utf-8"))
    lineage_path = root / "schema-pack" / "generated" / "kpi-lineage.json"
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if workspace.get("contractVersion") != "1.0.0":
        errors.append("Unexpected workspace contract version.")
    if "Local screenshots" not in workspace.get("sourcePolicy", ""):
        errors.append("Workspace source policy does not explicitly exclude local screenshots.")
    if lineage.get("contractVersion") != "1.0.0":
        errors.append("Unexpected KPI lineage contract version.")
    for collection in ("kpis", "nodes", "edges", "publications"):
        if not isinstance(lineage.get(collection), list):
            errors.append(f"KPI lineage {collection} must be a list.")
    if "No screenshots" not in lineage.get("sourcePolicy", ""):
        errors.append("KPI lineage source policy does not exclude screenshots.")

    report_ids: set[str] = set()
    for report in workspace.get("reports", []):
        report_id = report.get("id", "")
        if not report_id or report_id in report_ids:
            errors.append(f"Duplicate or empty report id: {report_id}")
        report_ids.add(report_id)
        if report.get("workflowStatus") not in ALLOWED_WORKFLOW:
            errors.append(f"Invalid workflow state for {report_id}.")
        if not isinstance(report.get("fields"), list) or not isinstance(report.get("tables"), list):
            errors.append(f"Missing fields or tables for {report_id}.")
            continue

        field_ids = [field.get("id", "") for field in report["fields"]]
        if len(field_ids) != len(set(field_ids)):
            errors.append(f"Duplicate workspace field id in {report_id}.")

        table_ids: set[str] = set()
        for table in report["tables"]:
            table_id = table.get("id", "")
            if not table_id or table_id in table_ids:
                errors.append(f"Duplicate or empty table id in {report_id}: {table_id}")
            table_ids.add(table_id)
            rows = table.get("rows", 0)
            columns = table.get("columns", 0)
            if not isinstance(rows, int) or not isinstance(columns, int) or rows < 1 or columns < 1:
                errors.append(f"Invalid grid dimensions in {report_id}/{table_id}.")
                continue
            if rows > 500 or columns > 500:
                errors.append(f"Grid exceeds safety limits in {report_id}/{table_id}.")
            if len(table.get("columnWidths", [])) != columns:
                errors.append(f"Column-width count mismatch in {report_id}/{table_id}.")

            occupied: set[tuple[int, int]] = set()
            cell_ids: set[str] = set()
            for cell in table.get("cells", []):
                cell_id = cell.get("id", "")
                if not cell_id or cell_id in cell_ids:
                    errors.append(f"Duplicate or empty cell id in {report_id}/{table_id}.")
                cell_ids.add(cell_id)
                row = cell.get("row", -1)
                column = cell.get("column", -1)
                row_span = cell.get("rowSpan", 0)
                column_span = cell.get("columnSpan", 0)
                if cell.get("kind") not in ALLOWED_CELL_KINDS:
                    errors.append(f"Invalid cell kind in {report_id}/{table_id}/{cell_id}.")
                if min(row, column) < 0 or min(row_span, column_span) < 1:
                    errors.append(f"Invalid cell bounds in {report_id}/{table_id}/{cell_id}.")
                    continue
                if row + row_span > rows or column + column_span > columns:
                    errors.append(f"Cell exceeds grid in {report_id}/{table_id}/{cell_id}.")
                    continue
                for grid_row in range(row, row + row_span):
                    for grid_column in range(column, column + column_span):
                        coordinate = (grid_row, grid_column)
                        if coordinate in occupied:
                            errors.append(f"Overlapping cells in {report_id}/{table_id} at {coordinate}.")
                        occupied.add(coordinate)

    p1_reports = [report for report in workspace.get("reports", []) if report.get("page") == "p1_main"]
    p1_active = [report for report in p1_reports if not report.get("isArchived")]
    p1_archived = [report for report in p1_reports if report.get("isArchived")]
    p1_statuses = Counter(report.get("schemaStatus") for report in p1_reports)
    p1_active_statuses = Counter(report.get("schemaStatus") for report in p1_active)
    p1_verification_statuses = Counter(report.get("verificationStatus") for report in p1_reports)

    if len(p1_reports) != P1_COMPLETION_BASELINE["catalog_reports"]:
        errors.append(
            "P1 catalogue count changed: "
            f"expected {P1_COMPLETION_BASELINE['catalog_reports']}, found {len(p1_reports)}."
        )
    if len(p1_active) != P1_COMPLETION_BASELINE["active_reports"]:
        errors.append(
            "P1 active count changed: "
            f"expected {P1_COMPLETION_BASELINE['active_reports']}, found {len(p1_active)}."
        )
    if len(p1_archived) != P1_COMPLETION_BASELINE["archived_reports"]:
        errors.append(
            "P1 archived count changed: "
            f"expected {P1_COMPLETION_BASELINE['archived_reports']}, found {len(p1_archived)}."
        )
    if p1_statuses != Counter(P1_COMPLETION_BASELINE["schema_statuses"]):
        errors.append(
            "P1 schema-status baseline changed: "
            f"expected {P1_COMPLETION_BASELINE['schema_statuses']}, found {dict(p1_statuses)}."
        )
    if p1_active_statuses != Counter(P1_COMPLETION_BASELINE["active_schema_statuses"]):
        errors.append(
            "P1 active schema-status baseline changed: "
            f"expected {P1_COMPLETION_BASELINE['active_schema_statuses']}, found {dict(p1_active_statuses)}."
        )
    if p1_verification_statuses != Counter(P1_COMPLETION_BASELINE["verification_statuses"]):
        errors.append(
            "P1 verification-status baseline changed: "
            f"expected {P1_COMPLETION_BASELINE['verification_statuses']}, "
            f"found {dict(p1_verification_statuses)}."
        )

    for report in p1_reports:
        report_id = report.get("id", "")
        status = report.get("schemaStatus")
        if status in {"partial", "pending"}:
            errors.append(f"P1 completion regression: {report_id} returned to {status}.")
        if status == "captured" and (not report.get("fields") or not report.get("tables")):
            errors.append(f"Captured P1 report has no usable schema: {report_id}.")
        if status == "unavailable" and not any(note.get("body", "").strip() for note in report.get("notes", [])):
            errors.append(f"Unavailable P1 report needs an evidence reason: {report_id}.")

    p2_reports = [report for report in workspace.get("reports", []) if report.get("page") == "p2_reports"]
    p2_statuses = Counter(report.get("schemaStatus") for report in p2_reports)
    p2_verification_statuses = Counter(report.get("verificationStatus") for report in p2_reports)

    if len(p2_reports) != P2_CAPTURE_BASELINE["catalog_reports"]:
        errors.append(
            "P2 catalogue count changed: "
            f"expected {P2_CAPTURE_BASELINE['catalog_reports']}, found {len(p2_reports)}."
        )
    if p2_statuses != Counter(P2_CAPTURE_BASELINE["schema_statuses"]):
        errors.append(
            "P2 schema-status baseline changed: "
            f"expected {P2_CAPTURE_BASELINE['schema_statuses']}, found {dict(p2_statuses)}."
        )
    if p2_verification_statuses != Counter(P2_CAPTURE_BASELINE["verification_statuses"]):
        errors.append(
            "P2 verification-status baseline changed: "
            f"expected {P2_CAPTURE_BASELINE['verification_statuses']}, "
            f"found {dict(p2_verification_statuses)}."
        )

    for section, baseline in P2_CAPTURE_BASELINE["sections"].items():
        section_reports = [report for report in p2_reports if report.get("section") == section]
        section_statuses = Counter(report.get("schemaStatus") for report in section_reports)
        section_verification_statuses = Counter(
            report.get("verificationStatus") for report in section_reports
        )
        if len(section_reports) != baseline["reports"]:
            errors.append(
                f"P2 {section} count changed: expected {baseline['reports']}, "
                f"found {len(section_reports)}."
            )
        if section_statuses != Counter(baseline["schema_statuses"]):
            errors.append(
                f"P2 {section} schema-status baseline changed: "
                f"expected {baseline['schema_statuses']}, found {dict(section_statuses)}."
            )
        if section_verification_statuses != Counter(baseline["verification_statuses"]):
            errors.append(
                f"P2 {section} verification-status baseline changed: "
                f"expected {baseline['verification_statuses']}, "
                f"found {dict(section_verification_statuses)}."
            )

    for report in p2_reports:
        report_id = report.get("id", "")
        status = report.get("schemaStatus")
        if status in {"captured", "partial"} and (
            not report.get("fields") or not report.get("tables")
        ):
            errors.append(f"Materialized P2 report has no usable schema: {report_id}.")
        if status == "partial" and not any(
            note.get("body", "").strip() for note in report.get("notes", [])
        ):
            errors.append(f"Partial P2 report needs a boundary reason: {report_id}.")

    p4_reports = [report for report in workspace.get("reports", []) if report.get("page") == "p4_stock_admin"]
    p4_statuses = Counter(report.get("schemaStatus") for report in p4_reports)
    p4_verification_statuses = Counter(report.get("verificationStatus") for report in p4_reports)
    if len(p4_reports) != P4_CAPTURE_BASELINE["catalog_reports"]:
        errors.append(
            f"P4 catalogue count changed: expected {P4_CAPTURE_BASELINE['catalog_reports']}, "
            f"found {len(p4_reports)}."
        )
    if p4_statuses != Counter(P4_CAPTURE_BASELINE["schema_statuses"]):
        errors.append(
            f"P4 schema-status baseline changed: expected {P4_CAPTURE_BASELINE['schema_statuses']}, "
            f"found {dict(p4_statuses)}."
        )
    if p4_verification_statuses != Counter(P4_CAPTURE_BASELINE["verification_statuses"]):
        errors.append(
            "P4 verification-status baseline changed: "
            f"expected {P4_CAPTURE_BASELINE['verification_statuses']}, "
            f"found {dict(p4_verification_statuses)}."
        )
    for section, baseline in P4_CAPTURE_BASELINE["sections"].items():
        section_reports = [report for report in p4_reports if report.get("section") == section]
        captured = [report for report in section_reports if report.get("schemaStatus") == "captured"]
        if len(section_reports) != baseline["reports"] or len(captured) != baseline["captured"]:
            errors.append(
                f"P4 {section} baseline changed: expected {baseline}, "
                f"found reports={len(section_reports)}, captured={len(captured)}."
            )
    for report in p4_reports:
        if report.get("schemaStatus") == "captured" and (
            not report.get("fields") or not report.get("tables")
        ):
            errors.append(f"Captured P4 report has no usable schema: {report.get('id', '')}.")

    report_lookup = {report.get("id", ""): report for report in workspace.get("reports", [])}
    enterprise_consumption = report_lookup.get(
        "report:p4_stock_admin:01_enterprise_reports:04_enterprise_consumption", {}
    )
    enterprise_keys = {field.get("key") for field in enterprise_consumption.get("fields", [])}
    required_positional_keys = {
        "purchase_qty", "purchase_amount", "consumption_qty", "consumption_amount",
        "closing_qty", "closing_amount", "physical_adjusted_closing_qty",
        "physical_adjusted_closing_amount",
    }
    if not required_positional_keys.issubset(enterprise_keys):
        errors.append("Enterprise Consumption lost one or more position-aware quantity/amount keys.")
    consumption_modes = report_lookup.get(
        "report:p4_stock_admin:05_aggregation_reports:02_consumption_report", {}
    )
    if len(consumption_modes.get("tables", [])) != 4:
        errors.append("Consumption Report must retain four separately modelled report modes.")
    margin_report = report_lookup.get("report:p2_reports:07_sales:33_food_sold_report", {})
    if margin_report.get("name") != "Gross/Net Margin Report" or len(margin_report.get("fields", [])) != 26:
        errors.append("Gross/Net Margin Report alias or 26-field schema is missing.")

    if errors:
        print("Workspace validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Workspace validation passed: {len(report_ids)} reports.")
    print("P1 completion guard passed: 76 captured, 14 unavailable, 80 reviewed, 0 partial, 0 pending.")
    print("P2 capture guard passed: 73 captured, 3 partial, 76 reviewed, 79 pending.")
    print("P4 capture guard passed: 24 captured, 24 reviewed, 50 pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
