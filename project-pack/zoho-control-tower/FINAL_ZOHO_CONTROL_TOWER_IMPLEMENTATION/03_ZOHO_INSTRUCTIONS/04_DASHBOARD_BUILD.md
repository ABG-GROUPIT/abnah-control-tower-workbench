# Zoho Control Tower v2 - Exact Dashboard Build

## Purpose

Build the exact saved Zoho KPI, chart, table and map views required by these
four control-tower pages:

1. Risk Action Center
2. Procurement, Vendor & Capital Control
3. Consumption Variance & Menu Profitability
4. SCM Descriptive Explorer & Data Quality

Use **consumption**, not yield, on Page 3.

The saved views are the canonical delivery objects. Each one is embedded in
its assigned external portal slot. A native four-tab Zoho dashboard may be
assembled later as a fallback, but it is not required before portal
integration.

This guide uses the exact Query Table names saved in Zoho. It does not use
logical aliases. Complete
`ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md` before starting.

For the exact build, validate, share, embed and external-filter sequence, keep
`ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md` open beside this guide.

If all 38 tables, lookups and the earlier formula list are already complete,
start with `ZOHO_CURRENT_WORKSPACE_MIGRATION.md`. The reference-first report
selection and native/custom decisions are defined in
`ABNAH_REFERENCE_TO_ZOHO_CAPABILITY_MATRIX.md`.

## Read This Before Building A Widget

Zoho has two different metric paths:

| Metric type | Build object | Where the metric appears |
| --- | --- | --- |
| Sum, average, count or distinct count of a physical field | Direct KPI Widget | Physical field appears in **Data Column** |
| Ratio or weighted rate defined as an Aggregate Formula | Saved Summary View | Formula appears in the report designer, not reliably in the KPI Widget **Data Column** list |

Never search for a business label such as `Working Capital Locked`, `Open Risky
PO Count` or `Consumption Leakage Value` in the direct widget Data Column list.
Select the exact physical column specified in this guide, then type the
business label in **Settings > Primary Value > Label**.

The only Aggregate Formulas required for this dashboard are:

| Physical table | Aggregate Formula |
| --- | --- |
| `23_fact_ct_purchase_receipt.sql` | `Weighted Unit Price` |
| `24_fact_ct_po_receipt_line.sql` | `PO Fill Rate %` |
| `24_fact_ct_po_receipt_line.sql` | `Vendor OTIF %` |
| `25_fact_ct_menu_profitability.sql` | `Menu Gross Margin %` |

The formula symbols used inside the Aggregate Formula editor are formula
syntax. They are never typed into a report filter.

## One-Time SQL Correction

If Queries 01-38 were created before this guide was updated, replace and save
only these five Query Tables, in this order:

1. `20_fact_ct_actual_consumption.sql`
2. `21_fact_ct_consumption_variance.sql`
3. `24_fact_ct_po_receipt_line.sql`
4. `31_sum_ct_price_movement.sql`
5. `33_sum_ct_scm_monthly.sql`

Do not recreate Queries 01-19, 22-23, 25-30, 32 or 34-38.

Confirm these physical columns now appear:

| Query Table | Required new physical columns |
| --- | --- |
| Query 20 | `bridge_transfer_out_qty`, `bridge_return_qty`, `bridge_closing_qty` |
| Query 21 | `signed_consumption_variance_value`, `consumption_variance_direction` |
| Query 24 | `eligible_lead_time_deviation_days` |
| Query 31 | `price_comparison_key`, `unit_price_change_percent`, `absolute_unit_price_change_percent`, `price_movement_direction` |
| Query 33 | `working_capital_value` |

Stop if any of these fields is absent. Refresh the table metadata after saving
the Query Table, then reopen the widget/report editor.

# Part 1 - Three Zoho Build Patterns

## Pattern A - Direct KPI Widget

Use this only when the build register names a physical Data Column.

1. Choose **Create > New Report** from the required Query Table, or create the
   KPI view through the report workspace available in the current Zoho UI.
2. Choose **KPI Widget**.
3. Choose **Single Label** or **Single Number**.
4. Open the **Data** tab.
5. For **Table**, select the exact numbered Query Table.
6. For **Data Column**, select the exact physical column from the register.
7. For **Show Value As** or **Calculation**, choose the stated operation.
8. Leave **Group By** empty.
9. Add the fixed filter only when the register says one is required.
10. Open **Settings > Values**.
11. Type the exact KPI label in **Primary Value > Label**.
12. Apply the stated number format.
13. Leave secondary value, indicator and target blank unless this guide says
    otherwise.
14. Click **Apply**.
15. Save the individual KPI view with the exact `CT_...` name.

If several numbers appear, **Group By** is not empty. If the business label is
missing from Data Column, that is expected: choose the physical column instead.

## Pattern B - Aggregate Formula KPI Tile

Use this for `PO Fill Rate %`, `Vendor OTIF %` and `Menu Gross Margin %`.

1. Click **Create > New Report**.
2. Choose **Summary View**.
3. Select the exact physical Query Table named in the register.
4. In the report designer, locate **Aggregate Formulas** in the left column
   pane.
5. Drag the named Aggregate Formula into the summary value area.
6. Do not add a grouping field.
7. Add no report filter unless the register explicitly requires one.
8. Format the result as percentage with two decimals.
9. Set the report title to the exact `CT_...` name.
10. Save the Summary View.
11. Hide the report toolbar, legend and unnecessary borders in its embed
    settings.
12. Keep the assigned outer-portal title as the KPI label.
13. Save the individual Summary View with the exact `CT_...` name.

This saved Summary View replaces a direct KPI Widget for that one ratio. Do not
try to find the Aggregate Formula in the direct widget Data Column dropdown.

## Pattern C - Fixed Report Filter

Zoho report filters are selected through the Filter shelf. Do not type SQL
criteria into the interface.

1. Open the saved report.
2. Click **Edit Design**.
3. Open the **Filters** tab.
4. Drag the exact physical field to the **Filter Shelf**.
5. Choose **Individual Values** for a text or flag field.
6. Tick the exact value or values listed in this guide.
7. Choose **Include**.
8. Confirm the selected filter appears in the right-side filter-items box.
9. Return to **View Mode**.
10. Validate the row count or total.
11. Save.

Example: for stockout action reports, drag `risk_type`, choose **Individual
Values**, tick `STOCKOUT`, and choose **Include**. Do not enter comparison text.

# Part 2 - Direct KPI Build Register

Every direct widget below uses **Group By: blank**.

## Page 1 - Risk Action Center KPIs

| Build order | Report name and label | Physical table | Data Column | Show Value As | Fixed report filter | Format | Default result |
| ---: | --- | --- | --- | --- | --- | --- | ---: |
| 1 | `CT_P1_KPI_Outlets_At_Stockout_Risk` / Outlets At Stockout Risk | `27_fact_ct_inventory_risk.sql` | `outlet_code` | Count Distinct | `risk_type`: Individual Values, Include `STOCKOUT` | Whole number | 3 |
| 2 | `CT_P1_KPI_Menu_Items_At_Risk` / Menu Items At Risk | `28_fact_ct_menu_impact.sql` | `menu_item_code` | Count Distinct | None | Whole number | 110 |
| 3 | `CT_P1_KPI_Stockout_Risk_Value` / Stockout Sales At Risk | `28_fact_ct_menu_impact.sql` | `allocated_forecast_net_sales_at_risk` | Sum | None | INR, 2 decimals | INR 411,695.55 |
| 4 | `CT_P1_KPI_Expiry_Risk_Value_Demo` / Expiry Risk Value - Demo Estimate | `38_fact_ct_expiry_risk.sql` | `expiry_risk_value` | Sum | None | INR, 2 decimals | INR 271,399.12 |
| 5 | `CT_P1_KPI_Open_Actions` / Open Actions | `27_fact_ct_inventory_risk.sql` | `action_id` | Count Distinct | `risk_type`: Individual Values, Include `STOCKOUT` | Whole number | 6 |

The expiry widget subtitle must read:

```text
Synthetic demo estimate - no POSIST batch/expiry source
```

## Page 2 - Procurement, Vendor & Capital KPIs

Build rows 1, 2, 3 and 5 with Pattern A. Build row 4 with Pattern B.

| Build order | Report name and label | Object | Physical table | Data Column or Aggregate Formula | Calculation | Format | Default result |
| ---: | --- | --- | --- | --- | --- | --- | ---: |
| 1 | `CT_P2_KPI_Monthly_Purchase` / Monthly Purchase | Direct KPI | `29_sum_ct_procurement_funnel.sql` | `ordered_value` | Sum | INR, 2 decimals | INR 1,565,981.32 |
| 2 | `CT_P2_KPI_Open_PO_Liability` / Open PO Exposure | Direct KPI | `29_sum_ct_procurement_funnel.sql` | `pending_value` | Sum | INR, 2 decimals | INR 177,145.39 |
| 3 | `CT_P2_KPI_Delayed_PO_Value` / Delayed PO Value | Direct KPI | `29_sum_ct_procurement_funnel.sql` | `delayed_value` | Sum | INR, 2 decimals | INR 156,529.82 |
| 4 | `CT_P2_KPI_OTIF` / Vendor OTIF - Formula Demo | Summary View | `24_fact_ct_po_receipt_line.sql` | `Vendor OTIF %` | Aggregate Formula | Percentage, 2 decimals | 53.70% |
| 5 | `CT_P2_KPI_Price_Watch` / Price Watch | Direct KPI | `31_sum_ct_price_movement.sql` | `item_code` | Count Distinct | Whole number | 42 |

Keep the wording **Ordered Gross Value** until ABNAH approves the production
purchase-value basis. Keep OTIF visibly marked as a formula demo until actual
PO-to-GRN linkage passes the documented source gate.

The earlier Closing Inventory, Working Capital, Open PO Count and Fill Rate
cards remain valid extended controls. Build them only after the five reference
cards above reconcile:

| Extended report | Physical field or formula | Default |
| --- | --- | ---: |
| `CT_P2_KPI_Closing_Inventory` | Query 33 Sum `closing_stock_value` | INR 3,344,237.44 |
| `CT_P2_KPI_Working_Capital` | Query 33 Sum `working_capital_value` | INR 3,521,382.83 |
| `CT_P2_KPI_Open_PO_Count` | Query 29 Sum `open_po_count` | 28 |
| `CT_P2_KPI_Fill_Rate` | Query 24 `PO Fill Rate %` Summary View | 86.39% |

## Page 3 - Consumption Variance & Menu Profitability KPIs

Build rows 1, 2, 4 and 5 with Pattern A. Build row 3 with Pattern B.

| Build order | Report name and label | Object | Physical table | Data Column or Aggregate Formula | Calculation | Format | Default result |
| ---: | --- | --- | --- | --- | --- | --- | ---: |
| 1 | `CT_P3_KPI_Net_Sales` / Net Sales | Direct KPI | `25_fact_ct_menu_profitability.sql` | `net_sales` | Sum | INR, 2 decimals | INR 2,192,475.48 |
| 2 | `CT_P3_KPI_Theoretical_COGS` / Theoretical COGS | Direct KPI | `25_fact_ct_menu_profitability.sql` | `theoretical_cogs` | Sum | INR, 2 decimals | INR 393,664.46 |
| 3 | `CT_P3_KPI_Menu_Gross_Margin` / Gross Margin | Summary View | `25_fact_ct_menu_profitability.sql` | `Menu Gross Margin %` | Aggregate Formula | Percentage, 2 decimals | 82.04% |
| 4 | `CT_P3_KPI_Menu_Items` / Menu Items | Direct KPI | `25_fact_ct_menu_profitability.sql` | `menu_item_code` | Count Distinct | Whole number | 110 |
| 5 | `CT_P3_KPI_Consumption_Leakage` / Consumption Leakage | Direct KPI | `21_fact_ct_consumption_variance.sql` | `leakage_value` | Sum | INR, 2 decimals | INR 38,632.37 |

Do not average `gross_margin_percent`. Do not sum mixed-UOM consumption
quantities into the all-item leakage KPI.

`CT_P3_KPI_Quantity_Sold` remains an optional extended card. It is not one of
the five reference cards.

## Page 4 - Descriptive Explorer KPIs

Build rows 1-5 as the reference KPI row.

| Build order | Report name and label | Physical table | Data Column | Show Value As | Fixed report filter | Format | Default result |
| ---: | --- | --- | --- | --- | --- | --- | ---: |
| 1 | `CT_P4_KPI_Closing_Stock` / Closing Stock Value | `33_sum_ct_scm_monthly.sql` | `closing_stock_value` | Sum | None | INR, 2 decimals | INR 3,344,237.44 |
| 2 | `CT_P4_KPI_Open_PO` / Open PO Value | `33_sum_ct_scm_monthly.sql` | `open_po_value` | Sum | None | INR, 2 decimals | INR 177,145.39 |
| 3 | `CT_P4_KPI_Net_Sales` / Net Sales | `33_sum_ct_scm_monthly.sql` | `net_sales` | Sum | None | INR, 2 decimals | INR 2,192,475.48 |
| 4 | `CT_P4_KPI_Actual_Consumption` / Actual Consumption Value | `33_sum_ct_scm_monthly.sql` | `actual_consumption_value` | Sum | None | INR, 2 decimals | INR 377,620.25 |
| 5 | `CT_P4_KPI_Consumption_Variance` / Signed Consumption Variance Value | `21_fact_ct_consumption_variance.sql` | `signed_consumption_variance_value` | Sum | None | INR, 2 decimals, allow negative | INR -22,106.87 |
| 6 | `CT_P4_KPI_Quantity_Sold` / Quantity Sold | `18_fact_ct_sales.sql` | `sold_qty` | Sum | None | Whole number | 8,471 |
| 7 | `CT_P4_KPI_Active_Menu_Items` / Active Menu Items | `18_fact_ct_sales.sql` | `item_code` | Count Distinct | None | Whole number | 110 |
| 8 | `CT_P4_KPI_Open_PO_Lines` / Open PO Lines | `22_fact_ct_purchase_order.sql` | `is_open_po` | Sum | None | Whole number | 47 |
| 9 | `CT_P4_KPI_GRN_Value` / GRN Value | `23_fact_ct_purchase_receipt.sql` | `receipt_total` | Sum | None | INR, 2 decimals | INR 1,504,689.72 |
| 10 | `CT_P4_KPI_Active_Vendors` / Active Vendors | `22_fact_ct_purchase_order.sql` | `vendor_name` | Count Distinct | None | Whole number | 12 |

Rows 6-10 are extended descriptive controls. These are descriptive totals. Do
not color a value red merely because it is large.

# Part 3 - Saved Reports To Build

Use **Create > New Report**, select the exact table, configure the shelves,
apply fixed filters through Pattern C, and save with the exact report name.

## Page 1 Reports

| Report | Type | Physical table | Exact shelves and sort | Fixed filter |
| --- | --- | --- | --- | --- |
| `CT_P1_Outlet_Risk_Map` | Map | `27_fact_ct_inventory_risk.sql` | Location: outlet lookup; latitude/longitude: Query 37 fields; color: Max `risk_severity_rank`; tooltip: outlet, Count Distinct `item_code`, Sum `shortage_cost_value`, Min `days_cover`, Max severity rank | `risk_type`: Include `STOCKOUT` |
| `CT_P1_Stockout_Priority_Stack` | Horizontal stacked bar | `27_fact_ct_inventory_risk.sql` | Y: `outlet_name`; X: Sum `shortage_cost_value`; color: `risk_severity`; sort Max severity rank descending, then value descending | `risk_type`: Include `STOCKOUT` |
| `CT_P1_Action_Center` | Tabular | `27_fact_ct_inventory_risk.sql` | `action_id`, outlet, item, severity, shortage, `recommended_action`, `action_owner`, `due_band`; sort severity rank descending, total risk value descending | `risk_type`: Include `STOCKOUT` |
| `CT_P1_Stockout_Risk_Detail` | Tabular | `27_fact_ct_inventory_risk.sql` | item, current stock, forecast, safety requirement, inbound, shortage, days cover, shortage cost, severity | `risk_type`: Include `STOCKOUT` |
| `CT_P1_Menu_Impact_Detail` | Tabular | `28_fact_ct_menu_impact.sql` | ingredient, menu item, severity, forecast menu quantity, allocated forecast sales at risk | None; Query 28 contains risk rows only |
| `CT_P1_Expiry_Risk_Detail_Demo` | Tabular | `38_fact_ct_expiry_risk.sql` | outlet, item, batch, receipt date, GRN, PO, vendor, receipt status, closing quantity, FIFO tranche, expected consumption, expiry quantity/value, estimated date, severity, method | None |
| `CT_P1_Vendor_PO_Risk` | Tabular | `36_fact_ct_risky_po.sql` | PO, vendor, item, expected date, remaining quantity, open liability, severity | None; Query 36 contains open risky PO rows only |

Enable **View Underlying Data** for the action and detail reports. Enable **Use
as Filter** only on the map and priority stack.

## Page 2 Reports

| Report | Type | Physical table | Exact shelves and sort | Fixed filter |
| --- | --- | --- | --- | --- |
| `CT_P2_Procurement_Funnel` | Funnel or grouped horizontal bar | `29_sum_ct_procurement_funnel.sql` | Values: Sum `ordered_value`, Sum `processed_value`, Sum `pending_value`, Sum `delayed_value`; tooltip: Sum `po_count`, Sum `open_po_count` | None |
| `CT_P2_PO_Status_Distribution` | Stacked bar | `22_fact_ct_purchase_order.sql` | X: `po_status`; Y: Count Distinct `po_number`; secondary value: Sum `open_po_value` | None |
| `CT_P2_Pending_By_Vendor` | Horizontal bar | `29_sum_ct_procurement_funnel.sql` | Y: `vendor_name`; X: Sum `pending_value`; sort value descending | None |
| `CT_P2_Pending_Ingredient_Risk` | Tabular | `36_fact_ct_risky_po.sql` | PO, vendor, item, remaining quantity, open value, expected date, severity | None |
| `CT_P2_Expected_Delivery_Breach` | Tabular | `22_fact_ct_purchase_order.sql` | PO, vendor, item, expected date, remaining quantity, open value | `delayed_po_flag`: Include `1` |
| `CT_P2_Vendor_Performance_Matrix` | Bubble | `24_fact_ct_po_receipt_line.sql` | Group: `vendor_name`; X: `Vendor OTIF %`; Y: Average `eligible_lead_time_deviation_days`; size: Sum `open_po_value` | None |
| `CT_P2_Vendor_Scorecard` | Summary or pivot | `24_fact_ct_po_receipt_line.sql` | Row: vendor; values: Sum gross order value, Sum open PO value, `Vendor OTIF %`, `PO Fill Rate %`, Average eligible lead deviation, Sum delayed flag | None |
| `CT_P2_Ingredient_Price_Trend` | Line | `23_fact_ct_purchase_receipt.sql` | X: `source_period_code`; Y: `Weighted Unit Price`; color: `item_name`; vendor is a user filter | None |
| `CT_P2_Vendor_Price_Comparison` | Grouped bar | `23_fact_ct_purchase_receipt.sql` | X: `vendor_name`; Y: `Weighted Unit Price`; require one item and one UOM selection | None |
| `CT_P2_Top_Price_Movement` | Horizontal bar | `31_sum_ct_price_movement.sql` | Y: `price_comparison_key`; X: `unit_price_change_percent`; color: `price_movement_direction`; sort `absolute_unit_price_change_percent` descending; Top 10 | None |
| `CT_P2_Inventory_Value` | Stacked bar | `05_std_ct_inventory_snapshot.sql` | X: `outlet_name`; Y: Sum `closing_value`; color: `category_name` | None |
| `CT_P2_High_Value_Slow_Stock` | Tabular | `27_fact_ct_inventory_risk.sql` | closing value, days cover, forecast demand and severity; sort closing value then days cover descending | None |
| `CT_P2_Observed_Wastage` | Column | `35_sum_ct_financial_leakage.sql` | X: `source_period_code`; Y: Sum `leakage_value` | None |
| `CT_P2_Expiry_Exposure_Demo` | Column | `38_fact_ct_expiry_risk.sql` | X: `source_period_code`; Y: Sum `expiry_risk_value` | None |

If Funnel cannot accept four value fields as stages, use the grouped horizontal
bar option. Do not create an unsupported custom chart.

Do not build vendor return rate, standing PO tracking or exact batch expiry as
actual-source KPIs. Their source gates remain unresolved.

## Page 3 Reports

| Report | Type | Physical table | Exact shelves and sort | Fixed filter |
| --- | --- | --- | --- | --- |
| `CT_P3_Consumption_Bridge` | Combination | `20_fact_ct_actual_consumption.sql` | X: `source_period_code`; bars: Sum opening, purchase, transfer in, `bridge_transfer_out_qty`, `bridge_return_qty`, `bridge_closing_qty`; line: Sum calculated actual consumption; require one UOM | None |
| `CT_P3_Consumption_Variance` | Butterfly | `21_fact_ct_consumption_variance.sql` | Dimension: item; value: Sum `signed_consumption_variance_value`; color: `consumption_variance_direction`; sort by absolute value | None |
| `CT_P3_Theoretical_Consumption_Detail` | Tabular | `19_fact_ct_theoretical_consumption.sql` | outlet, item, theoretical quantity/value, UOM, average cost | None |
| `CT_P3_Actual_vs_Theoretical` | Grouped bar | `21_fact_ct_consumption_variance.sql` | X: item; Y: Sum actual quantity and Sum theoretical quantity; require one UOM | None |
| `CT_P3_Consumption_Leakage_Rank` | Horizontal bar | `21_fact_ct_consumption_variance.sql` | Y: item; X: Sum `leakage_value`; sort descending | `consumption_variance_direction`: Include `OVER_CONSUMPTION` |
| `CT_P3_Low_Consumption_Check` | Tabular | `21_fact_ct_consumption_variance.sql` | outlet, item, actual, theoretical, variance, low-consumption quantity, UOM | `consumption_variance_direction`: Include `UNDER_CONSUMPTION` |
| `CT_P3_Menu_BCG` | Bubble | `32_sum_ct_menu_profitability.sql` | X: Sum sold quantity; Y: Max `gross_margin_percent`; size: Sum net sales; text: outlet and menu item; color: `bcg_quadrant`; use one period and retain outlet grouping | None |
| `CT_P3_Menu_COGS_Detail` | Tabular | `25_fact_ct_menu_profitability.sql` | menu item, sold quantity, theoretical cost per unit, COGS, net sales, margin value | None |
| `CT_P3_Menu_Margin_Rank` | Horizontal bar | `32_sum_ct_menu_profitability.sql` | Y: menu item; X: Sum gross margin value; tooltip: COGS and row-grain margin percent | None |
| `CT_P3_Sales_Trend` | Line | `18_fact_ct_sales.sql` | X: sales date; Y: Sum net sales and Sum sold quantity | None |
| `CT_P3_Category_Contribution` | Ring or stacked bar | `25_fact_ct_menu_profitability.sql` | Category; Sum net sales; **Show Values As: Percent of Total** | None |
| `CT_P3_Top_Slow_Menu_Ranking` | Horizontal bar | `32_sum_ct_menu_profitability.sql` | Menu item; selected additive metric; sort descending or ascending | None |
| `CT_P3_Outlet_Item_Heatmap` | Heat map | `25_fact_ct_menu_profitability.sql` | X: menu item or category; Y: outlet; color: Sum net sales or sold quantity | None |

`CT_P3_Low_Consumption_Check` is a data/process check, not a favorable saving.
The BCG thresholds are synthetic demonstration rules. Do not add a veg/non-veg
split until an approved menu classification exists.

## Page 4 Reports

| Report | Type | Physical table | Exact shelves | Fixed filter |
| --- | --- | --- | --- | --- |
| `CT_P4_SCM_Monthly_Trend` | Combination | `33_sum_ct_scm_monthly.sql` | X: period; bars: Sum stock and open PO; lines: Sum sales and actual consumption | None |
| `CT_P4_Consumption_Variance_Trend` | Bar/line | `21_fact_ct_consumption_variance.sql` | X: period; Y: Sum signed variance value and Sum leakage value | None |
| `CT_P4_Descriptive_Explorer` | Pivot or tabular | `33_sum_ct_scm_monthly.sql` | period, outlet, the five physical value fields; export enabled | None |
| `CT_P4_Sales_Explorer` | Tabular | `18_fact_ct_sales.sql` | date, outlet, menu item/category, sold quantity, net sales, realized unit price | None |
| `CT_P4_Item_Explorer` | Tabular | `27_fact_ct_inventory_risk.sql` | outlet, item, category, stock, cost, forecast, PO and severity | None |
| `CT_P4_PO_Explorer` | Tabular | `24_fact_ct_po_receipt_line.sql` | PO, vendor, item, ordered, received, remaining, expected date, receipt date, status | None |
| `CT_P4_GRN_Explorer` | Tabular | `23_fact_ct_purchase_receipt.sql` | receipt date, GRN, PO, vendor, item, received quantity, subtotal, tax/total, return status | None |
| `CT_P4_Vendor_Explorer` | Tabular | `30_sum_ct_vendor_scorecard.sql` | vendor, ordered/received value, open liability, fill, eligible OTIF, lead deviation, delayed lines | None; retain outlet as a visible group or select one outlet |
| `CT_P4_Expiry_Explorer_Demo` | Tabular | `38_fact_ct_expiry_risk.sql` | outlet, item, scenario inputs, estimated date, quantity/value, production-use label | None |

## Page 4 Data-Quality Tiles

Create six direct KPI Widgets from
`34_fact_ct_data_quality_exception.sql`.

For every tile:

- Data Column: `exception_count`
- Show Value As: Sum
- Group By: blank
- Filter field: `exception_type`
- Filter method: **Individual Values > Include**

| Tile label | Included value | Default result |
| --- | --- | ---: |
| Negative Stock | `NEGATIVE_STOCK` | 1 |
| Zero Stock With Demand | `ZERO_STOCK_WITH_DEMAND` | 2 |
| Sold Item Missing Recipe | `SOLD_ITEM_MISSING_RECIPE` | 0 |
| Operational Item Missing Master | `OPERATIONAL_ITEM_MISSING_MASTER` | 0 |
| UOM Mismatch Without Conversion | `UOM_MISMATCH_WITHOUT_CONVERSION` | 0 |
| Open PO Missing Expected Delivery | `OPEN_PO_MISSING_EXPECTED_DELIVERY` | 3 |

Create `CT_P4_Data_Quality_Detail` as a tabular report with exception type,
period, outlet, record key, item code, reference number and definition.

The six KPI widgets are display tiles. A single-number widget has no grouping
dimension to pass as a reliable report-as-filter criterion. Use the Page 4
**Exception Type** user filter, mapped only to the detail table, to inspect one
exception type.

# Part 4 - Dashboard Assembly

## Create The Dashboard

1. Click **Create > New Dashboard**.
2. Name it `ABNAH Supply Chain Control Tower v2`.
3. Add four tabs with the exact names at the start of this guide.
4. Place the saved reports and KPI objects using the layouts below.
5. Keep KPI rows at one consistent height.
6. Give detail tables more vertical space than charts.
7. Enable smart alignment.
8. Save after completing each tab.

## Layout

```text
Page 1
Row 1: five KPI objects
Row 2: risk map (7 columns) | priority stack (5)
Row 3: action center (12)
Row 4: stockout detail (6) | menu impact (6)
Row 5: expiry detail (6) | vendor/PO risk (6)

Page 2
Row 1: five reference KPI objects
Row 2: procurement funnel (6) | vendor scorecard (6)
Row 3: price trend (6) | top price movement (6)
Row 4: pending by vendor (6) | delivery breach (6)
Extended rows: PO status, vendor matrix, inventory/capital controls, wastage and expiry scenario

Page 3
Row 1: five KPI objects
Row 2: consumption bridge (6) | consumption variance (6)
Row 3: menu BCG (12)
Row 4: outlet-item heatmap (12)
Extended rows: actual/theoretical detail, leakage rank, menu COGS, margin rank, sales trend, category contribution and ranking

Page 4
Row 1: five reference KPI objects
Row 2: monthly trend (12)
Row 3: six data-quality tiles
Row 4: data-quality detail (12)
Row 5: descriptive/export explorer (12)
Extended rows: variance trend, sales/item/PO/GRN/vendor explorers and expiry scenario
```

# Part 5 - Dashboard Filters

## Do Not Add Every Filter Everywhere

Create only two dashboard-global controls:

1. **As-of Source Period**
2. **Outlet**

Create the remaining controls on their relevant tab only. For each report,
open **Options > Apply Dashboard Filters > Customize** and map only the fields
listed below. A filter that is not mapped must leave that report unchanged.

## Global Filter 1 - As-of Source Period

1. Open the dashboard in Edit Mode.
2. Click **Add User Filters**.
3. Drag `source_period_code` from a placed current-state report.
4. Set the display to dropdown.
5. Set selection to single-select.
6. Set the label to `As-of Source Period`.
7. Set the default to `month_03`.
8. Open each report's filter customization.
9. Map it to that report's `source_period_code` only when the matrix says
   **Apply**.

| Tab | Apply | Exclude |
| --- | --- | --- |
| Page 1 | Every Page 1 KPI and report | None |
| Page 2 | Current KPIs, procurement flow, PO/vendor/inventory/current-risk reports | `CT_P2_Ingredient_Price_Trend`, `CT_P2_Observed_Wastage`, `CT_P2_Expiry_Exposure_Demo` |
| Page 3 | Current KPIs, comparisons, leakage, profitability, BCG, contribution, ranking and heatmap | `CT_P3_Consumption_Bridge`, `CT_P3_Sales_Trend` |
| Page 4 | Current KPIs and current explorers | `CT_P4_SCM_Monthly_Trend`, `CT_P4_Consumption_Variance_Trend`, all Query 34 tiles and `CT_P4_Data_Quality_Detail` |

The excluded charts are historical trends and must retain all three periods.
Query 34 also contains model-wide rows whose period is `ALL`; mapping the
As-of filter would hide them.

## Global Filter 2 - Outlet

1. Add another User Filter.
2. Drag `outlet_code`.
3. Set the label to `Outlet`.
4. Use multi-select.
5. Keep the default as All.
6. Map it only to reports with a genuine `outlet_code`.
7. Exclude all Query 34 tiles and `CT_P4_Data_Quality_Detail`.

Use `outlet_code`, not outlet display name, as the mapping key.

## Tab-Local Filters

Add these filters only on the named tab.

| Tab | Filter label | Physical field | Map only to |
| --- | --- | --- | --- |
| Page 1 | Region | Query 37 lookup `region` | Query 27, 28, 36 and 38 reports with outlet lookup |
| Page 1 | New / Matured | Query 37 lookup `new_matured_flag` | Query 27, 28, 36 and 38 reports with outlet lookup |
| Page 1 | Stockout Severity | `risk_severity` | Query 27 stockout reports and Query 28 menu impact only |
| Page 1 | Action Owner | `action_owner` | Query 27 action and stockout-detail reports |
| Page 1 | Ingredient Category | `category_name` through item lookup | Query 27, 28, 36 and 38 ingredient reports |
| Page 2 | Region | Query 37 lookup `region` | Page 2 reports with outlet lookup |
| Page 2 | Vendor | `vendor_name` | Queries 22, 23, 24, 29, 30, 31 and 36 reports |
| Page 2 | Ingredient Category | item lookup `category_name` | PO/receipt/risky-PO/price/inventory reports with item lookup |
| Page 2 | Ingredient Item | `item_code` | PO/receipt/risky-PO/price/inventory reports with item grain |
| Page 2 | PO Status | `po_status` | `CT_P2_PO_Status_Distribution` and `CT_P2_Expected_Delivery_Breach` |
| Page 3 | Region | Query 37 lookup `region` | Page 3 reports with outlet lookup |
| Page 3 | Menu Category | `category_name` through menu lookup | Queries 18, 25 and 32 menu reports |
| Page 3 | Menu Item | menu `item_code` or `menu_item_code` as exposed by source | Queries 18, 25 and 32 menu reports |
| Page 3 | Ingredient Category | ingredient lookup `category_name` | Queries 19, 20 and 21 |
| Page 3 | Ingredient | `item_code` | Queries 19, 20 and 21 |
| Page 3 | Canonical UOM | `canonical_uom` | Quantity-only consumption reports |
| Page 4 | Region | Query 37 lookup `region` | Non-Query-34 Page 4 reports with outlet lookup |
| Page 4 | Ingredient | `item_code` | Consumption, inventory, PO-line, GRN and expiry reports |
| Page 4 | Menu Item | sales/menu item field | Sales explorer and menu reports |
| Page 4 | Vendor | `vendor_name` | PO, GRN and vendor explorer reports |
| Page 4 | Exception Type | `exception_type` | `CT_P4_Data_Quality_Detail` only |

Do not map the UOM filter to currency KPIs. Do not map menu filters to
ingredient facts. Do not map ingredient filters to menu sales facts.

## Filters That Stay Fixed Inside Reports

Apply these through Pattern C:

| Reports | Filter shelf field | Individual Values to Include |
| --- | --- | --- |
| Page 1 stockout map, priority, action and stockout detail | `risk_type` | `STOCKOUT` |
| Page 2 expected delivery breach | `delayed_po_flag` | `1` |
| Page 3 leakage rank | `consumption_variance_direction` | `OVER_CONSUMPTION` |
| Page 3 low-consumption check | `consumption_variance_direction` | `UNDER_CONSUMPTION` |
| Each Page 4 quality tile | `exception_type` | The one exact exception value assigned to that tile |

Query 28 already contains only menu-impact risk rows. Query 36 already contains
only open risky PO rows. Query 38 is the synthetic expiry-risk scenario. Do not
add redundant fixed filters to those reports.

# Part 6 - Formatting And Interaction

## Severity Colors

| State | Color |
| --- | --- |
| Purple | `#6C3B8C` |
| Red | `#C63D3D` |
| Amber | `#D49A22` |
| Green | `#2E7D5B` |
| Grey / no data | `#7C8793` |

Reserve these colors for actual states. Use neutral colors for Page 4
descriptive metrics.

Enable **Use as Filter** only for:

- Page 1 risk map and priority stack
- Page 2 vendor matrix and price movement
- Page 3 menu BCG and heatmap

Do not enable it on every report. Do not rely on single-number quality widgets
to pass an exception category.

Use native Zoho chart and conditional-format settings. JavaScript applies only
to a later externally embedded portal, not to the native dashboard editor.

# Part 7 - Validation Gates

Keep `ZOHO_DASHBOARD_EXPECTED_RESULTS.md` open while building.

For each saved KPI or report:

1. Set As-of Source Period to `month_03`.
2. Set Outlet to All.
3. Compare with the expected default result or chart table.
4. Test OUT001, OUT002 and OUT003 separately.
5. Clear the Outlet filter.
6. Confirm historical trends still show all three months.
7. Confirm Query 34 tiles and detail are unchanged by global period/outlet.
8. Export one detail report and trace its rows to the Query Table.

Stop and fix the source/report before styling if:

- a direct KPI Data Column is not the exact physical field in this guide;
- a formula KPI was built as a direct widget instead of a Summary View;
- Working Capital does not use `working_capital_value`;
- signed consumption variance does not allow negative values;
- a stockout report includes `HEALTHY` rows;
- a trend collapses to `month_03`;
- Query 34 model-wide checks disappear;
- stockout and expiry values are combined into one card;
- an expiry report omits the synthetic-estimate warning.

# Official Zoho References

- Aggregate formulas and report designer:
  https://www.zoho.com/analytics/help/analyze-data/aggregate-formula.html
- KPI widgets:
  https://www.zoho.com/analytics/help/dashboard/kpi-widgets.html
- Report Filter shelf, Individual Values, Include and Exclude:
  https://www.zoho.com/analytics/help/chart/applying-filters.html
- Dashboard user-filter mapping:
  https://www.zoho.com/analytics/help/dashboard/filter.html
