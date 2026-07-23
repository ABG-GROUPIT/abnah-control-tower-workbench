#!/usr/bin/env python3
"""Apply reviewed schema-only audit packet mappings to Workbench blueprints."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from validate_audit_packet import PacketReader


SOURCE_POLICY = (
    "Schema definitions and sanitized audit summaries only. Raw CSV rows, local evidence, "
    "screenshots, paths, and source images are excluded."
)

REPORT_PLANS = {
    "p1.item_recipe.detail": ("primary", "CSV item recipe detail", "replace"),
    "p2.bill_item_detail.item": ("primary", "CSV bill item detail", "replace"),
    "p2.gross_net_margin.item": ("primary", "CSV gross/net margin detail", "replace"),
    "p4.bulk_return.item": ("primary", "CSV bulk return detail", "replace"),
    "p4.closing_stock.item": ("primary", "CSV closing stock snapshot", "replace"),
    "p4.enterprise_consumption.detail": ("primary", "Enterprise consumption lifecycle", "align"),
    "p4.enterprise_entry.item": ("stock_entry_csv", "Stock entry CSV", "variant"),
    "p4.enterprise_opening.item": ("opening_stock_csv", "Opening stock CSV", "variant"),
    "p4.enterprise_physical.item": ("physical_stock_csv", "Physical stock CSV", "variant"),
    "p4.enterprise_transfer.from_item": ("transfer_from_csv", "Transfer from CSV", "variant"),
    "p4.enterprise_transfer.to_item": ("transfer_to_csv", "Transfer to CSV", "variant"),
    "p4.enterprise_purchase_order.item": ("primary", "CSV purchase order item detail", "replace"),
    "p4.enterprise_reorder.item": ("primary", "CSV reorder snapshot", "replace"),
    "p4.enterprise_stock_return.item": ("primary", "CSV stock entry return detail", "replace"),
    "p4.enterprise_variance.master": ("master", "Master variance CSV", "replace_variant"),
    "p4.enterprise_variance.normal": (
        "normal_detailed_csv",
        "Normal detailed CSV",
        "preserve_variant",
    ),
    "p4.enterprise_wastage.normal": (
        "transaction_detail_csv",
        "Transaction detail CSV",
        "preserve_variant",
    ),
    "p4.purchase_detail.po_enabled": ("primary", "Purchase detail with PO fields", "replace"),
    "p4.recipe_consumption.item": ("primary", "Recipe consumption CSV", "replace"),
    "p4.stock_in_stock_out.item": ("primary", "Stock movement detail", "align"),
}

ENTERPRISE_ENTRY_ID = "report:p4_stock_admin:01_enterprise_reports:01_enterprise_entry"
ENTERPRISE_VARIANCE_ID = "report:p4_stock_admin:01_enterprise_reports:08_enterprise_variance"
ENTERPRISE_WASTAGE_ID = "report:p4_stock_admin:01_enterprise_reports:12_enterprise_wastage_report"


def read_packet(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    reader = PacketReader(path)
    try:
        manifest = json.loads(reader.read_text("packet_manifest.json"))
        privacy = json.loads(reader.read_text("privacy_report.json"))
        changes = json.loads(reader.read_text("schema_changes.json")).get("changes", [])
        updates = json.loads(reader.read_text("workbench_updates.json")).get("updates", [])
    finally:
        reader.close()

    if manifest.get("status") != "ready_for_codex":
        raise ValueError("Packet status must be ready_for_codex.")
    for key in ("raw_data_included", "screenshots_included", "normalized_csv_included"):
        if manifest.get(key) is not False:
            raise ValueError(f"Packet must declare {key}=false.")
    if privacy.get("privacy_validation_errors"):
        raise ValueError("Packet contains privacy validation errors.")
    if changes:
        raise ValueError("Observed schema changes require manual reconciliation before import.")
    unknown = sorted({item.get("local_report_id", "") for item in updates} - REPORT_PLANS.keys())
    if unknown:
        raise ValueError(f"Packet contains unplanned report mappings: {', '.join(unknown)}")
    if len(updates) != len(REPORT_PLANS):
        raise ValueError(
            f"Expected {len(REPORT_PLANS)} report mappings, received {len(updates)}."
        )
    for item in updates:
        if item.get("action") != "ensure_blueprint_matches_contract":
            raise ValueError(
                f"Report {item.get('local_report_id')} is not mapped to a stable blueprint."
            )
        if not item.get("target", {}).get("target_report_id"):
            raise ValueError(f"Report {item.get('local_report_id')} has no stable target ID.")
    return manifest, updates


def semantic_role(column: dict[str, Any]) -> str:
    key = column["canonical_name"]
    declared_type = column["declared_type"]
    if declared_type in {"date", "datetime", "time"} or key.endswith(("_date", "_time")):
        return "date"
    if declared_type in {"decimal", "integer", "number"}:
        return "measure"
    identifier_tokens = (
        "_id",
        "_code",
        "_number",
        "_reference",
        "bill_number",
        "transaction_number",
        "invoice_number",
        "po_number",
        "pr_number",
    )
    if key.endswith(identifier_tokens) or key in identifier_tokens:
        return "document_identifier"
    return "dimension"


def data_points(columns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "key": item["canonical_name"],
            "label": item["source_label"],
            "semantic_role": semantic_role(item),
            "data_type": item["declared_type"],
        }
        for item in columns
    ]


def flat_columns(columns: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"label": item["source_label"], "key": item["canonical_name"]}
        for item in columns
    ]


def leaves(columns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for column in columns:
        if column.get("children"):
            output.extend(leaves(column["children"]))
        else:
            output.append(column)
    return output


def align_existing_block(
    block: dict[str, Any], columns: list[dict[str, Any]]
) -> dict[str, Any]:
    output = json.loads(json.dumps(block))
    targets = leaves(output.get("columns", []))
    if len(targets) != len(columns):
        raise ValueError(
            f"Cannot align block {block.get('id')}: {len(targets)} leaves vs {len(columns)} fields."
        )
    for target, source in zip(targets, columns, strict=True):
        target["key"] = source["canonical_name"]
    return output


def flat_block(block_id: str, name: str, columns: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": block_id,
        "name": name,
        "kind": "flat_table",
        "columns": flat_columns(columns),
    }


def load_blueprint(root: Path, relative_path: str, report_id: str) -> dict[str, Any]:
    path = (root / relative_path).resolve()
    report_root = (root / "schema-pack" / "source" / "report_structures").resolve()
    if report_root not in path.parents:
        raise ValueError(f"Blueprint path escapes report_structures: {relative_path}")
    if path.exists():
        blueprint = json.loads(path.read_text(encoding="utf-8"))
        if blueprint.get("report_id") != report_id:
            raise ValueError(f"Blueprint ID mismatch at {relative_path}")
        return blueprint
    return {"report_id": report_id, "blocks": [], "data_points": []}


def merge_points(
    existing: list[dict[str, Any]], additions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_key = {item["key"]: dict(item) for item in existing if item.get("key")}
    order = [item["key"] for item in existing if item.get("key")]
    for item in additions:
        if item["key"] not in by_key:
            order.append(item["key"])
        by_key[item["key"]] = item
    return [by_key[key] for key in order]


def block_point_fallbacks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    seen = set()
    for block in blocks:
        for column in leaves(block.get("columns", [])):
            key = column.get("key")
            if not key or key in seen:
                continue
            seen.add(key)
            output.append(
                {
                    "key": key,
                    "label": column.get("label", key),
                    "semantic_role": "unknown",
                    "data_type": "unknown",
                }
            )
    return output


def replace_block(
    blocks: list[dict[str, Any]], block: dict[str, Any], preserve_others: bool
) -> list[dict[str, Any]]:
    if not preserve_others:
        return [block]
    output = [item for item in blocks if item.get("id") != block["id"]]
    output.append(block)
    return output


def update_blueprint(
    blueprint: dict[str, Any],
    target_id: str,
    updates: list[dict[str, Any]],
    packet_id: str,
) -> dict[str, Any]:
    output = json.loads(json.dumps(blueprint))
    existing_blocks = output.get("blocks", [])
    packet_points: list[dict[str, Any]] = []

    if target_id == ENTERPRISE_ENTRY_ID:
        blocks = []
        for item in updates:
            block_id, name, _ = REPORT_PLANS[item["local_report_id"]]
            blocks.append(flat_block(block_id, name, item["semantic_columns"]))
            packet_points.extend(data_points(item["semantic_columns"]))
        output["blocks"] = blocks
        output["data_points"] = merge_points([], packet_points)
    else:
        blocks = existing_blocks
        preserve_existing_points = False
        for item in updates:
            block_id, name, mode = REPORT_PLANS[item["local_report_id"]]
            columns = item["semantic_columns"]
            packet_points.extend(data_points(columns))
            if mode == "align":
                current = next(
                    (block for block in blocks if block.get("id") == block_id), None
                )
                if current is None:
                    raise ValueError(f"Missing visual block {block_id} for {target_id}")
                block = align_existing_block(current, columns)
                blocks = replace_block(blocks, block, preserve_others=True)
            elif mode == "replace_variant":
                block = flat_block(block_id, name, columns)
                blocks = replace_block(blocks, block, preserve_others=True)
                preserve_existing_points = True
            elif mode == "preserve_variant":
                block = flat_block(block_id, name, columns)
                blocks = replace_block(blocks, block, preserve_others=True)
                preserve_existing_points = True
            else:
                block = flat_block(block_id, name, columns)
                blocks = replace_block(blocks, block, preserve_others=False)
        output["blocks"] = blocks
        if preserve_existing_points:
            points = merge_points(output.get("data_points", []), block_point_fallbacks(blocks))
            output["data_points"] = merge_points(points, packet_points)
        else:
            output["data_points"] = merge_points([], packet_points)

    output["schema_status"] = "captured"
    output["verification_status"] = "needs_review"
    output["layout_kind"] = (
        "mixed"
        if len(output["blocks"]) > 1
        else "grouped_columns"
        if output["blocks"] and output["blocks"][0].get("kind") == "column_tree"
        else "flat"
    )
    prior_method = output.get("capture_method", "")
    output["capture_method"] = (
        "manual_visual_and_local_csv_contract_review"
        if "manual_visual" in prior_method or len(output["blocks"]) > 1
        else "local_csv_contract_review"
    )
    output["source_policy"] = SOURCE_POLICY
    prior_note = output.get("structure_notes", "").strip()
    audit_note = (
        f"Sanitized local audit packet {packet_id} verified CSV header order, canonical field "
        "mapping, and declared types. Value-health findings are review evidence and do not "
        "alter this blank structure."
    )
    if "Sanitized local audit packet" in prior_note:
        prior_note = prior_note.split("Sanitized local audit packet", 1)[0].strip()
    output["structure_notes"] = f"{prior_note} {audit_note}".strip()
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write source blueprints; default is a dry-run validation.",
    )
    args = parser.parse_args()

    manifest, updates = read_packet(args.packet)
    grouped: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in updates:
        target = item["target"]
        grouped[(target["target_report_id"], target["blueprint_path"])].append(item)

    rendered = []
    for (target_id, relative_path), items in sorted(grouped.items()):
        blueprint = load_blueprint(root, relative_path, target_id)
        updated = update_blueprint(
            blueprint, target_id, items, manifest.get("packet_id", "unknown")
        )
        rendered.append((relative_path, updated, len(items)))

    for relative_path, payload, variant_count in rendered:
        print(f"{'WRITE' if args.write else 'CHECK'} {relative_path} ({variant_count} audit mapping(s))")
        if not args.write:
            continue
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
    print(
        f"{'Applied' if args.write else 'Validated'} {len(updates)} mappings across "
        f"{len(rendered)} source blueprint(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
