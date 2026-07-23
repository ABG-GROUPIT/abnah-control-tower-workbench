from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "local_data_auditor" / "contracts"
EXPORTS = ROOT / "exports" / "control_tower_zoho"
RAW_DATA = ROOT / "data" / "control_tower"
HEADER_ONLY_REPORTS = {"enterprise_reorder", "enterprise_stock_return"}


class ControlTowerExportTests(unittest.TestCase):
    def test_all_validated_contract_headers_match(self) -> None:
        contract_files = sorted(CONTRACTS.glob("*.json"))
        self.assertEqual(21, len(contract_files))
        for contract_path in contract_files:
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            export_path = EXPORTS / f"RAW_CT_{contract_path.stem}.csv"
            self.assertTrue(export_path.exists(), export_path)
            with export_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                self.assertEqual(
                    payload["expected_header"],
                    next(reader),
                    contract_path.stem,
                )
                first_row = next(reader, None)
                if contract_path.stem in HEADER_ONLY_REPORTS:
                    self.assertIsNone(first_row, contract_path.stem)
                else:
                    self.assertIsNotNone(first_row, contract_path.stem)

    def test_month_outlet_export_count(self) -> None:
        files = list(RAW_DATA.rglob("*.csv"))
        self.assertEqual(173, len(files))

    def test_reconciliation_results_all_pass(self) -> None:
        path = EXPORTS / "_RECONCILIATION_RESULTS.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(35, len(rows))
        self.assertEqual({"PASS"}, {row["status"] for row in rows})

    def test_normalized_landings_and_auxiliary_headers(self) -> None:
        landing_files = list((EXPORTS / "normalized").glob("RAWN_CT_*.csv"))
        self.assertEqual(21, len(landing_files))
        with (
            EXPORTS / "AUX_Theoretical_Consumption.csv"
        ).open("r", encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle))
        self.assertEqual("source_period_code", header[0])
        self.assertEqual("outlet_code", header[1])

    def test_expiry_demo_uses_explicit_batch_tranche_lineage(self) -> None:
        path = EXPORTS / "AUX_Expiry_Estimate.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(206, len(rows))
        allocation_keys = {
            (
                row["source_period_code"],
                row["outlet_code"],
                row["item_code"],
                row["batch_allocation_id"],
            )
            for row in rows
        }
        self.assertEqual(len(rows), len(allocation_keys))
        self.assertEqual(
            {
                "synthetic_internal_receipt_lineage",
                "synthetic_near_expiry_opening_tranche",
            },
            {row["receipt_source_status"] for row in rows},
        )
        self.assertEqual(
            {"demo_only_no_posist_batch_or_expiry_source"},
            {row["production_use_status"] for row in rows},
        )

        receipt_linked = []
        for row in rows:
            qty_at_risk = float(row["qty_at_risk"])
            batch_remaining = float(row["batch_remaining_qty"])
            item_closing = float(row["item_closing_qty"])
            self.assertGreater(qty_at_risk, 0)
            self.assertLessEqual(qty_at_risk, batch_remaining)
            self.assertLessEqual(batch_remaining, item_closing)
            if row["receipt_source_status"] == "synthetic_internal_receipt_lineage":
                receipt_linked.append(row)
                self.assertTrue(row["grn_number"])
                self.assertTrue(row["po_number"])
            else:
                self.assertTrue(row["batch_number"].startswith("SYN-EXP-"))
                self.assertFalse(row["grn_number"])

        with (
            EXPORTS / "normalized" / "RAWN_CT_purchase_detail.csv"
        ).open("r", encoding="utf-8-sig", newline="") as handle:
            purchase_rows = list(csv.DictReader(handle))
        purchase_keys = {
            (
                row["source_outlet_code"],
                row["item_code"],
                row["transaction_number"],
                row["po_number"],
                row["vendor_name"],
                row["transaction_date"],
            )
            for row in purchase_rows
        }
        self.assertEqual(79, len(receipt_linked))
        for row in receipt_linked:
            self.assertIn(
                (
                    row["outlet_code"],
                    row["item_code"],
                    row["grn_number"],
                    row["po_number"],
                    row["vendor_name"],
                    row["receipt_date"],
                ),
                purchase_keys,
            )

    def test_active_import_manifest_contains_only_supported_inputs(self) -> None:
        path = EXPORTS / "_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(14, len(rows))
        self.assertEqual({"yes"}, {row["active_v2_import"] for row in rows})
        active_files = {row["zoho_import_file"] for row in rows}
        self.assertNotIn("AUX_Item_Master.csv", active_files)
        self.assertNotIn("AUX_Vendor_Master.csv", active_files)
        self.assertIn("AUX_Expiry_Estimate.csv", active_files)
        self.assertIn("AUX_Outlet_Master.csv", active_files)
        self.assertIn("normalized/RAWN_CT_vendor_report.csv", active_files)
        self.assertFalse(any("reorder" in name.lower() for name in active_files))
        self.assertFalse(any("stock_return" in name.lower() for name in active_files))

    def test_controlled_quality_exceptions_are_documented(self) -> None:
        path = EXPORTS / "RAW_CT_closing_stock.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        quantities = [float(row["Total Qty"]) for row in rows]
        self.assertEqual(1, sum(quantity < 0 for quantity in quantities))
        self.assertGreaterEqual(sum(quantity == 0 for quantity in quantities), 2)

    def test_confirmed_blank_and_zero_only_source_fields_are_mirrored(self) -> None:
        expected_blank = {
            "RAW_CT_bill_item_detail.csv": {
                "customerName",
                "customerMobile",
                "Covers",
                "Waiter Name",
                "Source",
            },
            "RAW_CT_enterprise_entry.csv": {"Source"},
            "RAW_CT_enterprise_opening.csv": {"Source"},
        }
        expected_zero = {
            "RAW_CT_enterprise_entry.csv": {"MRP", "Item Charges Amount"},
            "RAW_CT_enterprise_purchase_order.csv": {
                "Item Wise Discount Amount",
                "Bill Wise Discount Amount",
            },
            "RAW_CT_purchase_detail.csv": {"Other Taxes"},
        }
        for filename, columns in expected_blank.items():
            with (EXPORTS / filename).open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            for column in columns:
                self.assertTrue(all(row[column] == "" for row in rows), column)
        for filename, columns in expected_zero.items():
            with (EXPORTS / filename).open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            for column in columns:
                self.assertTrue(
                    all(float(row[column] or 0) == 0 for row in rows),
                    column,
                )

    def test_truth_pack_acceptance_checks_pass(self) -> None:
        path = EXPORTS / "truth" / "CONTROL_TOWER_ACCEPTANCE_CHECKS.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(9, len(rows))
        self.assertEqual({"PASS"}, {row["status"] for row in rows})


if __name__ == "__main__":
    unittest.main()
