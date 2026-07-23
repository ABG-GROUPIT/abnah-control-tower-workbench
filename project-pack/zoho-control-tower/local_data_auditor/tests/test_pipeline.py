import csv
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit import load_contracts  # noqa: E402
from llm_review import (  # noqa: E402
    ANALYST_SCHEMA,
    OllamaClient,
    ground_verified_output,
    normalize_finding_categories,
    review_groups,
)
from packet_builder import build_packet, semantic_columns  # noqa: E402
from profiler import profile_file, safe_profile, unmatched_identity  # noqa: E402


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = load_contracts(ROOT / "contracts")

    def test_unknown_report_profiles_numeric_and_date_candidates(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "unknown_report.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Metric", "Business Date", "Label"])
                writer.writerow(["-5", "20-07-2026", "SECRET_ITEM"])
                writer.writerow(["0", "21-07-2026", "SECOND_ITEM"])

            profile = profile_file(source, None)
            fields = {field["field"]: field for field in profile["fields"]}
            self.assertEqual(fields["metric"]["inferred_type"], "decimal_candidate")
            self.assertEqual(fields["metric"]["negative_count"], 1)
            self.assertEqual(fields["metric"]["zero_count"], 1)
            self.assertEqual(
                fields["business_date"]["inferred_type"], "date_candidate"
            )
            safe = safe_profile(profile)
            self.assertNotIn("local_only_samples", safe)
            self.assertNotIn("numeric_min", safe["fields"][0])

    def test_declared_text_inference_does_not_create_parse_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "unknown_report.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Open Time", "Invoice Number"])
                writer.writerow(["20-07-2026 09:05:00 PM", "2026-99-99"])
                writer.writerow(["11:45 PM", "001234"])

            profile = profile_file(source, None)
            fields = {field["field"]: field for field in profile["fields"]}
            self.assertEqual(fields["open_time"]["parse_error_count"], 0)
            self.assertNotIn("type_mismatch", fields["open_time"]["flags"])
            self.assertEqual(fields["invoice_number"]["parse_error_count"], 0)
            self.assertNotIn("type_mismatch", fields["invoice_number"]["flags"])

    def test_unmatched_months_share_a_stable_report_identity(self):
        first = Path(
            "enterprise_food_cost__2026-03-01__2026-03-31__all.csv"
        )
        second = Path(
            "enterprise_food_cost__2026-04-01__2026-04-30__all.csv"
        )
        restroworks = Path(
            "_Enterprise Food Cost Report (05-07-2026 to 20-07-2026) "
            "_abnah_ 6a5f1c04b3a89e8c93c92309.csv"
        )
        self.assertEqual(unmatched_identity(first)[0], unmatched_identity(second)[0])
        self.assertEqual(
            unmatched_identity(restroworks)[0],
            "unmatched:enterprise_food_cost_report",
        )

    def test_variance_semantic_labels_preserve_repeated_amount_positions(self):
        contract = next(
            item
            for item in self.contracts
            if item["report_id"] == "p4.enterprise_variance.normal"
        )
        profile = {"schema": {"observed_header": contract["expected_header"]}}
        columns = semantic_columns(profile, contract)
        self.assertEqual(columns[27]["source_label"], "Return Qty")
        self.assertEqual(columns[28]["source_label"], "Amt")
        self.assertEqual(columns[29]["source_label"], "Closing Date")
        self.assertEqual(columns[32]["source_label"], "Latest Physical")

    def test_packet_scrubs_local_sample_values_and_contains_no_raw_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "unknown_report.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Metric", "Label"])
                writer.writerow(["123.45", "SECRET_ITEM"])
            profile = profile_file(source, None)
            review = {
                "report_id": profile["report_id"],
                "display_name": profile["display_name"],
                "verified": {
                    "report_id": profile["report_id"],
                    "verdict": "approved",
                    "safe_for_codex": True,
                    "codex_summary": "SECRET_ITEM has value Rs. 123.45.",
                    "confirmed_findings": [],
                    "rejected_findings": [],
                    "workbench_update": {
                        "required": False,
                        "change_type": "none",
                        "target_report_id": "",
                        "summary": "No schema change for SECRET_ITEM.",
                        "evidence_refs": [],
                    },
                    "questions": [],
                },
                "model_metadata": {
                    "deterministic_grounding": {
                        "grounding_version": "1.0.0",
                        "rejected_count": 0,
                        "rejections": [],
                    }
                },
            }

            packet_dir = base / "CODEX_PACKET"
            archive = build_packet(
                packet_dir,
                "test_run",
                [profile],
                [],
                [review],
                llm_enabled=True,
                llm_requested=True,
            )
            serialized = (packet_dir / "llm_verified_reviews.json").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("SECRET_ITEM", serialized)
            self.assertNotIn("123.45", serialized)
            self.assertNotIn("local_only_samples", serialized)
            manifest = json.loads(
                (packet_dir / "packet_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["status"], "ready_for_codex")
            with zipfile.ZipFile(archive) as handle:
                self.assertIn(
                    "CODEX_PACKET/packet_manifest.json", handle.namelist()
                )

    def test_ollama_client_rejects_non_localhost_url(self):
        with self.assertRaises(ValueError):
            OllamaClient("https://example.com")

    def test_deterministic_metrics_normalize_value_finding_categories(self):
        group = {
            "field_health": [
                {
                    "field": "closing_qty",
                    "zero_count": 7,
                    "negative_count": 2,
                    "blank_count": 0,
                    "null_count": 0,
                    "parse_error_count": 0,
                }
            ]
        }
        payload = {
            "findings": [
                {
                    "finding_id": "negative_closing_values",
                    "title": "Negative closing values",
                    "category": "schema",
                    "field_names": ["closing_qty"],
                },
                {
                    "finding_id": "all_zero_closing_values",
                    "title": "All-zero closing pattern",
                    "category": "type",
                    "field_names": ["closing_qty"],
                },
            ]
        }
        normalized = normalize_finding_categories(payload, group, "findings")
        self.assertEqual(normalized["findings"][0]["category"], "negative_pattern")
        self.assertEqual(normalized["findings"][1]["category"], "zero_pattern")

    def test_grounding_gate_rejects_value_claims_for_header_only_export(self):
        group = {
            "field_health": [
                {
                    "field": "reorder_level_qty",
                    "zero_count": 0,
                    "negative_count": 0,
                    "blank_count": 0,
                    "null_count": 0,
                    "parse_error_count": 0,
                    "numeric_count": 0,
                }
            ],
            "file_summaries": [
                {
                    "rows": {
                        "source_count": 0,
                        "valid_width_count": 0,
                        "duplicate_row_count": 0,
                    },
                    "schema": {"matches_contract": True},
                    "business_rule_issues": [],
                }
            ],
            "schema_variant_count": 1,
            "contract": {
                "workbench": {"target_report_id": "report:p4:test:reorder"}
            },
        }
        verified = {
            "report_id": "p4.enterprise_reorder.item",
            "verdict": "approved",
            "safe_for_codex": True,
            "codex_summary": "Values may be negative.",
            "confirmed_findings": [
                {
                    "finding_id": "unsupported_negative",
                    "category": "grain",
                    "severity": "review",
                    "title": "Quantity may be negative",
                    "field_names": ["reorder_level_qty"],
                    "affected_rows": 0,
                    "interpretation": "A negative quantity may be present.",
                    "evidence_refs": ["field_health.reorder_level_qty.flags"],
                    "recommended_action": "Review negative quantities.",
                    "requires_human_confirmation": True,
                }
            ],
            "rejected_findings": [],
            "workbench_update": {
                "required": False,
                "change_type": "notes",
                "target_report_id": "wrong-local-id",
                "summary": "Add a note.",
                "evidence_refs": [],
            },
            "questions": [],
        }

        grounded, metadata = ground_verified_output(verified, group)
        self.assertEqual(grounded["confirmed_findings"], [])
        self.assertEqual(len(grounded["rejected_findings"]), 1)
        self.assertIn("header-only", grounded["codex_summary"])
        self.assertEqual(grounded["workbench_update"]["change_type"], "none")
        self.assertEqual(
            grounded["workbench_update"]["target_report_id"],
            "report:p4:test:reorder",
        )
        self.assertEqual(metadata["rejected_count"], 1)

    def test_local_llm_passes_resume_from_evidence_checkpoint(self):
        class FakeClient:
            def __init__(self, report_id):
                self.report_id = report_id
                self.num_ctx = 32768
                self.calls = 0

            def require_model(self, model):
                return None

            def chat_json(self, model, system, user, schema):
                self.calls += 1
                if schema is ANALYST_SCHEMA:
                    return {
                        "report_id": self.report_id,
                        "assessment": {
                            "summary": "Deterministic evidence reviewed.",
                            "data_usable": True,
                            "confidence": "high",
                            "grain_interpretation": "One test row.",
                        },
                        "findings": [],
                        "schema_update": {
                            "action": "no_change",
                            "target_report_id": "",
                            "rationale": "Header is stable.",
                            "changed_fields": [],
                        },
                        "questions": [],
                    }, {"model": model}
                return {
                    "report_id": self.report_id,
                    "verdict": "approved",
                    "safe_for_codex": True,
                    "codex_summary": "No schema change.",
                    "confirmed_findings": [],
                    "rejected_findings": [],
                    "workbench_update": {
                        "required": False,
                        "change_type": "none",
                        "target_report_id": "",
                        "summary": "No change.",
                        "evidence_refs": [],
                    },
                    "questions": [],
                }, {"model": model}

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "unknown_report.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Metric"])
                writer.writerow(["1"])
            profile = profile_file(source, None)
            checkpoint_dir = base / "checkpoints"

            first = FakeClient(profile["report_id"])
            first_result = review_groups(
                [profile], [], first, "fake:analyst", "fake:verifier", checkpoint_dir
            )
            self.assertEqual(first.calls, 2)
            self.assertEqual(len(list(checkpoint_dir.glob("*.json"))), 1)

            resumed = FakeClient(profile["report_id"])
            resumed_result = review_groups(
                [profile], [], resumed, "fake:analyst", "fake:verifier", checkpoint_dir
            )
            self.assertEqual(resumed.calls, 0)
            self.assertEqual(first_result, resumed_result)


if __name__ == "__main__":
    unittest.main()
