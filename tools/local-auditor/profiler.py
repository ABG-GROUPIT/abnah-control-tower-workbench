#!/usr/bin/env python3
"""Deterministic structural and value profiling for local Restroworks CSVs."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from audit import (
    NULL_TOKENS,
    date_value,
    decimal_value,
    evaluate_rule,
    find_contract_header,
    normalize_header,
    normalized_header_row,
    open_csv,
    prepare_contract_row,
)


SENSITIVE_NAME_PATTERN = re.compile(
    r"(?i)(customer|mobile|phone|email|address|contact|whatsapp|card_number)"
)
DATE_PATTERN = re.compile(
    r"(?<!\d)(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4})(?!\d)"
)
DATE_PAREN_PATTERN = re.compile(
    r"\([^)]*(?:\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4})[^)]*\)"
)
ABNAH_SUFFIX_PATTERN = re.compile(
    r"(?i)[\s_-]*abnah[\s_-]*[a-f0-9]{12,}$"
)
HASH_SUFFIX_PATTERN = re.compile(r"(?i)[\s_-]+[a-f0-9]{16,}$")
NUMBER_LIKE_PATTERN = re.compile(
    r"^\s*\(?[-+]?(?:\u20b9|\$)?\s*\d[\d,]*(?:\.\d+)?%?\)?\s*$"
)
DATE_LIKE_PATTERN = re.compile(
    r"(?i)^\s*(?:\d{1,4}[-/]\d{1,2}[-/]\d{1,4}|\d{1,2}[- ](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[- ]\d{2,4})(?:\s+.*)?$"
)


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "unlabelled"


def unmatched_identity(path: Path) -> tuple[str, str]:
    stem = path.stem
    if "__" in stem:
        stem = stem.split("__", 1)[0]
    stem = DATE_PAREN_PATTERN.sub("", stem)
    stem = ABNAH_SUFFIX_PATTERN.sub("", stem)
    stem = HASH_SUFFIX_PATTERN.sub("", stem)
    display_name = re.sub(r"[_\s]+", " ", stem).strip(" -_") or path.stem
    return f"unmatched:{slug(display_name)}", display_name


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def portable_fingerprint(value: str) -> str:
    return "-".join(value[index : index + 4] for index in range(0, len(value), 4))


def display(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    return str(value)


def quantile(values: list[Decimal], fraction: Decimal) -> Decimal | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * Decimal(len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - Decimal(lower)
    return ordered[lower] * (Decimal(1) - weight) + ordered[upper] * weight


def header_diff(expected: list[str], observed: list[str]) -> dict[str, Any]:
    expected_normalized = [normalize_header(value) for value in expected]
    observed_normalized = [normalize_header(value) for value in observed]
    matcher = SequenceMatcher(a=expected_normalized, b=observed_normalized, autojunk=False)
    operations = []
    for operation, expected_start, expected_end, observed_start, observed_end in matcher.get_opcodes():
        if operation == "equal":
            continue
        operations.append(
            {
                "operation": operation,
                "expected_positions": [expected_start + 1, expected_end],
                "observed_positions": [observed_start + 1, observed_end],
                "expected_labels": expected_normalized[expected_start:expected_end],
                "observed_labels": observed_normalized[observed_start:observed_end],
            }
        )
    duplicates = {
        label: count
        for label, count in Counter(label for label in observed_normalized if label).items()
        if count > 1
    }
    return {
        "matches_contract": expected_normalized == observed_normalized,
        "expected_count": len(expected_normalized),
        "observed_count": len(observed_normalized),
        "operations": operations,
        "observed_duplicate_labels": duplicates,
        "fingerprint": portable_fingerprint(hash_text("\x1f".join(observed_normalized))),
    }


class FieldAccumulator:
    def __init__(self, name: str, kind: str, required: bool, sensitive: bool, sample_limit: int = 4096):
        self.name = name
        self.kind = kind
        self.required = required
        self.sensitive = sensitive
        self.sample_limit = sample_limit
        self.total = 0
        self.blank = 0
        self.null = 0
        self.non_null = 0
        self.zero = 0
        self.negative = 0
        self.positive = 0
        self.parse_errors = 0
        self.decimal_parseable = 0
        self.date_parseable = 0
        self.distinct_hashes: set[str] = set()
        self.distinct_truncated = False
        self.numeric_count = 0
        self.numeric_sum = Decimal(0)
        self.numeric_min: Decimal | None = None
        self.numeric_max: Decimal | None = None
        self.numeric_sample: list[Decimal] = []
        self.date_min: datetime | None = None
        self.date_max: datetime | None = None
        self._rng = random.Random(int(hash_text(name)[:16], 16))

    def add(self, raw: str) -> tuple[Any, str | None]:
        self.total += 1
        stripped = raw.strip()
        if not stripped:
            self.blank += 1
        if stripped.lower() in NULL_TOKENS:
            self.null += 1
            return None, None

        self.non_null += 1
        if len(self.distinct_hashes) < 10000:
            self.distinct_hashes.add(hash_text(stripped))
        else:
            self.distinct_truncated = True

        number: Decimal | None = None
        parsed_date: datetime | None = None
        try:
            if self.kind == "decimal":
                parsed = decimal_value(stripped)
                number = parsed
            elif self.kind == "date":
                parsed = date_value(stripped)
                parsed_date = parsed
            else:
                parsed = stripped
        except ValueError as exc:
            self.parse_errors += 1
            return None, str(exc)

        # Type inference for declared text is opportunistic. A text identifier or
        # time can resemble a number/date without being invalid text.
        if self.kind == "text":
            if NUMBER_LIKE_PATTERN.fullmatch(stripped):
                try:
                    number = decimal_value(stripped)
                except ValueError:
                    number = None
            if DATE_LIKE_PATTERN.fullmatch(stripped):
                try:
                    parsed_date = date_value(stripped)
                except ValueError:
                    parsed_date = None

        if number is not None:
            self.decimal_parseable += 1
        if parsed_date is not None:
            self.date_parseable += 1

        profile_number = parsed if self.kind == "decimal" else number
        if isinstance(profile_number, Decimal):
            self.numeric_count += 1
            self.numeric_sum += profile_number
            self.numeric_min = (
                profile_number
                if self.numeric_min is None
                else min(self.numeric_min, profile_number)
            )
            self.numeric_max = (
                profile_number
                if self.numeric_max is None
                else max(self.numeric_max, profile_number)
            )
            if profile_number == 0:
                self.zero += 1
            elif profile_number < 0:
                self.negative += 1
            else:
                self.positive += 1
            if len(self.numeric_sample) < self.sample_limit:
                self.numeric_sample.append(profile_number)
            else:
                replacement = self._rng.randrange(self.numeric_count)
                if replacement < self.sample_limit:
                    self.numeric_sample[replacement] = profile_number
        profile_date = parsed if self.kind == "date" else parsed_date
        if isinstance(profile_date, datetime):
            self.date_min = (
                profile_date if self.date_min is None else min(self.date_min, profile_date)
            )
            self.date_max = (
                profile_date if self.date_max is None else max(self.date_max, profile_date)
            )
        return parsed, None

    def result(self) -> dict[str, Any]:
        q1 = quantile(self.numeric_sample, Decimal("0.25"))
        median = quantile(self.numeric_sample, Decimal("0.5"))
        q3 = quantile(self.numeric_sample, Decimal("0.75"))
        mean = self.numeric_sum / self.numeric_count if self.numeric_count else None
        flags = []
        if self.total and self.null == self.total:
            flags.append("all_null")
        elif self.total and self.null / self.total >= 0.95:
            flags.append("mostly_null")
        numeric_population = self.kind == "decimal" or (
            self.non_null and self.decimal_parseable / self.non_null >= 0.95
        )
        if numeric_population and self.numeric_count and self.zero == self.numeric_count:
            flags.append("all_zero")
        elif numeric_population and self.numeric_count and self.zero / self.numeric_count >= 0.95:
            flags.append("mostly_zero")
        if self.negative:
            flags.append("contains_negative")
        if self.parse_errors:
            flags.append("type_mismatch")
        if self.required and self.null:
            flags.append("required_value_missing")
        if self.non_null and len(self.distinct_hashes) == 1 and not self.distinct_truncated:
            flags.append("constant_non_null")

        inferred = self.kind
        if self.kind == "text" and self.non_null:
            if self.date_parseable / self.non_null >= 0.95:
                inferred = "date_candidate"
            elif self.decimal_parseable / self.non_null >= 0.95:
                inferred = "decimal_candidate"

        return {
            "field": self.name,
            "declared_type": self.kind,
            "inferred_type": inferred,
            "required": self.required,
            "sensitive": self.sensitive,
            "total_count": self.total,
            "blank_count": self.blank,
            "null_count": self.null,
            "non_null_count": self.non_null,
            "zero_count": self.zero,
            "negative_count": self.negative,
            "positive_count": self.positive,
            "parse_error_count": self.parse_errors,
            "distinct_count_lower_bound": len(self.distinct_hashes),
            "distinct_count_truncated": self.distinct_truncated,
            "numeric_count": self.numeric_count,
            "numeric_min": display(self.numeric_min),
            "numeric_q1": display(q1),
            "numeric_median": display(median),
            "numeric_mean": display(mean),
            "numeric_q3": display(q3),
            "numeric_max": display(self.numeric_max),
            "date_min": display(self.date_min),
            "date_max": display(self.date_max),
            "flags": flags,
        }


def filename_dates(path: Path) -> list[str]:
    dates = []
    for match in DATE_PATTERN.finditer(path.stem):
        raw = match.group(1)
        try:
            value = date_value(raw)
        except ValueError:
            continue
        rendered = value.date().isoformat()
        if rendered not in dates:
            dates.append(rendered)
    return dates[:2]


def unknown_columns(path: Path, header: list[str]) -> list[dict[str, Any]]:
    maximum_width = len(header)
    with open_csv(path) as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for source_row in reader:
            row = list(source_row)
            while row and not row[-1].strip():
                row.pop()
            maximum_width = max(maximum_width, len(row))
    labels = [normalize_header(value) for value in header]
    labels.extend([f"Unlabelled Column {index + 1}" for index in range(maximum_width - len(labels))])
    counts: Counter[str] = Counter()
    columns = []
    for position, label in enumerate(labels, start=1):
        base = slug(label)
        counts[base] += 1
        name = base if counts[base] == 1 else f"{base}__{counts[base]}"
        columns.append(
            {
                "name": name,
                "type": "text",
                "required": False,
                "source_position": position,
                "source_label": label,
            }
        )
    return columns


def canonical_filename_check(path: Path, contract: dict[str, Any] | None) -> dict[str, Any]:
    if not contract:
        return {"canonical": False, "expected_prefix": "", "reason": "unmatched_report"}
    prefix = contract.get("canonical_filename_prefix", "")
    if not prefix:
        return {"canonical": True, "expected_prefix": "", "reason": "not_configured"}
    canonical = slug(path.stem).startswith(slug(prefix))
    return {
        "canonical": canonical,
        "expected_prefix": prefix,
        "reason": "matches" if canonical else "rename_before_final_batch",
    }


def profile_file(
    path: Path,
    contract: dict[str, Any] | None,
    sample_rows: int = 8,
    anomaly_rows: int = 12,
) -> dict[str, Any]:
    if contract:
        source_header, header_row_number = find_contract_header(path, contract)
        columns = contract["row_columns"]
        expected_header = contract["expected_header"]
        report_id = contract["report_id"]
        display_name = contract["display_name"]
        contract_status = contract.get("schema_status", "")
    else:
        with open_csv(path) as handle:
            reader = csv.reader(handle)
            source_header = next(reader, [])
        header_row_number = 1 if source_header else 0
        columns = unknown_columns(path, source_header)
        expected_header = source_header
        report_id, display_name = unmatched_identity(path)
        contract_status = "unmatched"

    sensitive_fields = {
        column["name"]
        for column in columns
        if column.get("sensitive") or SENSITIVE_NAME_PATTERN.search(column["name"])
    }
    accumulators = {
        column["name"]: FieldAccumulator(
            column["name"],
            column.get("type", "text"),
            bool(column.get("required")),
            column["name"] in sensitive_fields,
        )
        for column in columns
    }
    width_counts: Counter[int] = Counter()
    row_count = 0
    valid_width_count = 0
    blank_rows = 0
    auxiliary_rows = 0
    duplicate_rows = 0
    row_hashes: set[str] = set()
    samples: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    business_issue_counts: Counter[tuple[str, str]] = Counter()
    rng = random.Random(int(hash_text(str(path.resolve()))[:16], 16))
    adapter_state: dict[int, str] = {}

    with open_csv(path) as handle:
        reader = csv.reader(handle)
        for _ in range(header_row_number):
            next(reader, None)
        for row_number, source_row in enumerate(reader, start=header_row_number + 1):
            if contract:
                status, row = prepare_contract_row(source_row, contract, adapter_state)
            else:
                if not any(value.strip() for value in source_row):
                    status, row = "blank", None
                else:
                    row = list(source_row)
                    while len(row) > len(columns) and not row[-1].strip():
                        row.pop()
                    status = "data" if len(row) == len(columns) else "malformed"
            if status == "blank":
                blank_rows += 1
                continue
            if status == "auxiliary":
                auxiliary_rows += 1
                width_counts[len(source_row)] += 1
                continue
            row_count += 1
            width_counts[len(source_row)] += 1
            if status == "malformed" or row is None:
                if len(anomalies) < anomaly_rows:
                    anomalies.append(
                        {
                            "row_number": row_number,
                            "reasons": ["row_width_mismatch"],
                            "fields": [],
                            "values": {},
                        }
                    )
                continue
            valid_width_count += 1

            digest = hash_text("\x1f".join(row))
            if digest in row_hashes:
                duplicate_rows += 1
            else:
                row_hashes.add(digest)

            parsed: dict[str, Any] = {}
            local_values: dict[str, str] = {}
            reasons: list[str] = []
            reason_fields: list[str] = []
            for column, raw in zip(columns, row):
                name = column["name"]
                value, parse_error = accumulators[name].add(raw)
                parsed[name] = value
                local_values[name] = "[REDACTED]" if name in sensitive_fields and raw.strip() else raw
                if parse_error:
                    reasons.append("type_parse_error")
                    reason_fields.append(name)
                if column.get("required") and value is None:
                    reasons.append("required_value_missing")
                    reason_fields.append(name)
                if isinstance(value, Decimal) and value < 0:
                    reasons.append("negative_value_review")
                    reason_fields.append(name)

            if contract:
                for rule in contract.get("rules", []):
                    evaluation = evaluate_rule(rule, parsed)
                    if evaluation is None or evaluation[0]:
                        continue
                    business_issue_counts[(rule["id"], rule.get("severity", "warning"))] += 1
                    reasons.append(f"business_rule:{rule['id']}")
                    reason_fields.append(evaluation[3])

            sample = {"row_number": row_number, "values": local_values}
            if len(samples) < sample_rows:
                samples.append(sample)
            else:
                replacement = rng.randrange(valid_width_count)
                if replacement < sample_rows:
                    samples[replacement] = sample
            if reasons and len(anomalies) < anomaly_rows:
                relevant_values = {
                    name: local_values[name]
                    for name in sorted(set(reason_fields))
                    if name in local_values
                }
                anomalies.append(
                    {
                        "row_number": row_number,
                        "reasons": sorted(set(reasons)),
                        "fields": sorted(set(reason_fields)),
                        "values": relevant_values,
                    }
                )

    field_results = [accumulators[column["name"]].result() for column in columns]
    report_flags = []
    if not row_count:
        report_flags.append("header_only")
    if row_count and valid_width_count != row_count:
        report_flags.append("inconsistent_row_width")
    if duplicate_rows:
        report_flags.append("duplicate_rows")
    if any(field["parse_error_count"] for field in field_results):
        report_flags.append("type_mismatch")
    if any("all_null" in field["flags"] for field in field_results):
        report_flags.append("all_null_fields")
    if any("all_zero" in field["flags"] for field in field_results):
        report_flags.append("all_zero_fields")
    if any("contains_negative" in field["flags"] for field in field_results):
        report_flags.append("negative_values_present")

    observed_header = normalized_header_row(source_header)
    normalized_expected_header = normalized_header_row(expected_header)
    schema = header_diff(normalized_expected_header, observed_header)
    if not schema["matches_contract"]:
        report_flags.append("header_contract_mismatch")
    if not contract:
        report_flags.append("unmatched_report")

    return {
        "profile_version": "1.0.0",
        "file": str(path.resolve()),
        "file_name": path.name,
        "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "report_id": report_id,
        "display_name": display_name,
        "contract_status": contract_status,
        "matched_contract": contract is not None,
        "workbench": contract.get("workbench", {}) if contract else {},
        "filename_dates": filename_dates(path),
        "filename_check": canonical_filename_check(path, contract),
        "schema": {
            **schema,
            "observed_header": observed_header,
            "expected_header": normalized_expected_header,
            "semantic_row_width": len(columns),
            "header_row_number": header_row_number,
        },
        "rows": {
            "source_count": row_count,
            "valid_width_count": valid_width_count,
            "blank_row_count": blank_rows,
            "preamble_row_count": max(header_row_number - 1, 0),
            "auxiliary_row_count": auxiliary_rows,
            "row_width_counts": {str(key): value for key, value in sorted(width_counts.items())},
            "duplicate_row_count": duplicate_rows,
        },
        "fields": field_results,
        "business_rule_issues": [
            {"rule_id": rule_id, "severity": severity, "affected_rows": count}
            for (rule_id, severity), count in sorted(business_issue_counts.items())
        ],
        "report_flags": sorted(set(report_flags)),
        "local_only_samples": samples,
        "local_only_anomaly_rows": anomalies,
        "sensitive_fields_redacted": sorted(sensitive_fields),
    }


def safe_profile(profile: dict[str, Any]) -> dict[str, Any]:
    safe_fields = []
    for field in profile["fields"]:
        safe_fields.append(
            {
                "field": field["field"],
                "declared_type": field["declared_type"],
                "inferred_type": field["inferred_type"],
                "required": field["required"],
                "sensitive": field["sensitive"],
                "total_count": field["total_count"],
                "blank_count": field["blank_count"],
                "null_count": field["null_count"],
                "non_null_count": field["non_null_count"],
                "zero_count": field["zero_count"],
                "negative_count": field["negative_count"],
                "positive_count": field["positive_count"],
                "parse_error_count": field["parse_error_count"],
                "distinct_count_lower_bound": field["distinct_count_lower_bound"],
                "distinct_count_truncated": field["distinct_count_truncated"],
                "flags": field["flags"],
            }
        )
    return {
        "file_name": profile["file_name"],
        "file_sha256": portable_fingerprint(profile["file_sha256"]),
        "report_id": profile["report_id"],
        "display_name": profile["display_name"],
        "contract_status": profile["contract_status"],
        "matched_contract": profile["matched_contract"],
        "workbench": profile["workbench"],
        "filename_dates": profile["filename_dates"],
        "filename_check": profile["filename_check"],
        "schema": profile["schema"],
        "rows": profile["rows"],
        "fields": safe_fields,
        "business_rule_issues": profile["business_rule_issues"],
        "report_flags": profile["report_flags"],
        "sensitive_fields_redacted": profile["sensitive_fields_redacted"],
    }


def write_profiles(path: Path, profiles: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profiles, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
