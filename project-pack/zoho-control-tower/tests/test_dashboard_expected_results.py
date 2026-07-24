from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "zoho_control_tower_v2_dashboard_click_by_click.md"
EXPECTED = (
    ROOT
    / "exports"
    / "control_tower_zoho"
    / "truth"
    / "DASHBOARD_CHART_ACCEPTANCE.csv"
)


def _rows() -> list[dict[str, str]]:
    with EXPECTED.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DashboardExpectedResultsTests(unittest.TestCase):
    def test_every_named_dashboard_report_has_acceptance_evidence(self) -> None:
        guide = GUIDE.read_text(encoding="utf-8")
        named_reports = set(
            re.findall(r"`(CT_P[1-4]_[A-Za-z0-9_]+)`", guide)
        )
        captured_reports = {row["report_name"] for row in _rows()}
        self.assertFalse(named_reports - captured_reports)

    def test_acceptance_keys_are_unique_and_values_are_populated(self) -> None:
        key_fields = [
            "page",
            "report_name",
            "source_period_code",
            "outlet_code",
            "series",
            "category",
            "secondary_category",
            "metric",
        ]
        rows = _rows()
        keys = [tuple(row[field] for field in key_fields) for row in rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(row["expected_value"] != "" for row in rows))

    def test_final_stockout_and_expiry_split_controls(self) -> None:
        rows = _rows()

        def expected(report: str, metric: str) -> float:
            matches = [
                row
                for row in rows
                if row["report_name"] == report
                and row["metric"] == metric
                and row["source_period_code"] == "month_03"
                and row["outlet_code"] == "ALL"
            ]
            self.assertEqual(1, len(matches))
            return float(matches[0]["expected_value"])

        self.assertEqual(
            0,
            expected("CT_P1_KPI_Open_Risky_PO", "open_risky_po_count"),
        )
        self.assertEqual(
            6,
            expected("CT_P1_Action_Center", "row_count"),
        )
        self.assertEqual(
            68,
            expected("CT_P1_Expiry_Risk_Detail_Demo", "row_count"),
        )


if __name__ == "__main__":
    unittest.main()
