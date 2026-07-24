#!/usr/bin/env python3
"""Validate the consolidated, GitHub-safe ABNAH implementation pack."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from project_pack_integrity import TEXT_EXTENSIONS, canonical_size_sha256


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "project-pack" / "zoho-control-tower"
MANIFEST_PATH = ROOT / "project-pack" / "PROJECT_PACK_MANIFEST.csv"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
ALLOWED_LOCAL_PLACEHOLDERS = {
    "local_data_auditor/input/.gitkeep",
    "local_data_auditor/input/README.md",
    "local_data_auditor/output/.gitkeep",
    "source_intake/posist_uat/_incoming_drop/.gitkeep",
    "source_intake/posist_uat/_incoming_drop/README.md",
    "source_intake/posist_uat/batches/.gitkeep",
    "source_intake/posist_uat/ocr_runs/.gitkeep",
}
LOCAL_ONLY_PREFIXES = (
    "local_data_auditor/input/",
    "local_data_auditor/output/",
    "source_intake/posist_uat/_incoming_drop/",
    "source_intake/posist_uat/batches/",
    "source_intake/posist_uat/ocr_runs/",
)
REQUIRED_PATHS = (
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/START_HERE.md",
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/01_IMPORT_FILES/IMPORT_CHECKLIST.csv",
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/02_QUERY_TABLES/QUERY_TABLE_MANIFEST.csv",
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/03_ZOHO_INSTRUCTIONS/04_DASHBOARD_BUILD.md",
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/03_ZOHO_INSTRUCTIONS/04A_DASHBOARD_EXPECTED_RESULTS.md",
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/05_DEVELOPER_HANDOFF/MODEL_OVERVIEW.md",
    "docs/CONTROL_TOWER_KPI_AND_CHART_LINEAGE_HANDBOOK.md",
    "docs/PRESENTATION_SAFE_ACTUAL_DATA_ISSUES.md",
    "docs/control_tower_presentation_contract.json",
    "docs/control_tower_model_catalog.json",
    "local_data_auditor/run_full_pipeline.bat",
    "scripts/build_control_tower_presentation.py",
    "tests/test_control_tower_presentation.py",
)
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"gh[oprsu]_[A-Za-z0-9_]{20,}"),
    "Sites token": re.compile(r"art_v1_[A-Za-z0-9_]{20,}"),
    "OpenAI key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
}


def pack_files() -> dict[str, Path]:
    return {
        path.relative_to(PACK_ROOT).as_posix(): path
        for path in sorted(PACK_ROOT.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix.lower() not in {".pyc", ".pyo"}
    }


def write_manifest(files: dict[str, Path]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "size_bytes", "sha256"],
        )
        writer.writeheader()
        for relative, path in files.items():
            size_bytes, digest = canonical_size_sha256(path)
            writer.writerow(
                {
                    "path": relative,
                    "size_bytes": size_bytes,
                    "sha256": digest,
                }
            )


def read_manifest() -> dict[str, tuple[int, str]]:
    if not MANIFEST_PATH.exists():
        raise SystemExit(
            "Project-pack manifest is missing. Run with --write-manifest first."
        )
    with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            row["path"]: (int(row["size_bytes"]), row["sha256"])
            for row in csv.DictReader(handle)
        }


def validate(files: dict[str, Path]) -> None:
    violations: list[str] = []

    for required in REQUIRED_PATHS:
        if required not in files:
            violations.append(f"required artifact is missing: {required}")

    manifest = read_manifest()
    if set(files) != set(manifest):
        missing = sorted(set(manifest) - set(files))
        unexpected = sorted(set(files) - set(manifest))
        if missing:
            violations.append(f"manifested files are missing: {missing[:10]}")
        if unexpected:
            violations.append(f"unmanifested files are present: {unexpected[:10]}")

    for relative, path in files.items():
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            violations.append(f"image must remain local: {relative}")

        if (
            relative.startswith(LOCAL_ONLY_PREFIXES)
            and relative not in ALLOWED_LOCAL_PLACEHOLDERS
        ):
            violations.append(f"local runtime evidence is publishable: {relative}")

        expected = manifest.get(relative)
        if expected:
            actual = canonical_size_sha256(path)
            if actual != expected:
                violations.append(f"manifest mismatch: {relative}")

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                violations.append(f"{label} detected in {relative}")

    if violations:
        joined = "\n".join(f"- {item}" for item in violations)
        raise SystemExit(f"Project-pack validation failed:\n{joined}")

    size_mb = sum(path.stat().st_size for path in files.values()) / (1024 * 1024)
    print(
        "Project pack validated: "
        f"{len(files)} files, {size_mb:.2f} MB, no images, secrets, "
        "or local runtime evidence."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="Replace the manifest with hashes for the current intentional pack.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not PACK_ROOT.exists():
        raise SystemExit(f"Project pack is missing: {PACK_ROOT}")
    files = pack_files()
    if args.write_manifest:
        write_manifest(files)
        print(f"Wrote {MANIFEST_PATH} with {len(files)} file records.")
    validate(files)


if __name__ == "__main__":
    main()
