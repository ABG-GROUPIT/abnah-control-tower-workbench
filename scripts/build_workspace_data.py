#!/usr/bin/env python3
"""Compile report schema blueprints into the editable workspace contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable


CONTRACT_VERSION = "1.0.0"
SOURCE_POLICY = "Schema definitions only. Local screenshots, paths, and source images are excluded."


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "field"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def node_depth(node: dict[str, Any]) -> int:
    children = node.get("children") or []
    return 1 + max((node_depth(child) for child in children), default=0)


def leaf_count(node: dict[str, Any]) -> int:
    children = node.get("children") or []
    return sum(leaf_count(child) for child in children) if children else 1


def table_cell(
    table_id: str,
    index: int,
    row: int,
    column: int,
    text: str,
    kind: str,
    row_span: int = 1,
    column_span: int = 1,
    field_id: str | None = None,
) -> dict[str, Any]:
    cell = {
        "id": f"{table_id}:cell:{index}",
        "row": row,
        "column": column,
        "rowSpan": row_span,
        "columnSpan": column_span,
        "text": text,
        "kind": kind,
    }
    if field_id:
        cell["fieldId"] = field_id
    return cell


def compile_column_tree(block: dict[str, Any]) -> dict[str, Any]:
    table_id = block["id"]
    columns = block.get("columns") or []
    if not columns:
        return compile_grid({"id": table_id, "name": block.get("name", "Table"), "rows": 1, "columns": 1, "cells": []})

    depth = max(node_depth(node) for node in columns)
    total_columns = sum(leaf_count(node) for node in columns)
    cells: list[dict[str, Any]] = []
    widths: list[int] = []

    def place(node: dict[str, Any], row: int, column: int) -> int:
        children = node.get("children") or []
        span = leaf_count(node)
        field_id = node.get("key") or slug(node.get("label", ""))
        cells.append(
            table_cell(
                table_id,
                len(cells),
                row,
                column,
                node.get("label", ""),
                "group" if children else "field",
                1 if children else depth - row,
                span,
                None if children else field_id,
            )
        )
        if children:
            child_column = column
            for child in children:
                child_column += place(child, row + 1, child_column)
        else:
            widths.append(max(96, min(320, int(node.get("width", 150)))))
        return span

    cursor = 0
    for column in columns:
        cursor += place(column, 0, cursor)

    body_rows = max(0, min(12, int(block.get("body_rows", 1))))
    for row in range(depth, depth + body_rows):
        for column in range(total_columns):
            cells.append(table_cell(table_id, len(cells), row, column, "", "blank"))

    return {
        "id": table_id,
        "name": block.get("name", "Report table"),
        "rows": depth + body_rows,
        "columns": total_columns,
        "columnWidths": widths,
        "cells": cells,
    }


def compile_key_value(block: dict[str, Any]) -> dict[str, Any]:
    table_id = block["id"]
    entries = block.get("entries") or []
    cells: list[dict[str, Any]] = []
    for row, entry in enumerate(entries):
        item = entry if isinstance(entry, dict) else {"label": str(entry)}
        key = item.get("key") or slug(item.get("label", ""))
        cells.append(table_cell(table_id, len(cells), row, 0, item.get("label", ""), "field", field_id=key))
        cells.append(table_cell(table_id, len(cells), row, 1, "", "blank"))
    return {
        "id": table_id,
        "name": block.get("name", "Summary measures"),
        "rows": max(1, len(entries)),
        "columns": 2,
        "columnWidths": [220, 140],
        "cells": cells,
    }


def compile_matrix(block: dict[str, Any]) -> dict[str, Any]:
    table_id = block["id"]
    row_headers = block.get("row_headers") or ["Group", "Metric"]
    value_columns = block.get("value_columns") or [{"label": "Value", "key": "value"}]
    groups = block.get("row_groups") or []
    header_depth = max(node_depth(node) for node in value_columns)
    value_leaf_count = sum(leaf_count(node) for node in value_columns)
    cells: list[dict[str, Any]] = []

    for column, label in enumerate(row_headers):
        cells.append(
            table_cell(
                table_id,
                len(cells),
                0,
                column,
                label,
                "context",
                header_depth,
                1,
                slug(label),
            )
        )

    def place_value(node: dict[str, Any], row: int, column: int) -> int:
        children = node.get("children") or []
        span = leaf_count(node)
        field_id = node.get("key") or slug(node.get("label", ""))
        cells.append(
            table_cell(
                table_id,
                len(cells),
                row,
                column,
                node.get("label", ""),
                "group" if children else "field",
                1 if children else header_depth - row,
                span,
                None if children else field_id,
            )
        )
        if children:
            child_column = column
            for child in children:
                child_column += place_value(child, row + 1, child_column)
        return span

    cursor = len(row_headers)
    for node in value_columns:
        cursor += place_value(node, 0, cursor)

    row_cursor = header_depth
    for group in groups:
        metrics = group.get("metrics") or []
        if not metrics:
            continue
        cells.append(
            table_cell(
                table_id,
                len(cells),
                row_cursor,
                0,
                group.get("label", ""),
                "group",
                len(metrics),
            )
        )
        for offset, metric in enumerate(metrics):
            item = metric if isinstance(metric, dict) else {"label": str(metric)}
            row = row_cursor + offset
            key = item.get("key") or slug(item.get("label", ""))
            cells.append(table_cell(table_id, len(cells), row, 1, item.get("label", ""), "field", field_id=key))
            for value_column in range(value_leaf_count):
                cells.append(table_cell(table_id, len(cells), row, len(row_headers) + value_column, "", "blank"))
        row_cursor += len(metrics)

    return {
        "id": table_id,
        "name": block.get("name", "Matrix"),
        "rows": max(1, row_cursor),
        "columns": len(row_headers) + value_leaf_count,
        "columnWidths": [180, 190] + [150] * value_leaf_count,
        "cells": cells,
    }


def compile_grid(block: dict[str, Any]) -> dict[str, Any]:
    table_id = block["id"]
    cells = []
    for index, source in enumerate(block.get("cells") or []):
        cells.append(
            table_cell(
                table_id,
                index,
                int(source.get("row", 0)),
                int(source.get("column", 0)),
                source.get("text", ""),
                source.get("kind", "blank"),
                int(source.get("rowSpan", 1)),
                int(source.get("columnSpan", 1)),
                source.get("fieldId"),
            )
        )
    rows = max(1, int(block.get("rows", 1)))
    columns = max(1, int(block.get("columns", 1)))
    widths = [max(72, min(420, int(value))) for value in block.get("column_widths", [])]
    widths.extend([150] * (columns - len(widths)))
    return {
        "id": table_id,
        "name": block.get("name", "Freeform structure"),
        "rows": rows,
        "columns": columns,
        "columnWidths": widths[:columns],
        "cells": cells,
    }


def compile_block(block: dict[str, Any]) -> dict[str, Any]:
    kind = block.get("kind", "column_tree")
    if kind in {"flat_table", "column_tree"}:
        return compile_column_tree(block)
    if kind == "matrix":
        return compile_matrix(block)
    if kind == "key_value":
        return compile_key_value(block)
    if kind == "grid":
        return compile_grid(block)
    raise ValueError(f"Unsupported structure block kind: {kind}")


def column_leaves(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    leaves: list[dict[str, str]] = []
    for node in nodes:
        children = node.get("children") or []
        if children:
            leaves.extend(column_leaves(children))
        else:
            label = node.get("label", "")
            leaves.append({"key": node.get("key") or slug(label), "label": label})
    return leaves


def derive_points(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    if blueprint.get("data_points"):
        raw_points = blueprint["data_points"]
    else:
        raw_points = []
        for block in blueprint.get("blocks") or []:
            if block.get("kind") in {"flat_table", "column_tree"}:
                raw_points.extend(column_leaves(block.get("columns") or []))
            elif block.get("kind") == "key_value":
                for entry in block.get("entries") or []:
                    item = entry if isinstance(entry, dict) else {"label": str(entry)}
                    raw_points.append({"key": item.get("key") or slug(item.get("label", "")), "label": item.get("label", "")})

    points: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, source in enumerate(raw_points):
        item = source if isinstance(source, dict) else {"label": str(source)}
        key = item.get("key") or slug(item.get("label", ""))
        if key in seen:
            continue
        seen.add(key)
        points.append(
            {
                "id": f"workspace-field:{blueprint['report_id']}:{key}",
                "key": key,
                "label": item.get("label", key.replace("_", " ").title()),
                "semanticRole": item.get("semantic_role", "unknown"),
                "dataType": item.get("data_type", "unknown"),
                "status": item.get("status", "captured"),
                "notes": item.get("notes", ""),
                "order": index,
            }
        )
    return points


def default_document(report: dict[str, Any], fields: dict[str, dict[str, Any]], endpoints: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report_fields = [fields[field_id] for field_id in report.get("field_ids", []) if field_id in fields]
    has_legacy_ocr_candidates = any(field.get("status") == "ocr_candidate" for field in report_fields)
    points = [
        {
            "id": f"workspace-field:{report['id']}:{field['name']}",
            "key": field["name"],
            "label": field["label"],
            "semanticRole": (field.get("semantic_roles") or ["unknown"])[0],
            "dataType": (field.get("data_type_guesses") or ["unknown"])[0],
            "status": "needs_review" if field.get("status") == "ocr_candidate" else "captured",
            "notes": "Legacy OCR-derived candidate; verify structural placement before publication." if field.get("status") == "ocr_candidate" else "",
        }
        for field in report_fields
    ]
    if points:
        block = {
            "id": "primary",
            "name": "Report schema",
            "kind": "flat_table",
            "columns": [{"label": point["label"], "key": point["key"]} for point in points],
        }
        tables = [compile_block(block)]
        schema_status = "partial" if has_legacy_ocr_candidates else "captured"
    else:
        tables = [compile_grid({"id": "primary", "name": "Schema pending", "rows": 1, "columns": 1, "cells": []})]
        schema_status = "pending"

    api_tests = []
    for api_id in report.get("api_links", []):
        endpoint = endpoints.get(api_id)
        if not endpoint:
            continue
        api_tests.append(
            {
                "id": f"api-test:{slug(report['id'])}:{slug(api_id)}",
                "endpointId": api_id,
                "endpointName": endpoint.get("endpoint_name", api_id),
                "method": endpoint.get("method", "GET"),
                "path": endpoint.get("path", ""),
                "testType": "availability",
                "status": "not_tested",
                "result": "",
                "errorType": "",
                "notes": "Documented candidate only; ABNAH UAT not tested.",
                "testedAt": "",
            }
        )

    return {
        "id": report["id"],
        "name": report["name"],
        "page": report["page"],
        "section": report["section"],
        "domain": report["domain"],
        "priority": report["priority"],
        "schemaStatus": schema_status,
        "verificationStatus": "needs_review",
        "layoutKind": "flat",
        "captureMethod": report.get("capture_method", ""),
        "sourcePolicy": SOURCE_POLICY,
        "workflowStatus": "published",
        "version": 0,
        "isArchived": False,
        "isCustom": False,
        "fields": points,
        "tables": tables,
        "apiTests": api_tests,
        "notes": [],
        "updatedAt": "",
        "updatedBy": "generated baseline",
    }


def apply_blueprint(document: dict[str, Any], blueprint: dict[str, Any]) -> dict[str, Any]:
    result = dict(document)
    result.update(
        {
            "schemaStatus": blueprint.get("schema_status", result["schemaStatus"]),
            "verificationStatus": blueprint.get("verification_status", "needs_review"),
            "layoutKind": blueprint.get("layout_kind", result["layoutKind"]),
            "captureMethod": blueprint.get("capture_method", "manual_schema_reconstruction"),
            "fields": derive_points(blueprint),
            "tables": [compile_block(block) for block in blueprint.get("blocks") or []],
        }
    )
    if not result["tables"]:
        result["tables"] = document["tables"]
    note = blueprint.get("structure_notes", "").strip()
    if note:
        result["notes"] = [
            {
                "id": f"source-note:{slug(result['id'])}",
                "category": "source",
                "body": note,
                "author": "schema reconstruction",
                "createdAt": "",
            }
        ]
    return result


def build(root: Path) -> dict[str, Any]:
    generated_root = root / "schema-pack" / "generated"
    blueprint_root = root / "schema-pack" / "source" / "report_structures"
    lineage_source = root / "schema-pack" / "source" / "kpi_lineage" / "kpi-lineage.json"
    atlas = json.loads((generated_root / "atlas.json").read_text(encoding="utf-8"))
    fields = {item["id"]: item for item in atlas["fields"]}
    endpoints = {item["id"]: item for item in atlas["api_endpoints"]}
    reports = {item["id"]: default_document(item, fields, endpoints) for item in atlas["reports"]}

    source_files: list[dict[str, str]] = []
    status_overrides: dict[str, dict[str, Any]] = {}
    for path in sorted(blueprint_root.rglob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        source_files.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path)})
        if path.name.startswith("_"):
            status_overrides.update(payload.get("status_overrides", {}))
            continue
        report_id = payload.get("report_id", "")
        if report_id not in reports:
            raise ValueError(f"Structure blueprint references unknown report: {report_id}")
        reports[report_id] = apply_blueprint(reports[report_id], payload)

    for report_id, override in status_overrides.items():
        if report_id not in reports:
            raise ValueError(f"Status override references unknown report: {report_id}")
        report = reports[report_id]
        if "schema_status" in override:
            report["schemaStatus"] = override["schema_status"]
        if "verification_status" in override:
            report["verificationStatus"] = override["verification_status"]
        if "is_archived" in override:
            report["isArchived"] = bool(override["is_archived"])
        if override.get("note"):
            report["notes"].append(
                {
                    "id": f"availability-note:{slug(report_id)}",
                    "category": "source",
                    "body": override["note"],
                    "author": "schema intake",
                    "createdAt": "",
                }
            )

    workspace = {
        "contractVersion": CONTRACT_VERSION,
        "generatedAt": atlas["generated_at"],
        "sourcePolicy": SOURCE_POLICY,
        "reports": sorted(reports.values(), key=lambda item: (item["page"], item["section"], item["name"].lower())),
    }
    write_json(generated_root / "workspace.json", workspace)
    write_json(root / "public" / "data" / "workspace.json", workspace)

    lineage = json.loads(lineage_source.read_text(encoding="utf-8"))
    if lineage.get("contractVersion") != "1.0.0":
        raise ValueError("Unexpected KPI lineage contract version.")
    for collection in ("kpis", "nodes", "edges", "publications"):
        if not isinstance(lineage.get(collection), list):
            raise ValueError(f"KPI lineage {collection} must be a list.")
    write_json(generated_root / "kpi-lineage.json", lineage)
    write_json(root / "public" / "data" / "kpi-lineage.json", lineage)
    write_csv(
        generated_root / "workspace_report_catalog.csv",
        (
            {
                "report_id": report["id"],
                "report_name": report["name"],
                "page": report["page"],
                "section": report["section"],
                "schema_status": report["schemaStatus"],
                "verification_status": report["verificationStatus"],
                "layout_kind": report["layoutKind"],
                "workflow_status": report["workflowStatus"],
                "field_count": len(report["fields"]),
                "table_count": len(report["tables"]),
                "is_archived": report["isArchived"],
            }
            for report in workspace["reports"]
        ),
        [
            "report_id",
            "report_name",
            "page",
            "section",
            "schema_status",
            "verification_status",
            "layout_kind",
            "workflow_status",
            "field_count",
            "table_count",
            "is_archived",
        ],
    )

    manifest_path = root / "schema-pack" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["workspace_contract_version"] = CONTRACT_VERSION
    manifest["workspace_source_policy"] = SOURCE_POLICY
    manifest["workspace_source_files"] = source_files
    manifest.setdefault("entry_points", {})["workspace_data"] = "schema-pack/generated/workspace.json"
    manifest["entry_points"]["kpi_lineage"] = "schema-pack/generated/kpi-lineage.json"
    manifest["kpi_lineage_source"] = {
        "path": lineage_source.relative_to(root).as_posix(),
        "sha256": sha256(lineage_source),
    }
    manifest["counts"]["workspace_reports"] = len(workspace["reports"])
    manifest["counts"]["structural_blueprints"] = sum(1 for item in source_files if not Path(item["path"]).name.startswith("_"))
    manifest["counts"]["approved_kpis"] = len(lineage["kpis"])
    manifest["counts"]["published_lineage_maps"] = len(lineage["publications"])
    write_json(manifest_path, manifest)
    return workspace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    workspace = build(Path(args.root).resolve())
    print(
        f"Workspace contract generated: {len(workspace['reports'])} reports, "
        f"{sum(len(report['tables']) for report in workspace['reports'])} structural tables."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
