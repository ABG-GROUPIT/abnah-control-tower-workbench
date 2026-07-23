#!/usr/bin/env python3
"""Serve full local audit reports with deterministic issue highlighting.

This viewer binds only to a loopback address. It reads normalized CSV evidence
from LOCAL_EVIDENCE_DO_NOT_UPLOAD and never sends report rows to the hosted
Schema Atlas.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import os
import re
import threading
import webbrowser
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from issue_taxonomy import (
    SEVERITY_ORDER,
    classify_deterministic_issue,
    highest_severity,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "output"
VIEWER_HTML = ROOT / "local_report_viewer.html"


def stable_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def normalized_file_key(value: str) -> str:
    return os.path.normcase(os.path.normpath(value))


def rule_fields(rule: dict[str, Any]) -> list[str]:
    fields: list[str] = []
    for key in ("target", "left", "right", "field", "revenue", "cost", "earlier", "later"):
        if rule.get(key):
            fields.append(str(rule[key]))
    fields.extend(str(term["field"]) for term in rule.get("terms") or [])
    return list(dict.fromkeys(fields))


def latest_audit_run(output_dir: Path) -> Path:
    candidates = [
        path
        for path in output_dir.iterdir()
        if path.is_dir()
        and (path / "LOCAL_EVIDENCE_DO_NOT_UPLOAD" / "full_profiles_with_local_samples.json").exists()
    ]
    if not candidates:
        raise FileNotFoundError(f"No completed audit run found under {output_dir}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


class AuditDataset:
    def __init__(self, audit_run: Path, contracts_dir: Path) -> None:
        self.audit_run = audit_run.resolve()
        self.local_dir = self.audit_run / "LOCAL_EVIDENCE_DO_NOT_UPLOAD"
        self.normalized_dir = self.local_dir / "deterministic_audit" / "normalized"
        profiles_path = self.local_dir / "full_profiles_with_local_samples.json"
        issues_path = self.local_dir / "deterministic_audit" / "issues.csv"
        if not profiles_path.exists() or not issues_path.exists():
            raise FileNotFoundError(
                "The selected folder is not a completed local audit run with deterministic evidence."
            )

        self.profiles: list[dict[str, Any]] = json.loads(
            profiles_path.read_text(encoding="utf-8")
        )
        with issues_path.open(encoding="utf-8-sig", newline="") as handle:
            self.issues = list(csv.DictReader(handle))
        business_review_path = self.local_dir / "business_review.json"
        self.business_review: dict[str, Any] = (
            json.loads(business_review_path.read_text(encoding="utf-8"))
            if business_review_path.exists()
            else {"findings": [], "controls": [], "row_issues": []}
        )
        self.local_packet_path = self.local_dir / "local_review_packet.json"

        self.contracts: dict[str, dict[str, Any]] = {}
        for path in contracts_dir.glob("*.json"):
            contract = json.loads(path.read_text(encoding="utf-8"))
            self.contracts[contract["report_id"]] = contract

        self.profile_by_id: dict[str, dict[str, Any]] = {}
        self.profile_ids_by_report: dict[str, list[str]] = defaultdict(list)
        self.state_by_profile_id: dict[str, dict[str, Any]] = {}
        for profile in self.profiles:
            profile_id = stable_id(profile["file"])
            self.profile_by_id[profile_id] = profile
            self.profile_ids_by_report[profile["report_id"]].append(profile_id)

        self.issues_by_row: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
        for issue in self.issues:
            if not issue.get("row_number"):
                continue
            profile_file = normalized_file_key(issue["file"])
            report_id = issue["report_id"]
            rules = {
                rule["id"]: rule
                for rule in self.contracts.get(report_id, {}).get("rules") or []
            }
            rule = rules.get(issue.get("rule_id", ""), {})
            fields = rule_fields(rule)
            if issue.get("field"):
                fields.append(issue["field"])
            classification = classify_deterministic_issue(issue)
            entry = {
                "rule_id": issue.get("rule_id", ""),
                "phase": issue.get("phase", ""),
                **classification,
                "source": "deterministic_contract",
                "title": issue.get("message", ""),
                "message": issue.get("message", ""),
                "expected": issue.get("expected", ""),
                "observed": issue.get("observed", ""),
                "fields": list(dict.fromkeys(fields)),
                "production_treatment": (
                    "Preserve the source value and confirm the governing business definition."
                ),
            }
            self.issues_by_row[(profile_file, int(issue["row_number"]))].append(entry)
        for issue in self.business_review.get("row_issues") or []:
            profile_file = normalized_file_key(issue["file"])
            entry = {
                "rule_id": issue.get("finding_id", ""),
                "phase": "business_review",
                "severity": issue.get("severity", "major"),
                "issue_class": issue.get("issue_class", "business_logic"),
                "state": issue.get("state", "needs_business_definition"),
                "confidence": issue.get("confidence", "medium"),
                "impact_abs": issue.get("impact_abs", ""),
                "impact_pct": issue.get("impact_pct", ""),
                "source": "codex_business_review",
                "title": issue.get("title", ""),
                "message": issue.get("message", ""),
                "expected": issue.get("expected", ""),
                "observed": issue.get("observed", ""),
                "fields": issue.get("fields") or [],
                "production_treatment": issue.get("production_treatment", ""),
            }
            self.issues_by_row[(profile_file, int(issue["row_number"]))].append(entry)

        self.findings_by_report: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for finding in self.business_review.get("findings") or []:
            self.findings_by_report[finding["report_id"]].append(finding)
        self.controls_by_report: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for control in self.business_review.get("controls") or []:
            for report_id in control.get("reports") or []:
                self.controls_by_report[report_id].append(control)

    def normalized_path(self, profile: dict[str, Any]) -> Path:
        return self.normalized_dir / f"{Path(profile['file']).stem}__normalized.csv"

    def normalized_rows(
        self, profile: dict[str, Any]
    ) -> tuple[tuple[str, ...], tuple[dict[str, str], ...]]:
        path = self.normalized_path(profile)
        if path.exists():
            return self.read_rows(str(path))
        if int(profile.get("rows", {}).get("source_count", 0)) == 0:
            columns = tuple(
                str(field["field"]) for field in profile.get("fields") or []
            )
            return columns, ()
        raise FileNotFoundError(
            f"Normalized export is missing for {profile['display_name']}"
        )

    def cell_state_summary(self, profile_id: str) -> dict[str, Any]:
        cached = self.state_by_profile_id.get(profile_id)
        if cached:
            return cached
        profile = self.profile_by_id[profile_id]
        columns, rows = self.normalized_rows(profile)
        field_profiles = {
            field["field"]: field for field in profile.get("fields") or []
        }
        column_types = {
            column: str(field_profiles.get(column, {}).get("declared_type", "text"))
            for column in columns
        }
        expected_null = sum(
            int(field_profiles.get(column, {}).get("null_count", 0))
            for column in columns
        )
        expected_zero = sum(
            int(field_profiles.get(column, {}).get("zero_count", 0))
            for column in columns
            if column_types[column] == "decimal"
        )
        observed_null = 0
        observed_zero = 0
        for row in rows:
            for column in columns:
                value = (row.get(column) or "").strip()
                if not value:
                    observed_null += 1
                elif column_types[column] == "decimal":
                    try:
                        if Decimal(value) == 0:
                            observed_zero += 1
                    except InvalidOperation:
                        pass
        expected_rows = int(
            profile.get("rows", {}).get(
                "valid_width_count",
                profile.get("rows", {}).get("source_count", len(rows)),
            )
        )
        summary = {
            "source_null_cell_count": expected_null,
            "source_numeric_zero_cell_count": expected_zero,
            "normalized_null_cell_count": observed_null,
            "normalized_numeric_zero_cell_count": observed_zero,
            "normalization_fidelity": (
                "verified"
                if expected_rows == len(rows)
                and expected_null == observed_null
                and expected_zero == observed_zero
                else "difference_detected"
            ),
            "column_types": column_types,
        }
        self.state_by_profile_id[profile_id] = summary
        return summary

    @staticmethod
    @lru_cache(maxsize=32)
    def read_rows(path_text: str) -> tuple[tuple[str, ...], tuple[dict[str, str], ...]]:
        path = Path(path_text)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = tuple(reader.fieldnames or [])
            rows = tuple(dict(row) for row in reader)
        return columns, rows

    def report_index(self) -> dict[str, Any]:
        reports = []
        for report_id, profile_ids in sorted(
            self.profile_ids_by_report.items(),
            key=lambda item: self.profile_by_id[item[1][0]]["display_name"],
        ):
            exports = []
            for profile_id in profile_ids:
                profile = self.profile_by_id[profile_id]
                profile_file = normalized_file_key(profile["file"])
                issue_rows = {}
                issue_counts: Counter[str] = Counter()
                for (file_key, row_number), row_issues in self.issues_by_row.items():
                    if file_key != profile_file or not row_issues:
                        continue
                    issue_rows[row_number] = row_issues
                    issue_counts.update(issue["severity"] for issue in row_issues)
                exports.append(
                    {
                        "id": profile_id,
                        "label": profile["file_name"],
                        "row_count": int(profile["rows"]["source_count"]),
                        "issue_row_count": len(issue_rows),
                        "issue_counts": dict(issue_counts),
                        "cell_state": self.cell_state_summary(profile_id),
                    }
                )
            report_issue_counts: Counter[str] = Counter()
            for export in exports:
                report_issue_counts.update(export["issue_counts"])
            findings = self.findings_by_report.get(report_id, [])
            finding_counts = Counter(finding["severity"] for finding in findings)
            reports.append(
                {
                    "report_id": report_id,
                    "display_name": self.profile_by_id[profile_ids[0]]["display_name"],
                    "row_count": sum(item["row_count"] for item in exports),
                    "issue_row_count": sum(item["issue_row_count"] for item in exports),
                    "issue_counts": dict(report_issue_counts),
                    "finding_counts": dict(finding_counts),
                    "finding_count": len(findings),
                    "highest_severity": highest_severity(
                        [finding["severity"] for finding in findings]
                        + list(report_issue_counts.elements())
                    ),
                    "passed_control_count": sum(
                        control["status"] == "passed"
                        for control in self.controls_by_report.get(report_id, [])
                    ),
                    "exports": exports,
                }
            )
        all_findings = self.business_review.get("findings") or []
        all_row_issues = [
            issue
            for row_issues in self.issues_by_row.values()
            for issue in row_issues
        ]
        return {
            "audit_run_label": self.audit_run.name,
            "business_review_version": self.business_review.get("contract_version", ""),
            "summary": {
                "finding_counts": dict(Counter(item["severity"] for item in all_findings)),
                "row_issue_counts": dict(Counter(item["severity"] for item in all_row_issues)),
                "finding_count": len(all_findings),
                "row_observation_count": len(all_row_issues),
                "passed_control_count": sum(
                    item["status"] == "passed"
                    for item in self.business_review.get("controls") or []
                ),
                "failed_control_count": sum(
                    item["status"] == "failed"
                    for item in self.business_review.get("controls") or []
                ),
                "local_packet_available": self.local_packet_path.exists(),
            },
            "reports": reports,
        }

    def report_page(
        self,
        profile_id: str,
        page: int,
        page_size: int,
        issues_only: bool,
        query: str,
        severity: str = "all",
        issue_class: str = "all",
        state: str = "all",
    ) -> dict[str, Any]:
        profile = self.profile_by_id.get(profile_id)
        if not profile:
            raise KeyError("Unknown export")
        columns, source_rows = self.normalized_rows(profile)
        cell_state = self.cell_state_summary(profile_id)
        header_row = int(profile["schema"].get("header_row_number", 1))
        file_key = normalized_file_key(profile["file"])
        query_folded = query.casefold().strip()
        filtered: list[tuple[int, dict[str, str], list[dict[str, Any]]]] = []
        for index, row in enumerate(source_rows):
            source_row_number = header_row + index + 1
            row_issues = self.issues_by_row.get((file_key, source_row_number), [])
            if severity != "all":
                row_issues = [
                    issue for issue in row_issues if issue["severity"] == severity
                ]
            if issue_class != "all":
                row_issues = [
                    issue for issue in row_issues if issue["issue_class"] == issue_class
                ]
            if state != "all":
                row_issues = [issue for issue in row_issues if issue["state"] == state]
            if issues_only and not row_issues:
                continue
            if query_folded and not any(
                query_folded in str(value).casefold() for value in row.values()
            ):
                continue
            filtered.append((source_row_number, row, row_issues))

        page_size = max(25, min(250, page_size))
        page_count = max(1, (len(filtered) + page_size - 1) // page_size)
        page = max(1, min(page, page_count))
        start = (page - 1) * page_size
        visible = filtered[start : start + page_size]
        return {
            "report_id": profile["report_id"],
            "display_name": profile["display_name"],
            "export_id": profile_id,
            "export_label": profile["file_name"],
            "columns": list(columns),
            "column_types": cell_state["column_types"],
            "cell_state": {
                key: value
                for key, value in cell_state.items()
                if key != "column_types"
            },
            "source_row_count": len(source_rows),
            "filtered_row_count": len(filtered),
            "page": page,
            "page_count": page_count,
            "page_size": page_size,
            "rows": [
                {
                    "source_row_number": row_number,
                    "values": row,
                    "issues": row_issues,
                    "highest_severity": highest_severity(
                        [issue["severity"] for issue in row_issues]
                    ),
                    "issue_fields": list(
                        dict.fromkeys(
                            field
                            for issue in row_issues
                            for field in issue.get("fields") or []
                        )
                    ),
                }
                for row_number, row, row_issues in visible
            ],
            "findings": self.findings_by_report.get(profile["report_id"], []),
            "controls": self.controls_by_report.get(profile["report_id"], []),
            "severity_order": SEVERITY_ORDER,
        }


class ViewerServer(ThreadingHTTPServer):
    dataset: AuditDataset


class ViewerHandler(BaseHTTPRequestHandler):
    server: ViewerServer

    def log_message(self, format_string: str, *args: Any) -> None:
        print(f"[viewer] {self.address_string()} {format_string % args}")

    def send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            "connect-src 'self'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def send_download(self, path: Path, file_name: str) -> None:
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header(
            "Content-Disposition",
            f'attachment; filename="{file_name}"',
        )
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, value: Any, status: int = 200) -> None:
        self.send_bytes(
            json.dumps(value, ensure_ascii=True).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
        )

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self.send_bytes(
                    VIEWER_HTML.read_bytes(),
                    "text/html; charset=utf-8",
                )
                return
            if parsed.path == "/api/reports":
                self.send_json(self.server.dataset.report_index())
                return
            if parsed.path == "/api/local-packet":
                if not self.server.dataset.local_packet_path.exists():
                    self.send_json(
                        {"error": "Run business_review.py to generate the local packet."},
                        HTTPStatus.NOT_FOUND,
                    )
                    return
                self.send_download(
                    self.server.dataset.local_packet_path,
                    "abnah-local-review-packet.json",
                )
                return
            if parsed.path == "/api/report":
                query = parse_qs(parsed.query)
                export_id = (query.get("export_id") or [""])[0]
                page = int((query.get("page") or ["1"])[0])
                page_size = int((query.get("page_size") or ["100"])[0])
                issues_only = (query.get("issues_only") or ["false"])[0].lower() == "true"
                search = (query.get("q") or [""])[0]
                severity = (query.get("severity") or ["all"])[0]
                issue_class = (query.get("issue_class") or ["all"])[0]
                state = (query.get("state") or ["all"])[0]
                self.send_json(
                    self.server.dataset.report_page(
                        export_id,
                        page,
                        page_size,
                        issues_only,
                        search,
                        severity,
                        issue_class,
                        state,
                    )
                )
                return
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except (KeyError, ValueError) as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except FileNotFoundError as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover - final local safety net
            self.send_json({"error": f"Viewer error: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)


def validate_loopback(host: str) -> str:
    if host.lower() == "localhost":
        return "127.0.0.1"
    try:
        if ipaddress.ip_address(host).is_loopback:
            return host
    except ValueError:
        pass
    raise ValueError("The report viewer may bind only to localhost or a loopback IP.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-run",
        type=Path,
        help="Completed audit run. Defaults to the newest run under local_data_auditor/output.",
    )
    parser.add_argument("--contracts", type=Path, default=ROOT / "contracts")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open the local viewer in the default browser.")
    parser.add_argument(
        "--report-id",
        default="",
        help="Optional report to select when the viewer opens.",
    )
    args = parser.parse_args()

    audit_run = args.audit_run or latest_audit_run(DEFAULT_OUTPUT)
    host = validate_loopback(args.host)
    dataset = AuditDataset(audit_run, args.contracts)
    server = ViewerServer((host, args.port), ViewerHandler)
    server.dataset = dataset
    query = urlencode({"report_id": args.report_id}) if args.report_id else ""
    url = f"http://{host}:{args.port}/" + (f"?{query}" if query else "")
    print(f"ABNAH local report reviewer: {url}")
    print(f"Audit run: {audit_run.resolve()}")
    print("Press Ctrl+C to stop. Full report values remain on this PC.")
    if args.open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
