#!/usr/bin/env python3
"""Reject screenshot files, evidence paths, and scalar OCR values in portable outputs."""

from __future__ import annotations

import csv
import re
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".sql"}
IMAGE_REFERENCE_RE = re.compile(r"\.(?:png|jpe?g|webp|gif|bmp|tiff?)(?:\b|$)", re.IGNORECASE)
LOCAL_PATH_RE = re.compile(r"(?:^|\s)[A-Za-z]:\\")
SCALAR_VALUE_RE = re.compile(r"^[₹$€£]?\s*[-+]?\d[\d,]*(?:\.\d+)?\s*%?$")
DATE_VALUE_RE = re.compile(r"^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$")


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
