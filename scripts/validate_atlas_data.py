#!/usr/bin/env python3
"""Validate the generated ABNAH Schema Atlas graph and portable manifest."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    atlas_path = root / "schema-pack" / "generated" / "atlas.json"
    manifest_path = root / "schema-pack" / "manifest.json"
    if not atlas_path.exists() or not manifest_path.exists():
        print("Atlas has not been built. Run scripts/refresh_atlas.ps1 first.")
        return 1

    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
