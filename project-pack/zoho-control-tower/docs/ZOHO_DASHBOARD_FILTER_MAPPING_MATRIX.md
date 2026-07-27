# Zoho Dashboard Filter Mapping Matrix

## Product Boundary

Zoho dashboards are the governed build and validation surfaces. The GitHub
Pages control tower does not embed Zoho dashboard UI or depend on shared report
URLs. Supabase verifies Zoho access, exports allowlisted Query Table rows, and
the custom frontend applies the same field-level filter contract.

A dashboard user filter affects a KPI or report only after that object has been
mapped to a compatible physical field. A report-specific filter affects only
that report. A fixed report filter is part of the business definition and is
not user-toggleable.

## Page 1 - Risk Action Center

Create these dashboard user filters:

1. Date Range
2. Outlet
3. Region
4. Ingredient Category
5. Action Owner

### Date mapping

| Query | Date field |
| --- | --- |
| `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `28_fact_ct_menu_impact.sql` | `snapshot_date` |
| `38_fact_ct_expiry_risk.sql` | `as_of_date` |
| `36_fact_ct_risky_po.sql` | `as_of_date` |

### Dimension mapping

| Query | Outlet | Region | Category | Owner |
| --- | --- | --- | --- | --- |
| Query 27 | `outlet_code` | Query 37 lookup `region` | `category_name` | `action_owner` |
| Query 28 | `outlet_code` | Query 37 lookup `region` | ingredient lookup `category_name` | leave unmapped |
| Query 38 | `outlet_code` | Query 37 lookup `region` | `category_name` | `action_owner` |
| Query 36 | `outlet_code` | Query 37 lookup `region` | `category_name` | leave unmapped |

Fixed report conditions:

| Object | Field | Individual Values to include |
| --- | --- | --- |
| Stockout KPIs, map, queue and detail | `risk_type` | `STOCKOUT` |

Query 28 already contains only menu-impact risk rows. Query 36 already contains
open risky PO lines. Query 38 remains explicitly labelled as a synthetic expiry
estimate.

## Page 2 - Procurement, Vendor & Capital Control

Create these dashboard user filters in this order:

1. Date Range
2. Region
3. Outlet
4. Ingredient Category
5. Vendor
6. Raw Material
7. PO Status

Do not add `As-of Source Period` to Page 2. Do not place the Query 23
Raw Material, Vendor or UOM controls in the global filter bar. UOM remains
inside the Ingredient Price Trend report.

### Date mapping

| Query | Date field |
| --- | --- |
| `29_sum_ct_procurement_funnel.sql` | `po_date` |
| `30_sum_ct_vendor_scorecard.sql` | `po_date` |
| `31_sum_ct_price_movement.sql` | `price_as_of_date` |
| `22_fact_ct_purchase_order.sql` | `po_date` |
| `24_fact_ct_po_receipt_line.sql` | `po_date` |
| `23_fact_ct_purchase_receipt.sql` | `receipt_date` |
| `36_fact_ct_risky_po.sql` | `po_date` |

### Dimension mapping

| Query | Outlet | Region | Category | Vendor | Raw Material | PO Status |
| --- | --- | --- | --- | --- | --- | --- |
| Query 29 | `outlet_code` | Query 37 lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 30 | `outlet_code` | Query 37 lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 31 | `outlet_code` | Query 37 lookup `region` | `category_name` | `vendor_name` | `item_code` | leave unmapped |
| Query 22 | `outlet_code` | Query 37 lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 24 | `outlet_code` | Query 37 lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 23 | `outlet_code` | Query 37 lookup `region` | `category_name` | `vendor_name` | `item_code` | leave unmapped |
| Query 36 | `outlet_code` | Query 37 lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |

Fixed/report-only conditions:

| Object | Setting |
| --- | --- |
| Expected Delivery Breach | `delayed_po_flag`: Individual Values, include `1` |
| Ingredient Price Trend | exactly one Raw Material and one UOM |
| Top Price Movement | include `INCREASE`, `DECREASE`, `NO_CHANGE`; exclude `NO_BASELINE` |
| Price Watch KPI | Count Distinct `item_code`; keep `NO_BASELINE` |

The corrected Query 29 and Query 30 retain category, item and status. Therefore
the three PO-value KPI widgets and vendor scorecard must now respond to those
compatible controls.

## Page 3 - Consumption & Menu Profitability

Page 3 still uses the synthetic lineage field `source_period_code`, with
default `month_03`, plus Outlet and Region. Menu filters map only to Queries 18,
25 and 32. Ingredient and UOM filters map only to Queries 19, 20 and 21.

Do not map UOM to currency KPIs. Do not map menu filters to ingredient facts.
Do not map ingredient filters to menu sales facts.

## Page 4 - Explorer & Data Quality

Page 4 current-state objects may use `source_period_code` and Outlet. Historical
trends remain unmapped from the current-period control.

Query 34 includes model-wide exception rows with
`source_period_code = ALL` and `outlet_code = ALL`. Do not map Page 4 period or
outlet controls to Query 34 quality tiles or detail.

## Click Sequence

1. Open the dashboard in **Edit Design**.
2. Click **Add User Filters**.
3. Add only the filters listed for that page.
4. Open each filter's **Map Filter to Reports** screen.
5. Select the exact field from the matrix.
6. Leave incompatible reports unmapped.
7. Apply fixed definitions in each report's **Filters** shelf using
   **Individual Values > Include**.
8. Save.
9. Test one filter at a time, then test combinations.

## Acceptance

For Page 1 and Page 2:

- no row may remain visible outside the selected physical Date Range;
- Outlet must affect every applicable KPI and report;
- Category, Vendor and Raw Material must affect every source carrying the
  corresponding field;
- PO Status must affect only PO-aware Queries 22, 24, 29, 30 and 36;
- Price Watch must retain new observations without a prior baseline;
- Top Price Movement must exclude those no-baseline observations;
- no report-specific filter may be visually presented as a global control.

The live Page 2 evidence and exact March values are in
`LIVE_P2_DASHBOARD_AUDIT_2026-07-27.md` and
`PAGE_1_AND_PAGE_2_CORRECTIONS.md`.
