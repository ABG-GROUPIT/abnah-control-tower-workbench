"""Generate the Control Tower presentation contract, handbooks, and site snapshot.

The dashboard story register below is the single presentation source of truth.
It deliberately contains no screenshots, full operational rows, customer data,
or local source paths. The site receives only governed lineage metadata, exact
Query Table SQL, and narrowly redacted issue evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = ROOT / "docs" / "zoho_control_tower_v2_sql"
DOCS_ROOT = ROOT / "docs"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=True))


def report(
    name: str,
    report_id: str,
    role: str,
    fields: list[str],
    evidence: str = "captured_posist_report",
) -> dict[str, Any]:
    return {
        "name": name,
        "reportId": report_id,
        "role": role,
        "fields": fields,
        "evidence": evidence,
    }


PAGES = [
    {
        "id": "page_1_risk_action_center",
        "number": 1,
        "name": "Risk Action Center",
        "purpose": "Show what needs action now across stockout, menu impact, expiry demonstration, and linked open purchase orders.",
    },
    {
        "id": "page_2_procurement_vendor_capital",
        "number": 2,
        "name": "Procurement, Vendor & Capital Control",
        "purpose": "Explain purchase commitments, receipts, vendor performance, price movement, and capital exposure.",
    },
    {
        "id": "page_3_consumption_menu_profitability",
        "number": 3,
        "name": "Consumption Variance & Menu Profitability",
        "purpose": "Connect actual and theoretical consumption to leakage, menu cost, sales, and margin.",
    },
    {
        "id": "page_4_scm_explorer_data_quality",
        "number": 4,
        "name": "SCM Descriptive Explorer & Data Quality",
        "purpose": "Provide governed totals, trends, drilldowns, exports, and explicit data-quality exceptions.",
    },
]


SOURCE_PROFILES: dict[str, dict[str, Any]] = {
    "05_std_ct_inventory_snapshot.sql": {
        "grain": "Source period, outlet, and inventory item checkpoint",
        "reports": [
            report(
                "Closing Stock Report",
                "report:p4_stock_admin:06_analytical_reports:04_closing_stock_report",
                "Current quantity, average cost, and closing valuation evidence",
                [
                    "Deployment",
                    "Date",
                    "Generation Date",
                    "Item Code",
                    "Item Name",
                    "Category Name",
                    "Unit Name",
                    "Average Price",
                    "Total Qty",
                    "Total Amt",
                ],
            )
        ],
        "route": [
            "RAWN_CT_closing_stock-Copy",
            "05_std_ct_inventory_snapshot.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
        ],
        "joinLogic": "No cross-report join in the final table; normalize outlet, item, period, UOM, quantity, and value.",
        "guardrails": [
            "Use one source period for a current-state stock value.",
            "Do not add quantities across unlike UOMs.",
        ],
    },
    "18_fact_ct_sales.sql": {
        "grain": "Sales date, outlet, bill, and menu item",
        "reports": [
            report(
                "Gross/Net Margin Report",
                "report:p2_reports:07_sales:33_food_sold_report",
                "Bill-item sales, quantity, realized revenue, and source cost evidence",
                [
                    "Store Name",
                    "Date",
                    "Bill No.",
                    "Super Category",
                    "Category",
                    "SKU Code / Item No",
                    "SKU / Item Name",
                    "Item Qty",
                    "Net Sale Value",
                    "Purchase Value",
                ],
            )
        ],
        "route": [
            "RAWN_CT_gross_net_margin-Copy",
            "01_std_ct_sales_item.sql",
            "18_fact_ct_sales.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "sales_date -> 12_dim_ct_date.sql.calendar_date",
            "item_code -> 15_dim_ct_menu_item.sql.menu_item_code",
        ],
        "joinLogic": "No cross-report join in the fact; preserve the validated bill-item grain.",
        "guardrails": [
            "The sales item key is a menu item, not an inventory ingredient.",
            "Use source purchase value only where cost coverage is approved.",
        ],
    },
    "19_fact_ct_theoretical_consumption.sql": {
        "grain": "Source period, outlet, ingredient, and canonical UOM",
        "reports": [
            report(
                "Gross/Net Margin Report",
                "report:p2_reports:07_sales:33_food_sold_report",
                "Sold menu-item quantities used by the theoretical model",
                ["Store Name", "Date", "SKU Code / Item No", "SKU / Item Name", "Item Qty"],
            ),
            report(
                "Item Recipe Report",
                "report:p1_main:06_misc:18_item_recipe_report",
                "Menu-item to ingredient quantity and UOM bridge",
                [
                    "Item Number",
                    "Item Name",
                    "Qty",
                    "Recipe Unit",
                    "Ingredient Code",
                    "Ingredient Name",
                ],
            ),
            report(
                "Closing Stock Report",
                "report:p4_stock_admin:06_analytical_reports:04_closing_stock_report",
                "Ingredient UOM and average-cost reference",
                ["Item Code", "Item Name", "Unit Name", "Average Price"],
            ),
            report(
                "AUX Theoretical Consumption",
                "",
                "Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs",
                [
                    "source_period_code",
                    "outlet_code",
                    "item_code",
                    "canonical_uom",
                    "theoretical_consumption_qty",
                    "theoretical_consumption_value",
                ],
                "synthetic_model_input",
            ),
        ],
        "route": [
            "AUX_Theoretical_Consumption-Copy",
            "03_std_ct_theoretical_consumption.sql",
            "19_fact_ct_theoretical_consumption.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
        ],
        "joinLogic": "Sales quantity x governed recipe quantity x approved UOM conversion; cost value uses the normalized ingredient cost.",
        "guardrails": [
            "The current three-month values are synthetic, while the POSIST source fields and formula pattern are factual.",
            "Quantity comparisons require one canonical UOM.",
        ],
    },
    "20_fact_ct_actual_consumption.sql": {
        "grain": "Source period, outlet, inventory item, and canonical UOM",
        "reports": [
            report(
                "Enterprise Variance Report",
                "report:p4_stock_admin:01_enterprise_reports:08_enterprise_variance",
                "Opening, purchase, transfer, return, closing, and actual-consumption movement bridge",
                [
                    "Deployment Name",
                    "StoreKitchen Name",
                    "Item Code",
                    "Item Name",
                    "Average Price",
                    "Opening Qty",
                    "Purchase Qty",
                    "Stock In Qty",
                    "Stock Out Qty",
                    "Return Qty",
                    "Closing Qty",
                    "Actual Consumption",
                    "Unit",
                ],
            )
        ],
        "route": [
            "RAWN_CT_enterprise_variance_normal-Copy",
            "04_std_ct_inventory_period.sql",
            "20_fact_ct_actual_consumption.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
        ],
        "joinLogic": "Actual consumption = opening + receipts + transfer in - transfer out - returns - closing.",
        "guardrails": [
            "Signed bridge columns are report formula columns for presentation, not new source facts.",
            "Quantity totals require one canonical UOM.",
        ],
    },
    "21_fact_ct_consumption_variance.sql": {
        "grain": "Source period, outlet, inventory item, and canonical UOM",
        "reports": [],
        "inherits": ["20_fact_ct_actual_consumption.sql", "19_fact_ct_theoretical_consumption.sql"],
        "route": [
            "20_fact_ct_actual_consumption.sql",
            "19_fact_ct_theoretical_consumption.sql",
            "21_fact_ct_consumption_variance.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
        ],
        "joinLogic": "Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check.",
        "guardrails": [
            "Positive leakage is not the same as signed variance.",
            "Low consumption is a data/process check, not a favorable saving.",
        ],
    },
    "22_fact_ct_purchase_order.sql": {
        "grain": "Source period, outlet, purchase order, and item line",
        "reports": [
            report(
                "Enterprise Purchase Order Report",
                "report:p4_stock_admin:01_enterprise_reports:06_enterprise_purchase_order",
                "Ordered, processed, remaining, expected-date, status, and commitment-value evidence",
                [
                    "Deployment",
                    "Store Name",
                    "Vendor Name",
                    "PO Number",
                    "PO Date",
                    "Expected Delivery",
                    "PO Close Date/Partial Recieve Date",
                    "PO Status",
                    "Item Code",
                    "Item Name",
                    "Total Processed Qty",
                    "Remaining Balance Qty",
                    "Quantity",
                    "Unit",
                    "Unit Price",
                    "Total Item Cost",
                ],
            )
        ],
        "route": [
            "RAWN_CT_enterprise_purchase_order-Copy",
            "07_std_ct_purchase_order.sql",
            "22_fact_ct_purchase_order.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
            "vendor_name -> 16_dim_ct_vendor.sql.vendor_name",
        ],
        "joinLogic": "Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain.",
        "guardrails": [
            "Use distinct PO number for PO counts; row count is a PO-line count.",
            "Expected-date exceptions are operational states, not automatically source defects.",
        ],
    },
    "23_fact_ct_purchase_receipt.sql": {
        "grain": "Source period, outlet, stock-entry transaction, and item line",
        "reports": [
            report(
                "Enterprise Entry Report - Stock Entry",
                "report:p4_stock_admin:01_enterprise_reports:01_enterprise_entry",
                "GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference",
                [
                    "Deployment Name",
                    "Store/Kitchen Name",
                    "Vendor Name",
                    "Date",
                    "Transaction Number",
                    "Invoice Number",
                    "PO Number",
                    "Item Code",
                    "Item Name",
                    "Quantity",
                    "Unit",
                    "Unit Price",
                    "Amount",
                    "Total Tax",
                    "Total",
                ],
            )
        ],
        "route": [
            "RAWN_CT_enterprise_entry-Copy",
            "08_std_ct_purchase_receipt.sql",
            "23_fact_ct_purchase_receipt.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
            "vendor_name -> 16_dim_ct_vendor.sql.vendor_name",
        ],
        "joinLogic": "Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier.",
        "guardrails": [
            "Weighted price is receipt subtotal divided by received quantity.",
            "PO linkage remains sparse in the audited actual extract.",
        ],
    },
    "24_fact_ct_po_receipt_line.sql": {
        "grain": "Source period, outlet, purchase order, and item line",
        "reports": [],
        "inherits": ["22_fact_ct_purchase_order.sql", "23_fact_ct_purchase_receipt.sql"],
        "route": [
            "07_std_ct_purchase_order.sql",
            "08_std_ct_purchase_receipt.sql",
            "24_fact_ct_po_receipt_line.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
            "vendor_name -> 16_dim_ct_vendor.sql.vendor_name",
        ],
        "joinLogic": "Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join.",
        "guardrails": [
            "Actual PO-to-GRN linkage was sparse, so OTIF remains a formula demonstration.",
            "Fill rate uses sums of quantities, never an average of row percentages.",
        ],
    },
    "25_fact_ct_menu_profitability.sql": {
        "grain": "Source period, outlet, and menu item",
        "reports": [],
        "inherits": ["18_fact_ct_sales.sql", "19_fact_ct_theoretical_consumption.sql"],
        "route": [
            "01_std_ct_sales_item.sql",
            "17_dim_ct_recipe_effective.sql",
            "25_fact_ct_menu_profitability.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code",
        ],
        "joinLogic": "Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.",
        "guardrails": [
            "Menu gross margin percent is ratio of summed margin to summed sales.",
            "Do not average row-level margin percentages.",
        ],
    },
    "26_fact_ct_forecast_ingredient_demand.sql": {
        "grain": "Source period, outlet, forecast menu item, and recipe ingredient",
        "reports": [
            report(
                "Item Recipe Report",
                "report:p1_main:06_misc:18_item_recipe_report",
                "Menu-to-ingredient conversion",
                ["Item Number", "Qty", "Recipe Unit", "Ingredient Code", "Ingredient Name"],
            ),
            report(
                "AUX Menu Demand Forecast",
                "",
                "Synthetic seven-day menu demand and net-sales forecast",
                [
                    "source_period_code",
                    "outlet_code",
                    "menu_item_code",
                    "forecast_menu_qty",
                    "forecast_net_sales",
                ],
                "synthetic_model_input",
            ),
        ],
        "route": [
            "AUX_Menu_Demand_Forecast-Copy",
            "11_std_ct_menu_forecast.sql",
            "17_dim_ct_recipe_effective.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
            "menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code",
        ],
        "joinLogic": "Join forecast menu item to effective recipe and multiply forecast menu quantity by recipe ingredient quantity.",
        "guardrails": [
            "Forecast values are synthetic model output, not observed POSIST demand.",
            "Production needs an approved forecast source and version policy.",
        ],
    },
    "27_fact_ct_inventory_risk.sql": {
        "grain": "Source period, outlet, and inventory ingredient checkpoint",
        "reports": [],
        "inherits": [
            "05_std_ct_inventory_snapshot.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
            "22_fact_ct_purchase_order.sql",
        ],
        "route": [
            "05_std_ct_inventory_snapshot.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
            "22_fact_ct_purchase_order.sql",
            "27_fact_ct_inventory_risk.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
        ],
        "joinLogic": "Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.",
        "guardrails": [
            "The 15% safety factor is a demo rule pending ABNAH approval.",
            "Query 27 covers stockout exposure only; expiry is separate.",
        ],
    },
    "28_fact_ct_menu_impact.sql": {
        "grain": "Source period, outlet, risky ingredient, and impacted menu item",
        "reports": [],
        "inherits": [
            "05_std_ct_inventory_snapshot.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
            "22_fact_ct_purchase_order.sql",
        ],
        "route": [
            "05_std_ct_inventory_snapshot.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
            "22_fact_ct_purchase_order.sql",
            "28_fact_ct_menu_impact.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "ingredient_code -> 14_dim_ct_item.sql.item_code",
            "menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code",
        ],
        "joinLogic": "Identify shortage ingredients, connect them to forecast menu items, and allocate each menu item's forecast sales across its risky ingredients.",
        "guardrails": [
            "Sum allocated_forecast_net_sales_at_risk, not the repeating unallocated forecast value.",
            "Only risk rows are retained.",
        ],
    },
    "29_sum_ct_procurement_funnel.sql": {
        "grain": "Source period, outlet, and vendor",
        "reports": [],
        "inherits": ["22_fact_ct_purchase_order.sql"],
        "route": [
            "22_fact_ct_purchase_order.sql",
            "29_sum_ct_procurement_funnel.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "vendor_name -> 16_dim_ct_vendor.sql.vendor_name",
        ],
        "joinLogic": "Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts.",
        "guardrails": [
            "Monthly purchase is labelled Ordered Gross Value until the production basis is approved.",
            "Do not use row count as PO count.",
        ],
    },
    "30_sum_ct_vendor_scorecard.sql": {
        "grain": "Source period, outlet, and vendor",
        "reports": [],
        "inherits": ["24_fact_ct_po_receipt_line.sql"],
        "route": [
            "24_fact_ct_po_receipt_line.sql",
            "30_sum_ct_vendor_scorecard.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "vendor_name -> 16_dim_ct_vendor.sql.vendor_name",
        ],
        "joinLogic": "Aggregate PO/receipt line results into vendor purchase, open exposure, fill, eligible OTIF, and lead-time deviation.",
        "guardrails": [
            "Do not average vendor percentages across outlets.",
            "OTIF and lead deviation remain demonstration metrics until receipt linkage improves.",
        ],
    },
    "31_sum_ct_price_movement.sql": {
        "grain": "Source period, outlet, vendor, item, and canonical UOM",
        "reports": [],
        "inherits": ["23_fact_ct_purchase_receipt.sql"],
        "route": [
            "23_fact_ct_purchase_receipt.sql",
            "31_sum_ct_price_movement.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
            "vendor_name -> 16_dim_ct_vendor.sql.vendor_name",
        ],
        "joinLogic": "Calculate weighted receipt price per period and compare it with the immediately prior synthetic month at the same outlet/vendor/item/UOM grain.",
        "guardrails": [
            "Do not aggregate price-change percentages across items or UOMs.",
            "Use absolute change only for sorting; display the signed change.",
        ],
    },
    "32_sum_ct_menu_profitability.sql": {
        "grain": "Source period, outlet, and menu item",
        "reports": [],
        "inherits": ["25_fact_ct_menu_profitability.sql"],
        "route": [
            "25_fact_ct_menu_profitability.sql",
            "32_sum_ct_menu_profitability.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code",
        ],
        "joinLogic": "Classify menu items into synthetic BCG quadrants from sold quantity and gross margin percent.",
        "guardrails": [
            "Use one source period and one outlet, or keep outlet visible.",
            "BCG thresholds are demonstration rules pending business approval.",
        ],
    },
    "33_sum_ct_scm_monthly.sql": {
        "grain": "Source period and outlet",
        "reports": [],
        "inherits": [
            "18_fact_ct_sales.sql",
            "05_std_ct_inventory_snapshot.sql",
            "22_fact_ct_purchase_order.sql",
            "20_fact_ct_actual_consumption.sql",
        ],
        "route": [
            "18_fact_ct_sales.sql",
            "05_std_ct_inventory_snapshot.sql",
            "22_fact_ct_purchase_order.sql",
            "20_fact_ct_actual_consumption.sql",
            "33_sum_ct_scm_monthly.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
        ],
        "joinLogic": "Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.",
        "guardrails": [
            "Current-state stock and working-capital widgets require one source period.",
            "This is a descriptive monthly summary, not a transaction table.",
        ],
    },
    "34_fact_ct_data_quality_exception.sql": {
        "grain": "One generated exception record",
        "reports": [],
        "inherits": [
            "05_std_ct_inventory_snapshot.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
            "18_fact_ct_sales.sql",
            "22_fact_ct_purchase_order.sql",
            "23_fact_ct_purchase_receipt.sql",
        ],
        "route": [
            "Governed source and model checks",
            "34_fact_ct_data_quality_exception.sql",
        ],
        "lookups": [],
        "joinLogic": "UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.",
        "guardrails": [
            "Do not create outlet/item lookups; ALL and blank keys are intentional.",
            "A zero count means the check ran and found no exception.",
        ],
    },
    "35_sum_ct_financial_leakage.sql": {
        "grain": "Source period and outlet",
        "reports": [
            report(
                "Enterprise Wastage Report",
                "report:p4_stock_admin:01_enterprise_reports:12_enterprise_wastage_report",
                "Observed wastage quantity and value",
                [
                    "Deployment Name",
                    "Store/Kitchen Name",
                    "Date",
                    "Transaction Number",
                    "Item Code",
                    "Item Name",
                    "Quantity",
                    "Unit",
                    "Unit Price",
                    "Amount",
                ],
            )
        ],
        "route": [
            "RAWN_CT_enterprise_wastage_normal-Copy",
            "09_std_ct_wastage.sql",
            "35_sum_ct_financial_leakage.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
        ],
        "joinLogic": "Aggregate observed wastage value by period and outlet.",
        "guardrails": [
            "Label as Observed Wastage, not total financial leakage.",
            "Vendor returns and production expiry are unavailable.",
        ],
    },
    "36_fact_ct_risky_po.sql": {
        "grain": "Source period, outlet, open PO, and risky item line",
        "reports": [],
        "inherits": [
            "05_std_ct_inventory_snapshot.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
            "22_fact_ct_purchase_order.sql",
        ],
        "route": [
            "05_std_ct_inventory_snapshot.sql",
            "26_fact_ct_forecast_ingredient_demand.sql",
            "22_fact_ct_purchase_order.sql",
            "36_fact_ct_risky_po.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
            "vendor_name -> 16_dim_ct_vendor.sql.vendor_name",
        ],
        "joinLogic": "Retain open PO lines only where the matching item checkpoint is purple, red, or amber.",
        "guardrails": [
            "Count distinct PO number, not rows.",
            "Open PO quantity may reduce shortage risk but does not guarantee on-time receipt.",
        ],
    },
    "38_fact_ct_expiry_risk.sql": {
        "grain": "Source period, outlet, synthetic batch allocation, and item",
        "reports": [
            report(
                "Enterprise Entry Report - Stock Entry",
                "report:p4_stock_admin:01_enterprise_reports:01_enterprise_entry",
                "Receipt date, GRN, PO, vendor, quantity, and cost pattern used for traceable demo tranches",
                [
                    "Date",
                    "Transaction Number",
                    "PO Number",
                    "Vendor Name",
                    "Item Code",
                    "Item Name",
                    "Quantity",
                    "Unit",
                    "Unit Price",
                ],
            ),
            report(
                "Closing Stock Report",
                "report:p4_stock_admin:06_analytical_reports:04_closing_stock_report",
                "Current item quantity and average-cost boundary",
                ["Date", "Item Code", "Item Name", "Unit Name", "Average Price", "Total Qty"],
            ),
            report(
                "AUX Expiry Estimate",
                "",
                "Synthetic FIFO tranche and shelf-life scenario; not a POSIST batch or expiry source",
                [
                    "batch_allocation_id",
                    "receipt_date",
                    "estimated_expiry_date",
                    "expiry_qty_at_risk",
                    "expiry_risk_value",
                    "production_use_status",
                ],
                "synthetic_model_input",
            ),
        ],
        "route": [
            "AUX_Expiry_Estimate-Copy",
            "38_fact_ct_expiry_risk.sql",
        ],
        "lookups": [
            "outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code",
            "item_code -> 14_dim_ct_item.sql.item_code",
        ],
        "joinLogic": "Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels.",
        "guardrails": [
            "Every title or subtitle must say Synthetic demo estimate - no POSIST batch/expiry source.",
            "Do not present the scenario as actual batch ageing or expiry truth.",
        ],
    },
}


def inherit_profiles() -> None:
    """Expand inherited source reports while preserving first occurrence order."""
    for profile in SOURCE_PROFILES.values():
        inherited = profile.get("inherits", [])
        combined: list[dict[str, Any]] = list(profile.get("reports", []))
        seen = {(item["name"], item.get("evidence", "")) for item in combined}
        for parent_name in inherited:
            parent = SOURCE_PROFILES[parent_name]
            for item in parent.get("reports", []):
                key = (item["name"], item.get("evidence", ""))
                if key not in seen:
                    combined.append(item)
                    seen.add(key)
        profile["reports"] = combined


def story(
    page_id: str,
    story_id: str,
    name: str,
    kind: str,
    visual: str,
    source_table: str,
    question: str,
    final_fields: list[str],
    formula: str,
    aggregation: str,
    shelves: list[str],
    *,
    fixed_filters: list[str] | None = None,
    user_filters: list[str] | None = None,
    sort: str = "Business-relevant default order",
    tooltips: list[str] | None = None,
    formatting: list[str] | None = None,
    caveats: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": story_id,
        "pageId": page_id,
        "name": name,
        "kind": kind,
        "visual": visual,
        "sourceTable": source_table,
        "question": question,
        "finalFields": final_fields,
        "formula": formula,
        "aggregation": aggregation,
        "zoho": {
            "shelves": shelves,
            "fixedFilters": fixed_filters or [],
            "userFilters": user_filters or [],
            "sort": sort,
            "tooltips": tooltips or [],
            "formatting": formatting or [],
        },
        "caveats": caveats or [],
    }


P1 = "page_1_risk_action_center"
P2 = "page_2_procurement_vendor_capital"
P3 = "page_3_consumption_menu_profitability"
P4 = "page_4_scm_explorer_data_quality"


STORIES: list[dict[str, Any]] = []

P1_FILTERS = [
    "Source period (global, single-select; default month_03)",
    "Outlet (global, multi-select)",
    "Region",
    "New/matured",
    "Risk severity",
    "Action owner",
    "Ingredient category",
]
P2_FILTERS = [
    "Source period (global, single-select; default month_03)",
    "Outlet (global, multi-select)",
    "Region",
    "Vendor",
    "Ingredient category",
    "Item",
    "PO status",
]
P3_FILTERS = [
    "Source period (global, single-select; default month_03)",
    "Outlet (global, multi-select)",
    "Region",
    "Menu category",
    "Menu item",
    "Ingredient category",
    "Ingredient",
    "Canonical UOM",
]
P4_FILTERS = [
    "Source period (global, single-select; default month_03)",
    "Outlet (global, multi-select)",
    "Region",
    "Item",
    "Vendor",
    "Exception type",
]


# Page 1 - Risk Action Center
STORIES.extend(
    [
        story(
            P1,
            "CT_P1_KPI_Outlets_At_Stockout_Risk",
            "Outlets At Stockout Risk",
            "kpi",
            "KPI widget",
            "27_fact_ct_inventory_risk.sql",
            "How many outlets require stockout action in the selected checkpoint?",
            ["outlet_code", "risk_type"],
            'Direct KPI Data Column "outlet_code"; Show Value As Count Distinct.',
            "Distinct count of physical outlet_code",
            ["Data Column: outlet_code", "Show Value As: Count Distinct", "Group By: blank"],
            fixed_filters=["Filter shelf: risk_type / Individual Values / Include STOCKOUT"],
            user_filters=P1_FILTERS,
            formatting=["Whole number"],
        ),
        story(
            P1,
            "CT_P1_KPI_Menu_Items_At_Risk",
            "Menu Items At Risk",
            "kpi",
            "KPI widget",
            "28_fact_ct_menu_impact.sql",
            "How many menu items depend on ingredients that cannot meet the forecast requirement?",
            ["menu_item_code", "shortage_qty", "risk_severity"],
            'distinctcount("menu_item_code")',
            "Distinct count of menu_item_code",
            ["Data Column: menu_item_code", "Show Value As: Count Distinct", "Group By: blank"],
            user_filters=P1_FILTERS,
            formatting=["Whole number"],
        ),
        story(
            P1,
            "CT_P1_KPI_Stockout_Risk_Value",
            "Stockout Sales At Risk",
            "kpi",
            "KPI widget",
            "28_fact_ct_menu_impact.sql",
            "How much forecast menu revenue is allocated to current ingredient shortages?",
            ["shortage_qty", "allocated_forecast_net_sales_at_risk"],
            'sum("allocated_forecast_net_sales_at_risk")',
            "Sum allocated forecast net sales at risk",
            ["Data Column: allocated_forecast_net_sales_at_risk", "Show Value As: Sum", "Group By: blank"],
            user_filters=P1_FILTERS,
            formatting=["INR currency", "Compact notation"],
            caveats=["Never sum forecast_net_sales_at_risk because it repeats for multi-ingredient menu items."],
        ),
        story(
            P1,
            "CT_P1_KPI_Expiry_Risk_Value_Demo",
            "Expiry Risk Value - Demo Estimate",
            "kpi",
            "KPI widget",
            "38_fact_ct_expiry_risk.sql",
            "What value is exposed in the synthetic FIFO and shelf-life scenario?",
            ["expiry_risk_value", "production_use_status", "is_estimated"],
            'sum("expiry_risk_value")',
            "Sum expiry risk value",
            ["Data Column: expiry_risk_value", "Show Value As: Sum", "Group By: blank"],
            user_filters=P1_FILTERS,
            formatting=["INR currency", "Subtitle: Synthetic estimate - no POSIST batch/expiry source"],
        ),
        story(
            P1,
            "CT_P1_KPI_Open_Risky_PO",
            "Open Risky PO Count",
            "kpi",
            "KPI widget",
            "36_fact_ct_risky_po.sql",
            "How many distinct open POs relate to ingredients already in a stockout-risk state?",
            ["po_number", "risk_severity", "open_po_value"],
            'distinctcount("po_number")',
            "Distinct count of PO number",
            ["Data Column: po_number", "Show Value As: Count Distinct", "Group By: blank"],
            user_filters=P1_FILTERS,
            formatting=["Whole number"],
        ),
        story(
            P1,
            "CT_P1_Outlet_Risk_Map",
            "Outlet Risk Map",
            "chart",
            "Map",
            "27_fact_ct_inventory_risk.sql",
            "Where are stockout-risk outlets located and how severe is their highest current risk?",
            ["outlet_code", "risk_severity_rank", "shortage_cost_value", "days_cover"],
            "Maximum risk severity rank by outlet; supporting values remain additive or distinct at outlet scope.",
            "Max severity rank, distinct risk items, sum shortage cost",
            [
                "Location: outlet via 37_dim_ct_outlet_enriched.sql",
                "Latitude/longitude: enriched outlet fields",
                "Color: max risk_severity_rank",
            ],
            fixed_filters=["Filter shelf: risk_type / Individual Values / Include STOCKOUT"],
            user_filters=P1_FILTERS,
            tooltips=["Outlet", "Distinct risk item count", "Shortage cost", "Days cover", "Maximum severity"],
            caveats=["Synthetic geography must be replaced by an approved ABNAH outlet reference for production."],
        ),
        story(
            P1,
            "CT_P1_Stockout_Priority_Stack",
            "Stockout Priority Stack",
            "chart",
            "Horizontal stacked bar",
            "27_fact_ct_inventory_risk.sql",
            "Which outlets carry the largest shortage-cost exposure by severity?",
            ["outlet_code", "shortage_cost_value", "risk_severity", "risk_severity_rank"],
            'sum("shortage_cost_value")',
            "Sum shortage cost value",
            ["Y: outlet", "X: shortage cost value", "Color: risk severity"],
            fixed_filters=["Filter shelf: risk_type / Individual Values / Include STOCKOUT"],
            user_filters=P1_FILTERS,
            sort="Risk severity rank descending, then shortage cost descending",
            tooltips=["Item count", "Shortage quantity", "Days cover"],
            formatting=["RAG palette only for severity"],
        ),
        story(
            P1,
            "CT_P1_Action_Center",
            "Risk Action Center",
            "table",
            "Tabular",
            "27_fact_ct_inventory_risk.sql",
            "What exact stockout action, owner, and due band should operations see?",
            [
                "action_id",
                "outlet_code",
                "item_code",
                "risk_severity",
                "shortage_qty",
                "recommended_action",
                "action_owner",
                "due_band",
                "total_risk_value",
            ],
            "Direct fact fields; no dashboard-only calculation.",
            "One row per risk action",
            [
                "Columns: action ID, outlet, item, severity, shortage, recommended action, owner, due band",
            ],
            fixed_filters=["Filter shelf: risk_type / Individual Values / Include STOCKOUT"],
            user_filters=P1_FILTERS,
            sort="risk_severity_rank descending, total_risk_value descending, due_band ascending",
            formatting=["Conditional format severity with approved RAG palette", "Enable View Underlying Data"],
        ),
        story(
            P1,
            "CT_P1_Stockout_Risk_Detail",
            "Stockout Risk Detail",
            "table",
            "Tabular",
            "27_fact_ct_inventory_risk.sql",
            "Which stock, forecast, safety, inbound, and cost inputs created each shortage?",
            [
                "item_code",
                "current_stock_qty",
                "forecast_required_qty",
                "required_qty_with_safety",
                "valid_open_po_qty",
                "shortage_qty",
                "days_cover",
                "shortage_cost_value",
                "risk_severity",
            ],
            "shortage_qty = max(0, forecast_required_qty * 1.15 - current_stock_qty - valid_open_po_qty)",
            "Direct detail rows",
            ["Columns: item, stock, forecast, safety requirement, inbound, shortage, days cover, cost, severity"],
            fixed_filters=["Filter shelf: risk_type / Individual Values / Include STOCKOUT"],
            user_filters=P1_FILTERS,
            sort="risk_severity_rank descending, shortage_cost_value descending",
        ),
        story(
            P1,
            "CT_P1_Menu_Impact_Detail",
            "Menu Impact Detail",
            "table",
            "Tabular",
            "28_fact_ct_menu_impact.sql",
            "Which menu items and forecast sales are exposed by each risky ingredient?",
            [
                "ingredient_code",
                "menu_item_code",
                "risk_severity",
                "forecast_menu_qty",
                "allocated_forecast_net_sales_at_risk",
            ],
            "Allocated sales at risk = forecast menu sales / count of risky ingredients for that menu item.",
            "Direct rows; sum only the allocated value",
            ["Columns: ingredient, menu item, severity, forecast menu quantity, allocated sales at risk"],
            user_filters=P1_FILTERS,
            sort="Allocated sales at risk descending",
        ),
        story(
            P1,
            "CT_P1_Expiry_Risk_Detail_Demo",
            "Expiry Risk Detail - Demo",
            "table",
            "Tabular",
            "38_fact_ct_expiry_risk.sql",
            "How does the synthetic expiry scenario trace each at-risk FIFO tranche?",
            [
                "batch_allocation_id",
                "receipt_date",
                "grn_number",
                "po_number",
                "vendor_name",
                "item_closing_qty",
                "estimated_fifo_tranche_qty",
                "expected_consumption_before_expiry",
                "expiry_qty_at_risk",
                "expiry_risk_value",
                "estimated_expiry_date",
                "risk_severity",
                "estimation_method",
            ],
            "Scenario output is already calculated in AUX_Expiry_Estimate-Copy.",
            "One row per synthetic batch allocation",
            ["Columns: traceability, scenario inputs, at-risk quantity/value, estimated date, severity, method"],
            user_filters=P1_FILTERS,
            sort="risk_severity_rank descending, expiry_risk_value descending",
            formatting=["Permanent synthetic-source qualifier"],
        ),
        story(
            P1,
            "CT_P1_Vendor_PO_Risk",
            "Vendor PO Risk",
            "table",
            "Tabular",
            "36_fact_ct_risky_po.sql",
            "Which open vendor POs are linked to current shortage-risk ingredients?",
            [
                "po_number",
                "vendor_name",
                "expected_delivery_date",
                "remaining_qty",
                "open_po_value",
                "risk_severity",
            ],
            "Direct filtered risky-PO fact rows.",
            "One row per open risky PO item line",
            ["Columns: PO, vendor, expected date, remaining quantity, liability, severity"],
            user_filters=P1_FILTERS,
            sort="risk_severity_rank descending, open_po_value descending",
        ),
    ]
)


LAYER_DEFINITIONS = [
    {
        "id": "raw",
        "order": 0,
        "label": "RAW landing",
        "shortLabel": "RAW",
        "purpose": "Preserve the POSIST-shaped imports and synthetic auxiliary inputs without business reinterpretation.",
        "example": "RAWN_CT_enterprise_purchase_order-Copy preserves the purchase-order export before status and value rules.",
    },
    {
        "id": "standardized",
        "order": 1,
        "label": "Standardized",
        "shortLabel": "STD",
        "purpose": "Normalize identifiers, dates, status, UOM, signs, and reusable field names while retaining auditability.",
        "example": "07_std_ct_purchase_order.sql normalizes PO status and line measures before procurement KPIs use them.",
    },
    {
        "id": "dimension",
        "order": 2,
        "label": "Dimensions",
        "shortLabel": "DIM",
        "purpose": "Provide one governed parent row for dates, outlets, items, menu items, vendors, and effective recipes.",
        "example": "37_dim_ct_outlet_enriched.sql is the canonical outlet parent for dashboard lookups.",
    },
    {
        "id": "fact",
        "order": 3,
        "label": "Facts",
        "shortLabel": "FACT",
        "purpose": "Represent additive events or governed analytical grains such as sales, PO lines, consumption variance, and risk actions.",
        "example": "27_fact_ct_inventory_risk.sql joins stock, forecast requirement, and open PO supply at item-checkpoint grain.",
    },
    {
        "id": "summary",
        "order": 4,
        "label": "Summaries",
        "shortLabel": "SUM",
        "purpose": "Pre-aggregate reusable dashboard grains so Zoho charts do not repeat complex joins or invalid percentage aggregation.",
        "example": "30_sum_ct_vendor_scorecard.sql publishes vendor-period metrics for the scorecard and performance matrix.",
    },
]


def build_model_catalog() -> dict[str, Any]:
    manifest_path = SQL_ROOT / "QUERY_TABLE_MANIFEST.csv"
    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tables = []
    for row in rows:
        sql_path = SQL_ROOT / row["sql_file"]
        if not sql_path.exists():
            raise FileNotFoundError(f"Missing Query Table SQL: {sql_path}")
        sources = [value for value in row["sources"].split(";") if value]
        dependencies = [value for value in sources if value.endswith(".sql")]
        raw_inputs = [value for value in sources if not value.endswith(".sql")]
        tables.append(
            {
                "buildOrder": int(row["build_order"]),
                "layer": row["layer"],
                "physicalName": row["query_table_name"],
                "logicalName": row["logical_model_name"],
                "dependencyLevel": int(row["dependency_level"]),
                "purpose": row["purpose"],
                "sources": sources,
                "dependencies": dependencies,
                "rawInputs": raw_inputs,
                "sql": sql_path.read_text(encoding="utf-8").rstrip(),
            }
        )
    if len(tables) != 38:
        raise ValueError(f"Expected 38 Query Tables, found {len(tables)}")
    return {
        "contractVersion": "1.0.0",
        "title": "ABNAH Control Tower v2 Model Library",
        "sourcePolicy": "Exact Query Table SQL and model metadata only. No screenshots or operational rows.",
        "layers": LAYER_DEFINITIONS,
        "tables": tables,
    }


def build_presentation_contract() -> dict[str, Any]:
    inherit_profiles()
    page_order = {page["id"]: page["number"] for page in PAGES}
    ordered_stories = sorted(STORIES, key=lambda item: (page_order[item["pageId"]], item["id"]))
    story_ids = [item["id"] for item in ordered_stories]
    if len(story_ids) != len(set(story_ids)):
        raise ValueError("Presentation story IDs must be unique.")
    unknown_sources = sorted(
        {item["sourceTable"] for item in ordered_stories} - set(SOURCE_PROFILES)
    )
    if unknown_sources:
        raise ValueError(f"Stories reference unknown source profiles: {unknown_sources}")
    for item in ordered_stories:
        profile = SOURCE_PROFILES[item["sourceTable"]]
        source_names = [source["name"] for source in profile["reports"]]
        source_text = ", ".join(source_names)
        item["talkTrack"] = (
            f"{item['name']} starts from {source_text}. "
            f"The model follows {' -> '.join(profile['route'])} at {profile['grain'].lower()}. "
            f"The relationship rule is: {profile['joinLogic']} "
            f"In Zoho, use {item['aggregation'].lower()} and render it as {item['visual'].lower()} "
            f"to answer: {item['question']}"
        )
    return {
        "contractVersion": "1.0.0",
        "status": "dashboard_build_ready_on_synthetic_baseline",
        "title": "ABNAH KPI and Chart Story Register",
        "sourcePolicy": (
            "Schema, lineage, formulas, and redacted issue evidence only. "
            "No screenshots, full operational rows, customer fields, or local paths."
        ),
        "syncPolicy": (
            "Run scripts/build_control_tower_presentation.py after a Query Table or final chart change. "
            "The same contract regenerates the handbook and the site snapshot."
        ),
        "pages": PAGES,
        "sourceProfiles": SOURCE_PROFILES,
        "stories": ordered_stories,
        "counts": {
            "pages": len(PAGES),
            "stories": len(ordered_stories),
            "kpis": sum(item["kind"] == "kpi" for item in ordered_stories),
            "charts": sum(item["kind"] == "chart" for item in ordered_stories),
            "tables": sum(item["kind"] == "table" for item in ordered_stories),
            "queryTables": 38,
        },
    }


def markdown_list(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- None"


def source_table_markdown(profile: dict[str, Any]) -> str:
    rows = [
        "| Original report/input | Evidence level | Role | Exact fields used by this model profile |",
        "| --- | --- | --- | --- |",
    ]
    for item in profile["reports"]:
        rows.append(
            "| "
            + " | ".join(
                [
                    item["name"],
                    item["evidence"],
                    item["role"],
                    ", ".join(f"`{field}`" for field in item["fields"]),
                ]
            )
            + " |"
        )
    return "\n".join(rows)


def build_handbook(contract: dict[str, Any]) -> str:
    page_by_id = {page["id"]: page for page in contract["pages"]}
    lines = [
        "# ABNAH Control Tower KPI And Chart Lineage Handbook",
        "",
        "## Purpose",
        "",
        "Use this document when somebody asks where a KPI or chart came from, which POSIST fields support it, how the model joins them, and exactly how the final Zoho object is configured.",
        "",
        "This is generated from `docs/control_tower_presentation_contract.json`. Update the contract through `scripts/build_control_tower_presentation.py`; do not hand-edit this generated handbook.",
        "",
        "## Non-Negotiable Rules",
        "",
        "- The dashboard runs on a three-month synthetic baseline, but its source field names and transformation pattern follow the captured POSIST report contracts.",
        "- Expiry is always labelled as a synthetic demonstration because no enabled POSIST batch/expiry source exists.",
        "- OTIF and lead-time deviation remain formula demonstrations until actual PO-to-GRN linkage improves.",
        "- Current stock, risk, and working-capital widgets use exactly one source period.",
        "- Quantities across kg, litre, and pieces are never added without one canonical UOM.",
        "- Percentages are ratios of summed numerators and denominators, never averages of row percentages.",
        "",
        "## Search Index",
        "",
        "| Page | Object | Kind | Zoho visual | Final Query Table |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for item in contract["stories"]:
        page = page_by_id[item["pageId"]]
        lines.append(
            f"| {page['number']} | [{item['name']}](#{item['id'].lower().replace('_', '-')}) "
            f"| {item['kind']} | {item['visual']} | `{item['sourceTable']}` |"
        )
    for page in contract["pages"]:
        lines.extend(["", f"# Page {page['number']} - {page['name']}", "", page["purpose"]])
        for item in [story_item for story_item in contract["stories"] if story_item["pageId"] == page["id"]]:
            profile = contract["sourceProfiles"][item["sourceTable"]]
            combined_guardrails = list(dict.fromkeys(profile["guardrails"] + item["caveats"]))
            lines.extend(
                [
                    "",
                    f"<a id=\"{item['id'].lower().replace('_', '-')}\"></a>",
                    f"## {item['id']} - {item['name']}",
                    "",
                    f"**Business question:** {item['question']}",
                    "",
                    f"**Final object:** {item['kind']} / {item['visual']} from `{item['sourceTable']}`",
                    "",
                    f"**Final grain:** {profile['grain']}",
                    "",
                    "### Original Evidence",
                    "",
                    source_table_markdown(profile),
                    "",
                    "### Model Route And Relationship",
                    "",
                    f"`{' -> '.join(profile['route'])}`",
                    "",
                    f"**Join/relationship logic:** {profile['joinLogic']}",
                    "",
                    "**Zoho lookups:**",
                    "",
                    markdown_list([f"`{value}`" for value in profile["lookups"]]),
                    "",
                    "### Calculation",
                    "",
                    f"**Final fields:** {', '.join(f'`{field}`' for field in item['finalFields'])}",
                    "",
                    f"**Formula:** `{item['formula']}`",
                    "",
                    f"**Aggregation:** {item['aggregation']}",
                    "",
                    "### Exact Zoho Configuration",
                    "",
                    f"**Visual:** {item['visual']}",
                    "",
                    "**Shelves/columns:**",
                    "",
                    markdown_list(item["zoho"]["shelves"]),
                    "",
                    "**Fixed report filters:**",
                    "",
                    markdown_list(item["zoho"]["fixedFilters"]),
                    "",
                    "**User filters:**",
                    "",
                    markdown_list(item["zoho"]["userFilters"]),
                    "",
                    f"**Sort:** {item['zoho']['sort']}",
                    "",
                    "**Tooltips:**",
                    "",
                    markdown_list(item["zoho"]["tooltips"]),
                    "",
                    "**Formatting:**",
                    "",
                    markdown_list(item["zoho"]["formatting"]),
                    "",
                    "### Guardrails",
                    "",
                    markdown_list(combined_guardrails),
                    "",
                    "### How To Explain It",
                    "",
                    item["talkTrack"],
                ]
            )
    return "\n".join(lines)


def build_issue_brief() -> str:
    return """# Presentation-Safe Actual Data Findings

## What To Say First

The 26 captured CSV exports were structurally parseable: their headers matched the governed contracts, row widths were valid, and declared field types parsed. The reason for keeping the demo on synthetic data is not a parser failure. It is that several actual exports are not fit to publish the required current-state and valuation KPIs without freshness, cost-coverage, and valuation controls.

Present the three findings below. They are factual fit-for-use blockers. Do not say POSIST is definitively wrong; say the captured export cannot safely support the stated KPI without clarification or correction.

# 1. Critical - Closing Stock Snapshot Is Not Current

| Evidence | Verified value |
| --- | --- |
| Exact POSIST report | `Closing Stock Report` |
| Export context | Snapshot generated on 22 July 2026 |
| Exact source row | CSV row `2` (the same date pair appears across all 1,148 rows) |
| `Date` / stock date | `2026-06-16` |
| `Generation Date` | `2026-07-22` |
| Lag | `36 days` |

## Why This Claim Is Safe

The source explicitly dates the stock position 36 days before the generation date. The historical date may have been intentionally selected, so do not call the underlying quantity wrong. It is nevertheless guaranteed that this export cannot represent current stock as of 22 July.

## What Would Go Wrong In Zoho

- Current closing inventory would actually be a 16 June checkpoint.
- Days cover, projected stockout, shortage value, and working capital would inherit that stale quantity.
- A current action queue could recommend the wrong items or miss genuine shortages.

## Presentation Line

> The Closing Stock export generated on 22 July carried a 16 June stock date across all 1,148 rows. We therefore blocked it from current-state KPIs rather than presenting a 36-day-old checkpoint as live stock.

## Likely Question And Answer

**Could the older date have been selected intentionally?** Yes. That would make it a valid historical extract, but it still cannot be used as the current snapshot required by the Control Tower.

# 2. Critical - June Source Margin Has A Material Cost-Coverage Gap

| Evidence | Verified value |
| --- | --- |
| Exact POSIST report | `Gross/Net Margin Report` |
| Report range | `1 June 2026 to 30 June 2026` |
| Exact source row | CSV row `15` |
| `SKU Code / Item No` | `IGC0052` |
| `Net Sale Value` | `235.00` |
| `Purchase Rate` | `0.00` |
| `Purchase Value` | `0.00` |
| `Net Margin%` / `Gross Margin%` | `0` / `0` |
| Period-wide result | `2,843 of 5,995` non-zero-sales rows, or `47.4%`, have zero purchase value |

## Why This Claim Is Safe

The claim is not that every zero-cost line is erroneous. A genuine no-cost item is possible. The guaranteed issue is that a non-zero sale with no approved cost or explicit no-cost classification cannot support a source margin KPI. The concentration in June makes period-to-period margin comparison especially unsafe.

## What Would Go Wrong In Zoho

- Treating zero as actual cost would overstate margin.
- Treating the source margin percentage as valid would mix cost-covered and uncovered sales.
- June margin would not be comparable with May or July.

## Presentation Line

> In the June Gross/Net Margin export, 47.4% of non-zero sales lines had zero purchase value. We did not interpret zero as free inventory; source margin publication remains blocked until cost coverage or an approved no-cost classification is available.

## Likely Question And Answer

**Could some items genuinely have zero purchase cost?** Yes. That is why the control asks for an explicit no-cost classification. Without it, zero is ambiguous and cannot be used as a production cost fact.

# 3. Major - Opening Quantity Exists Without Opening Valuation

| Evidence | Verified value |
| --- | --- |
| Exact POSIST report | `Enterprise Opening Report - Opening Stock` |
| Report range | `22 April 2026 to 22 July 2026` |
| Exact source row | CSV row `2` |
| `Item Code` | `7742` |
| `Opening Qty` | `1` |
| `Unit Price` | `0` |
| Opening subtotal | `0` |
| Report-wide result | All `3` captured rows have zero unit price and subtotal |

## Why This Claim Is Safe

The quantity may be valid and the zero valuation may reflect configuration or missing historical cost. The guaranteed limitation is monetary: these rows can support a quantity bridge but cannot support opening stock value without an approved valuation basis.

## What Would Go Wrong In Zoho

- Opening inventory value would be understated.
- The value-based consumption bridge could be distorted.
- Working-capital and leakage values could inherit an artificial zero-cost opening balance.

## Presentation Line

> The Opening Stock report supplied quantities but zero unit price and subtotal for every captured row. We retained the quantity signal but excluded those rows from monetary KPIs until an approved opening valuation method is defined.

# Engineering Controls - Useful To Show, But Do Not Call Them Source Errors

## PO Identifier Standardization

- `Enterprise Entry Report - Stock Entry`, row `2`: PO number `PO-11`.
- `Enterprise Purchase Order Report`, row `69`: PO number `11`.
- Both can refer to the same business PO, but an exact text join fails.
- The standardization layer preserves the raw values and creates a canonical identifier before PO-to-receipt logic.

## Recipe UOM Conversion

- `Item Recipe Report`, row `3`: recipe unit `GRAM` for ingredient code `7900`.
- `Closing Stock Report`, row `151`: inventory unit `PKT (500 GM)` for the same ingredient.
- Both values can be valid. A direct unit-text join or quantity comparison is invalid until the 500-gram conversion is governed.

# Findings Not To Present As Confirmed Data Errors

- Overdue open POs: valid procurement exceptions; a revised delivery date may exist outside the report.
- Closed PO received after expected date: a valid service exception; close-date semantics need confirmation.
- Negative-margin sales: arithmetic can be valid for promotions, discounts, or loss leaders.
- Negative closing stock: operationally serious, but can arise from timing, backdated movements, UOM, or count adjustments.
- Repeated recipe or recipe-consumption rows: the export may omit effective-date or event keys, so equality is not proof of duplicate business events.
- Negative variance or consumption states: sign conventions require business approval before calling them wrong.

# Recommended Presentation Sequence

1. State that structural parsing passed.
2. Show the stale Closing Stock row and explain the current-state blocker.
3. Show the June missing-cost row and the 47.4% period-wide coverage result.
4. Show the opening-valuation row as a narrower major limitation.
5. Close with PO identifier and UOM standardization as examples of why the layered model is necessary.
"""


def sync_site(
    site_root: Path,
    contract_path: Path,
    model_path: Path,
    handbook_path: Path,
    issue_path: Path,
) -> None:
    control_target = site_root / "schema-pack" / "source" / "control_tower"
    model_target = site_root / "schema-pack" / "source" / "model"
    sql_target = model_target / "control_tower_v2_sql"
    docs_target = site_root / "docs"
    for path in (control_target, model_target, sql_target, docs_target):
        path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(contract_path, control_target / "control-tower-presentation.json")
    shutil.copy2(model_path, model_target / "control-tower-model.json")
    source_sql_names = {path.name for path in SQL_ROOT.glob("*.sql")}
    for stale in sql_target.glob("*.sql"):
        if stale.name not in source_sql_names:
            stale.unlink()
    for sql_path in SQL_ROOT.glob("*.sql"):
        shutil.copy2(sql_path, sql_target / sql_path.name)
    shutil.copy2(SQL_ROOT / "QUERY_TABLE_MANIFEST.csv", sql_target / "QUERY_TABLE_MANIFEST.csv")
    shutil.copy2(SQL_ROOT / "README.md", sql_target / "README.md")
    shutil.copy2(handbook_path, docs_target / handbook_path.name)
    shutil.copy2(issue_path, docs_target / issue_path.name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-root",
        type=Path,
        help="Optional ABNAH Schema Atlas root to receive the generated site snapshot.",
    )
    args = parser.parse_args()

    contract = build_presentation_contract()
    model = build_model_catalog()
    contract_path = DOCS_ROOT / "control_tower_presentation_contract.json"
    model_path = DOCS_ROOT / "control_tower_model_catalog.json"
    handbook_path = DOCS_ROOT / "CONTROL_TOWER_KPI_AND_CHART_LINEAGE_HANDBOOK.md"
    issue_path = DOCS_ROOT / "PRESENTATION_SAFE_ACTUAL_DATA_ISSUES.md"
    write_json(contract_path, contract)
    write_json(model_path, model)
    write_text(handbook_path, build_handbook(contract))
    write_text(issue_path, build_issue_brief())

    if args.site_root:
        sync_site(
            args.site_root.resolve(),
            contract_path,
            model_path,
            handbook_path,
            issue_path,
        )

    print(
        f"Generated {len(contract['stories'])} KPI/chart stories, "
        f"{len(model['tables'])} Query Table definitions, and 2 handbooks."
    )
    return 0


# Page 3 - Consumption Variance & Menu Profitability
STORIES.extend(
    [
        story(P3, "CT_P3_KPI_Net_Sales", "Net Sales", "kpi", "KPI widget", "25_fact_ct_menu_profitability.sql", "What net menu sales were realized in the selected scope?", ["net_sales"], 'sum("net_sales")', "Sum net sales", ["Data Column: net_sales", "Show Value As: Sum", "Group By: blank"], user_filters=P3_FILTERS, formatting=["INR currency"]),
        story(P3, "CT_P3_KPI_Quantity_Sold", "Quantity Sold", "kpi", "KPI widget", "25_fact_ct_menu_profitability.sql", "How many menu-item units were sold?", ["sold_qty"], 'sum("sold_qty")', "Sum sold quantity", ["Data Column: sold_qty", "Show Value As: Sum", "Group By: blank"], user_filters=P3_FILTERS, formatting=["Whole or decimal quantity as source requires"]),
        story(P3, "CT_P3_KPI_Theoretical_COGS", "Theoretical COGS", "kpi", "KPI widget", "25_fact_ct_menu_profitability.sql", "What should the sold menu mix have cost under the effective recipe and normalized ingredient cost?", ["sold_qty", "theoretical_cost_per_unit", "theoretical_cogs"], 'sum("theoretical_cogs")', "Sum theoretical COGS", ["Data Column: theoretical_cogs", "Show Value As: Sum", "Group By: blank"], user_filters=P3_FILTERS, formatting=["INR currency"]),
        story(P3, "CT_P3_KPI_Consumption_Leakage", "Consumption Leakage Value", "kpi", "KPI widget", "21_fact_ct_consumption_variance.sql", "What positive actual-over-theoretical consumption variance is valued as leakage?", ["leakage_value"], 'sum("leakage_value")', "Sum leakage value", ["Data Column: leakage_value", "Show Value As: Sum", "Group By: blank"], user_filters=P3_FILTERS, formatting=["INR currency"], caveats=["Use value, not a mixed-UOM all-item quantity."]),
        story(P3, "CT_P3_KPI_Menu_Gross_Margin", "Menu Gross Margin %", "kpi", "Saved Summary View", "25_fact_ct_menu_profitability.sql", "What share of net sales remains after theoretical menu COGS?", ["gross_margin_value", "net_sales"], 'Aggregate Formula "Menu Gross Margin %" in a saved Summary View.', "Ratio of summed gross margin value to summed net sales", ["Summary value: Menu Gross Margin %", "Grouping: none"], user_filters=P3_FILTERS, formatting=["Percentage; expected display near 82.02% in all-period synthetic truth"], caveats=["Never average gross_margin_percent.", "The Aggregate Formula is not selected from a direct KPI Widget Data Column list."]),
        story(P3, "CT_P3_Consumption_Bridge", "Consumption Bridge", "chart", "Combination", "20_fact_ct_actual_consumption.sql", "How do opening, receipts, transfers, returns, and closing stock reconcile to actual consumption?", ["source_period_code", "opening_qty", "purchase_qty", "transfer_in_qty", "bridge_transfer_out_qty", "bridge_return_qty", "bridge_closing_qty", "calculated_actual_consumption_qty"], "Physical bridge fields are already signed in Query 20.", "Sum each bridge component within one canonical UOM", ["X: source period", "Bars: opening, purchase, transfer in, bridge transfer out, bridge return, bridge closing", "Line: calculated actual consumption"], fixed_filters=["Canonical UOM user filter: select exactly one value for this quantity view"], user_filters=P3_FILTERS, tooltips=["Outlet", "Item", "Actual consumption value"]),
        story(P3, "CT_P3_Theoretical_Consumption_Detail", "Theoretical Consumption Detail", "table", "Tabular", "19_fact_ct_theoretical_consumption.sql", "What ingredient quantity and value should have been consumed?", ["outlet_code", "item_code", "theoretical_consumption_qty", "theoretical_consumption_value", "canonical_uom", "average_unit_cost"], "Sold menu quantity x normalized recipe ingredient quantity; value x normalized average cost.", "Direct detail rows", ["Columns: outlet, ingredient, theoretical quantity/value, UOM, average cost"], user_filters=P3_FILTERS, sort="Theoretical consumption value descending"),
        story(P3, "CT_P3_Actual_vs_Theoretical", "Actual vs Theoretical Consumption", "chart", "Grouped bar", "21_fact_ct_consumption_variance.sql", "For one UOM, where does actual ingredient consumption differ from theoretical?", ["item_code", "actual_consumption_qty", "theoretical_consumption_qty", "canonical_uom"], "Display both fact measures at the same joined grain.", "Sum quantities only within one canonical UOM", ["X: ingredient", "Y: actual quantity and theoretical quantity"], fixed_filters=["Exactly one canonical UOM"], user_filters=P3_FILTERS, sort="Absolute variance descending"),
        story(P3, "CT_P3_Consumption_Leakage_Rank", "Consumption Leakage Rank", "chart", "Horizontal bar", "21_fact_ct_consumption_variance.sql", "Which ingredients create the highest positive consumption leakage value?", ["item_code", "leakage_value", "consumption_variance_direction"], 'sum("leakage_value")', "Sum leakage value", ["Y: ingredient", "X: leakage value"], fixed_filters=["Filter shelf: consumption_variance_direction / Individual Values / Include OVER_CONSUMPTION"], user_filters=P3_FILTERS, sort="Leakage value descending", formatting=["INR currency"]),
        story(P3, "CT_P3_Low_Consumption_Check", "Low Consumption Check", "table", "Tabular", "21_fact_ct_consumption_variance.sql", "Where is theoretical consumption higher than calculated actual consumption?", ["outlet_code", "item_code", "actual_consumption_qty", "theoretical_consumption_qty", "low_consumption_qty", "canonical_uom", "consumption_variance_direction"], "low_consumption_qty is the positive under-consumption difference.", "Direct detail rows", ["Columns: outlet, ingredient, actual, theoretical, delta, UOM"], fixed_filters=["Filter shelf: consumption_variance_direction / Individual Values / Include UNDER_CONSUMPTION", "Canonical UOM user filter: select exactly one value for quantity comparison"], user_filters=P3_FILTERS, sort="Low consumption quantity descending", caveats=["Title and explanation must frame this as a data/process check, not a saving."]),
        story(P3, "CT_P3_Menu_BCG", "Menu BCG", "chart", "Bubble", "32_sum_ct_menu_profitability.sql", "Which menu items are high/low volume and high/low margin under the demo thresholds?", ["menu_item_code", "sold_qty", "gross_margin_percent", "net_sales", "bcg_quadrant"], "Quadrant is preclassified from sold quantity and gross margin percent.", "Direct summary at one period + one outlet + menu item", ["X: sold quantity", "Y: gross margin %", "Size: net sales", "Text: menu item", "Color: BCG quadrant"], fixed_filters=["Exactly one source period", "Exactly one outlet or keep outlet visible"], user_filters=P3_FILTERS, caveats=["Thresholds are synthetic demonstration rules."]),
        story(P3, "CT_P3_Menu_COGS_Detail", "Menu COGS Detail", "table", "Tabular", "25_fact_ct_menu_profitability.sql", "How do sold quantity, recipe cost, COGS, sales, and margin reconcile for each menu item?", ["menu_item_code", "sold_qty", "theoretical_cost_per_unit", "theoretical_cogs", "net_sales", "gross_margin_value", "gross_margin_percent"], "gross margin value = net sales - theoretical COGS", "Direct menu profitability rows", ["Columns: menu item, sold quantity, theoretical unit cost, COGS, net sales, margin"], user_filters=P3_FILTERS, sort="Net sales descending"),
        story(P3, "CT_P3_Menu_Margin_Rank", "Menu Margin Rank", "chart", "Horizontal bar", "32_sum_ct_menu_profitability.sql", "Which menu items contribute the most gross margin value?", ["menu_item_code", "gross_margin_value", "theoretical_cogs", "gross_margin_percent"], 'sum("gross_margin_value")', "Sum margin value within selected period/outlet", ["Y: menu item", "X: gross margin value"], fixed_filters=["One source period for like-for-like ranking"], user_filters=P3_FILTERS, sort="Gross margin value descending", tooltips=["Theoretical COGS", "Gross margin %"], formatting=["INR currency"]),
        story(P3, "CT_P3_Sales_Trend", "Sales Trend", "chart", "Line", "18_fact_ct_sales.sql", "How do net sales and menu quantity move by sales date?", ["sales_date", "net_sales", "sold_qty"], 'sum("net_sales") and sum("sold_qty")', "Sum additive sales measures by date", ["X: sales date", "Y: net sales and sold quantity"], user_filters=P3_FILTERS, tooltips=["Outlet", "Menu item", "Category"]),
        story(P3, "CT_P3_Category_Contribution", "Category Contribution", "chart", "Stacked bar or ring", "25_fact_ct_menu_profitability.sql", "What share of net sales comes from each menu category?", ["category_name", "net_sales"], 'sum("net_sales") shown as percent of report total', "Sum net sales; Show Values As > % of Total", ["Category: category name", "Measure: net sales"], user_filters=P3_FILTERS, sort="Net sales descending", formatting=["Percent of total"], caveats=["Do not create a separate table aggregate formula for percent-of-total."]),
        story(P3, "CT_P3_Top_Slow_Menu_Ranking", "Top / Slow Menu Ranking", "chart", "Horizontal bar", "32_sum_ct_menu_profitability.sql", "Which menu items rank highest or lowest on the selected commercial measure?", ["menu_item_code", "sold_qty", "net_sales", "theoretical_cogs", "gross_margin_value"], "Use one selected ranking measure; all fields are already at menu summary grain.", "Sum selected additive measure", ["Y: menu item", "X: selected sold quantity, net sales, COGS, or margin"], fixed_filters=["One source period for like-for-like ranking"], user_filters=P3_FILTERS, sort="Selected metric ascending for slow or descending for top"),
        story(P3, "CT_P3_Outlet_Item_Heatmap", "Outlet Item Heatmap", "chart", "Heat map", "25_fact_ct_menu_profitability.sql", "How does menu/category performance vary across outlets?", ["outlet_code", "menu_item_code", "category_name", "net_sales", "sold_qty"], 'sum("net_sales") or sum("sold_qty")', "Sum selected additive measure", ["X: menu item or category", "Y: outlet", "Color: net sales or sold quantity"], user_filters=P3_FILTERS, tooltips=["Gross margin value", "Theoretical COGS"]),
    ]
)


# Page 4 - SCM Descriptive Explorer & Data Quality
STORIES.extend(
    [
        story(P4, "CT_P4_KPI_Closing_Stock", "Closing Stock Value", "kpi", "KPI widget", "33_sum_ct_scm_monthly.sql", "What is the selected checkpoint's closing stock value?", ["closing_stock_value"], 'sum("closing_stock_value")', "Sum closing stock value", ["Data Column: closing_stock_value", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS, formatting=["INR currency"], caveats=["Require one source period."]),
        story(P4, "CT_P4_KPI_Open_PO", "Open PO Value", "kpi", "KPI widget", "33_sum_ct_scm_monthly.sql", "What open PO value exists in the selected checkpoint?", ["open_po_value"], 'sum("open_po_value")', "Sum open PO value", ["Data Column: open_po_value", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS, formatting=["INR currency"], caveats=["Require one source period for current-state display."]),
        story(P4, "CT_P4_KPI_Net_Sales", "Net Sales", "kpi", "KPI widget", "33_sum_ct_scm_monthly.sql", "What net sales are summarized for the selected period and outlet?", ["net_sales"], 'sum("net_sales")', "Sum net sales", ["Data Column: net_sales", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS, formatting=["INR currency"]),
        story(P4, "CT_P4_KPI_Actual_Consumption", "Actual Consumption Value", "kpi", "KPI widget", "33_sum_ct_scm_monthly.sql", "What calculated actual-consumption value is summarized for the selected scope?", ["actual_consumption_value"], 'sum("actual_consumption_value")', "Sum actual consumption value", ["Data Column: actual_consumption_value", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS, formatting=["INR currency"]),
        story(P4, "CT_P4_KPI_Consumption_Variance", "Signed Consumption Variance Value", "kpi", "KPI widget", "21_fact_ct_consumption_variance.sql", "What is the signed actual-versus-theoretical consumption variance value for the checkpoint?", ["signed_consumption_variance_value"], 'sum("signed_consumption_variance_value")', "Sum the physical signed variance value", ["Data Column: signed_consumption_variance_value", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS, formatting=["INR currency; allow negative values"], caveats=["Keep positive leakage as a separate control."]),
        story(P4, "CT_P4_KPI_Quantity_Sold", "Quantity Sold", "kpi", "KPI widget", "18_fact_ct_sales.sql", "How many menu-item units were sold?", ["sold_qty"], 'sum("sold_qty")', "Sum sold quantity", ["Data Column: sold_qty", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS),
        story(P4, "CT_P4_KPI_Active_Menu_Items", "Active Menu Items", "kpi", "KPI widget", "18_fact_ct_sales.sql", "How many distinct menu items had sales in the selected scope?", ["item_code"], 'distinctcount("item_code")', "Distinct menu-item count", ["Data Column: item_code", "Show Value As: Count Distinct", "Group By: blank"], user_filters=P4_FILTERS, formatting=["Whole number"]),
        story(P4, "CT_P4_KPI_Open_PO_Lines", "Open PO Line Count", "kpi", "KPI widget", "22_fact_ct_purchase_order.sql", "How many PO item lines remain open?", ["is_open_po"], 'sum("is_open_po")', "Sum the physical open-line flag", ["Data Column: is_open_po", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS, formatting=["Whole number"], caveats=["This is not a distinct PO count. No fixed filter is required because closed lines contribute zero."]),
        story(P4, "CT_P4_KPI_GRN_Value", "GRN Value", "kpi", "KPI widget", "23_fact_ct_purchase_receipt.sql", "What accepted receipt total was recorded in the selected scope?", ["receipt_total"], 'sum("receipt_total")', "Sum receipt total", ["Data Column: receipt_total", "Show Value As: Sum", "Group By: blank"], user_filters=P4_FILTERS, formatting=["INR currency"]),
        story(P4, "CT_P4_KPI_Active_Vendors", "Active Vendors", "kpi", "KPI widget", "22_fact_ct_purchase_order.sql", "How many distinct vendors appear on purchase orders in the selected scope?", ["vendor_name"], 'distinctcount("vendor_name")', "Distinct vendor count", ["Data Column: vendor_name", "Show Value As: Count Distinct", "Group By: blank"], user_filters=P4_FILTERS, formatting=["Whole number"]),
        story(P4, "CT_P4_SCM_Monthly_Trend", "SCM Monthly Trend", "chart", "Combination", "33_sum_ct_scm_monthly.sql", "How do stock value, open PO value, net sales, and actual consumption move together?", ["source_period_code", "closing_stock_value", "open_po_value", "net_sales", "actual_consumption_value"], "All four values are pre-aggregated to period + outlet before the summary join.", "Sum each additive value measure", ["X: source period", "Bars: closing stock and open PO", "Lines: net sales and actual consumption"], user_filters=P4_FILTERS, tooltips=["Outlet"]),
        story(P4, "CT_P4_Consumption_Variance_Trend", "Consumption Variance Trend", "chart", "Bar / line", "21_fact_ct_consumption_variance.sql", "How do signed consumption variance and positive leakage change by period?", ["source_period_code", "actual_consumption_value", "theoretical_consumption_value", "leakage_value"], "Signed variance = actual value - theoretical value; leakage is positive-only.", "Sum both explicitly labelled value measures", ["X: source period", "Y: signed variance value and leakage value"], user_filters=P4_FILTERS, formatting=["INR currency"]),
        story(P4, "CT_P4_Descriptive_Explorer", "SCM Descriptive Explorer", "table", "Pivot or tabular", "33_sum_ct_scm_monthly.sql", "What governed SCM values can be drilled and exported by period and outlet?", ["source_period_code", "outlet_code", "closing_stock_value", "open_po_value", "net_sales", "actual_consumption_value"], "Direct monthly summary values with drill reports for lower grain.", "Sum at selected period/outlet scope", ["Rows: period and outlet", "Measures: stock, open PO, sales, actual consumption"], user_filters=P4_FILTERS, formatting=["Enable export and underlying data"]),
        story(P4, "CT_P4_Sales_Explorer", "Sales Explorer", "table", "Tabular", "18_fact_ct_sales.sql", "Which date/outlet/menu rows explain the descriptive sales totals?", ["sales_date", "outlet_code", "item_code", "category_name", "sold_qty", "net_sales", "realized_unit_price"], "Direct bill-item fact detail.", "One row per validated sales item line", ["Columns: date, outlet, menu item/category, sold quantity, net sales, realized unit price"], user_filters=P4_FILTERS, sort="Sales date descending"),
        story(P4, "CT_P4_Item_Explorer", "Item Explorer", "table", "Tabular", "27_fact_ct_inventory_risk.sql", "Which item checkpoints explain stock, cost, forecast, PO, and risk totals?", ["outlet_code", "item_code", "category_name", "current_stock_qty", "average_unit_cost", "forecast_required_qty", "valid_open_po_qty", "risk_severity"], "Direct inventory-risk detail.", "One row per item checkpoint", ["Columns: outlet, item, category, stock, cost, forecast, PO, severity"], user_filters=P4_FILTERS, sort="Outlet, risk rank descending, item"),
        story(P4, "CT_P4_PO_Explorer", "PO Explorer", "table", "Tabular", "24_fact_ct_po_receipt_line.sql", "How do ordered, received, remaining, expected, actual, and status fields reconcile by PO line?", ["po_number", "vendor_name", "item_code", "ordered_qty", "received_qty", "remaining_qty", "expected_delivery_date", "actual_receipt_date", "po_status"], "PO lines left joined to aggregated receipt lines on canonical business keys.", "One row per PO item line", ["Columns: PO, vendor, item, ordered, received, remaining, expected, actual, status"], user_filters=P4_FILTERS, sort="PO number, item"),
        story(P4, "CT_P4_GRN_Explorer", "GRN Explorer", "table", "Tabular", "23_fact_ct_purchase_receipt.sql", "Which receipt lines explain GRN quantity and value?", ["receipt_date", "grn_number", "po_number", "vendor_name", "item_code", "received_qty", "receipt_subtotal", "receipt_tax", "receipt_total", "return_source_status"], "Direct normalized stock-entry receipt rows.", "One row per receipt item line", ["Columns: receipt date, GRN, PO, vendor, item, quantity, subtotal, tax, total, return-source status"], user_filters=P4_FILTERS, sort="Receipt date descending"),
        story(P4, "CT_P4_Vendor_Explorer", "Vendor Explorer", "table", "Tabular", "30_sum_ct_vendor_scorecard.sql", "Which vendor-level values and formula demonstrations explain procurement performance?", ["vendor_name", "monthly_purchase_value", "received_value", "open_po_value", "fill_rate_percent", "otif_percent", "average_lead_time_deviation_days", "delayed_line_count"], "Direct vendor scorecard summary.", "One row per period + outlet + vendor", ["Columns: vendor, ordered/received value, open liability, fill, eligible OTIF, lead deviation, delayed lines"], user_filters=P4_FILTERS, sort="Open PO value descending", caveats=["OTIF and lead deviation remain formula demonstrations."]),
        story(P4, "CT_P4_Expiry_Explorer_Demo", "Expiry Explorer - Demo", "table", "Tabular", "38_fact_ct_expiry_risk.sql", "Which scenario inputs and outputs explain the synthetic expiry exposure?", ["outlet_code", "item_code", "shelf_life_days_assumption", "estimated_fifo_tranche_qty", "estimated_expiry_date", "expiry_qty_at_risk", "expiry_risk_value", "production_use_status"], "Direct synthetic scenario rows.", "One row per synthetic batch allocation", ["Columns: outlet, item, scenario inputs, estimated date, quantity/value, production-use label"], user_filters=P4_FILTERS, formatting=["Permanent synthetic-source qualifier"]),
    ]
)


DQ_TYPES = [
    ("NEGATIVE_STOCK", "Negative Stock Count", "Closing quantity below zero"),
    ("ZERO_STOCK_WITH_DEMAND", "Zero Stock With Demand Count", "Zero closing stock while forecast demand is positive"),
    ("SOLD_ITEM_MISSING_RECIPE", "Sold Items Missing Recipe Count", "Sold menu item has no effective recipe"),
    ("OPERATIONAL_ITEM_MISSING_MASTER", "Operational Items Missing Master Count", "Operational item does not resolve to the canonical item reference"),
    ("UOM_MISMATCH_WITHOUT_CONVERSION", "UOM Mismatch Without Conversion Count", "Observed UOMs cannot be governed by an approved conversion"),
    ("OPEN_PO_MISSING_EXPECTED_DELIVERY", "Open PO Missing Expected Delivery Count", "Open PO lacks an expected delivery date"),
]
for exception_type, name, question in DQ_TYPES:
    STORIES.append(
        story(
            P4,
            f"CT_P4_DQ_{exception_type}",
            name,
            "kpi",
            "KPI widget",
            "34_fact_ct_data_quality_exception.sql",
            question,
            ["exception_type", "exception_count"],
            'sum("exception_count")',
            "Sum exception count",
            ["Data Column: exception_count", "Show Value As: Sum", "Group By: blank"],
            fixed_filters=[
                f"Filter shelf: exception_type / Individual Values / Include {exception_type}"
            ],
            user_filters=P4_FILTERS,
            formatting=["Whole number"],
            caveats=[
                "Use the Page 4 Exception Type user filter for the shared detail table; a single-number widget has no category dimension to pass."
            ],
        )
    )

STORIES.append(
    story(
        P4,
        "CT_P4_Data_Quality_Detail",
        "Data Quality Detail",
        "table",
        "Tabular",
        "34_fact_ct_data_quality_exception.sql",
        "Which exact governed exception records sit behind each quality tile?",
        [
            "exception_type",
            "source_period_code",
            "outlet_code",
            "record_key",
            "item_code",
            "reference_number",
            "definition",
            "exception_count",
        ],
        "Direct generated exception rows.",
        "One row per generated exception record",
        ["Columns: exception type, period, outlet, record key, item, PO/reference, definition"],
        user_filters=P4_FILTERS,
        sort="Exception type, period, outlet, record key",
        formatting=["Enable underlying data and export"],
    )
)


# Page 2 - Procurement, Vendor & Capital Control
STORIES.extend(
    [
        story(P2, "CT_P2_KPI_Monthly_Purchase", "Ordered Gross Value", "kpi", "KPI widget", "29_sum_ct_procurement_funnel.sql", "What was the selected-period ordered gross commitment?", ["ordered_value"], 'sum("ordered_value")', "Sum ordered value", ["Data Column: ordered_value", "Show Value As: Sum", "Group By: blank"], user_filters=P2_FILTERS, formatting=["INR currency", "Label Ordered Gross Value until basis is approved"]),
        story(P2, "CT_P2_KPI_Closing_Inventory", "Closing Inventory Value", "kpi", "KPI widget", "33_sum_ct_scm_monthly.sql", "What is the selected checkpoint's closing inventory value?", ["closing_stock_value"], 'sum("closing_stock_value")', "Sum closing stock value", ["Data Column: closing_stock_value", "Show Value As: Sum", "Group By: blank"], user_filters=P2_FILTERS, formatting=["INR currency"], caveats=["Require exactly one source period."]),
        story(P2, "CT_P2_KPI_Open_PO_Liability", "Open PO Liability", "kpi", "KPI widget", "29_sum_ct_procurement_funnel.sql", "How much value remains committed on open PO lines?", ["pending_value"], 'sum("pending_value")', "Sum pending value", ["Data Column: pending_value", "Show Value As: Sum", "Group By: blank"], user_filters=P2_FILTERS, formatting=["INR currency"]),
        story(P2, "CT_P2_KPI_Working_Capital", "Working Capital Locked", "kpi", "KPI widget", "33_sum_ct_scm_monthly.sql", "How much capital is represented by closing inventory plus open PO liability?", ["working_capital_value"], 'sum("working_capital_value")', "Sum the physical working-capital field", ["Data Column: working_capital_value", "Show Value As: Sum", "Group By: blank"], user_filters=P2_FILTERS, formatting=["INR currency"], caveats=["Show closing inventory and open PO liability separately beside this combined KPI.", "Require one source period."]),
        story(P2, "CT_P2_KPI_Open_PO_Count", "Open PO Count", "kpi", "KPI widget", "29_sum_ct_procurement_funnel.sql", "How many distinct purchase orders remain open?", ["open_po_count"], 'sum("open_po_count")', "Sum vendor-level distinct PO counts within the selected outlet scope", ["Data Column: open_po_count", "Show Value As: Sum", "Group By: blank"], user_filters=P2_FILTERS, formatting=["Whole number"]),
        story(P2, "CT_P2_KPI_Fill_Rate", "PO Fill Rate", "kpi", "Saved Summary View", "24_fact_ct_po_receipt_line.sql", "What proportion of ordered quantity was linked to accepted receipt quantity?", ["ordered_qty", "received_qty"], 'Aggregate Formula "PO Fill Rate %" in a saved Summary View.', "Ratio of summed quantities", ["Summary value: PO Fill Rate %", "Grouping: none"], user_filters=P2_FILTERS, formatting=["Percentage; expected display near 83.25% in all-period synthetic truth"], caveats=["The Aggregate Formula is not selected from a direct KPI Widget Data Column list."]),
        story(P2, "CT_P2_KPI_OTIF", "Vendor OTIF - Formula Demo", "kpi", "Saved Summary View", "24_fact_ct_po_receipt_line.sql", "What share of eligible closed PO lines met both quantity and date conditions in the demonstration?", ["eligible_closed_line_flag", "otif_success_flag"], 'Aggregate Formula "Vendor OTIF %" in a saved Summary View.', "Ratio of summed flags", ["Summary value: Vendor OTIF %", "Grouping: none"], user_filters=P2_FILTERS, formatting=["Percentage", "Visible Formula demo label"], caveats=["Production is blocked by sparse actual PO-to-GRN linkage.", "The Aggregate Formula is not selected from a direct KPI Widget Data Column list."]),
        story(P2, "CT_P2_Procurement_Funnel", "Procurement Funnel", "chart", "Funnel or grouped horizontal bar", "29_sum_ct_procurement_funnel.sql", "How does ordered value move through processed, pending, and delayed stages?", ["ordered_value", "processed_value", "pending_value", "delayed_value", "po_count", "open_po_count"], "Four direct stage measures from the procurement summary.", "Sum each value measure", ["Stages: ordered, processed, pending, delayed"], user_filters=P2_FILTERS, tooltips=["PO count", "Open PO count"], caveats=["Use a grouped horizontal bar if Zoho cannot use measure names as funnel stages."]),
        story(P2, "CT_P2_PO_Status_Distribution", "PO Status Distribution", "chart", "Stacked bar", "22_fact_ct_purchase_order.sql", "How are purchase orders distributed by normalized status and liability?", ["po_status", "po_number", "open_po_value"], 'distinctcount("po_number") and sum("open_po_value")', "Distinct PO count plus sum open liability", ["X: PO status", "Y: distinct PO count and open liability"], user_filters=P2_FILTERS, tooltips=["Ordered value", "Remaining quantity"]),
        story(P2, "CT_P2_Pending_By_Vendor", "Pending Value By Vendor", "chart", "Horizontal bar", "29_sum_ct_procurement_funnel.sql", "Which vendors hold the most open PO liability?", ["vendor_name", "pending_value"], 'sum("pending_value")', "Sum pending value", ["Y: vendor", "X: pending value"], fixed_filters=["Open PO summary only"], user_filters=P2_FILTERS, sort="Pending value descending", formatting=["INR currency"]),
        story(P2, "CT_P2_Pending_Ingredient_Risk", "Pending Ingredient Risk", "table", "Tabular", "36_fact_ct_risky_po.sql", "Which pending PO ingredients are already tied to operational stockout risk?", ["po_number", "vendor_name", "item_code", "remaining_qty", "open_po_value", "expected_delivery_date", "risk_severity"], "Direct risky-PO fact rows.", "One row per open risky PO item line", ["Columns: PO, vendor, ingredient, remaining quantity/value, expected date, severity"], user_filters=P2_FILTERS, sort="risk_severity_rank descending, open_po_value descending"),
        story(P2, "CT_P2_Expected_Delivery_Breach", "Expected Delivery Breach", "table", "Tabular", "22_fact_ct_purchase_order.sql", "Which open PO lines have passed their expected delivery date in the model?", ["po_number", "vendor_name", "item_code", "expected_delivery_date", "remaining_qty", "open_po_value", "delayed_po_flag"], "Select the physical delayed flag through the report Filter shelf.", "Direct detail rows", ["Columns: PO, vendor, item, expected date, remaining quantity/value"], fixed_filters=["Filter shelf: delayed_po_flag / Individual Values / Include 1"], user_filters=P2_FILTERS, sort="Expected delivery ascending", caveats=["Treat as an action queue; a revised date may exist outside the captured report."]),
        story(P2, "CT_P2_Vendor_Performance_Matrix", "Vendor Performance Matrix", "chart", "Bubble", "24_fact_ct_po_receipt_line.sql", "Which vendors combine low OTIF, lead-time deviation, and high open exposure?", ["vendor_name", "eligible_closed_line_flag", "otif_success_flag", "eligible_lead_time_deviation_days", "open_po_value"], "Use Vendor OTIF % Aggregate Formula and physical eligible lead-time deviation.", "Group by vendor over Query 24", ["X: Vendor OTIF %", "Y: average eligible_lead_time_deviation_days", "Size: sum open_po_value", "Text: vendor"], user_filters=P2_FILTERS, tooltips=["PO Fill Rate %", "Open PO value", "Delayed line count"], caveats=["Formula demonstration until actual PO-to-GRN linkage improves."]),
        story(P2, "CT_P2_Vendor_Scorecard", "Vendor Scorecard", "table", "Summary or pivot", "24_fact_ct_po_receipt_line.sql", "What purchase, exposure, fill, OTIF, lead, and delay profile does each vendor have?", ["vendor_name", "gross_order_value", "open_po_value", "ordered_qty", "received_qty", "eligible_closed_line_flag", "otif_success_flag", "eligible_lead_time_deviation_days", "delayed_po_flag"], "Use PO Fill Rate % and Vendor OTIF % Aggregate Formulas over Query 24.", "Group by vendor", ["Columns: vendor, purchase, open liability, OTIF, fill, eligible lead deviation, delayed lines"], user_filters=P2_FILTERS, sort="Open PO value descending", caveats=["Do not average precomputed Query 30 percentages across outlets."]),
        story(P2, "CT_P2_Ingredient_Price_Trend", "Ingredient Price Trend", "chart", "Line", "23_fact_ct_purchase_receipt.sql", "How has weighted received unit price changed by ingredient over time?", ["source_period_code", "item_code", "received_qty", "receipt_subtotal", "vendor_name"], 'Aggregate Formula "Weighted Unit Price".', "Weighted unit price", ["X: source period", "Y: Weighted Unit Price", "Color: item"], user_filters=P2_FILTERS, tooltips=["Vendor", "Received quantity", "Receipt subtotal"], formatting=["INR per selected UOM"]),
        story(P2, "CT_P2_Vendor_Price_Comparison", "Vendor Price Comparison", "chart", "Grouped bar", "23_fact_ct_purchase_receipt.sql", "For one ingredient and UOM, which vendor supplied at what weighted price?", ["vendor_name", "item_code", "canonical_uom", "received_qty", "receipt_subtotal"], 'Aggregate Formula "Weighted Unit Price".', "Weighted unit price", ["X: vendor", "Y: Weighted Unit Price"], fixed_filters=["Item user filter: select exactly one value", "Canonical UOM user filter: select exactly one value"], user_filters=P2_FILTERS, sort="Weighted unit price ascending", formatting=["INR per selected UOM"]),
        story(P2, "CT_P2_Top_Price_Movement", "Top Price Movement", "chart", "Divergent or horizontal bar", "31_sum_ct_price_movement.sql", "Which item/vendor prices changed most from the prior synthetic month?", ["price_comparison_key", "unit_price_change_percent", "absolute_unit_price_change_percent", "price_movement_direction"], "Signed physical change is displayed; absolute physical change is used only for sorting.", "Direct period-item-vendor-UOM result", ["Y: price_comparison_key", "X: unit_price_change_percent", "Color: price_movement_direction"], user_filters=P2_FILTERS, sort="absolute_unit_price_change_percent descending; Top 10", tooltips=["Vendor", "Previous weighted price", "Current weighted price"], formatting=["Signed percentage"]),
        story(P2, "CT_P2_Inventory_Value", "Inventory Value", "chart", "Stacked bar", "05_std_ct_inventory_snapshot.sql", "Where is closing inventory value concentrated by outlet and category?", ["outlet_code", "category_name", "closing_value"], 'sum("closing_value")', "Sum closing value", ["X: outlet", "Y: closing value", "Color: category"], fixed_filters=["Exactly one source period"], user_filters=P2_FILTERS, formatting=["INR currency"]),
        story(P2, "CT_P2_High_Value_Slow_Stock", "High Value / Slow Stock", "table", "Tabular", "27_fact_ct_inventory_risk.sql", "Which items combine high closing value with high days cover or weak demand?", ["item_code", "closing_value", "days_cover", "forecast_required_qty", "risk_severity"], "Direct inventory-risk rows; ranking uses closing value and days cover.", "One row per item checkpoint", ["Columns: item, closing value, days cover, forecast demand, severity"], fixed_filters=["Exactly one source period"], user_filters=P2_FILTERS, sort="Closing value descending, days cover descending"),
        story(P2, "CT_P2_Observed_Wastage", "Observed Wastage", "chart", "Column", "35_sum_ct_financial_leakage.sql", "How much source-observed wastage value occurred by period?", ["source_period_code", "leakage_value"], 'sum("leakage_value")', "Sum observed wastage value", ["X: source period", "Y: observed wastage value"], user_filters=P2_FILTERS, formatting=["INR currency"], caveats=["This is observed wastage only, not returns plus expiry plus wastage."]),
        story(P2, "CT_P2_Expiry_Exposure_Demo", "Expiry Exposure - Demo", "chart", "Column", "38_fact_ct_expiry_risk.sql", "How does the synthetic expiry-risk value vary by period?", ["source_period_code", "expiry_risk_value", "production_use_status"], 'sum("expiry_risk_value")', "Sum expiry risk value", ["X: source period", "Y: expiry risk value"], user_filters=P2_FILTERS, formatting=["INR currency", "Subtitle: Synthetic estimate - no POSIST batch/expiry source"]),
    ]
)


if __name__ == "__main__":
    raise SystemExit(main())
