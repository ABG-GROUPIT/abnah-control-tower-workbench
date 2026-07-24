from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = (
    ROOT
    / "docs"
    / "ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md"
)
SQL_ROOT = ROOT / "docs" / "zoho_control_tower_v2_sql"
MANIFEST = SQL_ROOT / "QUERY_TABLE_MANIFEST.csv"


def _manifest_files() -> set[str]:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["sql_file"] for row in csv.DictReader(handle)}


def _sql_dependency_closure(filename: str, seen: set[str] | None = None) -> str:
    seen = set() if seen is None else seen
    if filename in seen:
        return ""
    seen.add(filename)
    sql = (SQL_ROOT / filename).read_text(encoding="utf-8")
    dependencies = re.findall(r'"(\d{2}_[a-z0-9_]+\.sql)"', sql)
    return "\n".join(
        [sql]
        + [
            _sql_dependency_closure(dependency, seen)
            for dependency in dependencies
        ]
    )


class PreDashboardSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RUNBOOK.read_text(encoding="utf-8")
        cls.manifest_files = _manifest_files()

    def test_runbook_references_every_current_query_and_no_unknown_query(self) -> None:
        references = set(
            re.findall(r"\b\d{2}_[a-z0-9_]+\.sql\b", self.text)
        )
        self.assertEqual(self.manifest_files, references)
        for order in range(1, 39):
            self.assertIn(f"| {order:02d} |", self.text)

    def test_lookup_parent_keys_exist_in_their_sql(self) -> None:
        parents = {
            "37_dim_ct_outlet_enriched.sql": "outlet_code",
            "14_dim_ct_item.sql": "item_code",
            "15_dim_ct_menu_item.sql": "menu_item_code",
            "16_dim_ct_vendor.sql": "vendor_name",
            "12_dim_ct_date.sql": "calendar_date",
        }
        for filename, key in parents.items():
            sql = (SQL_ROOT / filename).read_text(encoding="utf-8")
            self.assertIn(f'AS "{key}"', sql, filename)

    def test_dashboard_source_columns_exist_in_their_sql(self) -> None:
        required = {
            "18_fact_ct_sales.sql": {"item_code"},
            "20_fact_ct_actual_consumption.sql": {
                "transfer_out_qty",
                "return_qty",
                "closing_qty",
                "bridge_transfer_out_qty",
                "bridge_return_qty",
                "bridge_closing_qty",
            },
            "21_fact_ct_consumption_variance.sql": {
                "variance_qty",
                "average_unit_cost",
                "leakage_value",
                "low_consumption_qty",
                "signed_consumption_variance_value",
                "consumption_variance_direction",
            },
            "22_fact_ct_purchase_order.sql": {
                "is_open_po",
                "po_number",
                "vendor_name",
                "delayed_po_flag",
            },
            "23_fact_ct_purchase_receipt.sql": {
                "received_qty",
                "receipt_subtotal",
                "grn_number",
            },
            "24_fact_ct_po_receipt_line.sql": {
                "ordered_qty",
                "received_qty",
                "eligible_closed_line_flag",
                "otif_success_flag",
                "eligible_lead_time_deviation_days",
            },
            "25_fact_ct_menu_profitability.sql": {
                "net_sales",
                "gross_margin_value",
            },
            "27_fact_ct_inventory_risk.sql": {
                "risk_severity",
                "outlet_code",
                "action_id",
            },
            "28_fact_ct_menu_impact.sql": {
                "menu_item_code",
                "allocated_forecast_net_sales_at_risk",
            },
            "31_sum_ct_price_movement.sql": {
                "price_comparison_key",
                "unit_price_change_percent",
                "absolute_unit_price_change_percent",
                "price_movement_direction",
            },
            "33_sum_ct_scm_monthly.sql": {
                "closing_stock_value",
                "open_po_value",
                "working_capital_value",
            },
            "34_fact_ct_data_quality_exception.sql": {"exception_count"},
            "36_fact_ct_risky_po.sql": {"po_number"},
            "38_fact_ct_expiry_risk.sql": {
                "action_id",
                "outlet_code",
                "expiry_qty_at_risk",
            },
        }
        for filename, columns in required.items():
            sql = _sql_dependency_closure(filename)
            for column in columns:
                self.assertIn(f'"{column}"', sql, f"{filename}.{column}")

    def test_critical_grain_guardrails_are_explicit(self) -> None:
        compact_text = " ".join(self.text.split())
        required_text = {
            "Do not create this lookup on Query 34",
            "Do not connect `18_fact_ct_sales.sql.item_code`",
            "Do not use row count as PO count",
            "Never average row unit prices",
            "Do not average the row-level `gross_margin_percent`",
            "Do not sum `forecast_net_sales_at_risk`",
            "Default value: month_03",
            "Synthetic demo estimate - no POSIST batch/expiry source",
            "do not search for an Aggregate Formula name in a direct KPI Widget",
            "Exactly four required formulas saved",
        }
        for statement in required_text:
            self.assertIn(statement, compact_text)

    def test_only_true_ratio_metrics_are_required_aggregate_formulas(self) -> None:
        formula_names = set(
            re.findall(r"^Name: (.+)$", self.text, flags=re.MULTILINE)
        )
        self.assertEqual(
            {
                "Weighted Unit Price",
                "PO Fill Rate %",
                "Vendor OTIF %",
                "Menu Gross Margin %",
            },
            formula_names,
        )


if __name__ == "__main__":
    unittest.main()
