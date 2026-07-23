"""Generate page-level schema capture README templates from POSist report scaffold.

These README files are a fast human staging layer for CSV header capture.
They are not the final schema memory; the OCR/schema extraction workflow can
later split them back into report-level folders and indexes.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


PAGE_TITLES = {
    "p2_reports": "P2 Reports Schema Capture",
    "p4_stock_admin": "P4 Stock Administration Schema Capture",
}


PAGE_NOTES = {
    "p2_reports": (
        "Use this file to paste CSV headers from the POSist Reports page. "
        "This page is mainly sales, audit, GST, CRM, attendance, and category/item reporting."
    ),
    "p4_stock_admin": (
        "Use this file to paste CSV headers from the separate POSist Stock Administration area. "
        "This is the first-priority branch for inventory, consumption, vendor, procurement, "
        "indent, stock movement, bill passing, and item-master discovery."
    ),
}


def load_rows(root: Path, page: str) -> list[dict[str, str]]:
    status_path = root / "00_REPORT_STATUS.csv"
    if not status_path.exists():
        raise FileNotFoundError(f"Missing report status CSV: {status_path}")
    with status_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("page") == page]
    if not rows:
        raise ValueError(f"No rows found for page {page!r} in {status_path}")
    return rows


def section_title(section: str) -> str:
    label = section
    if "_" in label:
        parts = label.split("_", 1)
        if parts[0].isdigit():
            label = parts[1]
    label = label.replace("_", " ").strip()
    return label.title()


def report_anchor(index: int, report_name: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in report_name)
    clean = "-".join(part for part in clean.split("-") if part)
    return f"r{index:03d}-{clean[:60]}"


def make_report_block(index: int, row: dict[str, str]) -> list[str]:
    report_name = row["report_name"]
    folder = row["report_folder"].replace("\\", "/")
    anchor = report_anchor(index, report_name)
    return [
        f"### {index:03d}. {report_name}",
        "",
        f"Anchor: `{anchor}`",
        f"Known scaffold folder: `{folder}`",
        "",
        "Only fill what is unknown below. Do not retype the report name.",
        "",
        "| Unknown Field | Fill Here |",
        "|---|---|",
        "| Configured in UAT | `yes/no/empty/blocked` |",
        "| CSV exported | `yes/no` |",
        "| Export file name, if saved |  |",
        "| Filter override, only if different from common profile |  |",
        "| Approx rows exported |  |",
        "| Grain, only if obvious | `one row per ...` |",
        "| Useful for ABNAH model | `yes/no/maybe` |",
        "| Notes/issues/empty reason |  |",
        "",
        "CSV column headers exactly as exported:",
        "",
        "```text",
        "",
        "```",
        "",
        "Important derived meaning or unclear columns:",
        "",
        "```text",
        "",
        "```",
        "",
    ]


def build_readme(root: Path, page: str, rows: list[dict[str, str]]) -> str:
    by_section: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_section[row["section"]].append(row)

    lines: list[str] = [
        f"# {PAGE_TITLES.get(page, page)}",
        "",
        PAGE_NOTES.get(page, "Use this file to paste CSV headers report by report."),
        "",
        "This is a staging README for Codex schema discovery. Paste CSV headers and short notes here when bulk capture is faster than placing every detail into individual report folders.",
        "",
        "Do not paste full CSV data unless a few sample rows are needed to understand ambiguous columns. If an export file exists, also keep the original CSV/XLS/XLSX in that report's `05_exports` folder.",
        "",
        "## Common Fill Rules",
        "",
        "- If filters are the same across reports, write the common filter once below and only override it inside report sections when different.",
        "- Paste column headers exactly as exported, preserving spelling, spaces, symbols, and order.",
        "- If exact CSV headers are pasted, `02_headers` and `03_hscroll` screenshots are optional for that report.",
        "- Take a report screenshot when export is unavailable, headers are not visible in the CSV, the UI is pivoted/grouped, or row buckets explain the grain.",
        "- Take a filter screenshot only when the report has unique filters that change grain or interpretation, such as vendor, item, store, transaction mode/status, document status, source/channel, or date-type filters.",
        "- For Stock Administration, prioritize screenshots for high-value filters on purchase, entry, indent, stock movement, consumption, wastage, bill passing, closing stock, reorder, vendor price, expiry, yield, and production reports.",
        "- Mark empty/unconfigured reports clearly instead of spending time on them.",
        "- Keep screenshots for unusual filters, wide headers, or reports that cannot export.",
        "- Do not paste credentials, tokens, customer personal data, or payment-sensitive details.",
        "",
        "## Common Filter Profile",
        "",
        "| Field | Value To Fill |",
        "|---|---|",
        "| Capture date |  |",
        "| POSist/UAT tenant |  |",
        "| Outlet/deployment/store scope |  |",
        "| Date range used |  |",
        "| Common filters |  |",
        "| Export format used | `csv/xls/xlsx/none/mixed` |",
        "| Notes |  |",
        "",
        "## Section Index",
        "",
    ]

    report_counter = 0
    for section, section_rows in by_section.items():
        report_counter += len(section_rows)
        lines.append(f"- `{section}`: {section_title(section)} ({len(section_rows)} reports)")
    lines.extend(
        [
            "",
            f"Total reports in this template: `{len(rows)}`",
            "",
            "## Report Header Capture",
            "",
        ]
    )

    report_index = 0
    for section, section_rows in by_section.items():
        lines.extend([f"## {section_title(section)}", "", f"Section folder: `{page}/{section}`", ""])
        for row in section_rows:
            report_index += 1
            lines.extend(make_report_block(report_index, row))

    lines.extend(
        [
            "## Post-Capture Codex Actions",
            "",
            "After this README is filled, Codex should:",
            "",
            "1. Split each report block into the matching report folder's `06_notes/schema_notes.md`.",
            "2. Copy or verify original export files under each report folder's `05_exports` slot.",
            "3. Build/update the custom schema index from all p1 OCR, p2 header text, and p4 Stock Administration header text.",
            "4. Map high-priority inventory/procurement reports to Restroworks/POSist API candidates and current model objects.",
            "",
        ]
    )
    return "\n".join(lines)


def write_template(root: Path, page: str) -> Path:
    rows = load_rows(root, page)
    page_dir = root / page
    page_dir.mkdir(parents=True, exist_ok=True)
    target = page_dir / "00_SCHEMA_CAPTURE_README.md"
    target.write_text(build_readme(root, page, rows), encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default="source_intake/posist_uat/_incoming_drop/posist_ss",
        help="Structured screenshot scaffold root containing 00_REPORT_STATUS.csv.",
    )
    parser.add_argument(
        "--pages",
        nargs="+",
        default=["p2_reports", "p4_stock_admin"],
        help="Page folders to generate templates for.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    for page in args.pages:
        target = write_template(root, page)
        print(f"Generated {target.resolve()}")


if __name__ == "__main__":
    main()
