import csv
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit import audit_file, evaluate_rule, load_contracts  # noqa: E402


class ContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = load_contracts(ROOT / "contracts")

    def test_all_contracts_have_unique_ids_and_columns(self):
        ids = [contract["report_id"] for contract in self.contracts]
        self.assertEqual(len(ids), len(set(ids)))
        for contract in self.contracts:
            names = [column["name"] for column in contract["row_columns"]]
            self.assertEqual(
                len(names),
                len(set(names)),
                f"Duplicate canonical column in {contract['report_id']}",
            )

    def test_each_contract_accepts_a_well_typed_synthetic_row(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            normalized = base / "normalized"
            for index, contract in enumerate(self.contracts):
                source = base / f"contract_{index}.csv"
                row = []
                for column in contract["row_columns"]:
                    kind = column.get("type", "text")
                    if kind == "date":
                        row.append("20-07-2026")
                    elif kind == "decimal":
                        row.append("0")
                    else:
                        row.append("TEST")
                row.extend([""] * contract.get("max_trailing_empty_fields", 0))
                with source.open("w", encoding="utf-8-sig", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(contract["expected_header"])
                    writer.writerow(row)

                result = audit_file(source, contract, normalized)
                errors = [issue for issue in result.issues if issue.severity == "error"]
                self.assertEqual(errors, [], contract["report_id"])
                self.assertEqual(result.normalized_rows, 1, contract["report_id"])

    def test_normal_variance_preserves_detailed_csv_positions(self):
        contract = next(
            item
            for item in self.contracts
            if item["report_id"] == "p4.enterprise_variance.normal"
        )
        names = [column["name"] for column in contract["row_columns"]]
        self.assertEqual(names[27], "return_qty")
        self.assertEqual(names[28], "return_amt")
        self.assertEqual(names[29], "closing_date")
        self.assertEqual(names[32], "latest_physical_date")
        self.assertEqual(len(contract["expected_header"]), 46)
        self.assertEqual(len(contract["row_columns"]), 46)

    def test_embedded_header_and_auxiliary_rows_are_supported(self):
        contract = next(
            item for item in self.contracts if item["report_id"] == "p2.gross_net_margin.item"
        )
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "gross.csv"
            row = []
            for column in contract["row_columns"]:
                if column.get("type") == "date":
                    row.append("20-07-2026")
                elif column.get("type") == "decimal":
                    row.append("0")
                else:
                    row.append("TEST")
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Report title"])
                writer.writerow(["Filter summary"])
                writer.writerow(contract["expected_header"])
                writer.writerow(row)
                writer.writerow(["Report footer"])
            result = audit_file(source, contract, base / "normalized")
            self.assertEqual(result.header_row_number, 3)
            self.assertEqual(result.normalized_rows, 1)
            self.assertEqual(result.auxiliary_rows, 1)
            self.assertEqual(
                [issue for issue in result.issues if issue.severity == "error"], []
            )

    def test_contract_files_are_valid_json(self):
        for path in (ROOT / "contracts").glob("*.json"):
            with path.open(encoding="utf-8") as handle:
                json.load(handle)

    def test_displayed_precision_prevents_false_product_mismatch(self):
        rule = {
            "type": "product_equals",
            "target": "amount",
            "left": "qty",
            "right": "price",
            "tolerance": 0.05,
            "display_rounding": {
                "left_decimals": 3,
                "right_decimals": 2,
                "target_decimals": 2,
            },
        }
        row = {
            "qty": Decimal("3000"),
            "price": Decimal("0.63"),
            "amount": Decimal("1875"),
        }
        self.assertTrue(evaluate_rule(rule, row)[0])
        row["amount"] = Decimal("1800")
        self.assertFalse(evaluate_rule(rule, row)[0])

    def test_margin_rule_skips_zero_cost_and_accepts_hidden_precision(self):
        rule = {
            "type": "margin_percent",
            "target": "margin",
            "revenue": "revenue",
            "cost": "cost",
            "tolerance": 0.1,
            "skip_when_cost_zero": True,
            "implied_cost_tolerance": 0.1,
        }
        self.assertIsNone(
            evaluate_rule(
                rule,
                {
                    "margin": Decimal("0"),
                    "revenue": Decimal("100"),
                    "cost": Decimal("0"),
                },
            )
        )
        self.assertTrue(
            evaluate_rule(
                rule,
                {
                    "margin": Decimal("-2124.72"),
                    "revenue": Decimal("5.67"),
                    "cost": Decimal("126.07"),
                },
            )[0]
        )

    def test_percent_of_rule_uses_taxable_base(self):
        rule = {
            "type": "percent_of",
            "target": "tax",
            "base": "taxable",
            "percent": 5,
            "tolerance": 0.01,
        }
        self.assertTrue(
            evaluate_rule(
                rule,
                {"taxable": Decimal("225"), "tax": Decimal("11.25")},
            )[0]
        )

    def test_normalization_preserves_blank_and_numeric_zero(self):
        contract = {
            "report_id": "test.state",
            "display_name": "State Test",
            "expected_header": ["Label", "Amount"],
            "row_columns": [
                {"name": "label", "type": "text"},
                {"name": "amount", "type": "decimal"},
            ],
            "rules": [],
        }
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "state.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(contract["expected_header"])
                writer.writerow(["", "0"])
            normalized = base / "normalized"
            result = audit_file(source, contract, normalized)
            with (normalized / "state__normalized.csv").open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(result.normalized_rows, 1)
            self.assertEqual(row["label"], "")
            self.assertEqual(row["amount"], "0")


if __name__ == "__main__":
    unittest.main()
