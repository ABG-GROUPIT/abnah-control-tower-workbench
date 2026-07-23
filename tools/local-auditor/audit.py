#!/usr/bin/env python3
"""Local, contract-driven auditor for ABNAH Restroworks CSV exports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable


NULL_TOKENS = {"", "na", "n/a", "null", "none", "-"}
DATE_FORMATS = (
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%d-%b-%Y",
    "%d %b %Y",
    "%d-%m-%Y %H:%M",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y %I:%M %p",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%d-%b-%Y %H:%M:%S",
)


@dataclass
class Issue:
    file: str
    report_id: str
    row_number: int | None
    phase: str
    rule_id: str
    severity: str
    field: str
    message: str
    expected: str = ""
    observed: str = ""

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class FileResult:
    file: str
    report_id: str
    display_name: str
    sha256: str
    source_rows: int = 0
    normalized_rows: int = 0
    skipped_rows: int = 0
    header_row_number: int = 1
    auxiliary_rows: int = 0
    issues: list[Issue] = field(default_factory=list)

    def counts(self) -> Counter[str]:
        return Counter(issue.severity for issue in self.issues)


def normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\ufeff", "").strip())


def text_value(value: str) -> str | None:
    value = value.strip()
    return None if value.lower() in NULL_TOKENS else value


def decimal_value(value: str) -> Decimal | None:
    raw = value.strip()
    if raw.lower() in NULL_TOKENS:
        return None
    negative = raw.startswith("(") and raw.endswith(")")
    cleaned = (
        raw.strip("()")
        .replace(",", "")
        .replace("\u20b9", "")
        .replace("$", "")
        .replace("%", "")
        .strip()
    )
    try:
        number = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"not a decimal: {raw}") from exc
    return -number if negative else number


def date_value(value: str) -> datetime | None:
    raw = value.strip()
    if raw.lower() in NULL_TOKENS:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"unrecognized date: {raw}")


def parse_value(value: str, kind: str) -> Any:
    if kind == "decimal":
        return decimal_value(value)
    if kind == "date":
        return date_value(value)
    return text_value(value)


def display_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    return str(value)


def close_enough(actual: Decimal, expected: Decimal, rule: dict[str, Any]) -> bool:
    absolute = Decimal(str(rule.get("tolerance", "0.01")))
    relative = Decimal(str(rule.get("relative_tolerance", "0")))
    allowed = max(absolute, abs(expected) * relative)
    return abs(actual - expected) <= allowed


def displayed_half_unit(value: Decimal, configured_places: int) -> Decimal:
    """Return half a displayed unit while preserving any extra exported precision."""
    observed_places = max(0, -value.as_tuple().exponent)
    places = max(configured_places, observed_places)
    return Decimal(5).scaleb(-places - 1)


def product_rounding_tolerance(
    left: Decimal,
    right: Decimal,
    target: Decimal,
    rule: dict[str, Any],
) -> Decimal:
    precision = rule.get("display_rounding")
    if not precision:
        return Decimal(0)
    left_half = displayed_half_unit(left, int(precision["left_decimals"]))
    right_half = displayed_half_unit(right, int(precision["right_decimals"]))
    target_half = displayed_half_unit(target, int(precision["target_decimals"]))
    return (
        abs(right) * left_half
        + abs(left) * right_half
        + left_half * right_half
        + target_half
    )


def condition_met(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    for name in rule.get("only_when_zero", []):
        value = row.get(name)
        if value is not None and value != 0:
            return False
    for name in rule.get("only_when_present", []):
        if row.get(name) is None:
            return False
    return True


def evaluate_rule(
    rule: dict[str, Any], row: dict[str, Any]
) -> tuple[bool, str, str, str] | None:
    if not condition_met(row, rule):
        return None
    kind = rule["type"]
    target_name = rule.get("target", "")
    target = row.get(target_name) if target_name else None

    if kind == "zero_only":
        value = row.get(rule["field"])
        if value is None or value == 0:
            return True, "0", display_value(value), rule["field"]
        return False, "0 until the missing source label is identified", display_value(value), rule["field"]

    if kind == "nonnegative":
        value = row.get(rule["field"])
        if value is None:
            return None
        return value >= 0, ">= 0", display_value(value), rule["field"]

    if kind == "date_order":
        earlier = row.get(rule["earlier"])
        later = row.get(rule["later"])
        if earlier is None or later is None:
            return None
        return later >= earlier, f"{rule['later']} >= {rule['earlier']}", display_value(later), rule["later"]

    if kind == "less_or_equal":
        left = row.get(rule["left"])
        right = row.get(rule["right"])
        if left is None or right is None:
            return None
        return (
            left <= right,
            f"{rule['left']} <= {rule['right']}",
            f"{display_value(left)} > {display_value(right)}" if left > right else display_value(left),
            rule["left"],
        )

    if target is None:
        return None

    if kind == "sum_equals":
        terms: list[Decimal] = []
        expression: list[str] = []
        for term in rule["terms"]:
            value = row.get(term["field"])
            if value is None:
                if term.get("null_as_zero", False):
                    value = Decimal(0)
                else:
                    return None
            coefficient = Decimal(str(term.get("coefficient", 1)))
            terms.append(coefficient * value)
            expression.append(f"{coefficient}*{term['field']}")
        expected = sum(terms, Decimal(0))
        return (
            close_enough(target, expected, rule),
            f"{target_name} = {' + '.join(expression)} = {expected}",
            display_value(target),
            target_name,
        )

    if kind == "product_equals":
        left = row.get(rule["left"])
        right = row.get(rule["right"])
        if left is None or right is None:
            return None
        expected = left * right
        absolute = Decimal(str(rule.get("tolerance", "0.01")))
        relative = Decimal(str(rule.get("relative_tolerance", "0")))
        allowed = max(
            absolute,
            abs(expected) * relative,
            product_rounding_tolerance(left, right, target, rule),
        )
        return (
            abs(target - expected) <= allowed,
            (
                f"{target_name} = {rule['left']} * {rule['right']} = {expected} "
                f"(allowed difference {allowed})"
            ),
            display_value(target),
            target_name,
        )

    if kind == "percent_of":
        base = row.get(rule["base"])
        if base is None:
            return None
        percent = Decimal(str(rule["percent"]))
        expected = base * percent / Decimal(100)
        return (
            close_enough(target, expected, rule),
            f"{target_name} = {rule['base']} * {percent} / 100 = {expected}",
            display_value(target),
            target_name,
        )

    if kind == "equals_field":
        source = row.get(rule["source"])
        if source is None:
            return None
        return (
            close_enough(target, source, rule),
            f"{target_name} = {rule['source']} = {source}",
            display_value(target),
            target_name,
        )

    if kind == "ratio_percent":
        numerator = row.get(rule["numerator"])
        denominator = row.get(rule["denominator"])
        if numerator is None or denominator in (None, 0):
            return None
        expected = numerator / denominator * Decimal(100)
        return (
            close_enough(target, expected, rule),
            f"{target_name} = {rule['numerator']} / {rule['denominator']} * 100 = {expected}",
            display_value(target),
            target_name,
        )

    if kind == "margin_percent":
        revenue = row.get(rule["revenue"])
        cost = row.get(rule["cost"])
        if revenue in (None, 0) or cost is None:
            return None
        if cost == 0 and rule.get("skip_when_cost_zero", False):
            return None
        expected = (revenue - cost) / revenue * Decimal(100)
        passed = close_enough(target, expected, rule)
        cost_tolerance = rule.get("implied_cost_tolerance")
        if not passed and cost_tolerance is not None:
            implied_cost = revenue * (Decimal(1) - target / Decimal(100))
            passed = abs(implied_cost - cost) <= Decimal(str(cost_tolerance))
        return (
            passed,
            f"{target_name} = ({rule['revenue']} - {rule['cost']}) / {rule['revenue']} * 100 = {expected}",
            display_value(target),
            target_name,
        )

    raise ValueError(f"Unsupported rule type: {kind}")


def load_contracts(contract_dir: Path) -> list[dict[str, Any]]:
    contracts = []
    for path in sorted(contract_dir.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            contract = json.load(handle)
        contract["_path"] = str(path)
        contracts.append(contract)
    return contracts


def match_contract(path: Path, contracts: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    for contract in contracts:
        if any(re.search(pattern, path.name) for pattern in contract["filename_regexes"]):
            return contract
    return None


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_csv(path: Path):
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            handle = path.open(encoding=encoding, newline="")
            handle.read(4096)
            handle.seek(0)
            return handle
        except UnicodeDecodeError:
            handle.close()
    raise UnicodeDecodeError("csv", b"", 0, 1, "unsupported encoding")


def trim_export_padding(row: list[str], target_width: int, max_trailing: int) -> list[str]:
    trimmed = list(row)
    removed = 0
    while len(trimmed) > target_width and removed < max_trailing and not trimmed[-1].strip():
        trimmed.pop()
        removed += 1
    return trimmed


def normalized_header_row(row: list[str]) -> list[str]:
    normalized = [normalize_header(value) for value in row]
    while normalized and not normalized[-1]:
        normalized.pop()
    return normalized


def find_contract_header(path: Path, contract: dict[str, Any]) -> tuple[list[str], int]:
    """Locate a literal report header while keeping preamble rows out of the data audit."""
    search_rows = max(1, int(contract.get("header_search_rows", 1)))
    expected = normalized_header_row(contract["expected_header"])
    candidates: list[tuple[list[str], int]] = []
    with open_csv(path) as handle:
        reader = csv.reader(handle)
        for row_number, row in enumerate(reader, start=1):
            candidates.append((row, row_number))
            if normalized_header_row(row) == expected:
                return row, row_number
            if row_number >= search_rows:
                break
    if not candidates:
        return [], 0

    def similarity(candidate: tuple[list[str], int]) -> float:
        observed = normalized_header_row(candidate[0])
        sequence = SequenceMatcher(a=expected, b=observed, autojunk=False).ratio()
        width = 1 - min(abs(len(expected) - len(observed)), max(len(expected), 1)) / max(
            len(expected), 1
        )
        return sequence * 0.8 + width * 0.2

    return max(candidates, key=similarity)


def prepare_contract_row(
    source_row: list[str],
    contract: dict[str, Any],
    adapter_state: dict[int, str],
) -> tuple[str, list[str] | None]:
    """Return data, blank, auxiliary or malformed for one post-header export row."""
    if not any(value.strip() for value in source_row):
        return "blank", None
    if normalized_header_row(source_row) == normalized_header_row(contract["expected_header"]):
        return "auxiliary", None
    if len(source_row) in set(contract.get("auxiliary_row_widths", [])):
        return "auxiliary", None
    auxiliary_blank_positions = [
        int(value) for value in contract.get("auxiliary_when_all_blank_positions", [])
    ]
    if auxiliary_blank_positions and all(
        position >= len(source_row) or not source_row[position].strip()
        for position in auxiliary_blank_positions
    ):
        return "auxiliary", None

    columns = contract["row_columns"]
    row = trim_export_padding(
        source_row,
        len(columns),
        int(contract.get("max_trailing_empty_fields", 0)),
    )
    adapter = contract.get("row_adapter", {})
    if adapter.get("type") != "hierarchical_forward_fill":
        return ("data", row) if len(row) == len(columns) else ("malformed", row)

    if len(row) != len(columns):
        return "malformed", row
    context_positions = [int(value) for value in adapter.get("context_positions", [])]
    detail_positions = [int(value) for value in adapter.get("detail_positions", [])]
    has_detail = any(row[position].strip() for position in detail_positions)
    for position in context_positions:
        if row[position].strip():
            adapter_state[position] = row[position]
    if not has_detail and adapter.get("skip_rows_without_detail", True):
        return "auxiliary", None
    for position in context_positions:
        if not row[position].strip() and position in adapter_state:
            row[position] = adapter_state[position]
    return "data", row


def audit_file(path: Path, contract: dict[str, Any], normalized_dir: Path) -> FileResult:
    result = FileResult(
        file=str(path),
        report_id=contract["report_id"],
        display_name=contract["display_name"],
        sha256=file_hash(path),
    )
    columns = contract["row_columns"]
    normalized_rows: list[dict[str, str]] = []
    sensitive = {column["name"] for column in columns if column.get("sensitive")}
    source_header, header_row_number = find_contract_header(path, contract)
    result.header_row_number = header_row_number

    if not source_header:
        result.issues.append(
            Issue(str(path), result.report_id, None, "structure", "empty_file", "error", "", "CSV is empty")
        )
        return result

    observed_header = normalized_header_row(source_header)
    expected_normalized = normalized_header_row(contract["expected_header"])
    if observed_header != expected_normalized:
        result.issues.append(
            Issue(
                str(path), result.report_id, header_row_number or 1, "structure", "header_contract", "error", "header",
                "Export header does not match the report contract.",
                json.dumps(expected_normalized, ensure_ascii=False),
                json.dumps(observed_header, ensure_ascii=False),
            )
        )

    adapter_state: dict[int, str] = {}
    with open_csv(path) as handle:
        reader = csv.reader(handle)
        for _ in range(header_row_number):
            try:
                next(reader)
            except StopIteration:
                break
        for row_number, source_row in enumerate(reader, start=header_row_number + 1):
            status, row = prepare_contract_row(source_row, contract, adapter_state)
            if status == "blank":
                result.skipped_rows += 1
                continue
            if status == "auxiliary":
                result.skipped_rows += 1
                result.auxiliary_rows += 1
                continue
            result.source_rows += 1
            if status == "malformed" or row is None:
                result.issues.append(
                    Issue(
                        str(path), result.report_id, row_number, "structure", "row_width", "error", "row",
                        "Row cell count does not match the semantic row contract.",
                        str(len(columns)), str(len(row or [])),
                    )
                )
                continue

            parsed: dict[str, Any] = {}
            normalized: dict[str, str] = {}
            row_failed = False
            for column, raw in zip(columns, row):
                name = column["name"]
                try:
                    value = parse_value(raw, column.get("type", "text"))
                except ValueError as exc:
                    row_failed = True
                    result.issues.append(
                        Issue(
                            str(path), result.report_id, row_number, "type", "type_parse", "error", name,
                            str(exc), column.get("type", "text"), "[redacted]" if name in sensitive else raw,
                        )
                    )
                    value = None
                if column.get("required") and value is None:
                    row_failed = True
                    result.issues.append(
                        Issue(
                            str(path), result.report_id, row_number, "completeness", "required_value", "error", name,
                            "Required field is empty.", "non-empty", "",
                        )
                    )
                parsed[name] = value
                if name not in sensitive:
                    normalized[name] = display_value(value)

            for rule in contract.get("rules", []):
                evaluation = evaluate_rule(rule, parsed)
                if evaluation is None:
                    continue
                passed, expected, observed, field_name = evaluation
                if not passed:
                    result.issues.append(
                        Issue(
                            str(path), result.report_id, row_number, "business", rule["id"],
                            rule.get("severity", "warning"), field_name,
                            rule["message"], expected, observed,
                        )
                    )

            if not row_failed:
                normalized_rows.append(normalized)
                result.normalized_rows += 1

    if result.source_rows == 0:
        result.issues.append(
            Issue(
                str(path), result.report_id, None, "coverage", "header_only_export", "warning", "",
                "The export contains a valid header but no data rows; business rules were not tested.",
            )
        )

    if normalized_rows:
        normalized_dir.mkdir(parents=True, exist_ok=True)
        output_path = normalized_dir / f"{path.stem}__normalized.csv"
        fieldnames = list(normalized_rows[0])
        with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(normalized_rows)
    return result


def write_outputs(output_dir: Path, results: list[FileResult], unmatched: list[Path]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    issues = [issue.as_dict() for result in results for issue in result.issues]
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "files": [
            {
                "file": result.file,
                "report_id": result.report_id,
                "display_name": result.display_name,
                "sha256": result.sha256,
                "source_rows": result.source_rows,
                "normalized_rows": result.normalized_rows,
                "skipped_rows": result.skipped_rows,
                "header_row_number": result.header_row_number,
                "auxiliary_rows": result.auxiliary_rows,
                "issue_counts": dict(result.counts()),
            }
            for result in results
        ],
        "unmatched_files": [str(path) for path in unmatched],
    }
    (output_dir / "audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    issue_columns = list(Issue("", "", None, "", "", "", "", "").as_dict())
    with (output_dir / "issues.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=issue_columns)
        writer.writeheader()
        writer.writerows(issues)

    lines = ["# ABNAH Local CSV Audit", "", f"Files matched: {len(results)}", f"Files unmatched: {len(unmatched)}", ""]
    for result in results:
        counts = result.counts()
        lines.extend(
            [
                f"## {result.display_name}",
                "",
                f"- File: `{Path(result.file).name}`",
                f"- Report contract: `{result.report_id}`",
                f"- Rows: {result.source_rows} source / {result.normalized_rows} normalized",
                f"- Issues: {counts.get('error', 0)} errors, {counts.get('warning', 0)} warnings, {counts.get('review', 0)} review items",
                "",
            ]
        )
    if unmatched:
        lines.extend(["## Unmatched Files", ""] + [f"- `{path.name}`" for path in unmatched] + [""])
    (output_dir / "audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def collect_csvs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() == ".csv" else []
    return sorted(path for path in input_path.rglob("*.csv") if path.is_file())


def main() -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Audit local ABNAH Restroworks CSV exports.")
    parser.add_argument("--input", type=Path, default=root / "input", help="CSV file or folder")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Local output folder; defaults to output/run_YYYYMMDD_HHMMSS",
    )
    parser.add_argument("--contracts", type=Path, default=root / "contracts", help="Contract folder")
    parser.add_argument("--list-contracts", action="store_true")
    args = parser.parse_args()

    contracts = load_contracts(args.contracts)
    if args.list_contracts:
        for contract in contracts:
            print(f"{contract['report_id']}: {contract['display_name']}")
        return 0

    csv_files = collect_csvs(args.input)
    if not csv_files:
        print(f"No CSV files found under {args.input}", file=sys.stderr)
        return 2

    output_dir = args.output or root / "output" / datetime.now().strftime("run_%Y%m%d_%H%M%S")
    results: list[FileResult] = []
    unmatched: list[Path] = []
    normalized_dir = output_dir / "normalized"
    for path in csv_files:
        contract = match_contract(path, contracts)
        if contract is None:
            unmatched.append(path)
            continue
        results.append(audit_file(path, contract, normalized_dir))

    write_outputs(output_dir, results, unmatched)
    errors = sum(result.counts().get("error", 0) for result in results)
    print(f"Audited {len(results)} file(s); {len(unmatched)} unmatched; {errors} error issue(s).")
    print(f"Results: {output_dir.resolve()}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
