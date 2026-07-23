from __future__ import annotations

import argparse
import csv
import hashlib
import math
import struct
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parents[1]
INTAKE_ROOT = ROOT_DIR / "source_intake" / "posist_uat"
DEFAULT_SOURCE_DIR = INTAKE_ROOT / "_incoming_drop"
DEFAULT_BATCHES_DIR = INTAKE_ROOT / "batches"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
API_DOC_EXTS = {".pdf", ".html", ".htm", ".md", ".txt", ".json", ".yaml", ".yml", ".har"}
REPORT_EXPORT_EXTS = {".csv", ".tsv", ".xlsx", ".xls", ".xml"}
IGNORED_NAMES = {"README.md", ".gitkeep", ".DS_Store", "Thumbs.db"}

MANIFEST_COLUMNS = [
    "artifact_id",
    "capture_order",
    "file_name",
    "relative_path",
    "artifact_kind",
    "posist_module",
    "screen_or_report_name",
    "menu_path_or_url",
    "outlet_filter",
    "date_filter",
    "other_filters",
    "visible_columns_or_metrics",
    "priority_domain",
    "analysis_status",
    "notes",
]

INVENTORY_COLUMNS = [
    "artifact_id",
    "relative_path",
    "absolute_path",
    "artifact_kind",
    "priority_domain",
    "byte_size",
    "image_width",
    "image_height",
    "content_hash",
    "duplicate_count",
    "manifest_status",
    "notes",
]

SCREEN_CATALOG_COLUMNS = [
    "artifact_id",
    "source_file",
    "posist_module",
    "screen_or_report_name",
    "chart_or_table_name",
    "visible_fields",
    "visible_filters",
    "visible_metrics",
    "grain_hint",
    "business_question",
    "priority_domain",
    "confidence",
    "notes",
]

API_ENDPOINT_COLUMNS = [
    "artifact_id",
    "endpoint_name",
    "method",
    "path",
    "auth_type",
    "request_params",
    "response_fields",
    "response_grain",
    "pagination",
    "incremental_key",
    "rate_limit",
    "priority_domain",
    "notes",
]

API_FIELD_COLUMNS = [
    "artifact_id",
    "endpoint_name",
    "field_name",
    "field_type",
    "description",
    "nullable",
    "sample_value",
    "semantic_role",
    "possible_current_mapping",
    "notes",
]

MAPPING_COLUMNS = [
    "priority_domain",
    "posist_source",
    "posist_field",
    "current_layer",
    "current_table",
    "current_field",
    "mapping_type",
    "grain_match",
    "action_required",
    "validation_rule",
    "notes",
]

DOMAIN_KEYWORDS = {
    "inventory_consumption": [
        "inventory",
        "stock",
        "closing",
        "opening",
        "consumption",
        "recipe",
        "bom",
        "waste",
        "wastage",
        "spoil",
        "transfer",
        "issue",
        "material",
        "ingredient",
        "reorder",
        "expiry",
        "batch",
    ],
    "vendor_procurement": [
        "vendor",
        "supplier",
        "purchase",
        "procurement",
        "po",
        "grn",
        "receipt",
        "invoice",
        "qc",
        "quality",
        "return",
        "delivery",
        "rate",
        "payable",
    ],
    "sales_revenue": [
        "sale",
        "sales",
        "revenue",
        "bill",
        "order",
        "menu",
        "item",
        "discount",
        "refund",
        "void",
        "payment",
        "channel",
        "cashier",
    ],
    "api_documentation": [
        "api",
        "endpoint",
        "swagger",
        "postman",
        "json",
        "token",
        "auth",
        "parameter",
        "response",
        "request",
    ],
    "master_data": [
        "master",
        "store",
        "outlet",
        "location",
        "category",
        "uom",
        "unit",
        "user",
        "employee",
        "tax",
    ],
    "settings_admin": [
        "setting",
        "admin",
        "configuration",
        "config",
        "permission",
        "role",
    ],
}

DOMAIN_RANK = {
    "inventory_consumption": 0,
    "vendor_procurement": 1,
    "sales_revenue": 2,
    "api_documentation": 3,
    "master_data": 4,
    "settings_admin": 5,
    "unknown": 9,
}


@dataclass(frozen=True)
class Artifact:
    path: Path
    relative_path: str
    artifact_kind: str
    priority_domain: str
    byte_size: int
    image_width: int | None
    image_height: int | None
    content_hash: str


def path_text(path: Path) -> str:
    return str(path).replace("\\", "/")


def relative_path(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def detect_artifact_kind(path: Path) -> str:
    ext = path.suffix.lower()
    haystack = path_text(path).lower()
    if ext in IMAGE_EXTS:
        if any(token in haystack for token in ["api", "swagger", "postman", "endpoint"]):
            return "api_documentation_screenshot"
        return "posist_ui_screenshot"
    if ext in REPORT_EXPORT_EXTS:
        return "report_export"
    if ext in API_DOC_EXTS:
        return "api_or_text_document"
    return "other"


def infer_domain(path: Path, artifact_kind: str) -> str:
    haystack = path_text(path).lower().replace("_", " ").replace("-", " ")
    if artifact_kind in {"api_documentation_screenshot", "api_or_text_document"}:
        if any(word in haystack for word in DOMAIN_KEYWORDS["api_documentation"]):
            return "api_documentation"
    best_domain = "unknown"
    best_score = 0
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in haystack)
        if score > best_score:
            best_score = score
            best_domain = domain
    return best_domain


def sha256_short(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def read_png_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", header[16:24])
        return width, height
    return None


def read_jpeg_size(path: Path) -> tuple[int, int] | None:
    sof_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    with path.open("rb") as handle:
        if handle.read(2) != b"\xff\xd8":
            return None
        while True:
            byte = handle.read(1)
            if not byte:
                return None
            while byte != b"\xff":
                byte = handle.read(1)
                if not byte:
                    return None
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if not marker:
                return None
            marker_code = marker[0]
            if marker_code in {0xD8, 0xD9}:
                continue
            if marker_code == 0xDA:
                return None
            size_bytes = handle.read(2)
            if len(size_bytes) != 2:
                return None
            segment_size = struct.unpack(">H", size_bytes)[0]
            if segment_size < 2:
                return None
            if marker_code in sof_markers:
                data = handle.read(segment_size - 2)
                if len(data) >= 5:
                    height = struct.unpack(">H", data[1:3])[0]
                    width = struct.unpack(">H", data[3:5])[0]
                    return width, height
                return None
            handle.seek(segment_size - 2, 1)


def read_image_size(path: Path) -> tuple[int | None, int | None]:
    try:
        try:
            from PIL import Image  # type: ignore

            with Image.open(path) as image:
                return int(image.width), int(image.height)
        except Exception:
            ext = path.suffix.lower()
            if ext == ".png":
                size = read_png_size(path)
            elif ext in {".jpg", ".jpeg"}:
                size = read_jpeg_size(path)
            else:
                size = None
            if size:
                return size
    except Exception:
        pass
    return None, None


def iter_candidate_files(source_dir: Path) -> Iterable[Path]:
    supported_exts = IMAGE_EXTS | API_DOC_EXTS | REPORT_EXPORT_EXTS
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in IGNORED_NAMES:
            continue
        if path.suffix.lower() in supported_exts:
            yield path


def scan_artifacts(source_dir: Path) -> list[Artifact]:
    artifacts: list[Artifact] = []
    for path in iter_candidate_files(source_dir):
        rel_path = relative_path(path, source_dir)
        rel_context = Path(rel_path)
        artifact_kind = detect_artifact_kind(rel_context)
        width, height = read_image_size(path) if path.suffix.lower() in IMAGE_EXTS else (None, None)
        artifacts.append(
            Artifact(
                path=path,
                relative_path=rel_path,
                artifact_kind=artifact_kind,
                priority_domain=infer_domain(rel_context, artifact_kind),
                byte_size=path.stat().st_size,
                image_width=width,
                image_height=height,
                content_hash=sha256_short(path),
            )
        )
    return artifacts


def read_manifest_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        for row in reader:
            rows.append({column: (row.get(column) or "") for column in MANIFEST_COLUMNS})
        return rows


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def next_artifact_number(rows: list[dict[str, str]]) -> int:
    max_number = 0
    for row in rows:
        artifact_id = row.get("artifact_id", "")
        if artifact_id.startswith("POSIST"):
            try:
                max_number = max(max_number, int(artifact_id.replace("POSIST", "")))
            except ValueError:
                pass
    return max_number + 1


def update_manifest(manifest_path: Path, artifacts: list[Artifact]) -> list[dict[str, str]]:
    rows = read_manifest_rows(manifest_path)
    by_relative_path = {row.get("relative_path", ""): row for row in rows if row.get("relative_path")}
    next_number = next_artifact_number(rows)
    capture_order = len(rows) + 1

    for artifact in artifacts:
        if artifact.relative_path in by_relative_path:
            existing = by_relative_path[artifact.relative_path]
            existing["file_name"] = artifact.path.name
            existing["artifact_kind"] = existing.get("artifact_kind") or artifact.artifact_kind
            existing["priority_domain"] = existing.get("priority_domain") or artifact.priority_domain
            continue

        row = {column: "" for column in MANIFEST_COLUMNS}
        row.update(
            {
                "artifact_id": f"POSIST{next_number:04d}",
                "capture_order": str(capture_order),
                "file_name": artifact.path.name,
                "relative_path": artifact.relative_path,
                "artifact_kind": artifact.artifact_kind,
                "priority_domain": artifact.priority_domain,
                "analysis_status": "new",
            }
        )
        rows.append(row)
        by_relative_path[artifact.relative_path] = row
        next_number += 1
        capture_order += 1

    write_csv(manifest_path, MANIFEST_COLUMNS, rows)
    return rows


def duplicate_counts(artifacts: list[Artifact]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for artifact in artifacts:
        counts[artifact.content_hash] = counts.get(artifact.content_hash, 0) + 1
    return counts


def write_inventory(output_dir: Path, artifacts: list[Artifact], manifest_rows: list[dict[str, str]]) -> None:
    manifest_by_path = {row.get("relative_path", ""): row for row in manifest_rows}
    dupes = duplicate_counts(artifacts)
    rows: list[dict[str, object]] = []
    for artifact in artifacts:
        manifest_row = manifest_by_path.get(artifact.relative_path, {})
        rows.append(
            {
                "artifact_id": manifest_row.get("artifact_id", ""),
                "relative_path": artifact.relative_path,
                "absolute_path": str(artifact.path.resolve()),
                "artifact_kind": artifact.artifact_kind,
                "priority_domain": manifest_row.get("priority_domain") or artifact.priority_domain,
                "byte_size": artifact.byte_size,
                "image_width": artifact.image_width or "",
                "image_height": artifact.image_height or "",
                "content_hash": artifact.content_hash,
                "duplicate_count": dupes.get(artifact.content_hash, 1),
                "manifest_status": "present" if manifest_row else "missing",
                "notes": "",
            }
        )
    write_csv(output_dir / "intake_inventory.csv", INVENTORY_COLUMNS, rows)


def write_seed_catalogs(output_dir: Path, manifest_rows: list[dict[str, str]]) -> None:
    screen_rows: list[dict[str, object]] = []
    api_endpoint_rows: list[dict[str, object]] = []
    api_field_rows: list[dict[str, object]] = []
    mapping_rows: list[dict[str, object]] = []

    for row in manifest_rows:
        artifact_kind = row.get("artifact_kind", "")
        priority_domain = row.get("priority_domain", "")
        if "screenshot" in artifact_kind:
            visible_filters = "; ".join(
                value
                for value in [
                    row.get("outlet_filter", ""),
                    row.get("date_filter", ""),
                    row.get("other_filters", ""),
                ]
                if value
            )
            screen_rows.append(
                {
                    "artifact_id": row.get("artifact_id", ""),
                    "source_file": row.get("relative_path", ""),
                    "posist_module": row.get("posist_module", ""),
                    "screen_or_report_name": row.get("screen_or_report_name", ""),
                    "chart_or_table_name": "",
                    "visible_fields": row.get("visible_columns_or_metrics", ""),
                    "visible_filters": visible_filters,
                    "visible_metrics": "",
                    "grain_hint": "",
                    "business_question": "",
                    "priority_domain": priority_domain,
                    "confidence": "seed",
                    "notes": row.get("notes", ""),
                }
            )
        if artifact_kind in {"api_documentation_screenshot", "api_or_text_document"}:
            api_endpoint_rows.append(
                {
                    "artifact_id": row.get("artifact_id", ""),
                    "endpoint_name": row.get("screen_or_report_name", ""),
                    "method": "",
                    "path": row.get("menu_path_or_url", ""),
                    "auth_type": "",
                    "request_params": "",
                    "response_fields": "",
                    "response_grain": "",
                    "pagination": "",
                    "incremental_key": "",
                    "rate_limit": "",
                    "priority_domain": priority_domain,
                    "notes": row.get("notes", ""),
                }
            )
        mapping_rows.append(
            {
                "priority_domain": priority_domain,
                "posist_source": row.get("screen_or_report_name") or row.get("relative_path", ""),
                "posist_field": "",
                "current_layer": "",
                "current_table": "",
                "current_field": "",
                "mapping_type": "",
                "grain_match": "",
                "action_required": "review",
                "validation_rule": "",
                "notes": row.get("notes", ""),
            }
        )

    write_csv(output_dir / "screen_catalog_seed.csv", SCREEN_CATALOG_COLUMNS, screen_rows)
    write_csv(output_dir / "api_endpoint_catalog_seed.csv", API_ENDPOINT_COLUMNS, api_endpoint_rows)
    write_csv(output_dir / "api_field_catalog_seed.csv", API_FIELD_COLUMNS, api_field_rows)
    write_csv(output_dir / "posist_to_current_model_mapping_seed.csv", MAPPING_COLUMNS, mapping_rows)


def sorted_for_review(manifest_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        manifest_rows,
        key=lambda row: (
            DOMAIN_RANK.get(row.get("priority_domain", "unknown"), 9),
            row.get("artifact_kind", ""),
            row.get("relative_path", ""),
        ),
    )


def write_review_packets(output_dir: Path, source_dir: Path, manifest_rows: list[dict[str, str]], packet_size: int) -> None:
    packet_dir = output_dir / "review_packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    rows = [row for row in sorted_for_review(manifest_rows) if "screenshot" in row.get("artifact_kind", "")]
    packet_count = max(1, math.ceil(len(rows) / packet_size)) if rows else 0

    index_lines = [
        "# Codex Review Packet Index",
        "",
        "Generated from POSist UAT intake files.",
        "",
        "These packets are working aids for Codex schema discovery only. They are not product artifacts.",
        "",
    ]

    for packet_number in range(packet_count):
        start = packet_number * packet_size
        chunk = rows[start : start + packet_size]
        packet_name = f"packet_{packet_number + 1:03d}.md"
        packet_path = packet_dir / packet_name
        index_lines.append(f"- `{packet_name}`: screenshots {start + 1}-{start + len(chunk)}")
        lines = [
            f"# Codex Review Packet {packet_number + 1:03d}",
            "",
            "Use this packet to inspect POSist screenshots and update the screen/API catalogs.",
            "The screenshot layer is working evidence for schema discovery, not an end-user feature.",
            "",
            "| Artifact ID | Priority | Kind | Relative path | Absolute path | Notes |",
            "|---|---|---|---|---|---|",
        ]
        for row in chunk:
            rel = row.get("relative_path", "")
            abs_path = source_dir / rel
            notes = (row.get("notes", "") or "").replace("|", "/")
            lines.append(
                f"| {row.get('artifact_id', '')} | {row.get('priority_domain', '')} | "
                f"{row.get('artifact_kind', '')} | `{rel}` | `{abs_path.resolve()}` | {notes} |"
            )
        packet_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    (packet_dir / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")


def write_next_steps(output_dir: Path, artifacts: list[Artifact], manifest_rows: list[dict[str, str]]) -> None:
    domain_counts: dict[str, int] = {}
    kind_counts: dict[str, int] = {}
    for row in manifest_rows:
        domain = row.get("priority_domain") or "unknown"
        kind = row.get("artifact_kind") or "unknown"
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    lines = [
        "# Codex POSist Intake Next Steps",
        "",
        "This file is generated for Codex analysis. It is not part of the final dashboard/product.",
        "",
        "## Batch Summary",
        "",
        f"- Files scanned: {len(artifacts)}",
        f"- Manifest rows: {len(manifest_rows)}",
        "",
        "## Priority Domain Counts",
        "",
    ]
    for domain, count in sorted(domain_counts.items(), key=lambda item: (DOMAIN_RANK.get(item[0], 9), item[0])):
        lines.append(f"- `{domain}`: {count}")
    lines.extend(["", "## Artifact Kind Counts", ""])
    for kind, count in sorted(kind_counts.items()):
        lines.append(f"- `{kind}`: {count}")
    lines.extend(
        [
            "",
            "## Codex Review Order",
            "",
            "1. Open `intake_inventory.csv` and check duplicate counts, missing dimensions, and unknown priority domains.",
            "2. Review `review_packets/packet_*.md` in P0 order: inventory/consumption first, vendor/procurement second.",
            "3. Fill `screen_catalog_seed.csv` with extracted report names, filters, visible fields, metrics, and grain hints.",
            "4. Fill API catalogs from API docs/screenshots/samples.",
            "5. Convert field observations into `posist_to_current_model_mapping_seed.csv`.",
            "6. Only after mapping, update raw landing/adapters and the canonical `STD_*`, `DIM_*`, `FACT_*`, and `SUM_*` model.",
        ]
    )
    (output_dir / "codex_next_steps.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_intake(source_dir: Path, batch_dir: Path, packet_size: int) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    output_dir = batch_dir / "05_codex_analysis_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = scan_artifacts(source_dir)
    manifest_path = batch_dir / "00_manifest.csv"
    manifest_rows = update_manifest(manifest_path, artifacts)
    write_inventory(output_dir, artifacts, manifest_rows)
    write_seed_catalogs(output_dir, manifest_rows)
    write_review_packets(output_dir, source_dir, manifest_rows, packet_size)
    write_next_steps(output_dir, artifacts, manifest_rows)

    print("POSist Codex intake prepared.")
    print(f"Source folder: {source_dir}")
    print(f"Batch folder:  {batch_dir}")
    print(f"Files scanned: {len(artifacts)}")
    print(f"Manifest:      {manifest_path}")
    print(f"Inventory:     {output_dir / 'intake_inventory.csv'}")
    print(f"Review index:  {output_dir / 'review_packets' / 'README.md'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare POSist UAT screenshot/API intake files for Codex analysis.")
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE_DIR),
        help="Folder containing dumped screenshots/docs/exports. Scanned recursively.",
    )
    parser.add_argument(
        "--batch-name",
        default=date.today().isoformat(),
        help="Batch folder name under source_intake/posist_uat/batches. Defaults to today's date.",
    )
    parser.add_argument(
        "--batches-dir",
        default=str(DEFAULT_BATCHES_DIR),
        help="Root folder where dated analysis batches are written.",
    )
    parser.add_argument("--packet-size", type=int, default=25, help="Screenshots per generated Codex review packet.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    source_dir = Path(args.source).resolve()
    batches_dir = Path(args.batches_dir).resolve()
    batch_dir = batches_dir / args.batch_name
    prepare_intake(source_dir, batch_dir, max(args.packet_size, 1))


if __name__ == "__main__":
    main()
