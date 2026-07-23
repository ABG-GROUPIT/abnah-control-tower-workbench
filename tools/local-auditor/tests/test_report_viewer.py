import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from local_report_viewer import AuditDataset, validate_loopback  # noqa: E402


class LocalReportViewerTests(unittest.TestCase):
    def build_fixture(self, base: Path) -> tuple[Path, Path]:
        run = base / "run"
        local = run / "LOCAL_EVIDENCE_DO_NOT_UPLOAD"
        normalized = local / "deterministic_audit" / "normalized"
        normalized.mkdir(parents=True)
        raw_file = base / "private" / "example.csv"
        raw_file.parent.mkdir()
        profile = {
            "report_id": "test.report",
            "display_name": "Test Report",
            "file": str(raw_file),
            "file_name": raw_file.name,
            "rows": {"source_count": 2, "valid_width_count": 2},
            "schema": {"header_row_number": 1},
            "fields": [
                {
                    "field": "item",
                    "declared_type": "text",
                    "null_count": 1,
                    "zero_count": 0,
                },
                {
                    "field": "amount",
                    "declared_type": "decimal",
                    "null_count": 0,
                    "zero_count": 1,
                },
            ],
        }
        (local / "full_profiles_with_local_samples.json").write_text(
            json.dumps([profile]), encoding="utf-8"
        )
        with (local / "deterministic_audit" / "issues.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "file",
                    "report_id",
                    "row_number",
                    "phase",
                    "rule_id",
                    "severity",
                    "field",
                    "message",
                    "expected",
                    "observed",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "file": str(raw_file),
                    "report_id": "test.report",
                    "row_number": 2,
                    "phase": "business",
                    "rule_id": "amount_check",
                    "severity": "warning",
                    "field": "amount",
                    "message": "Amount needs review.",
                    "expected": "10",
                    "observed": "11",
                }
            )
        with (normalized / "example__normalized.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=["item", "amount"])
            writer.writeheader()
            writer.writerow({"item": "A", "amount": "11"})
            writer.writerow({"item": "", "amount": "0"})

        contracts = base / "contracts"
        contracts.mkdir()
        (contracts / "test.json").write_text(
            json.dumps(
                {
                    "report_id": "test.report",
                    "rules": [{"id": "amount_check", "target": "amount"}],
                }
            ),
            encoding="utf-8",
        )
        return run, contracts

    def test_full_page_and_issue_only_views(self):
        with tempfile.TemporaryDirectory() as temporary:
            run, contracts = self.build_fixture(Path(temporary))
            dataset = AuditDataset(run, contracts)
            index = dataset.report_index()
            self.assertEqual(index["reports"][0]["row_count"], 2)
            self.assertNotIn("private", json.dumps(index).lower())
            export_id = index["reports"][0]["exports"][0]["id"]

            full = dataset.report_page(export_id, 1, 100, False, "")
            self.assertEqual(full["filtered_row_count"], 2)
            self.assertEqual(full["rows"][0]["source_row_number"], 2)
            self.assertEqual(full["rows"][0]["issue_fields"], ["amount"])
            self.assertEqual(full["column_types"]["amount"], "decimal")
            self.assertEqual(full["cell_state"]["source_null_cell_count"], 1)
            self.assertEqual(full["cell_state"]["source_numeric_zero_cell_count"], 1)
            self.assertEqual(full["cell_state"]["normalization_fidelity"], "verified")

            issues = dataset.report_page(export_id, 1, 100, True, "")
            self.assertEqual(issues["filtered_row_count"], 1)
            self.assertEqual(issues["rows"][0]["values"]["amount"], "11")

    def test_viewer_rejects_non_loopback_binding(self):
        self.assertEqual(validate_loopback("localhost"), "127.0.0.1")
        self.assertEqual(validate_loopback("127.0.0.1"), "127.0.0.1")
        with self.assertRaises(ValueError):
            validate_loopback("0.0.0.0")

    def test_header_only_export_is_visible_without_normalized_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            run, contracts = self.build_fixture(Path(temporary))
            profiles_path = (
                run
                / "LOCAL_EVIDENCE_DO_NOT_UPLOAD"
                / "full_profiles_with_local_samples.json"
            )
            profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
            profiles.append(
                {
                    "report_id": "test.header_only",
                    "display_name": "Header-only Report",
                    "file": str(Path(temporary) / "private" / "header_only.csv"),
                    "file_name": "header_only.csv",
                    "rows": {"source_count": 0, "valid_width_count": 0},
                    "schema": {"header_row_number": 1},
                    "fields": [
                        {
                            "field": "item_code",
                            "declared_type": "text",
                            "null_count": 0,
                            "zero_count": 0,
                        },
                        {
                            "field": "available_qty",
                            "declared_type": "decimal",
                            "null_count": 0,
                            "zero_count": 0,
                        },
                    ],
                }
            )
            profiles_path.write_text(json.dumps(profiles), encoding="utf-8")

            dataset = AuditDataset(run, contracts)
            report = next(
                item
                for item in dataset.report_index()["reports"]
                if item["report_id"] == "test.header_only"
            )
            export_id = report["exports"][0]["id"]
            page = dataset.report_page(export_id, 1, 100, False, "")

            self.assertEqual(page["columns"], ["item_code", "available_qty"])
            self.assertEqual(page["source_row_count"], 0)
            self.assertEqual(page["rows"], [])
            self.assertEqual(page["cell_state"]["normalization_fidelity"], "verified")


if __name__ == "__main__":
    unittest.main()
