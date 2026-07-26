#!/usr/bin/env python3
"""Verify that the GitHub Pages artifact contains the complete project handoff."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path

from project_pack_integrity import canonical_size_sha256


ROOT = Path(__file__).resolve().parents[1]
PAGES_ROOT = ROOT / "pages-dist"
PACK_ROOT = PAGES_ROOT / "project-pack"
CONTENT_ROOT = PACK_ROOT / "zoho-control-tower"
MANIFEST_PATH = ROOT / "project-pack" / "PROJECT_PACK_MANIFEST.csv"
INDEX_PATH = ROOT / "schema-pack" / "generated" / "project-pack-index.json"
DEPLOYMENT_PATH = PAGES_ROOT / "project-pack-deployment.json"
ARCHIVE_PATH = PAGES_ROOT / "ABNAH_COMPLETE_PROJECT_PACK.zip"
PORTAL_ENTRY_PATH = PAGES_ROOT / "portal" / "index.html"
META_FILES = ("README.md", "SOURCE_PROVENANCE.json", "PROJECT_PACK_MANIFEST.csv", "INDEX.json")
FORBIDDEN_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}


def fail(message: str) -> None:
    raise SystemExit(f"GitHub Pages artifact validation failed: {message}")


def main() -> None:
    with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    deployment = json.loads(DEPLOYMENT_PATH.read_text(encoding="utf-8"))

    if index["summary"]["files"] != len(manifest):
        fail("the searchable index and project manifest disagree")
    if deployment["packFiles"] != len(manifest):
        fail("the deployment manifest does not cover every project file")
    if deployment["publishedFiles"] != len(manifest) + len(META_FILES):
        fail("the deployment manifest has an unexpected published-file count")

    expected_archive_names: set[str] = set()
    for row in manifest:
        relative = Path(row["path"])
        published = CONTENT_ROOT / relative
        if not published.is_file():
            fail(f"missing hosted file {relative.as_posix()}")
        if published.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(f"forbidden screenshot or image {relative.as_posix()}")
        if canonical_size_sha256(published) != (int(row["size_bytes"]), row["sha256"]):
            fail(f"canonical size or checksum mismatch for {relative.as_posix()}")
        expected_archive_names.add(f"zoho-control-tower/{relative.as_posix()}")

    for name in META_FILES:
        if not (PACK_ROOT / name).is_file():
            fail(f"missing handoff metadata {name}")
        expected_archive_names.add(name)

    if not ARCHIVE_PATH.is_file() or ARCHIVE_PATH.stat().st_size == 0:
        fail("complete project download is missing")
    if not PORTAL_ENTRY_PATH.is_file():
        fail("standalone portal entry is missing")
    with zipfile.ZipFile(ARCHIVE_PATH) as archive:
        archive_names = set(archive.namelist())
    missing_from_archive = expected_archive_names - archive_names
    if missing_from_archive:
        fail(f"archive is missing {len(missing_from_archive)} files")

    print(
        "GitHub Pages artifact verified: "
        f"{len(manifest)} implementation files, "
        f"{len(META_FILES)} metadata files, and one complete archive."
    )


if __name__ == "__main__":
    main()
