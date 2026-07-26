#!/usr/bin/env python3
"""Add the complete validated project pack to the GitHub Pages artifact."""

from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path

from project_pack_integrity import canonical_size_sha256


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "project-pack" / "zoho-control-tower"
PACK_META = ROOT / "project-pack"
MANIFEST_PATH = PACK_META / "PROJECT_PACK_MANIFEST.csv"
INDEX_PATH = ROOT / "schema-pack" / "generated" / "project-pack-index.json"
PAGES_ROOT = ROOT / "pages-dist"
DESTINATION = PAGES_ROOT / "project-pack"
CONTENT_DESTINATION = DESTINATION / "zoho-control-tower"
ARCHIVE_PATH = PAGES_ROOT / "ABNAH_COMPLETE_PROJECT_PACK.zip"
META_FILES = ("README.md", "SOURCE_PROVENANCE.json", "PROJECT_PACK_MANIFEST.csv")


def main() -> None:
    if not PAGES_ROOT.is_dir():
        raise SystemExit("pages-dist is missing; run the Vite Pages build first.")
    if DESTINATION.exists():
        resolved = DESTINATION.resolve()
        if PAGES_ROOT.resolve() not in resolved.parents:
            raise SystemExit(f"Refusing to replace unsafe destination: {resolved}")
        shutil.rmtree(DESTINATION)
    CONTENT_DESTINATION.mkdir(parents=True)

    with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))

    copied: list[tuple[Path, str]] = []
    for row in manifest:
        relative = Path(row["path"])
        source = PACK_ROOT / relative
        if not source.is_file():
            raise SystemExit(f"Manifest file is missing: {relative.as_posix()}")
        if canonical_size_sha256(source) != (int(row["size_bytes"]), row["sha256"]):
            raise SystemExit(f"Manifest mismatch: {relative.as_posix()}")
        destination = CONTENT_DESTINATION / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append((source, f"zoho-control-tower/{relative.as_posix()}"))

    for name in META_FILES:
        source = PACK_META / name
        shutil.copy2(source, DESTINATION / name)
        copied.append((source, name))

    shutil.copy2(INDEX_PATH, DESTINATION / "INDEX.json")
    copied.append((INDEX_PATH, "INDEX.json"))
    (PAGES_ROOT / ".nojekyll").write_text("", encoding="utf-8")
    portal_root = PAGES_ROOT / "portal"
    portal_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PAGES_ROOT / "index.html", portal_root / "index.html")

    with zipfile.ZipFile(
        ARCHIVE_PATH,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        for source, archive_name in copied:
            archive.write(source, archive_name)

    deployment_manifest = {
        "packFiles": len(manifest),
        "publishedFiles": len(copied),
        "sourceBytes": sum(int(row["size_bytes"]) for row in manifest),
        "archiveBytes": ARCHIVE_PATH.stat().st_size,
        "archive": ARCHIVE_PATH.name,
    }
    (PAGES_ROOT / "project-pack-deployment.json").write_text(
        json.dumps(deployment_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "GitHub Pages project pack published: "
        f"{len(manifest)} implementation files; "
        f"{ARCHIVE_PATH.stat().st_size / (1024 * 1024):.2f} MB download."
    )


if __name__ == "__main__":
    main()
