#!/usr/bin/env python3
"""Build the deterministic project-library index used by the hosted workspace."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "project-pack" / "zoho-control-tower"
MANIFEST_PATH = ROOT / "project-pack" / "PROJECT_PACK_MANIFEST.csv"
PROVENANCE_PATH = ROOT / "project-pack" / "SOURCE_PROVENANCE.json"
SCHEMA_MANIFEST_PATH = ROOT / "schema-pack" / "manifest.json"
OUTPUTS = (
    ROOT / "schema-pack" / "generated" / "project-pack-index.json",
    ROOT / "public" / "data" / "project-pack-index.json",
)

CATEGORY_DEFINITIONS = (
    (
        "final_zoho",
        "Final Zoho implementation",
        "Production handoff imports, Query Tables, dashboard instructions, truth packs, and validation.",
    ),
    (
        "synthetic_data",
        "Synthetic data and exports",
        "Three-outlet synthetic source history, normalized Zoho imports, and expected-output truth tables.",
    ),
    (
        "sql",
        "SQL library",
        "Final Control Tower SQL, legacy analytical SQL, Ask Zia tables, and database setup scripts.",
    ),
    (
        "documentation",
        "Documentation",
        "Architecture, modeling, dashboard, Zoho, external-signal, validation, and presentation guidance.",
    ),
    (
        "local_auditor",
        "Local data auditor",
        "Local-only CSV profiling, semantic review, issue packets, viewer, contracts, and model setup.",
    ),
    (
        "generators",
        "Generators and loaders",
        "Synthetic-data generators, build scripts, database loaders, and repeatable automation.",
    ),
    (
        "schema_api",
        "Schema and API intake",
        "Screenshot intake structure, Restroworks API packet, schema contracts, and UAT templates.",
    ),
    (
        "tests",
        "Tests and verification",
        "Regression tests, validation scripts, package checks, and reproducibility controls.",
    ),
    (
        "application",
        "Application source",
        "FastAPI demo application, database schema, runtime configuration, and setup files.",
    ),
    (
        "other",
        "Other project files",
        "Supporting repository and configuration files retained for a complete handoff.",
    ),
)

FEATURED = {
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/START_HERE.md": (
        1,
        "Final implementation start",
        "The authoritative entry point for importing data, creating Query Tables, and building the four pages.",
    ),
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/03_ZOHO_INSTRUCTIONS/04_DASHBOARD_BUILD.md": (
        2,
        "Dashboard build guide",
        "Click-by-click page, chart, filter, color, and publication instructions.",
    ),
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/03_ZOHO_INSTRUCTIONS/04A_DASHBOARD_EXPECTED_RESULTS.md": (
        3,
        "Dashboard expected results",
        "Exact synthetic KPI cards, chart controls, rankings, trends, row counts, tolerances, and stop conditions.",
    ),
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/03_ZOHO_INSTRUCTIONS/09_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md": (
        4,
        "Report embed sequence",
        "The exact four-dashboard build, validation, secured embed, handoff, and User Filter workflow.",
    ),
    "docs/CONTROL_TOWER_KPI_AND_CHART_LINEAGE_HANDBOOK.md": (
        5,
        "KPI and chart lineage handbook",
        "All 76 final objects with source fields, formula, aggregation, Zoho shelves, filters, and talk tracks.",
    ),
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/02_QUERY_TABLES/QUERY_TABLE_MANIFEST.csv": (
        6,
        "Query Table manifest",
        "The exact 38-table build order and dependency register.",
    ),
    "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/03_ZOHO_INSTRUCTIONS/03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md": (
        7,
        "Lookups and formulas",
        "Many-to-one lookup, aggregate formula, grain, and pre-dashboard setup rules.",
    ),
    "local_data_auditor/README.md": (
        8,
        "Local audit workflow",
        "How to inspect real exports locally without publishing operational rows.",
    ),
}


def category_for(path: str) -> str:
    lowered = path.lower()
    suffix = Path(path).suffix.lower()
    if lowered.startswith("final_zoho_control_tower_implementation/"):
        return "final_zoho"
    if lowered.startswith(("data/", "exports/")):
        return "synthetic_data"
    if suffix == ".sql" or lowered.startswith("sql/"):
        return "sql"
    if lowered.startswith("local_data_auditor/"):
        return "local_auditor"
    if lowered.startswith(("generator/", "loaders/", "scripts/")):
        return "generators"
    if lowered.startswith("source_intake/"):
        return "schema_api"
    if "/tests/" in f"/{lowered}" or lowered.startswith("tests/"):
        return "tests"
    if suffix == ".md" or lowered.startswith("docs/"):
        return "documentation"
    if lowered.startswith("app/") or path in {
        "api.py",
        "manage_demo.py",
        "render.yaml",
        "requirements.txt",
        "requirements-ocr.txt",
        "setup_work_laptop.ps1",
    }:
        return "application"
    return "other"


def kind_for(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".csv": "CSV data",
        ".sql": "SQL",
        ".md": "Guide",
        ".json": "Contract",
        ".py": "Python",
        ".bat": "Windows command",
        ".ps1": "PowerShell",
        ".html": "Local tool",
        ".zip": "Archive",
        ".yaml": "Configuration",
        ".yml": "Configuration",
        ".txt": "Text",
    }.get(suffix, "Project file")


def title_for(path: str) -> str:
    name = Path(path).name
    if name in {".gitkeep", ".gitignore", ".gitattributes", ".env.example"}:
        return name
    return Path(name).stem.replace("_", " ").replace("-", " ").strip()


def build_index() -> dict[str, Any]:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))

    files: list[dict[str, Any]] = []
    for row in manifest_rows:
        path = row["path"]
        source = PACK_ROOT / Path(path)
        if not source.is_file():
            raise FileNotFoundError(f"Manifest file is missing: {path}")
        featured = FEATURED.get(path)
        files.append(
            {
                "path": path,
                "name": source.name,
                "title": title_for(path),
                "extension": source.suffix.lower() or "none",
                "kind": kind_for(path),
                "category": category_for(path),
                "sizeBytes": int(row["size_bytes"]),
                "sha256": row["sha256"],
                "featuredOrder": featured[0] if featured else None,
                "featuredTitle": featured[1] if featured else "",
                "description": featured[2] if featured else "",
            }
        )

    category_counts = Counter(item["category"] for item in files)
    category_bytes = Counter()
    extension_counts = Counter(item["extension"] for item in files)
    for item in files:
        category_bytes[item["category"]] += item["sizeBytes"]

    categories = [
        {
            "id": identifier,
            "label": label,
            "description": description,
            "count": category_counts[identifier],
            "sizeBytes": category_bytes[identifier],
        }
        for identifier, label, description in CATEGORY_DEFINITIONS
        if category_counts[identifier]
    ]

    return {
        "contractVersion": "1.0.0",
        "title": "Complete ABNAH Project Library",
        "sourceRepository": "https://github.com/ABG-GROUPIT/abnah-control-tower-workbench",
        "pagesUrl": "https://abg-groupit.github.io/abnah-control-tower-workbench/",
        "sourceCommit": provenance["source_commit"],
        "policy": provenance["content_policy"],
        "summary": {
            "files": len(files),
            "sizeBytes": sum(item["sizeBytes"] for item in files),
            "categories": len(categories),
            "csvFiles": extension_counts[".csv"],
            "sqlFiles": extension_counts[".sql"],
            "guideFiles": extension_counts[".md"],
            "testFiles": sum(
                1 for item in files if item["category"] == "tests"
            ),
        },
        "categories": categories,
        "files": sorted(
            files,
            key=lambda item: (
                item["featuredOrder"] is None,
                item["featuredOrder"] or 999,
                item["category"],
                item["path"].lower(),
            ),
        ),
    }


def main() -> None:
    index = build_index()
    encoded = json.dumps(index, indent=2, ensure_ascii=True) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    schema_manifest = json.loads(SCHEMA_MANIFEST_PATH.read_text(encoding="utf-8"))
    schema_manifest.setdefault("entry_points", {})["project_library"] = (
        "schema-pack/generated/project-pack-index.json"
    )
    schema_manifest.setdefault("counts", {})["project_pack_files"] = index["summary"]["files"]
    schema_manifest["counts"]["project_pack_categories"] = index["summary"]["categories"]
    SCHEMA_MANIFEST_PATH.write_text(
        json.dumps(schema_manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        "Project library indexed: "
        f"{index['summary']['files']} files across "
        f"{index['summary']['categories']} categories."
    )


if __name__ == "__main__":
    main()
