#!/usr/bin/env python3
"""Build a sanitized, portable Codex handoff packet from a local audit run."""

from __future__ import annotations

import csv
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from profiler import safe_profile


PROHIBITED_KEYS = {
    "local_only_samples",
    "local_only_anomaly_rows",
    "local_sample_rows",
    "local_anomaly_rows",
    "local_numeric_distributions",
    "normalized_rows",
    "raw_rows",
    "observed_value",
}
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?91[- ]?)?[6-9]\d{9}(?!\d)")
CURRENCY_PATTERN = re.compile(
    r"(?i)(?:INR|Rs\.?|\u20b9|\$)\s*[-+]?\d[\d,]*(?:\.\d+)?"
)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sanitize_text(value: str, sensitive_values: set[str]) -> str:
    result = value
    for sensitive in sorted(sensitive_values, key=len, reverse=True):
        if len(sensitive) >= 3:
            result = result.replace(sensitive, "[REDACTED]")
    result = EMAIL_PATTERN.sub("[EMAIL REDACTED]", result)
    result = PHONE_PATTERN.sub("[PHONE REDACTED]", result)
    result = CURRENCY_PATTERN.sub("[BUSINESS VALUE REDACTED]", result)
    return result


def sanitize_object(value: Any, sensitive_values: set[str]) -> Any:
    if isinstance(value, dict):
        return {
            key: sanitize_object(item, sensitive_values)
            for key, item in value.items()
            if key not in PROHIBITED_KEYS
        }
    if isinstance(value, list):
        return [sanitize_object(item, sensitive_values) for item in value]
    if isinstance(value, str):
        return sanitize_text(value, sensitive_values)
    return value


def collect_sensitive_values(profiles: list[dict[str, Any]]) -> set[str]:
    values = set()
    for profile in profiles:
        for collection in ("local_only_samples", "local_only_anomaly_rows"):
            for row in profile.get(collection, []):
                for value in row.get("values", {}).values():
                    rendered = str(value).strip()
                    if rendered and rendered != "[REDACTED]":
                        values.add(rendered)
        for field in profile.get("fields", []):
            for key in (
                "numeric_min",
                "numeric_q1",
                "numeric_median",
                "numeric_mean",
                "numeric_q3",
                "numeric_max",
                "date_min",
                "date_max",
            ):
                rendered = str(field.get(key, "")).strip()
                if rendered:
                    values.add(rendered)
    return values


def semantic_columns(profile: dict[str, Any], contract: dict[str, Any] | None) -> list[dict[str, Any]]:
    observed = profile["schema"]["observed_header"]
    if not contract:
        return [
            {
                "source_position": index,
                "source_label": label,
                "canonical_name": "",
                "declared_type": "unknown",
            }
            for index, label in enumerate(observed, start=1)
        ]
    source_labels = contract.get("row_source_labels", contract["expected_header"])
    columns = []
    for index, column in enumerate(contract["row_columns"], start=1):
        label = source_labels[index - 1] if index <= len(source_labels) else ""
        columns.append(
            {
                "source_position": index,
                "source_label": label,
                "canonical_name": column["name"],
                "declared_type": column.get("type", "text"),
            }
        )
    return columns


def schema_changes(
    profiles: list[dict[str, Any]], contracts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    contract_by_id = {contract["report_id"]: contract for contract in contracts}
    changes = []
    for profile in profiles:
        schema = profile["schema"]
        if schema["matches_contract"] and profile["matched_contract"]:
            continue
        changes.append(
            {
                "report_id": profile["report_id"],
                "display_name": profile["display_name"],
                "file_name": profile["file_name"],
                "matched_contract": profile["matched_contract"],
                "target_workbench": profile.get("workbench", {}),
                "expected_header": schema["expected_header"],
                "observed_header": schema["observed_header"],
                "operations": schema["operations"],
                "expected_count": schema["expected_count"],
                "observed_count": schema["observed_count"],
                "semantic_columns": semantic_columns(
                    profile, contract_by_id.get(profile["report_id"])
                ),
                "required_action": "map_new_report"
                if not profile["matched_contract"]
                else "review_contract_and_workbench_schema",
            }
        )
    return changes


def verified_reviews(reviews: list[dict[str, Any]], sensitive_values: set[str]) -> list[dict[str, Any]]:
    output = []
    for review in reviews:
        verified = review.get("verified", {})
        if not verified.get("safe_for_codex"):
            output.append(
                {
                    "report_id": review.get("report_id", ""),
                    "display_name": review.get("display_name", ""),
                    "packet_status": "withheld_by_privacy_gate",
                    "reason": "The local verifier did not certify this output as safe for Codex.",
                }
            )
            continue
        output.append(
            {
                "report_id": review.get("report_id", ""),
                "display_name": review.get("display_name", ""),
                "packet_status": "verified",
                "review": sanitize_object(verified, sensitive_values),
                "model_metadata": review.get("model_metadata", {}),
            }
        )
    return output


def workbench_updates(
    profiles: list[dict[str, Any]],
    contracts: list[dict[str, Any]],
    safe_reviews: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    contract_by_id = {contract["report_id"]: contract for contract in contracts}
    review_by_id = {review["report_id"]: review for review in safe_reviews}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for profile in profiles:
        grouped.setdefault(profile["report_id"], []).append(profile)

    updates = []
    for report_id, items in sorted(grouped.items()):
        contract = contract_by_id.get(report_id)
        review = review_by_id.get(report_id, {})
        verified = review.get("review", {})
        llm_action = verified.get("workbench_update", {})
        has_schema_change = any(not item["schema"]["matches_contract"] for item in items)
        target = contract.get("workbench", {}) if contract else {}
        action = "review_schema_change" if has_schema_change else "ensure_blueprint_matches_contract"
        if not contract or not target.get("target_report_id"):
            action = "catalog_reconciliation_required"
        if llm_action.get("required"):
            action = llm_action.get("change_type", action)
        representative = items[0]
        updates.append(
            {
                "local_report_id": report_id,
                "display_name": representative["display_name"],
                "target": target,
                "action": action,
                "llm_summary": llm_action.get("summary", ""),
                "schema_fingerprints": sorted(
                    {item["schema"]["fingerprint"] for item in items}
                ),
                "observed_headers": [
                    {
                        "file_name": item["file_name"],
                        "header": item["schema"]["observed_header"],
                        "matches_contract": item["schema"]["matches_contract"],
                    }
                    for item in items
                ],
                "semantic_columns": semantic_columns(representative, contract),
                "workflow": [
                    "Review this candidate against the Workbench source blueprint.",
                    "Edit schema-pack/source/report_structures, never generated JSON.",
                    "Keep verification_status as needs_review until a human checks the blank rendering.",
                    "Run refresh_atlas.bat and the complete Workbench validators.",
                ],
            }
        )
    return updates


def write_field_profiles(path: Path, profiles: list[dict[str, Any]]) -> None:
    columns = [
        "report_id",
        "display_name",
        "file_name",
        "field",
        "declared_type",
        "inferred_type",
        "required",
        "sensitive",
        "total_count",
        "blank_count",
        "null_count",
        "zero_count",
        "negative_count",
        "positive_count",
        "parse_error_count",
        "distinct_count_lower_bound",
        "flags",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for profile in profiles:
            for field in safe_profile(profile)["fields"]:
                writer.writerow(
                    {
                        "report_id": profile["report_id"],
                        "display_name": profile["display_name"],
                        "file_name": profile["file_name"],
                        **field,
                        "flags": "|".join(field["flags"]),
                    }
                )


def assert_packet_privacy(value: Any, location: str = "root") -> list[str]:
    errors = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PROHIBITED_KEYS:
                errors.append(f"Prohibited key {key} at {location}")
            errors.extend(assert_packet_privacy(item, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(assert_packet_privacy(item, f"{location}[{index}]"))
    return errors


def build_packet(
    packet_dir: Path,
    run_id: str,
    profiles: list[dict[str, Any]],
    contracts: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    llm_enabled: bool,
    llm_requested: bool = False,
) -> Path:
    packet_dir.mkdir(parents=True, exist_ok=True)
    sensitive_values = collect_sensitive_values(profiles)
    safe_profiles = [safe_profile(profile) for profile in profiles]
    safe_reviews = verified_reviews(reviews, sensitive_values)
    changes = schema_changes(profiles, contracts)
    updates = workbench_updates(profiles, contracts, safe_reviews)
    report_count = len({profile["report_id"] for profile in profiles})
    grounding_versions = sorted(
        {
            str(
                review.get("model_metadata", {})
                .get("deterministic_grounding", {})
                .get("grounding_version", "")
            )
            for review in reviews
            if review.get("model_metadata", {})
            .get("deterministic_grounding", {})
            .get("grounding_version")
        }
    )
    grounded_report_count = sum(
        1
        for review in reviews
        if review.get("model_metadata", {})
        .get("deterministic_grounding", {})
        .get("grounding_version")
    )
    status = "ready_for_codex" if llm_enabled else "deterministic_only"
    if llm_requested and not llm_enabled:
        status = "local_llm_failed"
    if llm_enabled and grounded_report_count != report_count:
        status = "grounding_review_required"
    withheld = sum(1 for review in safe_reviews if review["packet_status"] != "verified")
    if withheld:
        status = "privacy_review_required"

    manifest = {
        "packet_version": "1.0.0",
        "packet_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "raw_data_included": False,
        "screenshots_included": False,
        "normalized_csv_included": False,
        "local_llm_requested": llm_requested,
        "local_llm_used": llm_enabled,
        "report_count": report_count,
        "file_count": len(profiles),
        "schema_change_count": len(changes),
        "verified_review_count": sum(
            1 for review in safe_reviews if review["packet_status"] == "verified"
        ),
        "withheld_review_count": withheld,
        "deterministic_grounding_report_count": grounded_report_count,
        "deterministic_grounding_versions": grounding_versions,
        "read_order": [
            "00_READ_ME_FIRST.md",
            "packet_manifest.json",
            "schema_changes.json",
            "value_health.json",
            "llm_verified_reviews.json",
            "workbench_updates.json",
            "field_profiles.csv",
        ],
    }

    payloads = {
        "packet_manifest.json": manifest,
        "schema_changes.json": {"changes": changes},
        "value_health.json": {"profiles": safe_profiles},
        "llm_verified_reviews.json": {"reviews": safe_reviews},
        "workbench_updates.json": {"updates": updates},
    }
    privacy_errors = []
    for name, payload in payloads.items():
        privacy_errors.extend(assert_packet_privacy(payload, name))
    if privacy_errors:
        raise ValueError("Packet privacy validation failed: " + "; ".join(privacy_errors))

    for name, payload in payloads.items():
        write_json(packet_dir / name, payload)
    write_field_profiles(packet_dir / "field_profiles.csv", profiles)

    readme = f"""# ABNAH Codex Audit Packet

Packet: `{run_id}`  
Status: `{status}`

This folder is the only part of the local run intended for Codex/Workbench handoff.
It contains schema labels, counts, rates, deterministic findings and locally verified
interpretations. It contains no raw rows, screenshots, normalized CSVs or customer data.

## Codex Procedure

1. Read `packet_manifest.json`. Continue only when status is `ready_for_codex`; rerun a
   `local_llm_failed` packet and treat `deterministic_only` as an engineering test.
2. Reconcile `schema_changes.json` against the report contract and existing Workbench blueprint.
3. Read `llm_verified_reviews.json`; treat LLM findings as review evidence, never as source truth.
4. Apply approved changes only under `schema-pack/source`, not `schema-pack/generated`.
5. Run `refresh_atlas.bat`, data validation, typecheck, lint and tests.
6. Record data-quality findings as report notes when they clarify source behavior; do not alter the
   blank schema for value-only anomalies.

The full local evidence remains beside this packet in the audit run and must not be uploaded.
"""
    (packet_dir / "00_READ_ME_FIRST.md").write_text(readme, encoding="utf-8")
    write_json(
        packet_dir / "privacy_report.json",
        {
            "raw_data_included": False,
            "screenshots_included": False,
            "sample_values_registered_for_scrubbing": len(sensitive_values),
            "privacy_validation_errors": privacy_errors,
        },
    )

    archive = packet_dir.parent / f"{packet_dir.name}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(packet_dir.iterdir()):
            if path.is_file():
                handle.write(path, arcname=f"{packet_dir.name}/{path.name}")
    return archive
