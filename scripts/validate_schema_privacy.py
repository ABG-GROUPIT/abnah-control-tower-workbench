#!/usr/bin/env python3
"""Reject screenshot files, evidence paths, and scalar OCR values in portable outputs."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".sql"}
IMAGE_REFERENCE_RE = re.compile(r"\.(?:png|jpe?g|webp|gif|bmp|tiff?)(?:\b|$)", re.IGNORECASE)
LOCAL_PATH_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:\\")
SCALAR_VALUE_RE = re.compile(r"^[₹$€£]?\s*[-+]?\d[\d,]*(?:\.\d+)?\s*%?$")
DATE_VALUE_RE = re.compile(r"^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$")
APPROVED_DISCOVERY_BOUNDARY_KEYS = {
    "contract_version",
    "as_of_date",
    "scope",
    "catalog_reports",
    "historical_image_audit_universe",
    "historically_evidenced_report_groups",
    "strict_schema_only_images_retained",
    "operational_value_images_excluded",
    "schema_only_image_report_groups_covered",
    "report_groups_pending_schema_only_image",
    "pending_image_groups_with_verified_text_schema",
    "pending_image_groups_still_text_pending",
    "verified_text_schema_fields",
    "text_cards_count_as_screenshots",
    "public_website_screenshot_assets",
    "release_gate",
    "count_semantics",
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    files_checked = 0

    for scan_root in (root / "schema-pack", root / "public" / "data"):
        for path in scan_root.rglob("*"):
            if not path.is_file():
                continue
            files_checked += 1
            relative = path.relative_to(root).as_posix()
            if path.suffix.lower() in IMAGE_SUFFIXES:
                errors.append(f"Image file is prohibited: {relative}")
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            content = path.read_text(encoding="utf-8-sig", errors="replace")
            if IMAGE_REFERENCE_RE.search(content):
                errors.append(f"Image filename/reference is prohibited: {relative}")
            if LOCAL_PATH_RE.search(content):
                errors.append(f"Absolute local path is prohibited: {relative}")

    legacy_evidence = root / "schema-pack" / "source" / "catalog" / "evidence.csv"
    if legacy_evidence.exists():
        errors.append("The legacy screenshot evidence catalog must not be packaged.")

    catalog_root = root / "schema-pack" / "source" / "catalog"
    forbidden_private_metadata = re.compile(
        r"(?:private.*manifest|(?:image|screenshot).*manifest|crosswalk)", re.IGNORECASE
    )
    for path in catalog_root.iterdir():
        if path.is_file() and forbidden_private_metadata.search(path.name):
            errors.append(f"Private image metadata must not be imported: {path.name}")

    boundary_path = catalog_root / "discovery_evidence_boundary.json"
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
    if set(boundary) != APPROVED_DISCOVERY_BOUNDARY_KEYS:
        errors.append("Discovery evidence boundary contains missing or unapproved keys.")
    if not all(not isinstance(value, list) for value in boundary.values()):
        errors.append("Discovery evidence boundary must remain aggregate-only with no lists.")
    semantics = boundary.get("count_semantics")
    if not isinstance(semantics, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in semantics.items()
    ):
        errors.append("Discovery evidence count semantics must contain strings only.")
    boundary_text = json.dumps(boundary, ensure_ascii=True)
    if IMAGE_REFERENCE_RE.search(boundary_text):
        errors.append("Discovery evidence boundary must not contain an image filename or extension.")
    if LOCAL_PATH_RE.search(boundary_text):
        errors.append("Discovery evidence boundary must not contain an absolute path.")
    if re.search(r'"[^"\n]*(?:sha(?:256)?|hash|file_name|relative_path)"\s*:', boundary_text, re.IGNORECASE):
        errors.append("Discovery evidence boundary must not contain per-asset identifiers.")

    fields_path = root / "schema-pack" / "source" / "catalog" / "report_fields.csv"
    with fields_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            label = (row.get("raw_header_text") or "").strip()
            if SCALAR_VALUE_RE.fullmatch(label) or DATE_VALUE_RE.fullmatch(label):
                errors.append(f"Scalar OCR value remains in report_fields.csv:{row_number}: {label}")

    if errors:
        print("Schema privacy validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Schema privacy validation passed: {files_checked} portable files checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
