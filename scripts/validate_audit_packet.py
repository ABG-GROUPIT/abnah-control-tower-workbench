#!/usr/bin/env python3
"""Validate a sanitized local-audit packet before Workbench reconciliation."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any


EXPECTED_FILES = {
    "00_READ_ME_FIRST.md",
    "packet_manifest.json",
    "schema_changes.json",
    "value_health.json",
    "llm_verified_reviews.json",
    "workbench_updates.json",
    "field_profiles.csv",
    "privacy_report.json",
}
PROHIBITED_KEYS = {
    "local_only_samples",
    "local_only_anomaly_rows",
    "local_sample_rows",
    "local_anomaly_rows",
    "local_numeric_distributions",
    "normalized_rows",
    "raw_rows",
    "observed_value",
    "values",
    "numeric_min",
    "numeric_q1",
    "numeric_median",
    "numeric_mean",
    "numeric_q3",
    "numeric_max",
    "date_min",
    "date_max",
}
LOCAL_PATH_RE = re.compile(r"[A-Za-z]:[\\/]")
IMAGE_RE = re.compile(r"\.(?:png|jpe?g|webp|gif|bmp|tiff?)(?:\b|$)", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[- ]?)?[6-9]\d{9}(?!\d)")
CURRENCY_RE = re.compile(r"(?i)(?:INR|Rs\.?|\u20b9|\$)\s*[-+]?\d[\d,]*(?:\.\d+)?")


class PacketReader:
    def __init__(self, path: Path):
        self.path = path
        self.archive: zipfile.ZipFile | None = None
        self.prefix = ""
        if path.is_dir():
            self.names = {item.name for item in path.iterdir() if item.is_file()}
            return
        if not path.is_file() or path.suffix.lower() != ".zip":
            raise ValueError("Packet must be a CODEX_PACKET directory or .zip file.")
        self.archive = zipfile.ZipFile(path)
        members = [name for name in self.archive.namelist() if not name.endswith("/")]
        manifest = [name for name in members if name.endswith("/packet_manifest.json")]
        if len(manifest) != 1:
            raise ValueError("Zip must contain exactly one packet_manifest.json.")
        self.prefix = manifest[0][: -len("packet_manifest.json")]
        self.names = {
            name[len(self.prefix) :]
            for name in members
            if name.startswith(self.prefix) and "/" not in name[len(self.prefix) :]
        }

    def read_text(self, name: str) -> str:
        if self.archive:
            return self.archive.read(f"{self.prefix}{name}").decode("utf-8-sig")
        return (self.path / name).read_text(encoding="utf-8-sig")

    def close(self) -> None:
        if self.archive:
            self.archive.close()


def scan_value(value: Any, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PROHIBITED_KEYS:
                errors.append(f"Prohibited raw-evidence key at {location}.{key}")
            scan_value(item, f"{location}.{key}", errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            scan_value(item, f"{location}[{index}]", errors)
    elif isinstance(value, str):
        if LOCAL_PATH_RE.search(value):
            errors.append(f"Absolute local path at {location}")
        if IMAGE_RE.search(value):
            errors.append(f"Screenshot/image reference at {location}")
        if EMAIL_RE.search(value) or PHONE_RE.search(value) or CURRENCY_RE.search(value):
            errors.append(f"Possible row-level or personal value at {location}")


def report_ids(catalog_path: Path) -> set[str]:
    with catalog_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["report_id"] for row in csv.DictReader(handle)}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Validate packet shape while allowing a non-ready model status",
    )
    args = parser.parse_args()

    errors: list[str] = []
    try:
        reader = PacketReader(args.packet)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"Audit packet validation failed: {exc}")
        return 1

    try:
        missing = EXPECTED_FILES - reader.names
        unexpected = reader.names - EXPECTED_FILES
        if missing:
            errors.append(f"Missing packet files: {', '.join(sorted(missing))}")
        if unexpected:
            errors.append(f"Unexpected packet files: {', '.join(sorted(unexpected))}")
        if missing:
            raise ValueError("Cannot validate packet content until required files exist.")

        payloads = {
            name: json.loads(reader.read_text(name))
            for name in EXPECTED_FILES
            if name.endswith(".json")
        }
        manifest = payloads["packet_manifest.json"]
        if not args.allow_incomplete and manifest.get("status") != "ready_for_codex":
            errors.append(
                f"Packet status is {manifest.get('status')!r}, not 'ready_for_codex'."
            )
        for key in ("raw_data_included", "screenshots_included", "normalized_csv_included"):
            if manifest.get(key) is not False:
                errors.append(f"Manifest must set {key}=false.")
        if not args.allow_incomplete:
            if manifest.get("deterministic_grounding_report_count") != manifest.get(
                "report_count"
            ):
                errors.append("Every report must pass the deterministic post-LLM grounding gate.")
            supported_grounding_versions = {"1.0.0", "1.1.0"}
            declared_grounding_versions = set(
                manifest.get("deterministic_grounding_versions", [])
            )
            if not declared_grounding_versions & supported_grounding_versions:
                errors.append(
                    "Packet does not declare a supported deterministic grounding version "
                    "(1.0.0 or 1.1.0)."
                )
        privacy = payloads["privacy_report.json"]
        if privacy.get("privacy_validation_errors"):
            errors.append("Local packet builder reported privacy validation errors.")

        for name, payload in payloads.items():
            scan_value(payload, name, errors)
        for name in ("00_READ_ME_FIRST.md", "field_profiles.csv"):
            content = reader.read_text(name)
            if LOCAL_PATH_RE.search(content):
                errors.append(f"Absolute local path in {name}")
            if IMAGE_RE.search(content):
                errors.append(f"Screenshot/image reference in {name}")
            if EMAIL_RE.search(content) or PHONE_RE.search(content) or CURRENCY_RE.search(content):
                errors.append(f"Possible row-level or personal value in {name}")

        known_ids = report_ids(
            root / "schema-pack" / "generated" / "workspace_report_catalog.csv"
        )
        updates = payloads["workbench_updates.json"].get("updates", [])
        reconciliation_count = 0
        for index, update in enumerate(updates):
            target = update.get("target", {})
            target_id = target.get("target_report_id", "")
            blueprint = target.get("blueprint_path", "")
            if target_id and target_id not in known_ids:
                errors.append(f"Unknown Workbench report ID in update {index}: {target_id}")
            if blueprint and not blueprint.startswith("schema-pack/source/report_structures/"):
                errors.append(f"Invalid source blueprint path in update {index}: {blueprint}")
            if not target_id:
                reconciliation_count += 1
                if update.get("action") != "catalog_reconciliation_required":
                    errors.append(
                        f"Update {index} has no target report ID and must request catalog reconciliation."
                    )

        field_text = reader.read_text("field_profiles.csv")
        list(csv.DictReader(io.StringIO(field_text)))
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(str(exc))
        updates = []
        reconciliation_count = 0
    finally:
        reader.close()

    if errors:
        print("Audit packet validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Audit packet validation passed: "
        f"{len(updates)} Workbench update candidate(s), "
        f"{reconciliation_count} catalog reconciliation candidate(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
