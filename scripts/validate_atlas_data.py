#!/usr/bin/env python3
"""Validate the generated ABNAH Schema Atlas graph and portable manifest."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


EXPECTED_DISCOVERY_BOUNDARY = {
    "catalog_reports": 318,
    "historical_image_audit_universe": 182,
    "historically_evidenced_report_groups": 94,
    "strict_schema_only_images_retained": 95,
    "operational_value_images_excluded": 87,
    "schema_only_image_report_groups_covered": 64,
    "report_groups_pending_schema_only_image": 30,
    "pending_image_groups_with_verified_text_schema": 27,
    "pending_image_groups_still_text_pending": 3,
    "verified_text_schema_fields": 530,
    "text_cards_count_as_screenshots": False,
    "public_website_screenshot_assets": 0,
    "release_gate": "BLOCKED_PENDING_30_SAFE_IMAGES_AND_3_TEXT_SCHEMAS",
}
APPROVED_BOUNDARY_KEYS = {
    "contract_version",
    "as_of_date",
    "scope",
    *EXPECTED_DISCOVERY_BOUNDARY,
    "count_semantics",
}
IMAGE_REFERENCE_RE = re.compile(r"\.(?:png|jpe?g|webp|gif|bmp|tiff?)(?:\b|$)", re.IGNORECASE)
LOCAL_PATH_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:\\")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    atlas_path = root / "schema-pack" / "generated" / "atlas.json"
    manifest_path = root / "schema-pack" / "manifest.json"
    if not atlas_path.exists() or not manifest_path.exists():
        print("Atlas has not been built. Run scripts/refresh_atlas.ps1 first.")
        return 1

    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    boundary_path = root / "schema-pack" / "source" / "catalog" / "discovery_evidence_boundary.json"
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = list(atlas.get("quality", {}).get("warnings", []))

    nodes = atlas.get("nodes", [])
    edges = atlas.get("edges", [])
    node_ids = [node.get("id") for node in nodes]
    node_id_set = set(node_ids)
    duplicate_nodes = [key for key, count in Counter(node_ids).items() if count > 1]
    if duplicate_nodes:
        errors.append(f"Duplicate node IDs: {duplicate_nodes[:10]}")

    edge_ids = [edge.get("id") for edge in edges]
    duplicate_edges = [key for key, count in Counter(edge_ids).items() if count > 1]
    if duplicate_edges:
        errors.append(f"Duplicate edge IDs: {duplicate_edges[:10]}")

    dangling = [
        edge.get("id")
        for edge in edges
        if edge.get("source") not in node_id_set or edge.get("target") not in node_id_set
    ]
    if dangling:
        errors.append(f"Dangling edges: {dangling[:10]}")

    if atlas.get("schema_version") != manifest.get("schema_version"):
        errors.append("Atlas and manifest schema versions differ.")
    if atlas.get("generated_at") != manifest.get("generated_at"):
        errors.append("Atlas and manifest generation timestamps differ.")

    if set(boundary) != APPROVED_BOUNDARY_KEYS:
        errors.append("Discovery evidence boundary contains missing or unapproved keys.")
    for key, expected in EXPECTED_DISCOVERY_BOUNDARY.items():
        if boundary.get(key) != expected:
            errors.append(f"Discovery evidence boundary mismatch for {key}.")
    semantics = boundary.get("count_semantics")
    if not isinstance(semantics, dict) or not semantics or not all(
        isinstance(key, str) and isinstance(value, str) and value.strip()
        for key, value in semantics.items()
    ):
        errors.append("Discovery evidence count semantics must be a non-empty string map.")
    boundary_text = json.dumps(boundary, ensure_ascii=True)
    if IMAGE_REFERENCE_RE.search(boundary_text) or LOCAL_PATH_RE.search(boundary_text):
        errors.append("Discovery evidence boundary contains an image reference or absolute path.")
    if any(isinstance(value, list) for value in boundary.values()):
        errors.append("Discovery evidence boundary must not contain asset or report lists.")
    if boundary.get("schema_only_image_report_groups_covered", 0) + boundary.get(
        "report_groups_pending_schema_only_image", 0
    ) != boundary.get("historically_evidenced_report_groups"):
        errors.append("Discovery image report-group invariant failed.")
    if boundary.get("strict_schema_only_images_retained", 0) + boundary.get(
        "operational_value_images_excluded", 0
    ) != boundary.get("historical_image_audit_universe"):
        errors.append("Discovery historical image invariant failed.")
    if boundary.get("pending_image_groups_with_verified_text_schema", 0) + boundary.get(
        "pending_image_groups_still_text_pending", 0
    ) != boundary.get("report_groups_pending_schema_only_image"):
        errors.append("Discovery text-schema modality invariant failed.")
    if boundary.get("text_cards_count_as_screenshots") is not False:
        errors.append("Text-schema cards must never count as screenshots.")
    if boundary.get("catalog_reports") != len(atlas.get("reports", [])):
        errors.append("Discovery catalog count differs from the generated Atlas report count.")
    if atlas.get("discovery_evidence_boundary") != boundary:
        errors.append("Generated Atlas discovery boundary differs from its source contract.")
    if manifest.get("discovery_evidence_boundary") != boundary:
        errors.append("Manifest discovery boundary differs from its source contract.")
    if "evidence_items" in atlas.get("summary", {}):
        errors.append("Legacy ambiguous evidence_items key remains in the Atlas summary.")
    if any("evidence_count" in report for report in atlas.get("reports", [])):
        errors.append("Legacy ambiguous evidence_count key remains in an Atlas report.")

    report_ids = {report.get("id") for report in atlas.get("reports", [])}
    if not report_ids.issubset(node_id_set):
        errors.append("One or more report records have no graph node.")

    required_top_level = {
        "reports",
        "fields",
        "api_endpoints",
        "models",
        "mapping_options",
        "validation_tests",
    }
    missing_keys = sorted(required_top_level - set(atlas))
    if missing_keys:
        errors.append(f"Missing top-level contract keys: {missing_keys}")

    mapping_options = atlas.get("mapping_options", [])
    mapping_ids = [mapping.get("id") for mapping in mapping_options]
    duplicate_mapping_ids = [key for key, count in Counter(mapping_ids).items() if count > 1]
    if duplicate_mapping_ids:
        errors.append(f"Duplicate mapping IDs: {duplicate_mapping_ids[:10]}")
    for mapping in mapping_options:
        if mapping.get("source_id") not in node_id_set or mapping.get("target_id") not in node_id_set:
            errors.append(f"Mapping option has unknown node reference: {mapping.get('id')}")

    validation_tests = atlas.get("validation_tests", [])
    validation_ids = [validation.get("id") for validation in validation_tests]
    duplicate_validation_ids = [key for key, count in Counter(validation_ids).items() if count > 1]
    if duplicate_validation_ids:
        errors.append(f"Duplicate validation IDs: {duplicate_validation_ids[:10]}")
    for validation in validation_tests:
        if validation.get("subject_id") not in node_id_set:
            errors.append(f"Validation test has unknown subject: {validation.get('id')}")
        if validation.get("id") not in node_id_set:
            errors.append(f"Validation test has no graph node: {validation.get('id')}")

    print(f"Schema version: {atlas.get('schema_version')}")
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    print(f"Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1
    print("Atlas validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
