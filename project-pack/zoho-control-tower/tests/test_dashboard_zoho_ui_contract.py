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
            "`allocated_forecast_net_sales_at_risk` | Sum",
            "`expiry_risk_value` | Sum",
            "`action_id` | Count Distinct",
            "`ordered_value` | Sum",
            "`pending_value` | Sum",
            "`delayed_value` | Sum",
            "`net_sales` | Sum",
            "`theoretical_cogs` | Sum",
            "`leakage_value` | Sum",
            "`closing_stock_value` | Sum",
            "`open_po_value` | Sum",
            "`actual_consumption_value` | Sum",
            "`signed_consumption_variance_value` | Sum",
        }
        for mapping in required_mappings:
            self.assertIn(mapping, self.text)

    def test_ratio_kpis_use_saved_summary_views(self) -> None:
        self.assertIn("Saved Summary View", self.text)
        for formula in (
            "PO Fill Rate %",
            "Vendor OTIF %",
            "Menu Gross Margin %",
        ):
            self.assertIn(f"`{formula}`", self.text)
        compact_text = " ".join(self.text.split())
        self.assertIn(
            "Do not try to find an Aggregate Formula in the direct KPI Widget's "
            "Data Column selector.",
            compact_text,
        )

    def test_report_filters_use_zoho_filter_shelf_controls(self) -> None:
        for instruction in (
            "Filter shelf selection",
            "Individual Values",
            "Choose **Include**",
            "`risk_type`: Individual Values, Include `STOCKOUT`",
            "`is_open_po`: Individual Values, Include `1`",
            "`delayed_po_flag`: Individual Values, Include `1`",
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

    def test_guide_starts_after_all_queries_are_saved(self) -> None:
        self.assertIn(
            "Confirm Query Tables `01` through `38` have been saved successfully.",
            self.text,
        )
        self.assertNotIn("## One-Time SQL Correction", self.text)


if __name__ == "__main__":
    unittest.main()
