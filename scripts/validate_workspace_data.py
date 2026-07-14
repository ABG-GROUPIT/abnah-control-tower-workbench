#!/usr/bin/env python3
"""Validate the editable workspace contract and structural grids."""

from __future__ import annotations

import json
from pathlib import Path


ALLOWED_CELL_KINDS = {"group", "field", "label", "context", "blank"}
ALLOWED_WORKFLOW = {"draft", "in_review", "published"}


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

    if errors:
        print("Workspace validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Workspace validation passed: {len(report_ids)} reports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
