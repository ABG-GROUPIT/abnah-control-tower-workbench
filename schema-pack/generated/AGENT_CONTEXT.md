# ABNAH Data Discovery Atlas Agent Context

Generated: `2026-07-23T23:42:02+00:00`
Schema contract: `1.1.0`

## Start Here

1. Read `manifest.json` and `generated/quality_report.json`.
2. Query `generated/atlas.json` by stable node IDs; do not infer relationships from labels alone.
3. Treat `candidate_not_uat_verified` edges as hypotheses until ABNAH UAT samples confirm them.
4. Use `source/reference_chunks/` for report-level OCR/header evidence.
5. Keep Inventory & Consumption and Vendor & Procurement as phase-1 priorities.

## Current Snapshot

- Reports: `318`
- Reports with fields: `58`
- Unique normalized fields: `371`
- API endpoints: `34`
- Model objects: `67`
- Core phase-1 reports: `43`
- Recorded validation tests: `0`
- Selected relational mappings: `0`

## Non-Negotiable Evidence Rule

Never present semantic API candidates as exact report coverage. Promote an edge to verified only after endpoint payload, grain, filters, calculations and ABNAH UAT availability are checked.
Keep factual discovery separate from mapping decisions. Record alternatives, decisions and tests in the curation registries instead of rewriting source discovery records.

## Core Reports

- `report:p4_stock_admin:01_enterprise_reports:01_enterprise_entry`: Enterprise Entry
- `report:p4_stock_admin:01_enterprise_reports:02_erp_vendor_price`: ERP Vendor Price
- `report:p4_stock_admin:01_enterprise_reports:03_enterprise_stock_return`: Enterprise Stock Return
- `report:p4_stock_admin:01_enterprise_reports:04_enterprise_consumption`: Enterprise Consumption
- `report:p4_stock_admin:01_enterprise_reports:05_enterprise_stock_re_order`: Enterprise Stock Re-Order
- `report:p4_stock_admin:01_enterprise_reports:06_enterprise_purchase_order`: Enterprise Purchase Order
- `report:p4_stock_admin:01_enterprise_reports:07_enterprise_consolidated_indent`: Enterprise Consolidated Indent
- `report:p4_stock_admin:01_enterprise_reports:08_enterprise_variance`: Enterprise Variance
- `report:p4_stock_admin:01_enterprise_reports:10_enterprise_bill_passing`: Enterprise Bill Passing
- `report:p4_stock_admin:01_enterprise_reports:12_enterprise_wastage_report`: Enterprise Wastage Report
- `report:p4_stock_admin:01_enterprise_reports:13_enterprise_purchase_summary_report`: Enterprise Purchase Summary Report
- `report:p4_stock_admin:01_enterprise_reports:14_enterprise_internal_indent_report`: Enterprise Internal Indent Report
- `report:p4_stock_admin:01_enterprise_reports:15_enterprise_food_cost_report`: Enterprise Food Cost Report
- `report:p4_stock_admin:02_transactional_reports:01_entry_report`: Entry Report
- `report:p4_stock_admin:02_transactional_reports:04_stock_return`: Stock Return
- `report:p4_stock_admin:02_transactional_reports:05_purchase_detail`: Purchase Detail
- `report:p4_stock_admin:02_transactional_reports:06_purchase_detail_consolidated`: Purchase Detail Consolidated
- `report:p4_stock_admin:02_transactional_reports:09_bill_passing_report`: Bill Passing Report
- `report:p4_stock_admin:02_transactional_reports:10_stock_in_stock_out_report`: Stock In Stock Out Report
- `report:p4_stock_admin:03_po_so_reports:01_purchase_order`: Purchase Order
- `report:p4_stock_admin:03_po_so_reports:02_standing_purchase_order`: Standing Purchase Order
- `report:p4_stock_admin:03_po_so_reports:05_erp_vendor_invoice`: ERP Vendor Invoice
- `report:p4_stock_admin:04_indent_reports:01_indent_report`: Indent Report
- `report:p4_stock_admin:04_indent_reports:02_consolidated_indent`: Consolidated Indent
- `report:p4_stock_admin:04_indent_reports:03_consolidated_indent_items`: Consolidated Indent Items
- `report:p4_stock_admin:04_indent_reports:04_issue_report`: Issue Report
- `report:p4_stock_admin:04_indent_reports:05_consolidated_indent_report_outlet`: Consolidated Indent Report Outlet Wise
- `report:p4_stock_admin:04_indent_reports:06_suspense_report`: Suspense Report
- `report:p4_stock_admin:04_indent_reports:07_bulk_return_report`: Bulk Return Report
- `report:p4_stock_admin:05_aggregation_reports:02_consumption_report`: Consumption Report
- `report:p4_stock_admin:05_aggregation_reports:03_variance_report`: Variance Report
- `report:p4_stock_admin:05_aggregation_reports:05_movement_report`: Movement Report
- `report:p4_stock_admin:05_aggregation_reports:07_recipe_consumption_report`: Recipe Consumption Report
- `report:p4_stock_admin:06_analytical_reports:02_food_cost_report`: Food Cost Report
- `report:p4_stock_admin:06_analytical_reports:03_re_order_level`: Re-Order Level
- `report:p4_stock_admin:06_analytical_reports:04_closing_stock_report`: Closing Stock Report
- `report:p4_stock_admin:06_analytical_reports:07_purchase_summary`: Purchase Summary
- `report:p4_stock_admin:07_other_reports:02_nc_head_consumption_cost`: NC Head Consumption Cost
- `report:p4_stock_admin:07_other_reports:03_expiry_report`: Expiry Report
- `report:p4_stock_admin:07_other_reports:06_vendor_pricing_report`: Vendor Pricing Report
- `report:p4_stock_admin:07_other_reports:07_late_delivery_report`: Late Delivery Report
- `report:p4_stock_admin:07_other_reports:13_vendor_last_5_purchase_price`: Vendor Last 5 Purchase Price
- `report:p4_stock_admin:09_bill_passing:01_bill_passing`: Bill Passing
