from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "zoho_control_tower_v2_dashboard_click_by_click.md"


class DashboardZohoUiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = GUIDE.read_text(encoding="utf-8")

    def test_direct_kpis_name_real_physical_columns(self) -> None:
        required_mappings = {
            "`outlet_code` | Count Distinct",
            "`action_id` | Count Distinct",
            "`allocated_forecast_net_sales_at_risk` | Sum",
            "`expiry_risk_value` | Sum",
            "`delayed_value` | Sum",
            "`item_code` | Count Distinct",
            "`signed_consumption_variance_value` | Sum",
            "`is_open_po` | Sum",
            "`receipt_total` | Sum",
        }
        for mapping in required_mappings:
            self.assertIn(mapping, self.text)
        self.assertIn(
            "Query 33 Sum `working_capital_value`",
            self.text,
        )

    def test_ratio_kpis_use_saved_summary_views(self) -> None:
        self.assertIn("Pattern B - Aggregate Formula KPI Tile", self.text)
        for formula in (
            "PO Fill Rate %",
            "Vendor OTIF %",
            "Menu Gross Margin %",
        ):
            self.assertIn(f"`{formula}`", self.text)
        compact_text = " ".join(self.text.split())
        self.assertIn(
            "Do not try to find the Aggregate Formula in the direct widget",
            compact_text,
        )

    def test_report_filters_use_zoho_filter_shelf_controls(self) -> None:
        for instruction in (
            "Filter Shelf",
            "Individual Values",
            "Choose **Include**",
            "`risk_type`: Individual Values, Include `STOCKOUT`",
            "`delayed_po_flag`: Include `1`",
            "`consumption_variance_direction`: Include `UNDER_CONSUMPTION`",
        ):
            self.assertIn(instruction, self.text)

        forbidden_ui_criteria = (
            "risk_severity <> GREEN",
            "delayed_po_flag=1",
            "delayed_po_flag = 1",
            "is_open_po = 1",
            "low_consumption_qty>0",
            "low_consumption_qty > 0",
        )
        for criterion in forbidden_ui_criteria:
            self.assertNotIn(criterion, self.text)

    def test_only_three_page_two_queries_require_resave(self) -> None:
        expected = (
            "29_sum_ct_procurement_funnel.sql",
            "30_sum_ct_vendor_scorecard.sql",
            "31_sum_ct_price_movement.sql",
        )
        section = self.text.split("## One-Time SQL Correction", 1)[1].split(
            "# Part 1", 1
        )[0]
        for filename in expected:
            self.assertIn(f"`{filename}`", section)
        self.assertIn(
            "Do not recreate the other 35 Query Tables.",
            section,
        )

    def test_risky_po_uses_the_page_one_risk_snapshot_date(self) -> None:
        corrections = (ROOT.parents[1] / "docs" / "PAGE_1_AND_PAGE_2_CORRECTIONS.md").read_text(
            encoding="utf-8"
        )
        filter_matrix = (
            ROOT / "docs" / "ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "| `36_fact_ct_risky_po.sql` | `as_of_date` |",
            corrections,
        )
        self.assertIn(
            "| `CT_P1_Vendor_PO_Risk` | Query 36 | `as_of_date` |",
            filter_matrix,
        )
        self.assertNotIn(
            "| `36_fact_ct_risky_po.sql` | `po_date` |",
            corrections,
        )


if __name__ == "__main__":
    unittest.main()
