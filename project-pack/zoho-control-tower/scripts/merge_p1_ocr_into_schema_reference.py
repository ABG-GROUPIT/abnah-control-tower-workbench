"""Merge p1 OCR output into the central POSist schema reference.

This script consumes an OCR run produced by run_posist_screenshot_extraction.py
and updates:
- indexes/p1_ocr_screen_index.csv
- indexes/p1_ocr_line_index.csv
- indexes/p1_ocr_report_summary.csv
- indexes/report_field_index.csv
- reference_chunks/p1_main/**.md
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path


SCHEMA_SLOTS = {"02_headers", "03_hscroll"}
FILTER_SLOTS = {"01_filters"}
CONTEXT_SLOTS = {"04_vscroll", "06_notes"}

DISPLAY_FIXES = {
    "OUTLETNAME": "OUTLET NAME",
    "NETSALES": "NET SALES",
    "TOTALNETSALES": "TOTAL NET SALES",
    "GROSSAMOUNT": "GROSS AMOUNT",
    "TOTALBILLS": "TOTAL BILLS",
    "AVGPERBILL": "AVG PER BILL",
    "EMPLOYEEMEALBILLS": "EMPLOYEE MEAL BILLS",
    "EMPLOYEEMEALS": "EMPLOYEE MEALS",
    "COMPLIMENTARYCOVERS": "COMPLIMENTARY COVERS",
    "AVGPERCOVER": "AVG PER COVER",
    "TOTALGROSSSALE": "TOTAL GROSS SALE",
    "GROSSSALE": "GROSS SALE",
    "OPENHOUR": "OPEN HOUR",
    "OPENTIME": "OPEN TIME",
    "ORDERMETHOD": "ORDER METHOD",
    "PAYMENTMODE": "PAYMENT MODE",
    "PAYMENTTYPE": "PAYMENT TYPE",
    "SECTIONNAME": "SECTION NAME",
    "ITEMNAME": "ITEM NAME",
    "ITEMCODE": "ITEM CODE",
    "CATEGORYNAME": "CATEGORY NAME",
    "SUBCATEGORY": "SUB CATEGORY",
    "SUPERGROUP": "SUPER GROUP",
    "SUPERGROUPNAME": "SUPER GROUP NAME",
    "NO.OFTICKETS": "NO. OF TICKETS",
    "NO.OF TICKETS": "NO. OF TICKETS",
    "NOOFTICKETS": "NO. OF TICKETS",
    "GST@5%": "GST@5%",
    "GST@18%": "GST@18%",
}

FIELD_INDEX_COLUMNS = [
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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def display_header(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    compact_key = text.upper().replace(" ", "")
    if compact_key in DISPLAY_FIXES:
        return DISPLAY_FIXES[compact_key]
    if text.upper() in DISPLAY_FIXES:
        return DISPLAY_FIXES[text.upper()]
    return text


def normalize_field(text: str) -> str:
    shown = display_header(text).lower()
    shown = shown.replace("@", " at ")
    shown = shown.replace("%", " pct ")
    shown = re.sub(r"[^a-z0-9]+", "_", shown)
    return shown.strip("_")


def semantic_role(text: str) -> str:
    value = display_header(text).lower()
    if any(term in value for term in ["date", "hour", "time", "day", "month", "session"]):
        return "time"
    if any(
        term in value
        for term in [
            "sale",
            "amount",
            "discount",
            "tax",
            "gst",
            "charges",
            "bill",
            "ticket",
            "cover",
            "qty",
            "quantity",
            "nob",
            "avg",
            "percentage",
            "%",
        ]
    ):
        return "measure"
    if any(
        term in value
        for term in [
            "outlet",
            "cluster",
            "format",
            "brand",
            "source",
            "category",
            "item",
            "section",
            "tab",
            "user",
            "employee",
            "payment",
            "order",
        ]
    ):
        return "dimension"
    return "unknown"


def data_type_guess(text: str) -> str:
    role = semantic_role(text)
    value = display_header(text).lower()
    if role == "time":
        return "date_or_time"
    if role == "measure":
        return "numeric"
    if any(term in value for term in ["id", "code", "no"]):
        return "text_or_identifier"
    return "text"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def group_ocr(ocr_run: Path) -> tuple[dict[str, list[dict]], dict[str, dict[str, str]]]:
    screens = read_csv(ocr_run / "screen_index.csv")
    screens_by_id = {row["artifact_id"]: row for row in screens}
    by_report: dict[str, list[dict]] = defaultdict(list)
    for screen in screens:
        report_folder = screen.get("report_folder", "")
        if not report_folder:
            continue
        json_path = ocr_run / screen["ocr_json_path"]
        if not json_path.exists():
            continue
        payload = load_json(json_path)
        by_report[report_folder].append({"screen": screen, "payload": payload})
    return by_report, screens_by_id


def extract_schema_words(items: list[dict]) -> list[dict[str, str]]:
    words = []
    seen_per_report: set[tuple[str, str]] = set()
    order_by_report: Counter[str] = Counter()
    for item in items:
        screen = item["screen"]
        slot = screen.get("slot", "")
        if slot not in SCHEMA_SLOTS:
            continue
        report_folder = screen.get("report_folder", "")
        page = screen.get("page", "")
        section = screen.get("section", "")
        report_name = screen.get("report_name", "")
        source = f"{screen.get('artifact_id')}:{screen.get('relative_path')}"
        # RapidOCR already returns text boxes in reading order for these UI
        # screenshots. Coordinate sorting can break order when blue header
        # cells have slightly different detected y positions.
        raw_words = item["payload"].get("words", [])
        for word in raw_words:
            raw_text = str(word.get("text", "")).strip()
            if not raw_text:
                continue
            display = display_header(raw_text)
            normalized = normalize_field(display)
            if not normalized:
                continue
            key = (report_folder, normalized)
            if key in seen_per_report:
                continue
            seen_per_report.add(key)
            order_by_report[report_folder] += 1
            role = semantic_role(display)
            words.append(
                {
                    "page": page,
                    "section": section,
                    "report_name": report_name,
                    "report_folder": report_folder,
                    "field_order": str(order_by_report[report_folder]),
                    "raw_header_text": display,
                    "normalized_field_name": normalized,
                    "source_kind": "p1_schema_ocr_word",
                    "source_evidence": source,
                    "semantic_role": role,
                    "data_type_guess": data_type_guess(display),
                    "grain_role": role,
                    "model_candidate": "FACT_Sales or sales validation staging",
                    "notes": "",
                }
            )
    return words


def lines_for_slots(items: list[dict], slots: set[str]) -> list[str]:
    lines = []
    for item in items:
        screen = item["screen"]
        if screen.get("slot") not in slots:
            continue
        artifact_id = screen.get("artifact_id", "")
        for line in item["payload"].get("lines", []):
            line = re.sub(r"\s+", " ", str(line)).strip()
            if line:
                lines.append(f"{artifact_id}: {line}")
    return lines


def schema_field_lines(field_rows: list[dict[str, str]], report_folder: str) -> list[str]:
    rows = [row for row in field_rows if row["report_folder"] == report_folder]
    rows.sort(key=lambda row: int(row["field_order"]))
    return [f"{row['field_order']}. {row['raw_header_text']} (`{row['normalized_field_name']}`)" for row in rows]


def update_reference_chunks(reference_root: Path, by_report: dict[str, list[dict]], field_rows: list[dict[str, str]]) -> None:
    master_rows = read_csv(reference_root / "indexes" / "report_master_index.csv")
    for master in master_rows:
        if master.get("page") != "p1_main":
            continue
        report_folder = master.get("report_folder", "")
        items = by_report.get(report_folder, [])
        if not items:
            continue
        chunk_path = (
            reference_root
            / "reference_chunks"
            / master["page"]
            / master["section"]
            / f"{slugify(master['report_name'])}.md"
        )
        if not chunk_path.exists():
            continue
        original = chunk_path.read_text(encoding="utf-8")
        base = original.split("\n## OCR Text Extracted", 1)[0].rstrip()
        filter_lines = lines_for_slots(items, FILTER_SLOTS)
        schema_lines = lines_for_slots(items, SCHEMA_SLOTS)
        context_lines = lines_for_slots(items, CONTEXT_SLOTS)
        parsed_fields = schema_field_lines(field_rows, report_folder)

        lines = [base, "", "## OCR Text Extracted", ""]
        lines.extend(["### Filter Text", ""])
        lines.extend([f"- {line}" for line in filter_lines] or ["-"])
        lines.extend(["", "### Schema Header Text", ""])
        lines.extend([f"- {line}" for line in schema_lines] or ["-"])
        lines.extend(["", "### Parsed Schema Field Candidates", ""])
        lines.extend([f"- {line}" for line in parsed_fields] or ["-"])
        lines.extend(["", "### Context Text", ""])
        lines.extend([f"- {line}" for line in context_lines] or ["-"])
        lines.append("")
        chunk_path.write_text("\n".join(lines), encoding="utf-8")


def write_report_summary(reference_root: Path, by_report: dict[str, list[dict]], field_rows: list[dict[str, str]]) -> None:
    field_counts = Counter(row["report_folder"] for row in field_rows)
    rows = []
    for report_folder, items in sorted(by_report.items()):
        first = items[0]["screen"]
        slot_counts = Counter(item["screen"].get("slot", "") for item in items)
        line_count = sum(len(item["payload"].get("lines", [])) for item in items)
        mean_conf = []
        for item in items:
            for word in item["payload"].get("words", []):
                try:
                    mean_conf.append(float(word.get("confidence", 0)))
                except Exception:
                    pass
        rows.append(
            {
                "page": first.get("page", ""),
                "section": first.get("section", ""),
                "report_name": first.get("report_name", ""),
                "report_folder": report_folder,
                "ocr_screens": str(len(items)),
                "filter_screens": str(slot_counts["01_filters"]),
                "schema_screens": str(slot_counts["02_headers"] + slot_counts["03_hscroll"]),
                "context_screens": str(slot_counts["04_vscroll"] + slot_counts["06_notes"]),
                "ocr_line_count": str(line_count),
                "parsed_schema_field_count": str(field_counts[report_folder]),
                "mean_word_confidence": f"{sum(mean_conf) / len(mean_conf):.4f}" if mean_conf else "",
                "ocr_status": "converted_to_text",
            }
        )
    write_csv(reference_root / "indexes" / "p1_ocr_report_summary.csv", rows)


def update_readme(reference_root: Path, run_id: str, field_count: int) -> None:
    readme_path = reference_root / "README.md"
    if not readme_path.exists():
        return
    content = readme_path.read_text(encoding="utf-8")
    base = content.split("\n## OCR Conversion Status", 1)[0].rstrip()
    section = f"""

## OCR Conversion Status

- p1 OCR run: `{run_id}`
- p1 screenshots converted: `161`
- parsed p1 schema field candidates: `{field_count}`
- OCR engine: `RapidOCR ONNXRuntime`
- quality note: good for report titles, filters, and column headers; some multi-word headers lose spaces, so normalized fields should be audited before SQL/model changes.
"""
    readme_path.write_text(base + section, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reference-root",
        default=r"C:\Users\ARNAV\OneDrive\Desktop\ABNAH actual demo\POSist Schema Reference",
        help="Central POSist schema reference folder.",
    )
    parser.add_argument(
        "--ocr-run",
        default=r"C:\Users\ARNAV\OneDrive\Desktop\ABNAH actual demo\POSist Schema Reference\ocr_runs\p1_main_rapidocr_20260714",
        help="OCR run folder created by run_posist_screenshot_extraction.py.",
    )
    args = parser.parse_args()

    reference_root = Path(args.reference_root)
    ocr_run = Path(args.ocr_run)
    if not ocr_run.exists():
        raise FileNotFoundError(f"OCR run not found: {ocr_run}")

    shutil.copy2(ocr_run / "screen_index.csv", reference_root / "indexes" / "p1_ocr_screen_index.csv")
    shutil.copy2(ocr_run / "ocr_line_catalog.csv", reference_root / "indexes" / "p1_ocr_line_index.csv")

    by_report, _ = group_ocr(ocr_run)
    field_rows: list[dict[str, str]] = []
    for items in by_report.values():
        field_rows.extend(extract_schema_words(items))
    write_csv(reference_root / "indexes" / "report_field_index.csv", field_rows, FIELD_INDEX_COLUMNS)
    write_report_summary(reference_root, by_report, field_rows)
    update_reference_chunks(reference_root, by_report, field_rows)
    update_readme(reference_root, ocr_run.name, len(field_rows))

    print(f"Merged OCR run: {ocr_run}")
    print(f"Reports with OCR: {len(by_report)}")
    print(f"Parsed schema field candidates: {len(field_rows)}")


if __name__ == "__main__":
    main()
