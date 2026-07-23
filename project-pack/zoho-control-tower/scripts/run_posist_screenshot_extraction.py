"""Screenshot-first OCR extraction for POSist UAT report screenshots.

Input:
    source_intake/posist_uat/_incoming_drop/posist_ss/

Output:
    source_intake/posist_uat/ocr_runs/<run_id>/

The script preserves folder context, extracts OCR text, creates report-level
chunks, and produces CSV catalogs for later Codex model mapping.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ROOT_DIR = Path(__file__).resolve().parents[1]
INTAKE_ROOT = ROOT_DIR / "source_intake" / "posist_uat"
DEFAULT_INPUT = INTAKE_ROOT / "_incoming_drop" / "posist_ss"
DEFAULT_OUTPUT_ROOT = INTAKE_ROOT / "ocr_runs"
RESTROWORKS_PACKET = INTAKE_ROOT / "restroworks_api_docs_packet"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
TEXT_EXTS = {".txt", ".md"}
GENERIC_FIELD_STOPWORDS = {
    "generate",
    "report",
    "export",
    "selected",
    "search",
    "posist",
    "arnavkhade",
    "download",
    "reports",
    "page",
    "part",
}


@dataclass
class OcrWord:
    text: str
    confidence: float | None
    bbox: list[float] | None


@dataclass
class ScreenRecord:
    artifact_id: str
    relative_path: str
    absolute_path: str
    page: str
    section: str
    report_folder: str
    report_name: str
    slot: str
    capture_type: str
    image_width: int | None
    image_height: int | None
    content_hash: str
    ocr_text_path: str
    ocr_json_path: str
    ocr_word_count: int
    ocr_mean_confidence: float | None
    priority_domain: str
    api_endpoint_candidate: str
    notes: str


def slugify(value: str) -> str:
    value = value.strip().lower()
    chars: list[str] = []
    last_us = False
    for char in value:
        if char.isalnum():
            chars.append(char)
            last_us = False
        elif not last_us:
            chars.append("_")
            last_us = True
    return "".join(chars).strip("_") or "unnamed"


def read_report_status(input_root: Path) -> dict[str, dict[str, str]]:
    status_path = input_root / "00_REPORT_STATUS.csv"
    if not status_path.exists():
        return {}
    with status_path.open(newline="", encoding="utf-8") as handle:
        return {
            row["report_folder"].replace("\\", "/"): row
            for row in csv.DictReader(handle)
            if row.get("report_folder")
        }


def load_restroworks_endpoint_names() -> list[str]:
    endpoint_path = RESTROWORKS_PACKET / "endpoint_inventory.csv"
    if not endpoint_path.exists():
        return []
    endpoints: list[str] = []
    with endpoint_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            path = row.get("path", "")
            name = row.get("endpoint_name", "")
            if path and path != "documentation_only":
                endpoints.append(f"{name} {path}")
    return endpoints


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def image_size(path: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.size
    except Exception:
        return None, None


def infer_context(path: Path, input_root: Path, status: dict[str, dict[str, str]]) -> dict[str, str]:
    rel_parts = path.relative_to(input_root).parts
    page = rel_parts[0] if len(rel_parts) > 0 else ""
    section = rel_parts[1] if len(rel_parts) > 1 else ""
    report_folder = ""
    slot = ""
    report_name = ""
    capture_type = "unknown"

    if len(rel_parts) >= 2 and rel_parts[1] == "00_page_menu_screenshots":
        slot = "00_page_menu_screenshots"
        capture_type = "page_menu"
    elif len(rel_parts) >= 3 and rel_parts[2] == "00_section_menu_screenshots":
        slot = "00_section_menu_screenshots"
        capture_type = "section_menu"
    elif len(rel_parts) >= 4:
        report_folder = "/".join(rel_parts[:3])
        slot = rel_parts[3]
        report_name = status.get(report_folder, {}).get("report_name", rel_parts[2])
        capture_type = slot_to_capture_type(slot)
    elif len(rel_parts) >= 3:
        report_folder = "/".join(rel_parts[:3])
        report_name = status.get(report_folder, {}).get("report_name", rel_parts[2])

    return {
        "page": page,
        "section": section,
        "report_folder": report_folder,
        "report_name": report_name,
        "slot": slot,
        "capture_type": capture_type,
    }


def slot_to_capture_type(slot: str) -> str:
    if slot == "01_filters":
        return "filters"
    if slot == "02_headers":
        return "table_header"
    if slot == "03_hscroll":
        return "hscroll"
    if slot == "04_vscroll":
        return "vscroll"
    if slot == "05_exports":
        return "export"
    if slot == "06_notes":
        return "note"
    return "unknown"


def build_ocr_engine(engine: str, gpu: bool = False):
    if engine == "none":
        return None
    if engine == "rapidocr":
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as exc:
            raise RuntimeError(
                "RapidOCR is not installed. Run: python -m pip install -r requirements-ocr.txt"
            ) from exc
        return RapidOCR()
    if engine == "tesseract":
        try:
            import pytesseract  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "pytesseract is not installed. Run: python -m pip install -r requirements-ocr.txt"
            ) from exc
        return "tesseract"
    if engine == "easyocr":
        try:
            import easyocr
        except ImportError as exc:
            raise RuntimeError(
                "easyocr is not installed. Install it on the OCR PC if you want GPU OCR."
            ) from exc
        return easyocr.Reader(["en"], gpu=gpu)
    raise ValueError(f"Unsupported OCR engine: {engine}")


def run_ocr(path: Path, engine_name: str, engine_obj: Any) -> list[OcrWord]:
    if engine_name == "none":
        return []
    if engine_name == "rapidocr":
        result, _ = engine_obj(str(path))
        words: list[OcrWord] = []
        for item in result or []:
            if len(item) >= 3:
                bbox, text, conf = item[0], item[1], item[2]
                words.append(OcrWord(str(text).strip(), safe_float(conf), flatten_bbox(bbox)))
        return [w for w in words if w.text]
    if engine_name == "tesseract":
        from PIL import Image
        import pytesseract
        from pytesseract import Output

        with Image.open(path) as image:
            data = pytesseract.image_to_data(image, output_type=Output.DICT)
        words = []
        for idx, text in enumerate(data.get("text", [])):
            text = str(text).strip()
            if not text:
                continue
            conf = safe_float(data.get("conf", [""])[idx])
            left = safe_float(data.get("left", [0])[idx]) or 0
            top = safe_float(data.get("top", [0])[idx]) or 0
            width = safe_float(data.get("width", [0])[idx]) or 0
            height = safe_float(data.get("height", [0])[idx]) or 0
            words.append(OcrWord(text, conf, [left, top, left + width, top + height]))
        return words
    if engine_name == "easyocr":
        result = engine_obj.readtext(str(path), detail=1, paragraph=False)
        words = []
        for bbox, text, conf in result:
            words.append(OcrWord(str(text).strip(), safe_float(conf), flatten_bbox(bbox)))
        return [w for w in words if w.text]
    return []


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except Exception:
        return None
    if number < 0:
        return None
    return number


def flatten_bbox(bbox: Any) -> list[float] | None:
    try:
        if bbox and isinstance(bbox[0], (list, tuple)):
            xs = [float(point[0]) for point in bbox]
            ys = [float(point[1]) for point in bbox]
            return [min(xs), min(ys), max(xs), max(ys)]
        if len(bbox) == 4:
            return [float(x) for x in bbox]
    except Exception:
        return None
    return None


def words_to_lines(words: list[OcrWord]) -> list[str]:
    positioned = [w for w in words if w.bbox]
    if not positioned:
        return [w.text for w in words if w.text]
    positioned.sort(key=lambda w: ((w.bbox or [0, 0])[1], (w.bbox or [0, 0])[0]))
    heights = [max(1.0, (w.bbox or [0, 0, 0, 1])[3] - (w.bbox or [0, 0, 0, 1])[1]) for w in positioned]
    avg_height = sum(heights) / len(heights)
    y_threshold = max(8.0, avg_height * 0.7)
    lines: list[list[OcrWord]] = []
    current: list[OcrWord] = []
    current_y: float | None = None
    for word in positioned:
        y = (word.bbox or [0, 0])[1]
        if current_y is None or abs(y - current_y) <= y_threshold:
            current.append(word)
            current_y = y if current_y is None else (current_y + y) / 2
        else:
            lines.append(current)
            current = [word]
            current_y = y
    if current:
        lines.append(current)

    text_lines: list[str] = []
    for line in lines:
        line.sort(key=lambda w: (w.bbox or [0])[0])
        joined = " ".join(w.text for w in line if w.text)
        joined = re.sub(r"\s+", " ", joined).strip()
        if joined:
            text_lines.append(joined)
    return text_lines


def infer_priority_domain(text: str, section: str, report_name: str) -> str:
    combined = f"{section} {report_name} {text}".lower()
    procurement = [
        "bill passing",
        "vendor",
        "supplier",
        "purchase",
        "purchase order",
        "po/so",
        "po_so",
        "invoice",
        "requisition",
        "payment",
        "credit note",
        "late delivery",
        "pricing",
        "price",
        "rr report",
        "gate pass",
        "pending request",
        "entry",
        "return",
    ]
    inventory = [
        "stock",
        "inventory",
        "wastage",
        "food cost",
        "item stock",
        "consumption",
        "recipe",
        "indent",
        "grn",
        "variance",
        "re-order",
        "reorder",
        "closing stock",
        "expiry",
        "yield",
        "production",
        "movement",
        "default cost",
        "kitchen wise item",
    ]
    sales = ["sales", "bill", "kot", "payment", "settlement", "tax", "discount", "menu", "item"]
    if any(k in combined for k in procurement):
        return "vendor_procurement"
    if any(k in combined for k in inventory):
        return "inventory_consumption"
    if any(k in combined for k in sales):
        return "sales_revenue"
    return "unknown"


def infer_api_candidate(text: str, section: str, report_name: str) -> str:
    combined = f"{section} {report_name} {text}".lower()
    candidates: list[str] = []
    if any(
        k in combined
        for k in [
            "stock",
            "inventory",
            "wastage",
            "food cost",
            "physical",
            "consumption",
            "variance",
            "movement",
            "recipe",
            "entry",
            "return",
            "purchase",
            "vendor",
            "bill passing",
            "credit note",
            "re-order",
            "reorder",
            "expiry",
            "yield",
            "production",
            "pricing",
            "price",
        ]
    ):
        candidates.append("GET /api/v1/pos/fetch_Inventory_data")
    if "indent" in combined or "transfer" in combined or "requisition" in combined:
        candidates.append("GET /api/v1/pos/get_indents")
    if any(k in combined for k in ["bill", "kot", "sales", "payment", "settlement", "discount", "tax"]):
        if "bill passing" not in combined:
            candidates.append("GET /api/v1/pos/bills")
    if "invoice" in combined:
        candidates.append("GET /api/v1/pos/get_all_invoices")
    if any(k in combined for k in ["menu", "item stock status", "out of stock"]):
        candidates.append("GET /api/v1/online_order/menu")
    return "; ".join(dict.fromkeys(candidates))


def extract_field_candidates(lines: Iterable[str], report_name: str) -> list[str]:
    fields: list[str] = []
    for line in lines:
        normalized = re.sub(r"[^A-Za-z0-9@%/_ -]+", " ", line)
        parts = re.split(r"\s{2,}|\s+\|\s+|,", normalized)
        if len(parts) == 1:
            parts = re.split(r" (?=[A-Z][A-Za-z0-9@%/]+(?: |$))", normalized)
        for part in parts:
            candidate = re.sub(r"\s+", " ", part).strip(" -_/")
            if is_field_candidate(candidate, report_name):
                fields.append(candidate)
    seen = set()
    output = []
    for field in fields:
        key = field.lower()
        if key not in seen:
            seen.add(key)
            output.append(field)
    return output


def is_field_candidate(value: str, report_name: str) -> bool:
    if len(value) < 2 or len(value) > 80:
        return False
    lower = value.lower()
    if lower in GENERIC_FIELD_STOPWORDS:
        return False
    if lower == report_name.lower():
        return False
    if re.fullmatch(r"\d+([:.]\d+)?", value):
        return False
    useful_tokens = [
        "date",
        "time",
        "deployment",
        "store",
        "category",
        "item",
        "bill",
        "amount",
        "discount",
        "tax",
        "gst",
        "cgst",
        "sgst",
        "qty",
        "quantity",
        "number",
        "payment",
        "settlement",
        "open",
        "close",
        "stock",
        "vendor",
        "supplier",
        "invoice",
        "po",
        "grn",
        "status",
        "source",
        "tab",
    ]
    if any(token in lower for token in useful_tokens):
        return True
    return value.isupper() and any(c.isalpha() for c in value)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_notes_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def collect_inputs(input_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in input_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.lower() == "readme.md":
            continue
        if path.name.startswith("00_"):
            continue
        if path.suffix.lower() in IMAGE_EXTS or path.suffix.lower() in TEXT_EXTS:
            files.append(path)
    return sorted(files)


def make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def process(args: argparse.Namespace) -> Path:
    input_root = Path(args.input)
    if not input_root.exists():
        raise FileNotFoundError(f"Input folder does not exist: {input_root}")

    run_id = args.run_id or make_run_id()
    output_root = Path(args.output_root) / run_id
    text_dir = output_root / "01_ocr_text"
    json_dir = output_root / "02_ocr_json"
    chunk_dir = output_root / "03_report_chunks"
    for directory in [text_dir, json_dir, chunk_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    status = read_report_status(input_root)
    engine_obj = build_ocr_engine(args.engine, gpu=args.gpu)
    records: list[ScreenRecord] = []
    line_rows: list[dict[str, Any]] = []
    report_texts: dict[str, list[str]] = defaultdict(list)
    report_records: dict[str, list[ScreenRecord]] = defaultdict(list)
    report_lines: dict[str, list[str]] = defaultdict(list)

    for index, path in enumerate(collect_inputs(input_root), start=1):
        rel = path.relative_to(input_root).as_posix()
        artifact_id = f"SCR_{index:05d}"
        context = infer_context(path, input_root, status)
        width, height = image_size(path) if path.suffix.lower() in IMAGE_EXTS else (None, None)
        content_hash = sha256_file(path)

        if path.suffix.lower() in IMAGE_EXTS:
            words = run_ocr(path, args.engine, engine_obj)
            lines = words_to_lines(words)
        else:
            text = read_notes_text(path)
            words = []
            lines = [line.strip() for line in text.splitlines() if line.strip()]

        text = "\n".join(lines).strip()
        confidence_values = [w.confidence for w in words if w.confidence is not None]
        mean_conf = (
            round(sum(confidence_values) / len(confidence_values), 4)
            if confidence_values
            else None
        )
        text_path = text_dir / f"{artifact_id}.txt"
        json_path = json_dir / f"{artifact_id}.json"
        text_path.write_text(text + ("\n" if text else ""), encoding="utf-8")
        json_path.write_text(
            json.dumps(
                {
                    "artifact_id": artifact_id,
                    "relative_path": rel,
                    "context": context,
                    "engine": args.engine,
                    "lines": lines,
                    "words": [
                        {
                            "text": w.text,
                            "confidence": w.confidence,
                            "bbox": w.bbox,
                        }
                        for w in words
                    ],
                },
                indent=2,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )

        priority = infer_priority_domain(text, context["section"], context["report_name"])
        api_candidate = infer_api_candidate(text, context["section"], context["report_name"])
        record = ScreenRecord(
            artifact_id=artifact_id,
            relative_path=rel,
            absolute_path=str(path.resolve()),
            page=context["page"],
            section=context["section"],
            report_folder=context["report_folder"],
            report_name=context["report_name"],
            slot=context["slot"],
            capture_type=context["capture_type"],
            image_width=width,
            image_height=height,
            content_hash=content_hash,
            ocr_text_path=str(text_path.relative_to(output_root)),
            ocr_json_path=str(json_path.relative_to(output_root)),
            ocr_word_count=len(words),
            ocr_mean_confidence=mean_conf,
            priority_domain=priority,
            api_endpoint_candidate=api_candidate,
            notes="",
        )
        records.append(record)

        report_key = context["report_folder"] or f"{context['page']}/{context['section']}"
        report_records[report_key].append(record)
        if text:
            report_texts[report_key].append(f"## {rel}\n{text}")
            report_lines[report_key].extend(lines)

        for line_number, line in enumerate(lines, start=1):
            line_rows.append(
                {
                    "artifact_id": artifact_id,
                    "relative_path": rel,
                    "page": context["page"],
                    "section": context["section"],
                    "report_folder": context["report_folder"],
                    "report_name": context["report_name"],
                    "slot": context["slot"],
                    "line_number": line_number,
                    "text": line,
                }
            )

    screen_rows = [record.__dict__ for record in records]
    write_csv(
        output_root / "screen_index.csv",
        list(ScreenRecord.__dataclass_fields__.keys()),
        screen_rows,
    )
    write_csv(
        output_root / "ocr_line_catalog.csv",
        [
            "artifact_id",
            "relative_path",
            "page",
            "section",
            "report_folder",
            "report_name",
            "slot",
            "line_number",
            "text",
        ],
        line_rows,
    )

    report_catalog_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    api_rows: list[dict[str, Any]] = []
    backlog_rows: list[dict[str, Any]] = []

    for report_key, grouped_records in sorted(report_records.items()):
        first = grouped_records[0]
        combined_text = "\n".join(report_texts.get(report_key, []))
        field_candidates = extract_field_candidates(report_lines.get(report_key, []), first.report_name)
        priority = infer_priority_domain(combined_text, first.section, first.report_name)
        api_candidate = infer_api_candidate(combined_text, first.section, first.report_name)
        chunk_name = f"{slugify(report_key.replace('/', '_'))}.md"
        chunk_path = chunk_dir / chunk_name
        write_report_chunk(
            chunk_path,
            first,
            grouped_records,
            combined_text,
            field_candidates,
            priority,
            api_candidate,
        )
        report_catalog_rows.append(
            {
                "report_key": report_key,
                "page": first.page,
                "section": first.section,
                "report_folder": first.report_folder,
                "report_name": first.report_name,
                "screen_count": len(grouped_records),
                "capture_types": "; ".join(sorted({r.capture_type for r in grouped_records})),
                "priority_domain": priority,
                "api_endpoint_candidate": api_candidate,
                "field_candidates": "; ".join(field_candidates[:80]),
                "chunk_path": str(chunk_path.relative_to(output_root)),
                "notes": "",
            }
        )
        for field in field_candidates:
            field_rows.append(
                {
                    "report_key": report_key,
                    "page": first.page,
                    "section": first.section,
                    "report_name": first.report_name,
                    "field_or_metric": field,
                    "source_slots": "; ".join(sorted({r.slot for r in grouped_records if r.slot})),
                    "priority_domain": priority,
                    "api_endpoint_candidate": api_candidate,
                    "notes": "",
                }
            )
        api_rows.append(
            {
                "report_key": report_key,
                "report_name": first.report_name,
                "priority_domain": priority,
                "api_endpoint_candidate": api_candidate,
                "api_coverage_status": "candidate" if api_candidate else "unknown",
                "evidence": "heuristic match from OCR text and report folder",
                "next_check": "confirm against ABNAH UAT API docs/sample response",
            }
        )
        backlog_rows.append(
            {
                "report_key": report_key,
                "report_name": first.report_name,
                "priority_domain": priority,
                "model_layer": suggested_model_layer(priority),
                "model_action": suggested_model_action(priority, api_candidate),
                "api_endpoint_candidate": api_candidate,
                "evidence_chunk": str(chunk_path.relative_to(output_root)),
                "notes": "",
            }
        )

    write_csv(
        output_root / "report_catalog.csv",
        [
            "report_key",
            "page",
            "section",
            "report_folder",
            "report_name",
            "screen_count",
            "capture_types",
            "priority_domain",
            "api_endpoint_candidate",
            "field_candidates",
            "chunk_path",
            "notes",
        ],
        report_catalog_rows,
    )
    write_csv(
        output_root / "field_catalog.csv",
        [
            "report_key",
            "page",
            "section",
            "report_name",
            "field_or_metric",
            "source_slots",
            "priority_domain",
            "api_endpoint_candidate",
            "notes",
        ],
        field_rows,
    )
    write_csv(
        output_root / "api_coverage_matrix.csv",
        [
            "report_key",
            "report_name",
            "priority_domain",
            "api_endpoint_candidate",
            "api_coverage_status",
            "evidence",
            "next_check",
        ],
        api_rows,
    )
    write_csv(
        output_root / "model_impact_backlog.csv",
        [
            "report_key",
            "report_name",
            "priority_domain",
            "model_layer",
            "model_action",
            "api_endpoint_candidate",
            "evidence_chunk",
            "notes",
        ],
        backlog_rows,
    )
    write_run_readme(output_root, args, len(records), len(report_catalog_rows), len(field_rows))
    return output_root


def suggested_model_layer(priority: str) -> str:
    if priority in {"inventory_consumption", "vendor_procurement"}:
        return "STD/DIM/FACT/SUM candidate"
    if priority == "sales_revenue":
        return "FACT/SUM candidate"
    return "defer or classify"


def suggested_model_action(priority: str, api_candidate: str) -> str:
    if priority in {"inventory_consumption", "vendor_procurement"} and api_candidate:
        return "P0 review API sample and map fields"
    if priority == "sales_revenue" and api_candidate:
        return "P1 review after inventory/procurement"
    if api_candidate:
        return "review if dashboard value is clear"
    return "hold until API coverage is proven"


def write_report_chunk(
    path: Path,
    first: ScreenRecord,
    records: list[ScreenRecord],
    combined_text: str,
    field_candidates: list[str],
    priority: str,
    api_candidate: str,
) -> None:
    lines = [
        f"# {first.report_name or first.section or first.page}",
        "",
        f"- Page: `{first.page}`",
        f"- Section: `{first.section}`",
        f"- Report folder: `{first.report_folder}`",
        f"- Priority domain: `{priority}`",
        f"- API candidate: `{api_candidate}`",
        f"- Screen count: `{len(records)}`",
        "",
        "## Captures",
        "",
    ]
    for record in records:
        lines.append(
            f"- `{record.capture_type}` `{record.relative_path}` "
            f"words={record.ocr_word_count} confidence={record.ocr_mean_confidence}"
        )
    lines.extend(["", "## Field Candidates", ""])
    if field_candidates:
        for field in field_candidates[:120]:
            lines.append(f"- `{field}`")
    else:
        lines.append("- No field candidates detected.")
    lines.extend(["", "## OCR Text", "", "```text", combined_text[:30000], "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_readme(output_root: Path, args: argparse.Namespace, screen_count: int, report_count: int, field_count: int) -> None:
    text = f"""# POSist Screenshot OCR Run

Run id: `{output_root.name}`

Input folder:

```text
{Path(args.input).resolve()}
```

OCR engine: `{args.engine}`

Generated artifacts:

| File/folder | Purpose |
|---|---|
| `screen_index.csv` | One row per screenshot/note. |
| `ocr_line_catalog.csv` | OCR lines with page/section/report context. |
| `report_catalog.csv` | One row per report or menu group. |
| `field_catalog.csv` | Field/header/metric candidates extracted from OCR. |
| `api_coverage_matrix.csv` | Heuristic report-to-API candidate mapping. |
| `model_impact_backlog.csv` | First-pass model adaptation backlog. |
| `01_ocr_text/` | Plain text OCR per screenshot. |
| `02_ocr_json/` | OCR words, boxes, confidence per screenshot. |
| `03_report_chunks/` | Report-level markdown chunks for Codex review. |

Counts:

- Screens processed: `{screen_count}`
- Report chunks: `{report_count}`
- Field rows: `{field_count}`

Next step: copy this run folder back to the Codex workspace if it was created on another PC, then ask Codex to review `report_catalog.csv`, `api_coverage_matrix.csv`, and `model_impact_backlog.csv`.
"""
    (output_root / "README.md").write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Structured screenshot input folder.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="OCR run output root.")
    parser.add_argument("--run-id", default="", help="Optional fixed run id.")
    parser.add_argument(
        "--engine",
        choices=["rapidocr", "tesseract", "easyocr", "none"],
        default="rapidocr",
        help="OCR engine to use. Use none for index-only dry run.",
    )
    parser.add_argument("--gpu", action="store_true", help="Enable GPU for EasyOCR if installed.")
    args = parser.parse_args()

    try:
        output = process(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created OCR run: {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
