#!/usr/bin/env python3
"""Build the portable ABNAH Data Discovery Atlas from the working references."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.1.0"
MODEL_TOKEN_RE = re.compile(r"\b(?:RAW|STD|DIM|FACT|SUM)_[A-Za-z0-9_]+\b")
MODEL_FILE_RE = re.compile(r"^\d{2}_(std|dim|fact|sum)_(.+)\.sql$", re.IGNORECASE)
ACRONYMS = {"bom": "BOM", "po": "PO", "kpis": "KPIs", "gst": "GST", "crm": "CRM"}
IMAGE_REFERENCE_RE = re.compile(r"\.(?:png|jpe?g|webp|gif|bmp|tiff?)(?:\b|$)", re.IGNORECASE)
LOCAL_PATH_RE = re.compile(r"(?:^|\s)[A-Za-z]:\\")
SCALAR_VALUE_RE = re.compile(r"^[₹$€£]?\s*[-+]?\d[\d,]*(?:\.\d+)?\s*%?$")
DATE_VALUE_RE = re.compile(r"^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$")
REPORT_STAMP_RE = re.compile(r"(?:generated\s*0?n|report\s*\()[^)]*\d{4}", re.IGNORECASE)
DEPLOYMENT_VALUE_RE = re.compile(r"(?:in\s*g[o0]{2}d\s*co|ingoodco)", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "unknown"


def number(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def model_name_from_file(path: Path) -> str | None:
    match = MODEL_FILE_RE.match(path.name)
    if not match:
        return None
    prefix, body = match.groups()
    words = [ACRONYMS.get(word.lower(), word.capitalize()) for word in body.split("_")]
    return f"{prefix.upper()}_{'_'.join(words)}"


def readable_model_name(name: str) -> str:
    prefix, _, body = name.partition("_")
    return f"{prefix} {body.replace('_', ' ')}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_snapshot(source: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    record: dict[str, Any] = {
        "source_name": source.name,
        "snapshot_path": destination.as_posix(),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
    }
    if source.suffix.lower() == ".csv":
        record["rows"] = len(read_csv(source))
    return record


def is_sensitive_reference(value: str) -> bool:
    return bool(IMAGE_REFERENCE_RE.search(value) or LOCAL_PATH_RE.search(value))


def is_likely_scalar_value(value: str) -> bool:
    text = value.strip()
    return bool(SCALAR_VALUE_RE.fullmatch(text) or DATE_VALUE_RE.fullmatch(text))


def sanitize_candidate_label(report_name: str, value: str) -> str | None:
    label = value.strip()
    if is_likely_scalar_value(label) or REPORT_STAMP_RE.search(label):
        return None
    if DEPLOYMENT_VALUE_RE.search(label):
        if label.lower().startswith("cluster-"):
            return "Cluster"
        if label.lower().startswith("format-"):
            return "Format"
        return "Deployment"
    lowered = label.lower()
    if lowered.startswith("cluster-"):
        return "Cluster"
    if lowered.startswith("format-"):
        return "Format"
    if re.match(r"^(breakfast|lunch|dinner|late\s*night)\d", lowered):
        return "Day Session"
    if report_name.lower() == "meal count report":
        if lowered.startswith("tab name "):
            return "Tab Name"
        allowed = {"deployment name", "hour", "tab name", "rate", "qty", "total price"}
        return label if lowered in allowed else None
    return label


def sanitize_field_row(original: dict[str, str]) -> dict[str, str] | None:
    row = dict(original)
    label = sanitize_candidate_label(row.get("report_name", ""), row.get("raw_header_text", ""))
    if not label:
        return None
    row["raw_header_text"] = label
    row["normalized_field_name"] = slug(label).replace("-", "_")
    if is_sensitive_reference(row.get("source_evidence", "")):
        row["source_evidence"] = ""
    return row


def sanitized_csv_snapshot(source: Path, destination: Path, logical_name: str) -> dict[str, Any]:
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        rows = []
        for original in reader:
            candidate = sanitize_field_row(original) if logical_name == "report_fields" else dict(original)
            if candidate is None:
                continue
            row = {
                key: "" if is_sensitive_reference(value or "") else value
                for key, value in candidate.items()
            }
            rows.append(row)
    write_csv(destination, rows, columns)
    return {
        "source_name": source.name,
        "snapshot_path": destination.as_posix(),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
        "rows": len(rows),
    }


def sanitize_reference_chunk(text: str) -> str:
    output: list[str] = []
    section = ""
    keep_parsed_candidates = False
    emitted_derived_heading = False
    report_name = ""

    for line in text.splitlines():
        if line.startswith("# ") and not report_name:
            report_name = line[2:].strip()
        if line.startswith("## "):
            section = line[3:].strip()
            keep_parsed_candidates = False
            if section in {"Evidence Counts", "Evidence Files", "OCR Text Extracted"}:
                continue
        if section in {"Evidence Counts", "Evidence Files"}:
            continue
        if section == "OCR Text Extracted":
            if line.startswith("### Parsed Schema Field Candidates"):
                keep_parsed_candidates = True
                if not emitted_derived_heading:
                    output.extend(["", "## Derived Schema Field Candidates", ""])
                    emitted_derived_heading = True
                continue
            if line.startswith("### "):
                keep_parsed_candidates = False
                continue
            if not keep_parsed_candidates:
                continue
            candidate = re.match(r"^-\s+\d+\.\s+(.+?)(?:\s+\(`|$)", line)
            if candidate:
                original_label = candidate.group(1)
                label = sanitize_candidate_label(report_name, original_label)
                if not label:
                    continue
                if label != original_label:
                    sequence_match = re.match(r"^-\s+(\d+)\.", line)
                    if sequence_match:
                        sequence = sequence_match.group(1)
                        line = f"- {sequence}. {label} (`{slug(label).replace('-', '_')}`)"
        if line.startswith("- Capture method:") or line.startswith("- Screenshot rule:"):
            continue
        if is_sensitive_reference(line):
            continue
        output.append(line.rstrip())

    compact: list[str] = []
    for line in output:
        if line or not compact or compact[-1]:
            compact.append(line)
    return "\n".join(compact).strip() + "\n"


def report_id(row: dict[str, str]) -> str:
    folder = row.get("report_folder", "").strip("/")
    if folder:
        return "report:" + folder.replace("/", ":")
    return "report:" + ":".join(
        slug(row.get(key, "")) for key in ("page", "section", "report_name")
    )


def priority_for_report(row: dict[str, str], core_keywords: list[str]) -> tuple[str, bool]:
    haystack = f"{row.get('report_name', '')} {row.get('section', '')}".lower()
    is_core = row.get("page") == "p4_stock_admin" and any(
        keyword in haystack for keyword in core_keywords
    )
    if is_core:
        return "P0", True
    if row.get("priority_domain") in {"inventory_consumption", "vendor_procurement"}:
        return "P1", False
    return "P2", False


def model_domain(name: str) -> str:
    lowered = name.lower()
    if any(token in lowered for token in ("inventory", "consumption", "ingredient", "recipe")):
        return "inventory_consumption"
    if any(token in lowered for token in ("vendor", "purchase", "entry", "receipt", "indent")):
        return "vendor_procurement"
    return "sales_revenue"


def match_endpoint(value: str, endpoints: list[dict[str, str]]) -> dict[str, str] | None:
    value_lower = value.lower()
    for endpoint in endpoints:
        candidates = (
            endpoint.get("packet_id", ""),
            endpoint.get("path", ""),
            endpoint.get("endpoint_name", ""),
        )
        if any(candidate and candidate.lower() in value_lower for candidate in candidates):
            return endpoint
    return None


def add_edge(
    edges: list[dict[str, Any]],
    seen: set[tuple[str, str, str]],
    source: str,
    target: str,
    edge_type: str,
    *,
    label: str,
    status: str = "current",
    confidence: float = 1.0,
    rationale: str = "",
) -> None:
    key = (source, target, edge_type)
    if source == target or key in seen:
        return
    seen.add(key)
    edges.append(
        {
            "id": f"edge:{slug(edge_type)}:{slug(source)}:{slug(target)}",
            "source": source,
            "target": target,
            "type": edge_type,
            "label": label,
            "status": status,
            "confidence": round(confidence, 2),
            "rationale": rationale,
        }
    )


def upsert_edge(
    edges: list[dict[str, Any]],
    seen: set[tuple[str, str, str]],
    source: str,
    target: str,
    edge_type: str,
    *,
    label: str,
    status: str,
    confidence: float,
    rationale: str,
) -> None:
    for edge in edges:
        if edge["source"] == source and edge["target"] == target and edge["type"] == edge_type:
            edge.update(
                {
                    "label": label,
                    "status": status,
                    "confidence": round(confidence, 2),
                    "rationale": rationale,
                }
            )
            return
    add_edge(
        edges,
        seen,
        source,
        target,
        edge_type,
        label=label,
        status=status,
        confidence=confidence,
        rationale=rationale,
    )


def build_model_catalog(sql_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    model_files: dict[str, Path] = {}
    referenced_names: set[str] = set()
    dependencies: list[tuple[str, str, str]] = []

    for sql_path in sorted(sql_root.glob("*.sql")):
        output_name = model_name_from_file(sql_path)
        if not output_name:
            continue
        model_files[output_name] = sql_path
        sql_text = sql_path.read_text(encoding="utf-8-sig", errors="replace")
        for referenced in sorted(set(MODEL_TOKEN_RE.findall(sql_text))):
            referenced_names.add(referenced)
            if referenced != output_name:
                dependencies.append((output_name, referenced, sql_path.name))

    all_names = set(model_files) | referenced_names
    models: list[dict[str, Any]] = []
    for name in sorted(all_names):
        layer = name.split("_", 1)[0].lower()
        source_path = model_files.get(name)
        models.append(
            {
                "id": f"model:{name.lower()}",
                "name": name,
                "label": readable_model_name(name),
                "layer": layer,
                "domain": model_domain(name),
                "status": "current",
                "source_path": source_path.name if source_path else "imported RAW source",
                "description": (
                    f"Current {layer.upper()} object in the synthetic Zoho model."
                    if source_path
                    else "Imported synthetic RAW source used by one or more current query tables."
                ),
            }
        )

    dependency_rows = [
        {"source_name": source, "target_name": target, "evidence": evidence}
        for source, target, evidence in dependencies
    ]
    return models, dependency_rows


def build(args: argparse.Namespace) -> dict[str, Any]:
    atlas_root = Path(__file__).resolve().parents[1]
    reference_root = Path(args.reference_root).resolve()
    project_root = Path(args.project_root).resolve()
    output_root = Path(args.output_root).resolve()
    generated_root = output_root / "generated"
    source_root = output_root / "source"
    public_root = atlas_root / "public" / "data"

    curation = json.loads((atlas_root / "config" / "curation.json").read_text(encoding="utf-8"))
    core_keywords = curation["core_report_keywords"]
    domain_labels = curation["domain_labels"]

    reference_files = {
        "reports": reference_root / "indexes" / "report_master_index.csv",
        "report_fields": reference_root / "indexes" / "report_field_index.csv",
        "evidence": reference_root / "indexes" / "p1_capture_file_index.csv",
        "report_api_mappings": reference_root / "indexes" / "report_to_api_mapping.csv",
        "report_model_mappings": reference_root / "indexes" / "report_to_model_mapping.csv",
        "questions": reference_root / "indexes" / "unresolved_questions.csv",
        "api_endpoints": project_root
        / "source_intake"
        / "posist_uat"
        / "restroworks_api_docs_packet"
        / "endpoint_inventory.csv",
        "api_model_seed": project_root
        / "source_intake"
        / "posist_uat"
        / "restroworks_api_docs_packet"
        / "model_mapping_seed.csv",
    }
    curation_files = {
        "mapping_options": atlas_root / "curation" / "mapping_options.csv",
        "validation_tests": atlas_root / "curation" / "validation_tests.csv",
    }
    missing = [str(path) for path in reference_files.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Required source files are missing:\n" + "\n".join(missing))

    reports_raw = read_csv(reference_files["reports"])
    fields_raw = [
        sanitized
        for row in read_csv(reference_files["report_fields"])
        if (sanitized := sanitize_field_row(row)) is not None
    ]
    evidence_raw = read_csv(reference_files["evidence"])
    endpoints_raw = read_csv(reference_files["api_endpoints"])
    api_model_seed = read_csv(reference_files["api_model_seed"])
    report_api_verified = read_csv(reference_files["report_api_mappings"])
    report_model_verified = read_csv(reference_files["report_model_mappings"])
    questions_raw = read_csv(reference_files["questions"])
    mapping_options_raw = read_csv(curation_files["mapping_options"])
    validation_tests_raw = read_csv(curation_files["validation_tests"])

    generated_at = utc_now()
    nodes: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    edges: list[dict[str, Any]] = []
    edge_keys: set[tuple[str, str, str]] = set()

    def push_node(node: dict[str, Any]) -> None:
        if node["id"] in node_ids:
            return
        node_ids.add(node["id"])
        nodes.append(node)

    pages = sorted({row["page"] for row in reports_raw})
    for page in pages:
        push_node(
            {
                "id": f"page:{page}",
                "type": "page",
                "label": page.replace("_", " ").title(),
                "status": "current",
                "priority": "P1" if page == "p4_stock_admin" else "P2",
                "domain": "platform",
                "description": "Restroworks report surface captured in the schema reference.",
            }
        )

    domains = sorted({row.get("priority_domain", "unclassified") for row in reports_raw})
    for domain in domains:
        push_node(
            {
                "id": f"domain:{domain}",
                "type": "domain",
                "label": domain_labels.get(domain, domain.replace("_", " ").title()),
                "status": "current",
                "priority": "P0" if domain != "sales_revenue" else "P2",
                "domain": domain,
                "description": "ABNAH analytical workstream.",
            }
        )

    section_keys = sorted({(row["page"], row["section"]) for row in reports_raw})
    for page, section in section_keys:
        section_node_id = f"section:{page}:{section}"
        push_node(
            {
                "id": section_node_id,
                "type": "section",
                "label": re.sub(r"^\d+_", "", section).replace("_", " ").title(),
                "status": "current",
                "priority": "P1" if page == "p4_stock_admin" else "P2",
                "domain": "platform",
                "page": page,
                "section": section,
                "description": "Report family in the Restroworks navigation hierarchy.",
            }
        )
        add_edge(
            edges,
            edge_keys,
            f"page:{page}",
            section_node_id,
            "contains",
            label="contains section",
        )

    evidence_by_report: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in evidence_raw:
        if row.get("report_folder"):
            evidence_by_report[row["report_folder"]].append(row)

    questions_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in questions_raw:
        questions_by_key[(row.get("page", ""), row.get("section", ""), row.get("report_name", ""))].append(row)

    fields_by_report: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fields_raw:
        fields_by_report[row.get("report_folder", "")].append(row)

    report_records: list[dict[str, Any]] = []
    report_lookup: dict[str, dict[str, Any]] = {}
    for row in reports_raw:
        rid = report_id(row)
        priority, is_core = priority_for_report(row, core_keywords)
        report_fields = sorted(
            fields_by_report.get(row.get("report_folder", ""), []),
            key=lambda item: int(item.get("field_order") or 999999),
        )
        evidence = evidence_by_report.get(row.get("report_folder", ""), [])
        questions = questions_by_key.get((row["page"], row["section"], row["report_name"]), [])
        record = {
            "id": rid,
            "name": row["report_name"],
            "page": row["page"],
            "section": row["section"],
            "report_folder": row["report_folder"],
            "domain": row.get("priority_domain", "unclassified"),
            "priority": priority,
            "is_core": is_core,
            "status": row.get("schema_source_status", "unknown"),
            "capture_method": row.get("capture_method", ""),
            "next_action": row.get("next_action", ""),
            "field_ids": [],
            "evidence_count": len(evidence),
            "questions": questions,
            "api_links": [],
            "model_links": [],
        }
        report_records.append(record)
        report_lookup[rid] = record
        push_node(
            {
                "id": rid,
                "type": "report",
                "label": row["report_name"],
                "status": record["status"],
                "priority": priority,
                "domain": record["domain"],
                "is_core": is_core,
                "page": row["page"],
                "section": row["section"],
                "description": f"{row['report_name']} in {row['section'].replace('_', ' ')}.",
                "evidence_count": len(evidence),
                "field_count": len(report_fields),
                "schema_ready": bool(report_fields),
            }
        )
        add_edge(
            edges,
            edge_keys,
            f"section:{row['page']}:{row['section']}",
            rid,
            "contains",
            label="contains report",
        )
        add_edge(
            edges,
            edge_keys,
            f"domain:{record['domain']}",
            rid,
            "classifies",
            label="analytical domain",
        )

    field_occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fields_raw:
        normalized = row.get("normalized_field_name", "").strip()
        if normalized:
            field_occurrences[normalized].append(row)

    field_records: list[dict[str, Any]] = []
    for normalized, occurrences in sorted(field_occurrences.items()):
        fid = f"field:{normalized}"
        labels = Counter(item.get("raw_header_text", "") for item in occurrences if item.get("raw_header_text"))
        label = labels.most_common(1)[0][0] if labels else normalized.replace("_", " ").title()
        roles = sorted({item.get("semantic_role", "unknown") for item in occurrences})
        types = sorted({item.get("data_type_guess", "unknown") for item in occurrences})
        linked_reports: list[str] = []
        for item in occurrences:
            rid = report_id(item)
            if rid not in report_lookup:
                continue
            linked_reports.append(rid)
            if fid not in report_lookup[rid]["field_ids"]:
                report_lookup[rid]["field_ids"].append(fid)
            add_edge(
                edges,
                edge_keys,
                rid,
                fid,
                "exposes_field",
                label="exposes field",
                status="extracted",
                confidence=0.75 if "ocr" in item.get("source_kind", "") else 0.95,
                rationale="Derived schema candidate; local evidence references are excluded.",
            )
        record = {
            "id": fid,
            "name": normalized,
            "label": label,
            "occurrence_count": len(occurrences),
            "report_ids": sorted(set(linked_reports)),
            "semantic_roles": roles,
            "data_type_guesses": types,
            "status": "ocr_candidate" if any("ocr" in item.get("source_kind", "") for item in occurrences) else "captured",
        }
        field_records.append(record)
        push_node(
            {
                "id": fid,
                "type": "field",
                "label": label,
                "status": record["status"],
                "priority": "P2",
                "domain": "data_point",
                "description": f"Normalized data point seen in {len(set(linked_reports))} report(s).",
                "occurrence_count": len(occurrences),
            }
        )

    endpoint_records: list[dict[str, Any]] = []
    endpoint_by_packet: dict[str, dict[str, Any]] = {}
    for row in endpoints_raw:
        eid = f"api:{row['packet_id'].lower()}"
        priority = row.get("abnah_priority", "P2")
        record = {
            "id": eid,
            **row,
            "status": "documented_public_not_uat_verified",
            "validation_status": "not_tested",
            "validation_test_ids": [],
            "report_links": [],
            "model_links": [],
        }
        endpoint_records.append(record)
        endpoint_by_packet[row["packet_id"]] = record
        push_node(
            {
                "id": eid,
                "type": "api",
                "label": row["endpoint_name"],
                "status": record["status"],
                "priority": priority,
                "domain": (
                    "inventory_consumption"
                    if priority == "P0"
                    else "sales_revenue"
                ),
                "description": row.get("notes", ""),
                "method": row.get("method", ""),
                "path": row.get("path", ""),
                "validation_status": "not_tested",
            }
        )

    for mapping in report_api_verified:
        endpoint = match_endpoint(mapping.get("api_endpoint_candidate", ""), endpoints_raw)
        rid = report_id(mapping)
        if not endpoint or rid not in report_lookup:
            continue
        eid = f"api:{endpoint['packet_id'].lower()}"
        add_edge(
            edges,
            edge_keys,
            rid,
            eid,
            "api_coverage",
            label="verified report/API mapping",
            status=mapping.get("api_coverage_status", "verified"),
            confidence=1.0,
            rationale=mapping.get("evidence", ""),
        )
        report_lookup[rid]["api_links"].append(eid)
        endpoint_by_packet[endpoint["packet_id"]]["report_links"].append(rid)

    for rule in curation["api_report_rules"]:
        endpoint = endpoint_by_packet.get(rule["endpoint_packet_id"])
        if not endpoint:
            continue
        eid = endpoint["id"]
        for report in report_records:
            if report["page"] not in rule["pages"]:
                continue
            haystack = f"{report['name']} {report['section']}".lower()
            if not any(keyword in haystack for keyword in rule["keywords"]):
                continue
            add_edge(
                edges,
                edge_keys,
                report["id"],
                eid,
                "api_coverage",
                label="candidate API coverage",
                status="candidate_not_uat_verified",
                confidence=float(rule["confidence"]),
                rationale=rule["rationale"],
            )
            if eid not in report["api_links"]:
                report["api_links"].append(eid)
            if report["id"] not in endpoint["report_links"]:
                endpoint["report_links"].append(report["id"])

    sql_root = project_root / "docs" / "zoho_query_table_sql"
    model_records, model_dependencies = build_model_catalog(sql_root)
    model_by_name = {model["name"]: model for model in model_records}

    for seed in api_model_seed:
        for model_name in sorted(set(MODEL_TOKEN_RE.findall(seed.get("current_or_candidate_model_target", "")))):
            if model_name not in model_by_name:
                proposed = {
                    "id": f"model:{model_name.lower()}",
                    "name": model_name,
                    "label": readable_model_name(model_name),
                    "layer": model_name.split("_", 1)[0].lower(),
                    "domain": model_domain(model_name),
                    "status": "proposed",
                    "source_path": "API model mapping seed",
                    "description": "Candidate model object proposed during Restroworks API planning.",
                }
                model_records.append(proposed)
                model_by_name[model_name] = proposed

    for model in model_records:
        priority = "P0" if model["domain"] in {"inventory_consumption", "vendor_procurement"} else "P1"
        push_node(
            {
                "id": model["id"],
                "type": "model",
                "label": model["name"],
                "status": model["status"],
                "priority": priority,
                "domain": model["domain"],
                "layer": model["layer"],
                "description": model["description"],
            }
        )

    for dependency in model_dependencies:
        source = model_by_name.get(dependency["source_name"])
        target = model_by_name.get(dependency["target_name"])
        if not source or not target:
            continue
        add_edge(
            edges,
            edge_keys,
            source["id"],
            target["id"],
            "model_depends_on",
            label="depends on",
            rationale=dependency["evidence"],
        )

    for seed in api_model_seed:
        endpoint = match_endpoint(seed.get("api_endpoint_or_mode", ""), endpoints_raw)
        if not endpoint:
            continue
        eid = f"api:{endpoint['packet_id'].lower()}"
        for model_name in sorted(set(MODEL_TOKEN_RE.findall(seed.get("current_or_candidate_model_target", "")))):
            model = model_by_name.get(model_name)
            if not model:
                continue
            add_edge(
                edges,
                edge_keys,
                eid,
                model["id"],
                "api_maps_to_model",
                label="candidate model target",
                status="candidate_not_uat_verified",
                confidence=0.8 if seed.get("fit_status") == "strong" else 0.6,
                rationale=seed.get("open_questions", ""),
            )
            endpoint_by_packet[endpoint["packet_id"]]["model_links"].append(model["id"])

    for mapping in report_model_verified:
        rid = report_id(mapping)
        model = model_by_name.get(mapping.get("current_model_object", ""))
        if rid not in report_lookup or not model:
            continue
        add_edge(
            edges,
            edge_keys,
            rid,
            model["id"],
            "report_maps_to_model",
            label=mapping.get("mapping_type", "report model mapping"),
            status="verified",
            confidence=1.0,
            rationale=mapping.get("validation_rule", ""),
        )
        report_lookup[rid]["model_links"].append(model["id"])

    node_by_id = {node["id"]: node for node in nodes}
    mapping_options: list[dict[str, Any]] = []
    invalid_mapping_refs: list[str] = []
    allowed_mapping_statuses = {"candidate", "selected", "rejected", "deferred"}
    allowed_mapping_relationships = {"report_maps_to_model", "api_maps_to_model"}
    seen_mapping_ids: set[str] = set()
    for index, row in enumerate(mapping_options_raw, start=1):
        source_id = row.get("source_id", "").strip()
        target_id = row.get("target_id", "").strip()
        relationship_type = row.get("relationship_type", "").strip() or "maps_to"
        status = row.get("status", "candidate").strip().lower()
        mapping_id = row.get("mapping_id", "").strip() or f"map-{index:03d}"
        if status not in allowed_mapping_statuses:
            invalid_mapping_refs.append(f"{mapping_id}: invalid status {status}")
            status = "candidate"
        normalized_mapping_id = f"mapping:{slug(mapping_id)}"
        if normalized_mapping_id in seen_mapping_ids:
            invalid_mapping_refs.append(f"{mapping_id}: duplicate mapping ID")
        seen_mapping_ids.add(normalized_mapping_id)
        if relationship_type not in allowed_mapping_relationships:
            invalid_mapping_refs.append(f"{mapping_id}: invalid relationship type {relationship_type}")
        record = {
            "id": normalized_mapping_id,
            "mapping_id": mapping_id,
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type,
            "status": status,
            "confidence": round(max(0.0, min(1.0, number(row.get("confidence", ""), 0.5))), 2),
            "rationale": row.get("rationale", ""),
            "decision_reason": row.get("decision_reason", ""),
            "evidence_ref": row.get("evidence_ref", ""),
            "owner": row.get("owner", ""),
            "updated_at": row.get("updated_at", ""),
        }
        mapping_options.append(record)
        if relationship_type not in allowed_mapping_relationships:
            continue
        source_node = node_by_id.get(source_id)
        target_node = node_by_id.get(target_id)
        if not source_node or not target_node:
            invalid_mapping_refs.append(f"{mapping_id}: unknown source or target ID")
            continue
        if source_node["type"] not in {"report", "api"} or target_node["type"] != "model":
            invalid_mapping_refs.append(f"{mapping_id}: mapping must connect a report/API source to a model target")
            continue
        expected_relationship = f"{source_node['type']}_maps_to_model"
        if relationship_type != expected_relationship:
            invalid_mapping_refs.append(f"{mapping_id}: expected relationship type {expected_relationship}")
            continue
        upsert_edge(
            edges,
            edge_keys,
            source_id,
            target_id,
            relationship_type,
            label="selected mapping" if status == "selected" else "mapping option",
            status=status,
            confidence=record["confidence"],
            rationale=record["decision_reason"] or record["rationale"],
        )

    validation_tests: list[dict[str, Any]] = []
    invalid_validation_refs: list[str] = []
    allowed_validation_statuses = {"planned", "passed", "partial", "failed", "blocked"}
    seen_validation_ids: set[str] = set()
    endpoint_by_id = {endpoint["id"]: endpoint for endpoint in endpoint_records}
    for index, row in enumerate(validation_tests_raw, start=1):
        test_id = row.get("test_id", "").strip() or f"test-{index:03d}"
        subject_id = row.get("subject_id", "").strip()
        status = row.get("status", "planned").strip().lower()
        if status not in allowed_validation_statuses:
            invalid_validation_refs.append(f"{test_id}: invalid status {status}")
            status = "planned"
        validation_id = f"validation:{slug(test_id)}"
        if validation_id in seen_validation_ids:
            invalid_validation_refs.append(f"{test_id}: duplicate validation test ID")
        seen_validation_ids.add(validation_id)
        record = {
            "id": validation_id,
            "test_id": test_id,
            "subject_id": subject_id,
            "test_type": row.get("test_type", "").strip() or "unspecified",
            "status": status,
            "result": row.get("result", ""),
            "evidence_ref": row.get("evidence_ref", ""),
            "tested_at": row.get("tested_at", ""),
            "owner": row.get("owner", ""),
            "notes": row.get("notes", ""),
        }
        validation_tests.append(record)
        subject_node = node_by_id.get(subject_id)
        if not subject_node:
            invalid_validation_refs.append(f"{test_id}: unknown subject ID")
            continue
        push_node(
            {
                "id": validation_id,
                "type": "validation",
                "label": f"{record['test_type'].replace('_', ' ').title()} test",
                "status": status,
                "priority": subject_node.get("priority", "P2"),
                "domain": subject_node.get("domain", "evidence"),
                "description": record["result"] or record["notes"] or "UAT validation record.",
                "subject_id": subject_id,
                "test_type": record["test_type"],
            }
        )
        add_edge(
            edges,
            edge_keys,
            subject_id,
            validation_id,
            "validated_by",
            label="validated by",
            status=status,
            confidence=1.0 if status == "passed" else 0.5,
            rationale=record["result"] or record["notes"],
        )
        subject_node["validation_status"] = status
        endpoint_record = endpoint_by_id.get(subject_id)
        if endpoint_record:
            endpoint_record["validation_status"] = status
            endpoint_record["validation_test_ids"].append(validation_id)

    node_types = Counter(node["type"] for node in nodes)
    edge_types = Counter(edge["type"] for edge in edges)
    reports_with_fields = sum(bool(report["field_ids"]) for report in report_records)
    reports_with_api = sum(bool(report["api_links"]) for report in report_records)
    verified_api_links = sum(
        edge["type"] == "api_coverage" and edge["status"] not in {"candidate_not_uat_verified"}
        for edge in edges
    )
    candidate_relationships = sum("candidate" in edge["status"] for edge in edges)
    selected_mappings = sum(item["status"] == "selected" for item in mapping_options)
    tested_api_ids = {
        item["subject_id"]
        for item in validation_tests
        if item["subject_id"].startswith("api:") and item["status"] != "planned"
    }
    passed_validation_tests = sum(item["status"] == "passed" for item in validation_tests)

    errors: list[str] = []
    warnings: list[str] = []
    all_node_ids = {node["id"] for node in nodes}
    dangling = [edge["id"] for edge in edges if edge["source"] not in all_node_ids or edge["target"] not in all_node_ids]
    if dangling:
        errors.append(f"{len(dangling)} graph edges have missing endpoints.")
    if len(all_node_ids) != len(nodes):
        errors.append("Graph node IDs are not unique.")
    if reports_with_fields < len(report_records):
        warnings.append(f"{len(report_records) - reports_with_fields} reports do not yet have captured fields.")
    if verified_api_links == 0:
        warnings.append("No report-to-API mapping is UAT verified; displayed API links are semantic candidates.")
    if not report_model_verified:
        warnings.append("No report-to-model mapping is verified yet.")
    if not validation_tests:
        warnings.append("No ABNAH UAT validation tests have been recorded yet.")
    if selected_mappings == 0:
        warnings.append("No final relational mapping option has been selected yet.")
    errors.extend(invalid_mapping_refs)
    errors.extend(invalid_validation_refs)

    quality = {
        "status": "failed" if errors else "usable_with_warnings" if warnings else "passed",
        "errors": errors,
        "warnings": warnings,
        "coverage": {
            "reports_total": len(report_records),
            "reports_with_fields": reports_with_fields,
            "reports_with_fields_pct": round(100 * reports_with_fields / max(len(report_records), 1), 1),
            "reports_with_api_candidates_or_verified": reports_with_api,
            "verified_report_api_links": verified_api_links,
            "verified_report_model_links": len(report_model_verified),
            "tested_api_endpoints": len(tested_api_ids),
            "selected_mappings": selected_mappings,
            "validation_tests": len(validation_tests),
            "passed_validation_tests": passed_validation_tests,
        },
    }

    atlas = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "title": "ABNAH Data Discovery Atlas",
        "summary": {
            "reports": len(report_records),
            "reports_with_fields": reports_with_fields,
            "unique_fields": len(field_records),
            "field_occurrences": len(fields_raw),
            "evidence_items": len(evidence_raw),
            "api_endpoints": len(endpoint_records),
            "model_objects": len(model_records),
            "mapping_options": len(mapping_options),
            "selected_mappings": selected_mappings,
            "validation_tests": len(validation_tests),
            "passed_validation_tests": passed_validation_tests,
            "candidate_relationships": candidate_relationships,
            "unresolved_questions": len(questions_raw),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
        },
        "quality": quality,
        "facets": {
            "pages": pages,
            "domains": [{"id": key, "label": domain_labels.get(key, key)} for key in domains],
            "priorities": ["P0", "P1", "P2"],
            "node_types": sorted(node_types),
            "mapping_statuses": ["candidate", "selected", "rejected", "deferred"],
            "validation_statuses": ["planned", "passed", "partial", "failed", "blocked"],
        },
        "nodes": nodes,
        "edges": edges,
        "reports": report_records,
        "fields": field_records,
        "api_endpoints": endpoint_records,
        "models": sorted(model_records, key=lambda item: (item["layer"], item["name"])),
        "mapping_options": mapping_options,
        "validation_tests": validation_tests,
        "unresolved_questions": questions_raw,
    }

    generated_root.mkdir(parents=True, exist_ok=True)
    public_root.mkdir(parents=True, exist_ok=True)
    write_json(generated_root / "atlas.json", atlas)
    write_json(public_root / "atlas.json", atlas)
    write_json(generated_root / "quality_report.json", quality)

    snapshot_records = []
    legacy_evidence_snapshot = source_root / "catalog" / "evidence.csv"
    legacy_evidence_snapshot.unlink(missing_ok=True)
    for logical_name, source_path in {**reference_files, **curation_files}.items():
        if logical_name == "evidence":
            continue
        destination = source_root / "catalog" / f"{logical_name}{source_path.suffix.lower()}"
        snapshot = (
            sanitized_csv_snapshot(source_path, destination, logical_name)
            if source_path.suffix.lower() == ".csv"
            else copy_snapshot(source_path, destination)
        )
        snapshot["snapshot_path"] = destination.relative_to(atlas_root).as_posix()
        snapshot["logical_name"] = logical_name
        snapshot_records.append(snapshot)

    chunk_source = reference_root / "reference_chunks"
    chunk_destination = source_root / "reference_chunks"
    if chunk_source.exists():
        for source_path in chunk_source.rglob("*"):
            if not source_path.is_file():
                continue
            destination = chunk_destination / source_path.relative_to(chunk_source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source_path.suffix.lower() == ".md":
                destination.write_text(
                    sanitize_reference_chunk(source_path.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )
            else:
                shutil.copy2(source_path, destination)

    sql_destination = source_root / "model_sql"
    sql_destination.mkdir(parents=True, exist_ok=True)
    for sql_path in sql_root.glob("*.sql"):
        shutil.copy2(sql_path, sql_destination / sql_path.name)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "portable": True,
        "source_inputs": {
            "schema_reference": "external local input; not packaged",
            "modelling_project": "external local input; not packaged",
        },
        "source_snapshots": snapshot_records,
        "counts": atlas["summary"],
        "quality_status": quality["status"],
        "entry_points": {
            "human": "README.md",
            "developer": "docs/ARCHITECTURE.md",
            "ai_agent": "AGENT_HANDOFF.md",
            "graph_data": "schema-pack/generated/atlas.json",
            "quality": "schema-pack/generated/quality_report.json",
            "mapping_registry": "curation/mapping_options.csv",
            "validation_registry": "curation/validation_tests.csv",
        },
    }
    write_json(output_root / "manifest.json", manifest)

    write_csv(
        generated_root / "report_catalog.csv",
        (
            {
                "report_id": item["id"],
                "report_name": item["name"],
                "page": item["page"],
                "section": item["section"],
                "domain": item["domain"],
                "priority": item["priority"],
                "is_core": item["is_core"],
                "schema_status": item["status"],
                "field_count": len(item["field_ids"]),
                "evidence_count": item["evidence_count"],
                "api_link_count": len(item["api_links"]),
                "model_link_count": len(item["model_links"]),
            }
            for item in report_records
        ),
        [
            "report_id",
            "report_name",
            "page",
            "section",
            "domain",
            "priority",
            "is_core",
            "schema_status",
            "field_count",
            "evidence_count",
            "api_link_count",
            "model_link_count",
        ],
    )
    write_csv(
        generated_root / "field_catalog.csv",
        (
            {
                "field_id": item["id"],
                "field_name": item["name"],
                "display_label": item["label"],
                "report_count": len(item["report_ids"]),
                "occurrence_count": item["occurrence_count"],
                "semantic_roles": "|".join(item["semantic_roles"]),
                "data_type_guesses": "|".join(item["data_type_guesses"]),
                "status": item["status"],
            }
            for item in field_records
        ),
        [
            "field_id",
            "field_name",
            "display_label",
            "report_count",
            "occurrence_count",
            "semantic_roles",
            "data_type_guesses",
            "status",
        ],
    )
    write_csv(
        generated_root / "edge_catalog.csv",
        edges,
        ["id", "source", "target", "type", "label", "status", "confidence", "rationale"],
    )
    write_csv(
        generated_root / "api_catalog.csv",
        (
            {
                "api_id": item["id"],
                "packet_id": item["packet_id"],
                "name": item["endpoint_name"],
                "method": item["method"],
                "path": item["path"],
                "priority": item["abnah_priority"],
                "status": item["status"],
                "report_link_count": len(item["report_links"]),
                "model_link_count": len(item["model_links"]),
            }
            for item in endpoint_records
        ),
        [
            "api_id",
            "packet_id",
            "name",
            "method",
            "path",
            "priority",
            "status",
            "report_link_count",
            "model_link_count",
        ],
    )
    write_csv(
        generated_root / "model_catalog.csv",
        (
            {
                "model_id": item["id"],
                "name": item["name"],
                "layer": item["layer"],
                "domain": item["domain"],
                "status": item["status"],
                "source_path": item["source_path"],
                "description": item["description"],
            }
            for item in model_records
        ),
        ["model_id", "name", "layer", "domain", "status", "source_path", "description"],
    )
    write_csv(
        generated_root / "mapping_option_catalog.csv",
        mapping_options,
        [
            "id",
            "mapping_id",
            "source_id",
            "target_id",
            "relationship_type",
            "status",
            "confidence",
            "rationale",
            "decision_reason",
            "evidence_ref",
            "owner",
            "updated_at",
        ],
    )
    write_csv(
        generated_root / "validation_test_catalog.csv",
        validation_tests,
        [
            "id",
            "test_id",
            "subject_id",
            "test_type",
            "status",
            "result",
            "evidence_ref",
            "tested_at",
            "owner",
            "notes",
        ],
    )

    core_reports = [item for item in report_records if item["is_core"]]
    agent_context = [
        "# ABNAH Data Discovery Atlas Agent Context",
        "",
        f"Generated: `{generated_at}`",
        f"Schema contract: `{SCHEMA_VERSION}`",
        "",
        "## Start Here",
        "",
        "1. Read `manifest.json` and `generated/quality_report.json`.",
        "2. Query `generated/atlas.json` by stable node IDs; do not infer relationships from labels alone.",
        "3. Treat `candidate_not_uat_verified` edges as hypotheses until ABNAH UAT samples confirm them.",
        "4. Use `source/reference_chunks/` for report-level OCR/header evidence.",
        "5. Keep Inventory & Consumption and Vendor & Procurement as phase-1 priorities.",
        "",
        "## Current Snapshot",
        "",
        f"- Reports: `{len(report_records)}`",
        f"- Reports with fields: `{reports_with_fields}`",
        f"- Unique normalized fields: `{len(field_records)}`",
        f"- API endpoints: `{len(endpoint_records)}`",
        f"- Model objects: `{len(model_records)}`",
        f"- Core phase-1 reports: `{len(core_reports)}`",
        f"- Recorded validation tests: `{len(validation_tests)}`",
        f"- Selected relational mappings: `{selected_mappings}`",
        "",
        "## Non-Negotiable Evidence Rule",
        "",
        "Never present semantic API candidates as exact report coverage. Promote an edge to verified only after endpoint payload, grain, filters, calculations and ABNAH UAT availability are checked.",
        "Keep factual discovery separate from mapping decisions. Record alternatives, decisions and tests in the curation registries instead of rewriting source discovery records.",
        "",
        "## Core Reports",
        "",
    ]
    agent_context.extend(f"- `{item['id']}`: {item['name']}" for item in core_reports)
    (generated_root / "AGENT_CONTEXT.md").write_text("\n".join(agent_context) + "\n", encoding="utf-8")

    if errors:
        raise RuntimeError("Atlas validation failed during build: " + "; ".join(errors))
    return atlas


def parse_args() -> argparse.Namespace:
    atlas_root = Path(__file__).resolve().parents[1]
    sibling_root = atlas_root.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference-root",
        default=str(sibling_root / "POSist Schema Reference"),
        help="POSist Schema Reference folder.",
    )
    parser.add_argument(
        "--project-root",
        default=str(sibling_root / "abnah-zoho-synthetic-demo"),
        help="ABNAH modelling project containing API packet and Zoho SQL.",
    )
    parser.add_argument(
        "--output-root",
        default=str(atlas_root / "schema-pack"),
        help="Portable schema-pack output folder.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    result = build(parse_args())
    summary = result["summary"]
    print(
        "Built ABNAH Data Discovery Atlas: "
        f"{summary['reports']} reports, {summary['unique_fields']} fields, "
        f"{summary['api_endpoints']} APIs, {summary['model_objects']} model objects."
    )
