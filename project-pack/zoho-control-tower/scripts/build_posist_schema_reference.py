"""Build a central POSist schema reference folder for Codex.

The reference folder is generated outside the repo by default:

    C:/Users/ARNAV/OneDrive/Desktop/ABNAH actual demo/POSist Schema Reference

It indexes:
- filled p1 screenshot evidence from Downloads,
- p2 and p4 report/template targets from the scaffold,
- capture strategy rules for when text is enough vs screenshots are needed.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


SLOTS = {
    "01_filters": "filter_context",
    "02_headers": "schema_full_header",
    "03_hscroll": "schema_horizontal_segment",
    "04_vscroll": "row_grain_or_group_context",
    "05_exports": "original_export",
    "06_notes": "context_note",
    "00_page_menu_screenshots": "page_menu",
    "00_section_menu_screenshots": "section_menu",
}


P1_MISC_TOTAL_COUNT = 27
P1_MISC_REPORTS = [
    ("Void Bill Item Wise", "https://abnah.restroworks.biz/enterpriseReports/enterpriseVoidsBillwise"),
    ("Cashier Report", "https://abnah.restroworks.biz/enterpriseReports/cashierReport"),
    ("Budget DSR Report", "https://abnah.restroworks.biz/enterpriseReports/budgetReport"),
    ("CRM Report", "https://abnah.restroworks.biz/enterpriseReports/crmReport"),
    ("Voucher Report", "https://abnah.restroworks.biz/enterpriseReports/voucherReport"),
    ("sales_and_reload_report", "https://abnah.restroworks.biz/enterpriseReports/salesAndReloadReport"),
    ("msr_reload_report", "https://abnah.restroworks.biz/enterpriseReports/msrReloadReport"),
    ("Gift Card Report", "https://abnah.restroworks.biz/enterpriseReports/giftCardReport"),
    ("Super Categories DSR", "https://abnah.restroworks.biz/enterpriseReports/enterpriseSuperCategoriesDSR"),
    ("Online Orders Time Log", "https://abnah.restroworks.biz/enterpriseReports/onlineOrdersTimeLog"),
    ("Entp EDC Report", "https://abnah.restroworks.biz/enterpriseReports/entpEDCreport"),
    ("Entp Day Report", "https://abnah.restroworks.biz/enterpriseReports/entpDayReport"),
    ("Entp Reprint Report", "https://abnah.restroworks.biz/enterpriseReports/reprintReport"),
    ("filter_invoices_report", "https://abnah.restroworks.biz/enterpriseReports/enterpriseFilterInvoicesReport"),
    ("item_out_of_stock", "https://abnah.restroworks.biz/enterpriseReports/itemOutOfStock"),
    ("Whatsapp Message Report", "https://abnah.restroworks.biz/enterpriseReports/whatsappReport"),
    ("Call Center Report", "https://abnah.restroworks.biz/enterpriseReports/ccpReport"),
    ("Item Recipe Report", "https://abnah.restroworks.biz/enterpriseReports/enterpriseRecipeReport"),
    ("Refund Item Detail Report", "https://abnah.restroworks.biz/enterpriseReports/refundItemDetail"),
    ("Shift Report", "https://abnah.restroworks.biz/enterpriseReports/shiftReport"),
    ("Expense Report", "https://abnah.restroworks.biz/enterpriseReports/expenseReport"),
    ("Aggregator Status Report", "https://abnah.restroworks.biz/enterpriseReports/aggregatorStatusReport"),
    ("Staff Meal Report", "https://abnah.restroworks.biz/enterpriseReports/entStaffMealReport"),
    ("Advance Booking Report", "https://abnah.restroworks.biz/enterpriseReports/entAdvanceBookingReport"),
    ("Removed Taxes Charges Report", "https://abnah.restroworks.biz/enterpriseReports/entRemovedTaxesCharges"),
]


def slugify(value: str) -> str:
    clean = []
    previous = False
    for char in value.strip().lower():
        if char.isalnum():
            clean.append(char)
            previous = False
        elif not previous:
            clean.append("_")
            previous = True
    return "".join(clean).strip("_") or "unnamed"


def normalize_report_folder(value: str) -> str:
    return value.replace("\\", "/").strip("/")


def read_report_status(scaffold_root: Path) -> list[dict[str, str]]:
    status_path = scaffold_root / "00_REPORT_STATUS.csv"
    if not status_path.exists():
        raise FileNotFoundError(f"Missing scaffold report status: {status_path}")
    with status_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["report_folder_norm"] = normalize_report_folder(row["report_folder"])
    return rows


def infer_priority(page: str, section: str, report_name: str) -> str:
    combined = f"{page} {section} {report_name}".lower()
    if page == "p4_stock_admin":
        procurement_terms = [
            "vendor",
            "purchase",
            "invoice",
            "bill passing",
            "price",
            "pricing",
            "late delivery",
            "po",
            "requisition",
            "credit note",
            "gate pass",
        ]
        if any(term in combined for term in procurement_terms):
            return "vendor_procurement"
        return "inventory_consumption"
    if any(term in combined for term in ["stock", "food cost", "wastage", "recipe", "inventory"]):
        return "inventory_consumption"
    if any(term in combined for term in ["vendor", "purchase", "invoice", "indent"]):
        return "vendor_procurement"
    if page in {"p1_main", "p2_reports"}:
        return "sales_revenue"
    return "unknown"


def page_capture_method(page: str) -> str:
    if page == "p1_main":
        return "screenshots_ocr_then_schema_index"
    if page == "p2_reports":
        return "csv_header_text_first_optional_screenshots"
    if page == "p4_stock_admin":
        return "csv_header_text_first_priority_screenshots_for_grain_filters"
    return "unknown"


def screenshot_rule(page: str) -> str:
    if page == "p1_main":
        return "already screenshot-first; OCR headers/hscroll segments and preserve filter/context screenshots"
    if page == "p2_reports":
        return "not required when exact CSV headers are pasted; take screenshots only for no-export reports, unique filters, grouped/pivot layouts, or confusing totals"
    if page == "p4_stock_admin":
        return "CSV headers are enough for plain tables; screenshots required for high-value lifecycle filters, grouped stock movement/consumption layouts, no-export reports, or grain ambiguity"
    return "decide after source review"


def evidence_status(page: str, folder: str, capture_counts: Counter[tuple[str, str]]) -> str:
    if page != "p1_main":
        return "schema_text_template_ready"
    total = sum(capture_counts[(folder, slot)] for slot in SLOTS)
    schema = (
        capture_counts[(folder, "02_headers")]
        + capture_counts[(folder, "03_hscroll")]
        + capture_counts[(folder, "05_exports")]
    )
    filters = capture_counts[(folder, "01_filters")]
    context = capture_counts[(folder, "04_vscroll")] + capture_counts[(folder, "06_notes")]
    if total == 0:
        return "not_captured"
    if schema > 0 and filters > 0:
        return "screenshot_schema_and_filter_available"
    if schema > 0:
        return "screenshot_schema_available_filter_missing_or_common"
    if filters > 0 and context > 0:
        return "filter_and_context_only_needs_schema"
    if filters > 0:
        return "filter_only_needs_schema"
    return "captured_but_needs_review"


def next_action(page: str, folder: str, capture_counts: Counter[tuple[str, str]]) -> str:
    if page == "p1_main":
        status = evidence_status(page, folder, capture_counts)
        if "needs_schema" in status or status == "not_captured":
            return "capture/paste headers or export if report is still needed"
        return "run OCR later and extract field list"
    if page == "p4_stock_admin":
        return "paste CSV headers first; add screenshots only for high-value filters or grouped stock/procurement grain"
    if page == "p2_reports":
        return "paste CSV headers; screenshots only for no-export or confusing grouped reports"
    return "classify source"


def index_p1_files(p1_root: Path, status_by_folder: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    if not p1_root.exists():
        return []
    rows = []
    files = sorted(path for path in p1_root.rglob("*") if path.is_file())
    sequence_by_report_slot: Counter[tuple[str, str]] = Counter()
    for index, path in enumerate(files, start=1):
        rel = path.relative_to(p1_root)
        parts = rel.parts
        if len(parts) == 2 and parts[0] == "00_page_menu_screenshots":
            section = ""
            report_folder = ""
            slot = "00_page_menu_screenshots"
            report_name = "p1 page menu"
        elif len(parts) >= 4:
            section, report_slug, slot = parts[0], parts[1], parts[2]
            report_folder = f"p1_main/{section}/{report_slug}"
            report_name = status_by_folder.get(report_folder, {}).get("report_name", report_slug)
        elif len(parts) >= 3:
            section, report_slug, slot = parts[0], parts[1], parts[2]
            report_folder = f"p1_main/{section}/{report_slug}"
            report_name = status_by_folder.get(report_folder, {}).get("report_name", report_slug)
        else:
            section = parts[0] if parts else ""
            report_folder = ""
            slot = ""
            report_name = ""
        sequence_by_report_slot[(report_folder, slot)] += 1
        rows.append(
            {
                "capture_id": f"p1cap_{index:04d}",
                "page": "p1_main",
                "section": section,
                "report_folder": report_folder,
                "report_name": report_name,
                "slot": slot,
                "slot_role": SLOTS.get(slot, "unknown"),
                "slot_sequence": str(sequence_by_report_slot[(report_folder, slot)]),
                "file_name": path.name,
                "source_path": str(path),
                "relative_path": str(rel).replace("\\", "/"),
                "needs_ocr": "yes" if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} else "no",
                "notes": "",
            }
        )
    return rows


def capture_counts(file_rows: list[dict[str, str]]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in file_rows:
        counts[(row["report_folder"], row["slot"])] += 1
    return counts


def copy_p1_evidence(output_root: Path, file_rows: list[dict[str, str]]) -> None:
    evidence_root = output_root / "evidence" / "p1_main"
    for row in file_rows:
        source = Path(row["source_path"])
        if not source.exists():
            row["reference_path"] = ""
            continue
        target = evidence_root / row["relative_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        row["reference_path"] = str(target)


def build_report_master(
    status_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    scaffold_root: Path,
) -> list[dict[str, str]]:
    counts = capture_counts(file_rows)
    rows = []
    for row in status_rows:
        page = row["page"]
        if page not in {"p1_main", "p2_reports", "p4_stock_admin"}:
            continue
        folder = row["report_folder_norm"]
        section = row["section"]
        report_name = row["report_name"]
        template_path = ""
        if page in {"p2_reports", "p4_stock_admin"}:
            template_path = str(scaffold_root / page / "00_SCHEMA_CAPTURE_README.md")
        rows.append(
            {
                "page": page,
                "section": section,
                "report_name": report_name,
                "report_folder": folder,
                "priority_domain": infer_priority(page, section, report_name),
                "capture_method": page_capture_method(page),
                "schema_source_status": evidence_status(page, folder, counts),
                "filters_count": str(counts[(folder, "01_filters")]),
                "headers_count": str(counts[(folder, "02_headers")]),
                "hscroll_count": str(counts[(folder, "03_hscroll")]),
                "vscroll_count": str(counts[(folder, "04_vscroll")]),
                "exports_count": str(counts[(folder, "05_exports")]),
                "notes_count": str(counts[(folder, "06_notes")]),
                "screenshot_required_rule": screenshot_rule(page),
                "schema_template_path": template_path,
                "next_action": next_action(page, folder, counts),
            }
        )
    return rows


def build_strategy_rows() -> list[dict[str, str]]:
    return [
        {
            "area": "p1_main",
            "primary_schema_source": "existing screenshots",
            "text_or_csv_enough": "no for existing p1; OCR needed because schema is already captured as images",
            "screenshots_required": "already captured except Miscellaneous",
            "rule": "Use filters for context, headers/hscroll for field list, vscroll/notes for grain or grouped row meaning.",
        },
        {
            "area": "p1_main/06_misc",
            "primary_schema_source": "text README with report names and CSV headers",
            "text_or_csv_enough": "yes if exact headers and report names are pasted",
            "screenshots_required": "only if no export, unique filters, or grouped/pivot row layout",
            "rule": "Because Miscellaneous has 27 unknown reports, capture names first, then headers only for useful/configured reports.",
        },
        {
            "area": "p2_reports",
            "primary_schema_source": "00_SCHEMA_CAPTURE_README.md pasted CSV headers",
            "text_or_csv_enough": "yes for normal tabular exports",
            "screenshots_required": "only for no-export reports, unique filters, pivot/grouped layouts, or confusing totals",
            "rule": "Do not repeat common filter screenshots. Put common filter profile once, then override per report only when different.",
        },
        {
            "area": "p4_stock_admin",
            "primary_schema_source": "00_SCHEMA_CAPTURE_README.md pasted CSV headers plus selective screenshots",
            "text_or_csv_enough": "yes for plain tables, no for ambiguous stock/procurement lifecycle screens",
            "screenshots_required": "required for high-value filters affecting grain/status, grouped movement/consumption, no-export reports, or item master detail screens",
            "rule": "Prioritize Stock Admin screenshots only where filters or layout determine inventory/procurement meaning.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_report_chunks(output_root: Path, master_rows: list[dict[str, str]], file_rows: list[dict[str, str]]) -> None:
    files_by_folder: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in file_rows:
        if row["report_folder"]:
            files_by_folder[row["report_folder"]].append(row)

    chunk_root = output_root / "reference_chunks"
    for row in master_rows:
        page = row["page"]
        section = row["section"]
        report_name = row["report_name"]
        folder = row["report_folder"]
        chunk_path = chunk_root / page / section / f"{slugify(report_name)}.md"
        lines = [
            f"# {report_name}",
            "",
            f"- Page: `{page}`",
            f"- Section: `{section}`",
            f"- Scaffold folder: `{folder}`",
            f"- Priority domain: `{row['priority_domain']}`",
            f"- Capture method: `{row['capture_method']}`",
            f"- Schema source status: `{row['schema_source_status']}`",
            f"- Screenshot rule: {row['screenshot_required_rule']}",
            f"- Next action: {row['next_action']}",
            "",
            "## Evidence Counts",
            "",
            f"- Filters: `{row['filters_count']}`",
            f"- Headers: `{row['headers_count']}`",
            f"- Horizontal scroll: `{row['hscroll_count']}`",
            f"- Vertical/context scroll: `{row['vscroll_count']}`",
            f"- Exports: `{row['exports_count']}`",
            f"- Notes: `{row['notes_count']}`",
            "",
        ]
        report_files = files_by_folder.get(folder, [])
        if report_files:
            lines.extend(["## Evidence Files", ""])
            for file_row in report_files:
                reference_path = file_row.get("reference_path") or file_row["source_path"]
                lines.append(
                    f"- `{file_row['slot']}` #{file_row['slot_sequence']}: `{reference_path}`"
                )
            lines.append("")
        if page in {"p2_reports", "p4_stock_admin"}:
            lines.extend(
                [
                    "## Header Capture Placeholder",
                    "",
                    "Use the page-level `00_SCHEMA_CAPTURE_README.md` first. Later this chunk should be updated with normalized CSV headers and field meanings.",
                    "",
                    "```text",
                    "",
                    "```",
                    "",
                ]
            )
        write_text(chunk_path, "\n".join(lines))


def write_readme(output_root: Path, master_rows: list[dict[str, str]], file_rows: list[dict[str, str]]) -> None:
    page_counts = Counter(row["page"] for row in master_rows)
    p1_files = len(file_rows)
    status_counts = Counter(row["schema_source_status"] for row in master_rows if row["page"] == "p1_main")
    lines = [
        "# POSist Schema Reference",
        "",
        "This folder is Codex's working schema reference for ABNAH POSist/UAT discovery.",
        "",
        "It combines the filled p1 screenshot evidence, p2/p4 CSV-header staging templates, and a durable report-level index. It is not a production connector and not a client-facing deliverable.",
        "",
        f"Generated: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "## Current Coverage",
        "",
        f"- p1 reports indexed: `{page_counts.get('p1_main', 0)}`",
        f"- p1 screenshot files indexed: `{p1_files}`",
        f"- p2 report placeholders indexed: `{page_counts.get('p2_reports', 0)}`",
        f"- p4 Stock Administration placeholders indexed: `{page_counts.get('p4_stock_admin', 0)}`",
        "",
        "## Key Files",
        "",
        "- `indexes/report_master_index.csv`: one row per report target across p1, p2, and p4.",
        "- `indexes/p1_capture_file_index.csv`: one row per p1 screenshot evidence file.",
        "- `indexes/schema_capture_strategy.csv`: rules for text vs screenshot capture.",
        "- `indexes/report_field_index.csv`: normalized field catalog populated from OCR or pasted/exported headers.",
        "- `indexes/report_to_api_mapping.csv`: report-to-API candidates, empty until headers/API samples are compared.",
        "- `indexes/report_to_model_mapping.csv`: report-to-current-model mapping, empty until schema evidence is normalized.",
        "- `indexes/unresolved_questions.csv`: follow-ups before model changes.",
        "- `plans/revised_p2_p4_capture_plan.md`: revised capture plan after reviewing p1 screenshot patterns.",
        "- `capture_templates/p1_miscellaneous_schema_readme.md`: text-first placeholder for the 27 p1 Miscellaneous reports.",
        "- `evidence/p1_main/`: copied p1 screenshots, preserving the same folder structure.",
        "- `reference_chunks/`: one markdown chunk per report for Codex lookup.",
        "",
        "## P1 Screenshot Pattern Learned",
        "",
        "- `01_filters` stores report title and filter context.",
        "- `02_headers` stores full schema when all columns fit on screen.",
        "- `03_hscroll` stores schema in ordered horizontal column segments.",
        "- `04_vscroll` stores grouped row/bucket context when vertical scrolling explains grain.",
        "- `06_notes` stores extra context, not primary schema.",
        "",
        "## P1 Schema Status Counts",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(
        [
            "",
            "## Working Rule",
            "",
            "For p2 and p4, exact CSV headers pasted as text are enough for plain tabular reports. Add screenshots only when the export is missing, filters change the grain, the UI is grouped/pivoted, or the report is high-value Stock Administration evidence where layout/status fields affect model meaning.",
            "",
            "## Visual And Handoff Layer",
            "",
            "The sibling `ABNAH Schema Atlas/` project snapshots these indexes, report chunks, API packets and current model SQL into a portable graph contract and interactive explorer. This folder remains the capture/evidence authority; the Atlas is the generated navigation, presentation and transfer layer.",
            "",
            "After any schema-index change, run `ABNAH Schema Atlas/refresh_atlas.bat` to rebuild and validate the portable snapshot.",
            "",
        ]
    )
    write_text(output_root / "README.md", "\n".join(lines))


def write_revised_plan(output_root: Path) -> None:
    content = """# Revised P2 And P4 Capture Plan

This plan is based on the filled p1 screenshot pattern.

## What P1 Taught Us

P1 schema appears in five ways:

| Slot | Meaning | How to use |
|---|---|---|
| `01_filters` | Report title and filter profile | Context only. Not the main schema source. |
| `02_headers` | Full table headers fit on screen | Direct schema evidence. |
| `03_hscroll` | Wide table headers need multiple screenshots | Direct schema evidence, but replaceable by exact CSV header text. |
| `04_vscroll` | Row groups, buckets, or repeated layout | Grain/context evidence. Use only when row structure matters. |
| `06_notes` | Extra context screenshots | Supporting evidence only. |

## Revised P2 Rule

For `p2_reports`, text is enough when CSV headers can be exported.

Do:

1. Fill the common filter profile once in `p2_reports/00_SCHEMA_CAPTURE_README.md`.
2. Paste exact CSV headers for every configured/useful report.
3. Mark empty, blocked, or irrelevant reports clearly.
4. Add screenshots only for no-export reports, unique filters, pivot/grouped layouts, or confusing totals.

Do not repeat filter screenshots for every normal p2 report.

## Revised P4 Rule

For `p4_stock_admin`, CSV headers are still the first source, but screenshots are more important than p2 when filters or layout define inventory/procurement meaning.

Screenshots are required for p4 reports when any of these are true:

1. No CSV/XLS export exists.
2. Filters include vendor, item, store, supplier/receiver, transaction mode, document status, date type, approval/payment status, or inventory mode.
3. The report is grouped by movement type, stock bucket, consumption bucket, PO/GRN lifecycle, or indent lifecycle.
4. The report is a master/detail screen such as raw material item detail, vendor price detail, recipe, stock recipe, expiry, yield, or production plan.
5. The export headers alone do not explain whether the grain is header-level, line-level, outlet-date-item, stock movement, PO-line, GRN-line, or indent-line.

For plain p4 tables with complete exported headers, screenshots are optional.

## Priority Order

1. `p4_stock_admin`: Enterprise Consumption, Wastage, Purchase Order, Vendor Price, Internal Indent, Food Cost, Entry, Purchase Detail, Stock In Stock Out, Closing Stock, Re-Order Level, Vendor Pricing, Late Delivery, Expiry, Yield, Production Plan.
2. `p2_reports`: reports that overlap with sales validation, item/category mix, GST/tax, bill-line detail, settlement/payment, and item stock status.
3. `p1_main/06_misc`: capture names first, then headers only for configured/useful reports.

## Later Codex Normalization

After the staging READMEs are filled, Codex should split each report block into:

```text
report_folder/
  05_exports/
  06_notes/schema_notes.md
```

Then update:

```text
indexes/report_master_index.csv
indexes/report_field_index.csv
indexes/report_to_api_mapping.csv
indexes/report_to_model_mapping.csv
```
"""
    write_text(output_root / "plans" / "revised_p2_p4_capture_plan.md", content)


def write_empty_mapping_indexes(output_root: Path) -> None:
    indexes = {
        "report_field_index.csv": [
            "page",
            "section",
            "report_name",
            "report_folder",
            "field_order",
            "raw_header_text",
            "normalized_field_name",
            "source_kind",
            "source_evidence",
            "semantic_role",
            "data_type_guess",
            "grain_role",
            "model_candidate",
            "notes",
        ],
        "report_to_api_mapping.csv": [
            "page",
            "section",
            "report_name",
            "report_folder",
            "api_endpoint_candidate",
            "api_coverage_status",
            "evidence",
            "next_check",
            "notes",
        ],
        "report_to_model_mapping.csv": [
            "page",
            "section",
            "report_name",
            "report_folder",
            "priority_domain",
            "current_model_object",
            "mapping_type",
            "grain_match",
            "model_action",
            "validation_rule",
            "notes",
        ],
    }
    for filename, fieldnames in indexes.items():
        write_csv(output_root / "indexes" / filename, [], fieldnames)


def write_misc_template(output_root: Path) -> None:
    lines = [
        "# P1 Miscellaneous Reports Schema Capture",
        "",
        "The p1 menu shows `Miscellaneous Reports` with 27 reports. The pasted list provides 25 known report names/URLs, so only two names remain unknown.",
        "",
        "Text is fine for this section. Capture screenshots only if a report has no export, unique filters, or grouped/pivoted layout.",
        "",
        "## Common Filter Profile",
        "",
        "| Field | Value To Fill |",
        "|---|---|",
        "| Capture date |  |",
        "| Date range used |  |",
        "| Company/outlet/deployment scope |  |",
        "| Other common filters |  |",
        "| Notes |  |",
        "",
        "## Known Report Header Capture",
        "",
    ]
    for index, (report_name, report_url) in enumerate(P1_MISC_REPORTS, start=1):
        lines.extend(
            [
                f"### {index:02d}. {report_name}",
                "",
                f"Known URL: `{report_url}`",
                "",
                "Only fill what is unknown below. Do not retype the report name or URL.",
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
            ]
        )
    if len(P1_MISC_REPORTS) < P1_MISC_TOTAL_COUNT:
        lines.extend(
            [
                "## Unknown Names Still Missing",
                "",
                "The menu count suggests two more Miscellaneous reports. Fill these only if you find them.",
                "",
            ]
        )
    for index in range(len(P1_MISC_REPORTS) + 1, P1_MISC_TOTAL_COUNT + 1):
        lines.extend(
            [
                f"### {index:02d}. Unknown Miscellaneous Report {index}",
                "",
                "| Unknown Field | Fill Here |",
                "|---|---|",
                "| Actual report name |  |",
                "| URL/menu path |  |",
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
            ]
        )
    write_text(output_root / "capture_templates" / "p1_miscellaneous_schema_readme.md", "\n".join(lines))


def write_unresolved(output_root: Path, master_rows: list[dict[str, str]]) -> None:
    rows = []
    for row in master_rows:
        if row["page"] == "p1_main" and row["schema_source_status"] != "screenshot_schema_and_filter_available":
            if row["schema_source_status"] == "not_captured":
                continue
            priority = "medium"
            if row["schema_source_status"] == "screenshot_schema_available_filter_missing_or_common":
                priority = "low"
            rows.append(
                {
                    "question_id": f"p1_schema_{len(rows)+1:03d}",
                    "page": row["page"],
                    "section": row["section"],
                    "report_name": row["report_name"],
                    "issue": row["schema_source_status"],
                    "needed_action": row["next_action"],
                    "priority": priority,
                }
            )
    rows.append(
        {
            "question_id": f"p1_misc_{len(rows)+1:03d}",
            "page": "p1_main",
            "section": "06_misc",
            "report_name": "Miscellaneous Reports",
            "issue": "25 of 27 names known; two names and all useful CSV headers still need capture if relevant",
            "needed_action": "fill only export/header/status values in capture_templates/p1_miscellaneous_schema_readme.md",
            "priority": "medium",
        }
    )
    rows.append(
        {
            "question_id": f"p4_api_{len(rows)+1:03d}",
            "page": "p4_stock_admin",
            "section": "all",
            "report_name": "Stock Administration Reports",
            "issue": "UI availability confirmed, API/sample response coverage still unknown",
            "needed_action": "after headers are captured, map each high-value report to Restroworks/POSist API samples",
            "priority": "high",
        }
    )
    write_csv(
        output_root / "indexes" / "unresolved_questions.csv",
        rows,
        ["question_id", "page", "section", "report_name", "issue", "needed_action", "priority"],
    )


def copy_templates(output_root: Path, scaffold_root: Path) -> None:
    for page in ["p2_reports", "p4_stock_admin"]:
        src = scaffold_root / page / "00_SCHEMA_CAPTURE_README.md"
        if src.exists():
            dst = output_root / "capture_templates" / f"{page}_schema_capture_readme.md"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def write_top_level_templates(output_root: Path) -> None:
    copies = [
        ("capture_templates/p1_miscellaneous_schema_readme.md", "00_P1_MISCELLANEOUS_SCHEMA_README.md"),
        ("capture_templates/p2_reports_schema_capture_readme.md", "00_P2_REPORTS_SCHEMA_CAPTURE_README.md"),
        ("capture_templates/p4_stock_admin_schema_capture_readme.md", "00_P4_STOCK_ADMIN_SCHEMA_CAPTURE_README.md"),
    ]
    for source_rel, target_name in copies:
        source = output_root / source_rel
        if source.exists():
            shutil.copy2(source, output_root / target_name)
    index = """# Template Index

Fill these files directly in this folder:

1. `00_P4_STOCK_ADMIN_SCHEMA_CAPTURE_README.md`
   - First priority.
   - Report names are already filled as headings.
   - Only fill availability/export status, filter override if different, CSV headers, and notes.

2. `00_P2_REPORTS_SCHEMA_CAPTURE_README.md`
   - Second priority.
   - Report names are already filled as headings.
   - Only fill availability/export status, filter override if different, CSV headers, and notes.

3. `00_P1_MISCELLANEOUS_SCHEMA_README.md`
   - Third priority.
   - 25 report names and URLs are already filled as headings.
   - Only two miscellaneous report names remain unknown from the menu count.
"""
    write_text(output_root / "00_TEMPLATE_INDEX.md", index)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--p1-root",
        default=r"C:\Users\ARNAV\Downloads\p1_main\p1_main",
        help="Filled p1 screenshot root.",
    )
    parser.add_argument(
        "--scaffold-root",
        default=r"C:\Users\ARNAV\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS",
        help="Structured POSist scaffold root containing 00_REPORT_STATUS.csv.",
    )
    parser.add_argument(
        "--output-root",
        default=r"C:\Users\ARNAV\OneDrive\Desktop\ABNAH actual demo\POSist Schema Reference",
        help="Central schema reference output folder.",
    )
    args = parser.parse_args()

    p1_root = Path(args.p1_root)
    scaffold_root = Path(args.scaffold_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    status_rows = read_report_status(scaffold_root)
    status_by_folder = {row["report_folder_norm"]: row for row in status_rows}
    file_rows = index_p1_files(p1_root, status_by_folder)
    copy_p1_evidence(output_root, file_rows)
    master_rows = build_report_master(status_rows, file_rows, scaffold_root)

    write_csv(output_root / "indexes" / "p1_capture_file_index.csv", file_rows)
    write_csv(output_root / "indexes" / "report_master_index.csv", master_rows)
    write_csv(output_root / "indexes" / "schema_capture_strategy.csv", build_strategy_rows())
    write_empty_mapping_indexes(output_root)
    write_report_chunks(output_root, master_rows, file_rows)
    write_unresolved(output_root, master_rows)
    write_revised_plan(output_root)
    write_misc_template(output_root)
    copy_templates(output_root, scaffold_root)
    write_top_level_templates(output_root)
    write_readme(output_root, master_rows, file_rows)

    print(f"Generated POSist schema reference: {output_root.resolve()}")
    print(f"Report rows: {len(master_rows)}")
    print(f"P1 capture files: {len(file_rows)}")
    print(f"Reference chunks: {len(master_rows)}")


if __name__ == "__main__":
    main()
