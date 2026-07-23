#!/usr/bin/env python3
"""Two-pass local Ollama review for deterministic ABNAH audit evidence."""

from __future__ import annotations

import json
import hashlib
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from profiler import safe_profile


FINDING_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "finding_id": {"type": "string", "maxLength": 80},
        "category": {
            "type": "string",
            "enum": [
                "schema",
                "row_shape",
                "type",
                "completeness",
                "zero_pattern",
                "negative_pattern",
                "duplicate",
                "business_logic",
                "outlier",
                "grain",
                "naming",
            ],
        },
        "severity": {"type": "string", "enum": ["error", "warning", "review", "info"]},
        "title": {"type": "string", "maxLength": 160},
        "field_names": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 8,
        },
        "affected_rows": {"type": "integer", "minimum": 0},
        "interpretation": {"type": "string", "maxLength": 400},
        "evidence_refs": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 8,
        },
        "recommended_action": {"type": "string", "maxLength": 300},
        "requires_human_confirmation": {"type": "boolean"},
    },
    "required": [
        "finding_id",
        "category",
        "severity",
        "title",
        "field_names",
        "affected_rows",
        "interpretation",
        "evidence_refs",
        "recommended_action",
        "requires_human_confirmation",
    ],
}

ANALYST_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "report_id": {"type": "string"},
        "assessment": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "summary": {"type": "string", "maxLength": 600},
                "data_usable": {"type": "boolean"},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                "grain_interpretation": {"type": "string", "maxLength": 300},
            },
            "required": ["summary", "data_usable", "confidence", "grain_interpretation"],
        },
        "findings": {"type": "array", "items": FINDING_SCHEMA, "maxItems": 5},
        "schema_update": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["no_change", "update_existing", "add_variant", "new_report", "hold"],
                },
                "target_report_id": {"type": "string"},
                "rationale": {"type": "string", "maxLength": 400},
                "changed_fields": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "source_position": {"type": "integer", "minimum": 0},
                            "source_label": {"type": "string"},
                            "canonical_name": {"type": "string"},
                            "data_type": {"type": "string"},
                            "semantic_role": {"type": "string"},
                            "parent_group": {"type": "string"},
                            "notes": {"type": "string"},
                        },
                        "required": [
                            "source_position",
                            "source_label",
                            "canonical_name",
                            "data_type",
                            "semantic_role",
                            "parent_group",
                            "notes",
                        ],
                    },
                    "maxItems": 8,
                },
            },
            "required": ["action", "target_report_id", "rationale", "changed_fields"],
        },
        "questions": {
            "type": "array",
            "items": {"type": "string", "maxLength": 240},
            "maxItems": 3,
        },
    },
    "required": ["report_id", "assessment", "findings", "schema_update", "questions"],
}

VERIFIER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "report_id": {"type": "string"},
        "verdict": {"type": "string", "enum": ["approved", "revised", "rejected"]},
        "safe_for_codex": {"type": "boolean"},
        "codex_summary": {"type": "string", "maxLength": 800},
        "confirmed_findings": {
            "type": "array",
            "items": FINDING_SCHEMA,
            "maxItems": 5,
        },
        "rejected_findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "finding_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["finding_id", "reason"],
            },
            "maxItems": 5,
        },
        "workbench_update": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "required": {"type": "boolean"},
                "change_type": {
                    "type": "string",
                    "enum": ["none", "schema", "variant", "notes", "new_report", "contract_only", "hold"],
                },
                "target_report_id": {"type": "string"},
                "summary": {"type": "string", "maxLength": 500},
                "evidence_refs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 8,
                },
            },
            "required": ["required", "change_type", "target_report_id", "summary", "evidence_refs"],
        },
        "questions": {
            "type": "array",
            "items": {"type": "string", "maxLength": 240},
            "maxItems": 3,
        },
    },
    "required": [
        "report_id",
        "verdict",
        "safe_for_codex",
        "codex_summary",
        "confirmed_findings",
        "rejected_findings",
        "workbench_update",
        "questions",
    ],
}


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: int = 1800,
        num_ctx: int = 32768,
        keep_alive: str = "0",
    ):
        parsed = urllib.parse.urlparse(base_url)
        if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("Ollama URL must be localhost so ABNAH evidence cannot leave the machine.")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.num_ctx = num_ctx
        self.keep_alive: str | int = 0 if keep_alive == "0" else keep_alive

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                f"Ollama request failed for {path}: HTTP {exc.code}. {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Ollama request failed for {path}: {exc}") from exc

    def models(self) -> list[str]:
        response = self._request("GET", "/api/tags")
        return [item.get("name", "") for item in response.get("models", [])]

    def require_model(self, model: str) -> None:
        installed = self.models()
        accepted = {name for value in installed for name in {value, value.removesuffix(":latest")}}
        if model not in accepted and model.removesuffix(":latest") not in accepted:
            raise RuntimeError(
                f"Ollama model '{model}' is not installed. Run: ollama pull {model}. "
                f"Installed models: {', '.join(installed) or 'none'}"
            )

    def chat_json(
        self,
        model: str,
        system: str,
        user: str,
        schema: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "format": schema,
            "options": {
                "temperature": 0,
                "seed": 42,
                "num_ctx": self.num_ctx,
                "num_predict": 2048,
            },
            "keep_alive": self.keep_alive,
        }
        last_error: Exception | None = None
        for _ in range(2):
            response = self._request("POST", "/api/chat", payload)
            content = response.get("message", {}).get("content", "")
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as exc:
                last_error = exc
                payload["messages"].append(
                    {
                        "role": "user",
                        "content": "The prior response was not valid JSON. Return only an object matching the supplied schema.",
                    }
                )
                continue
            metadata = {
                "model": response.get("model", model),
                "total_duration_ns": response.get("total_duration", 0),
                "load_duration_ns": response.get("load_duration", 0),
                "prompt_eval_count": response.get("prompt_eval_count", 0),
                "eval_count": response.get("eval_count", 0),
                "done_reason": response.get("done_reason", ""),
            }
            return parsed, metadata
        raise RuntimeError(f"Ollama returned invalid structured output: {last_error}")


def aggregate_field_health(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for file_index, item in enumerate(items, start=1):
        for field in item["fields"]:
            grouped[field["field"]].append((file_index, field))

    output = []
    count_keys = (
        "total_count",
        "blank_count",
        "null_count",
        "non_null_count",
        "zero_count",
        "negative_count",
        "positive_count",
        "parse_error_count",
        "numeric_count",
    )
    for name, entries in grouped.items():
        aggregate = {key: sum(field[key] for _, field in entries) for key in count_keys}
        first = entries[0][1]
        output.append(
            {
                "field": name,
                "declared_type": first["declared_type"],
                "inferred_types": sorted({field["inferred_type"] for _, field in entries}),
                "required": first["required"],
                "sensitive": first["sensitive"],
                **aggregate,
                "flags": sorted({flag for _, field in entries for flag in field["flags"]}),
                "flagged_files": [
                    {
                        "file_index": file_index,
                        "flags": field["flags"],
                        "blank_count": field["blank_count"],
                        "null_count": field["null_count"],
                        "zero_count": field["zero_count"],
                        "negative_count": field["negative_count"],
                        "parse_error_count": field["parse_error_count"],
                    }
                    for file_index, field in entries
                    if len(items) > 1 and field["flags"]
                ],
            }
        )
    return output


def decimal_or_none(value: str) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def aggregate_local_distributions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for file_index, item in enumerate(items, start=1):
        for field in item["fields"]:
            if field["numeric_count"] or field["date_min"]:
                grouped[field["field"]].append((file_index, field))

    output = []
    for name, entries in grouped.items():
        minimums = [
            value
            for _, field in entries
            if (value := decimal_or_none(field["numeric_min"])) is not None
        ]
        maximums = [
            value
            for _, field in entries
            if (value := decimal_or_none(field["numeric_max"])) is not None
        ]
        date_mins = [field["date_min"] for _, field in entries if field["date_min"]]
        date_maxs = [field["date_max"] for _, field in entries if field["date_max"]]
        output.append(
            {
                "field": name,
                "numeric_min": str(min(minimums)) if minimums else "",
                "numeric_max": str(max(maximums)) if maximums else "",
                "date_min": min(date_mins) if date_mins else "",
                "date_max": max(date_maxs) if date_maxs else "",
                "per_file_medians": [
                    {"file_index": file_index, "median": field["numeric_median"]}
                    for file_index, field in entries
                    if field["numeric_median"]
                ],
            }
        )
    return output


def file_summary(profile: dict[str, Any], file_index: int) -> dict[str, Any]:
    safe = safe_profile(profile)
    source_schema = safe["schema"]
    schema = {
        "matches_contract": source_schema["matches_contract"],
        "expected_count": source_schema["expected_count"],
        "observed_count": source_schema["observed_count"],
        "operations": source_schema["operations"],
        "observed_duplicate_labels": source_schema["observed_duplicate_labels"],
        "fingerprint": source_schema["fingerprint"],
        "semantic_row_width": source_schema["semantic_row_width"],
    }
    if not source_schema["matches_contract"]:
        schema["expected_header"] = source_schema["expected_header"]
        schema["observed_header"] = source_schema["observed_header"]
    return {
        "file_index": file_index,
        "filename_check": safe["filename_check"],
        "schema": schema,
        "rows": safe["rows"],
        "business_rule_issues": safe["business_rule_issues"],
        "report_flags": safe["report_flags"],
    }


def report_groups(
    profiles: list[dict[str, Any]],
    contracts: list[dict[str, Any]],
    sample_limit: int = 8,
    anomaly_limit: int = 12,
) -> list[dict[str, Any]]:
    contract_by_id = {contract["report_id"]: contract for contract in contracts}
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for profile in profiles:
        grouped[profile["report_id"]].append(profile)

    output = []
    for report_id, items in sorted(grouped.items()):
        contract = contract_by_id.get(report_id)
        if contract:
            contract = {
                key: value
                for key, value in contract.items()
                if key not in {"_path", "filename_regexes", "canonical_filename_prefix"}
            }
        fingerprints = Counter(item["schema"]["fingerprint"] for item in items)
        local_samples = []
        anomaly_samples = []
        for file_index, item in enumerate(items, start=1):
            for sample in item["local_only_samples"]:
                if len(local_samples) < sample_limit:
                    local_samples.append({"file_index": file_index, **sample})
            for sample in item["local_only_anomaly_rows"]:
                if len(anomaly_samples) < anomaly_limit:
                    anomaly_samples.append({"file_index": file_index, **sample})
        output.append(
            {
                "report_id": report_id,
                "display_name": items[0]["display_name"],
                "contract": contract or {},
                "files": [
                    {
                        "file_index": index,
                        "file_name": item["file_name"],
                        "file_sha256": item["file_sha256"],
                        "filename_dates": item["filename_dates"],
                    }
                    for index, item in enumerate(items, start=1)
                ],
                "file_summaries": [
                    file_summary(item, index) for index, item in enumerate(items, start=1)
                ],
                "field_health": aggregate_field_health(items),
                "local_numeric_distributions": aggregate_local_distributions(items),
                "schema_variant_count": len(fingerprints),
                "schema_fingerprints": dict(fingerprints),
                "local_sample_rows": local_samples,
                "local_anomaly_rows": anomaly_samples,
            }
        )
    return output


def prune_empty(value: Any) -> Any:
    """Remove empty containers/strings from the prompt view while preserving 0 and False."""
    if isinstance(value, dict):
        return {
            key: compacted
            for key, item in value.items()
            if (compacted := prune_empty(item)) not in ("", [], {})
        }
    if isinstance(value, list):
        return [prune_empty(item) for item in value]
    return value


def compact_contract_for_llm(contract: dict[str, Any]) -> dict[str, Any]:
    headers = contract.get("expected_header", [])
    canonical_fields = [
        column.get("name", "") for column in contract.get("row_columns", [])
    ]

    rules = []
    for source_rule in contract.get("rules", []):
        rule = {key: value for key, value in source_rule.items() if key != "message"}
        if "terms" in rule:
            rule["terms"] = [
                [
                    term.get("field", ""),
                    term.get("coefficient", 1),
                    int(bool(term.get("null_as_zero"))),
                ]
                for term in rule["terms"]
            ]
            rule["terms_legend"] = ["field", "coefficient", "null_as_zero"]
        rules.append(rule)

    row_handling_keys = (
        "header_search_rows",
        "max_trailing_empty_fields",
        "auxiliary_row_widths",
        "auxiliary_when_all_blank_positions",
        "row_adapter",
    )
    return prune_empty(
        {
            "report_id": contract.get("report_id", ""),
            "display_name": contract.get("display_name", ""),
            "grain": contract.get("grain", ""),
            "schema_status": contract.get("schema_status", ""),
            "position_semantics": (
                "The two arrays align by one-based position; repeated source labels are distinct."
            ),
            "source_headers_by_position": headers,
            "canonical_fields_by_position": canonical_fields,
            "row_handling": {
                key: contract[key] for key in row_handling_keys if key in contract
            },
            "filter_profile": contract.get("filter_profile", {}),
            "rules": rules,
            "workbench": contract.get("workbench", {}),
        }
    )


def compact_field_health_for_llm(fields: list[dict[str, Any]]) -> dict[str, Any]:
    flagged_file_legend = [
        "field",
        "file_index",
        "flags",
        "blank",
        "null",
        "zero",
        "negative",
        "parse_errors",
    ]
    rows = []
    flagged_file_rows = []
    for field in fields:
        contract_flags = ""
        if field.get("required"):
            contract_flags += "R"
        if field.get("sensitive"):
            contract_flags += "S"
        rows.append(
            [
                field["field"],
                field.get("declared_type", ""),
                field.get("inferred_types", []),
                contract_flags,
                field.get("total_count", 0),
                field.get("blank_count", 0),
                field.get("null_count", 0),
                field.get("zero_count", 0),
                field.get("negative_count", 0),
                field.get("parse_error_count", 0),
                field.get("numeric_count", 0),
                field.get("flags", []),
            ]
        )
        flagged_file_rows.extend(
            [
                field["field"],
                item["file_index"],
                item.get("flags", []),
                item.get("blank_count", 0),
                item.get("null_count", 0),
                item.get("zero_count", 0),
                item.get("negative_count", 0),
                item.get("parse_error_count", 0),
            ]
            for item in field.get("flagged_files", [])
        )
    return {
        "legend": [
            "field",
            "declared_type",
            "inferred_types",
            "contract_flags_R_required_S_sensitive",
            "total",
            "blank",
            "null",
            "zero",
            "negative",
            "parse_errors",
            "numeric",
            "flags",
        ],
        "flagged_file_legend": flagged_file_legend,
        "rows": rows,
        "flagged_file_rows": flagged_file_rows,
    }


def compact_distributions_for_llm(distributions: list[dict[str, Any]]) -> dict[str, Any]:
    numeric_rows = []
    date_rows = []
    for item in distributions:
        medians = [
            decimal_or_none(entry.get("median", ""))
            for entry in item.get("per_file_medians", [])
        ]
        medians = [value for value in medians if value is not None]
        if item.get("numeric_min", "") or item.get("numeric_max", ""):
            numeric_rows.append(
                [
                    item["field"],
                    item.get("numeric_min", ""),
                    item.get("numeric_max", ""),
                    str(min(medians)) if medians else "",
                    str(max(medians)) if medians else "",
                    len(medians),
                ]
            )
        if item.get("date_min", "") or item.get("date_max", ""):
            date_rows.append(
                [item["field"], item.get("date_min", ""), item.get("date_max", "")]
            )
    return {
        "numeric_legend": [
            "field",
            "numeric_min",
            "numeric_max",
            "per_file_median_min",
            "per_file_median_max",
            "files_with_median",
        ],
        "numeric_rows": numeric_rows,
        "date_legend": ["field", "date_min", "date_max"],
        "date_rows": date_rows,
    }


def compact_samples_for_llm(
    samples: list[dict[str, Any]], field_names: list[str]
) -> dict[str, Any]:
    return {
        "legend": ["file_index", "source_row_number", "values_aligned_to_columns"],
        "columns": field_names,
        "rows": [
            [
                sample.get("file_index", 0),
                sample.get("row_number", 0),
                [sample.get("values", {}).get(name, "") for name in field_names],
            ]
            for sample in samples
        ],
    }


def compact_anomalies_for_llm(samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "legend": [
            "file_index",
            "source_row_number",
            "deterministic_reasons",
            "flagged_field_value_pairs",
        ],
        "rows": [
            [
                sample.get("file_index", 0),
                sample.get("row_number", 0),
                sample.get("reasons", []),
                list(sample.get("values", {}).items()),
            ]
            for sample in samples
        ],
    }


def compact_group_for_llm(group: dict[str, Any]) -> dict[str, Any]:
    field_names = [item["field"] for item in group["field_health"]]
    return prune_empty(
        {
            "evidence_conventions": {
                "table_encoding": "Array rows align positionally with the adjacent legend.",
                "counts": "All counts are deterministic; zero means not observed.",
                "citations": (
                    "Cite semantic paths such as field_health.<field>.flags, "
                    "file_summaries[n].rows, contract.rules, local_sample_rows, "
                    "or local_anomaly_rows."
                ),
                "privacy": "Sensitive sample values are redacted before this prompt.",
            },
            "report_id": group["report_id"],
            "display_name": group["display_name"],
            "contract": compact_contract_for_llm(group.get("contract", {})),
            "files": {
                "legend": ["file_index", "file_name", "safe_fingerprint", "filename_dates"],
                "rows": [
                    [
                        item["file_index"],
                        item["file_name"],
                        item["file_sha256"],
                        item["filename_dates"],
                    ]
                    for item in group["files"]
                ],
            },
            "file_summaries": [prune_empty(item) for item in group["file_summaries"]],
            "field_health": compact_field_health_for_llm(group["field_health"]),
            "local_numeric_distributions": compact_distributions_for_llm(
                group["local_numeric_distributions"]
            ),
            "schema_variant_count": group["schema_variant_count"],
            "schema_fingerprints": group["schema_fingerprints"],
            "local_sample_rows": compact_samples_for_llm(
                group["local_sample_rows"], field_names
            ),
            "local_anomaly_rows": compact_anomalies_for_llm(
                group["local_anomaly_rows"]
            ),
        }
    )


ANALYST_SYSTEM = """You are the local ABNAH Restroworks data-quality analyst.
Use only the supplied deterministic evidence. Distinguish structural schema changes from value-quality issues.
Repeated labels such as Amt are positional children of their parent measure and must not be deduplicated.
When every file matches its contract and schema_variant_count is 1, do not report schema, naming or row-shape defects and do not request a schema update.
Use zero_pattern, negative_pattern, completeness, type, business_logic or outlier for value findings; never classify value counts as schema findings.
Even when every row is affected, a zero or negative value pattern remains zero_pattern or negative_pattern; prevalence never turns it into a schema or type issue.
Negative or zero values are not automatically errors; interpret them from field semantics and report grain.
Do not invent formulas. Rules marked review are hypotheses until populated evidence supports them.
Deterministic counts and flags are valid evidence even though identifying and exact business values are redacted from transferable output.
Do not mark data unusable solely because review-level formula, zero or negative patterns need business confirmation.
Customer-identifying fields are redacted. Do not request or reconstruct them.
Return at most five distinct, highest-impact findings. Keep every text field concise.
Return only JSON matching the supplied schema."""

VERIFIER_SYSTEM = """You are the strict second-pass verifier for a local ABNAH CSV audit.
Compare the analyst claims against the deterministic evidence. Reject unsupported business interpretations and false schema changes.
Your output will be transferred to Codex, so it must contain no raw row values, customer information, invoice numbers, transaction numbers, or exact business amounts. Counts, percentages, field names, report labels and schema positions are allowed.
Deterministic field counts, flags and business-rule affected-row counts are sufficient to confirm a factual pattern; do not reject them merely because exact values are redacted.
Correct an analyst's category or severity when the factual finding is supported. Value patterns must not be categorized as schema findings.
Expected repeated positional source labels are not duplicates when the observed schema matches the contract.
Even when every row is affected, a zero or negative value pattern remains zero_pattern or negative_pattern; prevalence never turns it into a schema or type issue.
Only request a Workbench update when the evidence shows a schema/variant/notes change. Value-quality findings alone do not change the blank schema.
Rules marked review may be confirmed only as hypotheses requiring business validation, not as established source-system defects.
When every file is header-only, do not infer blank, zero, negative, outlier or rule behavior; state that value quality was not assessed.
Return at most five supported or rejected findings and keep every text field concise.
Return only JSON matching the supplied schema."""


GROUNDING_VERSION = "1.1.0"


def reference_is_valid(reference: str, field_names: set[str]) -> bool:
    allowed_roots = {
        "contract",
        "files",
        "file_summaries",
        "field_health",
        "local_numeric_distributions",
        "schema_variant_count",
        "schema_fingerprints",
        "local_sample_rows",
        "local_anomaly_rows",
    }
    root = reference.split(".", 1)[0].split("[", 1)[0]
    if root not in allowed_roots:
        return False
    if reference.startswith("field_health."):
        parts = reference.split(".")
        return len(parts) >= 3 and parts[1] in field_names
    return True


def field_metric(group: dict[str, Any], names: list[str], metric: str) -> int:
    health = {field["field"]: field for field in group["field_health"]}
    selected = names or list(health)
    return sum(int(health[name].get(metric, 0)) for name in selected if name in health)


def normalize_finding_categories(
    payload: dict[str, Any], group: dict[str, Any], findings_key: str
) -> dict[str, Any]:
    """Let the model interpret meaning while deterministic metrics enforce category semantics."""
    output = dict(payload)
    normalized = []
    for source in payload.get(findings_key, []):
        finding = dict(source)
        names = finding.get("field_names", [])
        identity_text = " ".join(
            str(finding.get(key, "")) for key in ("finding_id", "title")
        ).lower()
        if "negative" in identity_text and field_metric(group, names, "negative_count"):
            finding["category"] = "negative_pattern"
        elif "zero" in identity_text and field_metric(group, names, "zero_count"):
            finding["category"] = "zero_pattern"
        elif any(word in identity_text for word in ("blank", "null", "missing")) and (
            field_metric(group, names, "blank_count")
            + field_metric(group, names, "null_count")
        ):
            finding["category"] = "completeness"
        elif any(word in identity_text for word in ("parse", "type")) and field_metric(
            group, names, "parse_error_count"
        ):
            finding["category"] = "type"
        normalized.append(finding)
    output[findings_key] = normalized
    return output


def ground_verified_output(
    verified: dict[str, Any], group: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    field_names = {field["field"] for field in group["field_health"]}
    row_count = sum(item["rows"]["source_count"] for item in group["file_summaries"])
    invalid_width = sum(
        item["rows"]["source_count"] - item["rows"]["valid_width_count"]
        for item in group["file_summaries"]
    )
    duplicates = sum(
        item["rows"]["duplicate_row_count"] for item in group["file_summaries"]
    )
    business_issues = sum(
        issue["affected_rows"]
        for item in group["file_summaries"]
        for issue in item["business_rule_issues"]
    )
    schema_change = any(
        not item["schema"]["matches_contract"] for item in group["file_summaries"]
    )
    schema_change = schema_change or group["schema_variant_count"] > 1

    supported = []
    rejected = list(verified.get("rejected_findings", []))
    rejection_details = []
    for finding in verified.get("confirmed_findings", []):
        reasons = []
        names = finding.get("field_names", [])
        unknown = sorted(set(names) - field_names)
        if unknown:
            reasons.append(f"unknown field(s): {', '.join(unknown)}")
        invalid_refs = [
            reference
            for reference in finding.get("evidence_refs", [])
            if not reference_is_valid(reference, field_names)
        ]
        if invalid_refs:
            reasons.append(f"invalid evidence reference(s): {', '.join(invalid_refs)}")

        category = finding.get("category", "")
        if category == "schema" and not schema_change:
            reasons.append("no deterministic schema change")
        elif category == "row_shape" and invalid_width == 0:
            reasons.append("no invalid-width rows")
        elif category == "type" and field_metric(group, names, "parse_error_count") == 0:
            reasons.append("no type parse errors")
        elif category == "completeness":
            text = " ".join(
                str(finding.get(key, "")) for key in ("title", "interpretation")
            ).lower()
            missing = field_metric(group, names, "blank_count") + field_metric(
                group, names, "null_count"
            )
            if missing == 0 and not (row_count == 0 and "header" in text):
                reasons.append("no blank/null evidence")
        elif category == "zero_pattern" and field_metric(group, names, "zero_count") == 0:
            reasons.append("no observed zero values")
        elif category == "negative_pattern" and field_metric(
            group, names, "negative_count"
        ) == 0:
            reasons.append("no observed negative values")
        elif category == "duplicate" and duplicates == 0:
            reasons.append("no duplicate rows")
        elif category == "business_logic" and business_issues == 0:
            reasons.append("no observed business-rule failures")
        elif category == "outlier" and field_metric(group, names, "numeric_count") == 0:
            reasons.append("no populated numeric evidence")

        text = " ".join(
            str(finding.get(key, ""))
            for key in ("title", "interpretation", "recommended_action")
        ).lower()
        keyword_metrics = {
            "zero": "zero_count",
            "negative": "negative_count",
            "blank": "blank_count",
            "null": "null_count",
        }
        for keyword, metric in keyword_metrics.items():
            if keyword in text and field_metric(group, names, metric) == 0:
                reasons.append(f"claim mentions {keyword} without observed evidence")

        if reasons:
            reason = "; ".join(sorted(set(reasons)))
            rejected.append({"finding_id": finding.get("finding_id", ""), "reason": reason})
            rejection_details.append(
                {"finding_id": finding.get("finding_id", ""), "reason": reason}
            )
        else:
            grounded_finding = dict(finding)
            if category == "schema":
                grounded_finding["affected_rows"] = 0
            elif row_count:
                grounded_finding["affected_rows"] = min(
                    int(grounded_finding.get("affected_rows", 0)), row_count
                )
            supported.append(grounded_finding)

    output = dict(verified)
    output["confirmed_findings"] = supported
    output["rejected_findings"] = rejected
    if rejection_details:
        output["verdict"] = "revised"

    workbench_update = dict(output.get("workbench_update", {}))
    target_id = group.get("contract", {}).get("workbench", {}).get("target_report_id", "")
    workbench_update["target_report_id"] = target_id
    if not workbench_update.get("required"):
        workbench_update["change_type"] = "none"
    elif workbench_update.get("change_type") in {"schema", "variant", "new_report"} and not schema_change:
        workbench_update.update(
            {
                "required": False,
                "change_type": "none",
                "summary": "The deterministic evidence does not support a structural Workbench change.",
                "evidence_refs": [],
            }
        )
    if row_count == 0:
        output["codex_summary"] = (
            "The export is header-only. Its observed header can be compared with the contract, "
            "but value quality and business-rule behavior were not assessed."
        )
        if not schema_change:
            workbench_update.update(
                {
                    "required": False,
                    "change_type": "none",
                    "summary": "No structural change is supported by this header-only export.",
                    "evidence_refs": ["file_summaries[0].schema.matches_contract"],
                }
            )
    output["workbench_update"] = workbench_update
    return output, {
        "grounding_version": GROUNDING_VERSION,
        "rejected_count": len(rejection_details),
        "rejections": rejection_details,
    }


def checkpoint_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "report"


def write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def review_groups(
    profiles: list[dict[str, Any]],
    contracts: list[dict[str, Any]],
    client: OllamaClient,
    analyst_model: str,
    verifier_model: str,
    checkpoint_dir: Path | None = None,
) -> list[dict[str, Any]]:
    client.require_model(analyst_model)
    if verifier_model != analyst_model:
        client.require_model(verifier_model)
    if client.num_ctx <= 24576:
        sample_limit, anomaly_limit = 1, 3
    else:
        sample_limit, anomaly_limit = 8, 12
    groups = report_groups(profiles, contracts, sample_limit, anomaly_limit)
    reviews = []
    for index, group in enumerate(groups, start=1):
        prompt_group = compact_group_for_llm(group)
        evidence_hash = hashlib.sha256(
            json.dumps(
                {
                    "group": group,
                    "prompt_group": prompt_group,
                    "analyst_model": analyst_model,
                    "verifier_model": verifier_model,
                    "num_ctx": client.num_ctx,
                    "analyst_system": ANALYST_SYSTEM,
                    "verifier_system": VERIFIER_SYSTEM,
                    "analyst_schema": ANALYST_SCHEMA,
                    "verifier_schema": VERIFIER_SCHEMA,
                    "grounding_version": GROUNDING_VERSION,
                },
                sort_keys=True,
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        checkpoint_path = (
            checkpoint_dir
            / f"{checkpoint_slug(group['report_id'])}__{evidence_hash[:16]}.json"
            if checkpoint_dir
            else None
        )
        checkpoint: dict[str, Any] = {}
        if checkpoint_path and checkpoint_path.exists():
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            if checkpoint.get("evidence_hash") != evidence_hash:
                checkpoint = {}

        analyst_prompt = (
            "Assess this report group. Every claim must cite an evidence reference such as "
            "file_summaries[n].schema.operations, field_health.<name>.flags, "
            "file_summaries[n].rows.row_width_counts, "
            "file_summaries[n].business_rule_issues, "
            "local_sample_rows or local_anomaly_rows.\n\n"
            + json.dumps(prompt_group, separators=(",", ":"), ensure_ascii=True)
        )
        if checkpoint.get("analyst"):
            print(f"Local LLM analyst {index}: resumed checkpoint for {group['display_name']}")
            analysis = checkpoint["analyst"]
            analyst_meta = checkpoint.get("analyst_metadata", {})
        else:
            print(f"Local LLM analyst {index}: {group['display_name']}")
            analysis, analyst_meta = client.chat_json(
                analyst_model, ANALYST_SYSTEM, analyst_prompt, ANALYST_SCHEMA
            )
            if analysis.get("report_id") != group["report_id"]:
                raise RuntimeError(
                    f"Local analyst returned report_id {analysis.get('report_id')!r}; "
                    f"expected {group['report_id']!r}."
                )
            analysis = normalize_finding_categories(analysis, group, "findings")
            checkpoint.update(
                {
                    "evidence_hash": evidence_hash,
                    "report_id": group["report_id"],
                    "analyst_model": analyst_model,
                    "verifier_model": verifier_model,
                    "num_ctx": client.num_ctx,
                    "analyst": analysis,
                    "analyst_metadata": analyst_meta,
                }
            )
            if checkpoint_path:
                write_checkpoint(checkpoint_path, checkpoint)
        analysis = normalize_finding_categories(analysis, group, "findings")

        verifier_evidence = {**prompt_group, "analyst_output": analysis}
        verifier_prompt = (
            "Verify and, where needed, recategorize the analyst output. Remove raw values and unsupported claims. "
            "Use affected_rows=0 when a finding is schema-level rather than row-level.\n\n"
            + json.dumps(verifier_evidence, separators=(",", ":"), ensure_ascii=True)
        )
        if checkpoint.get("verified"):
            print(f"Local LLM verifier {index}: resumed checkpoint for {group['display_name']}")
            verified = checkpoint["verified"]
            verifier_meta = checkpoint.get("verifier_metadata", {})
            grounding_meta = checkpoint.get("grounding_metadata", {})
        else:
            print(f"Local LLM verifier {index}: {group['display_name']}")
            verifier_output, verifier_meta = client.chat_json(
                verifier_model, VERIFIER_SYSTEM, verifier_prompt, VERIFIER_SCHEMA
            )
            if verifier_output.get("report_id") != group["report_id"]:
                raise RuntimeError(
                    f"Local verifier returned report_id {verifier_output.get('report_id')!r}; "
                    f"expected {group['report_id']!r}."
                )
            verifier_output = normalize_finding_categories(
                verifier_output, group, "confirmed_findings"
            )
            verified, grounding_meta = ground_verified_output(verifier_output, group)
            checkpoint.update(
                {
                    "verifier_raw": verifier_output,
                    "verified": verified,
                    "verifier_metadata": verifier_meta,
                    "grounding_metadata": grounding_meta,
                }
            )
            if checkpoint_path:
                write_checkpoint(checkpoint_path, checkpoint)
        reviews.append(
            {
                "report_id": group["report_id"],
                "display_name": group["display_name"],
                "analyst": analysis,
                "verified": verified,
                "model_metadata": {
                    "analyst": analyst_meta,
                    "verifier": verifier_meta,
                    "deterministic_grounding": grounding_meta,
                },
            }
        )
    return reviews
