# Zoho Control Tower v2 - Dashboard Build

## Objective

Build one Zoho Analytics dashboard with four tabs:

1. Risk Action Center
2. Procurement, Vendor & Capital Control
3. Consumption Variance & Menu Profitability
4. SCM Descriptive Explorer & Data Quality

Use **consumption**, not yield, on Page 3.

## Physical Query Table Names

The uppercase table names used below are logical model labels. In Zoho, select
the corresponding numbered `.sql` Query Table. Resolve each label through
`logical_model_name` in `zoho_control_tower_v2_sql/QUERY_TABLE_MANIFEST.csv`;
for example, `FACT_CT_Inventory_Risk` is
`27_fact_ct_inventory_risk.sql`.

Native Zoho charts are sufficient for the current design. Zoho supports KPI
widgets, maps, bar, stacked, line, combination, funnel, bubble and heat-map
charts. Use JavaScript only if the finished dashboard is later embedded in a
separate custom application.

Official chart reference:
https://www.zoho.com/analytics/help/chart/chart-types.html

## Prerequisites

Before creating reports:

- All 38 active Query Tables exist.
- Query Table validation is complete.
- The full checklist in
  `ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md` passes.
- All required lookups, row formula columns and aggregate formulas exist.
- `13_dim_ct_outlet.sql` contains `OUT001`, `OUT002` and `OUT003`.
- Every synthetic outlet has a resolved map point in
  `37_dim_ct_outlet_enriched.sql`.
- Truth files have been generated.
- Keep `04A_DASHBOARD_EXPECTED_RESULTS.md` open and reconcile every saved
  report to its expected value, chart point or row count before placing it on a
  dashboard tab.

## Lookup Columns

Do not improvise lookup relationships while creating reports. Use the exact
physical child-to-parent matrix in
`ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md`. In particular,
sales `item_code` maps to the menu-item dimension, Query 34 has no outlet/item
lookups, and Query 37 is the canonical outlet parent.

## Reusable Formula Columns

### Risk Severity Rank

Query 27 now publishes `risk_severity_rank` directly. Do not recreate it as a
formula column. Its fixed ordering is:

```text
PURPLE = 4
RED = 3
AMBER = 2
GREEN = 1
```

### Signed Consumption Bridge

Create on `FACT_CT_Actual_Consumption`:

```text
bridge_transfer_out = -1 * "transfer_out_qty"
bridge_return = -1 * "return_qty"
bridge_closing = -1 * "closing_qty"
```

These fields make the inventory bridge readable in a combination chart. They do
not replace the final `calculated_actual_consumption_qty`.

## Aggregation Contract

Create these as reusable aggregate formulas before any KPI widget:

| Business metric | Formula |
| --- | --- |
| Working Capital Locked | `sum("closing_stock_value") + sum("open_po_value")` |
| PO Fill Rate % | `if(sum("ordered_qty") <> 0, sum("received_qty") / sum("ordered_qty") * 100, null)` |
| Vendor OTIF % | `if(sum("eligible_closed_line_flag") <> 0, sum("otif_success_flag") / sum("eligible_closed_line_flag") * 100, null)` |
| Weighted Unit Price | `if(sum("received_qty") <> 0, sum("receipt_subtotal") / sum("received_qty"), null)` |
| Menu Gross Margin % | `if(sum("net_sales") <> 0, sum("gross_margin_value") / sum("net_sales") * 100, null)` |
| Category Sales Contribution % | `sum("net_sales") / sum("net_sales" over the current report total) * 100`, configured as percent-of-total in the chart |
| Stockout Sales At Risk | `sum(if("shortage_qty" > 0, "allocated_forecast_net_sales_at_risk", 0))` |
| Expiry Risk Value - Demo | `sum("expiry_risk_value")` |

Do not average percentages, sum row unit prices, or add quantities across kg,
litre and pieces. Counts of POs, outlets, items and menu items use distinct
count at their stated identifier.

## Create A Report

For each report below:

1. Click **Create**.
2. Select the stated report type.
3. Choose the stated source table.
4. Drag dimensions and measures to the listed shelves.
5. Apply the listed report filters.
6. Set the sort.
7. Add tooltip fields.
8. Save with the exact report name.

Use the saved reports as components in the dashboard. Do not build calculations
directly inside only one dashboard component when the same metric is reused.

# Page 1 - Risk Action Center

## KPI Widgets

| Report name | Source | Measure | Filter |
| --- | --- | --- | --- |
| `CT_P1_KPI_Outlets_At_Stockout_Risk` | `FACT_CT_Inventory_Risk` | Outlets At Stockout Risk | `risk_severity <> GREEN` |
| `CT_P1_KPI_Menu_Items_At_Risk` | `FACT_CT_Menu_Impact` | Menu Items At Risk | none |
| `CT_P1_KPI_Stockout_Risk_Value` | `FACT_CT_Menu_Impact` | Stockout Risk Value | `shortage_qty > 0` |
| `CT_P1_KPI_Expiry_Risk_Value_Demo` | `FACT_CT_Expiry_Risk` | Expiry Risk Value - Demo Estimate | none |
| `CT_P1_KPI_Open_Risky_PO` | `FACT_CT_Risky_PO` | Open Risky PO Count | none |

Format values as:

- Counts: whole number
- Values: INR currency with compact notation
- Subtitle the expiry widget **Synthetic estimate - no POSIST batch/expiry
  source**. Never remove this qualifier.

## Outlet Risk Location

Create `CT_P1_Outlet_Risk_Map` from `FACT_CT_Inventory_Risk`.

- Location: outlet through the lookup to `DIM_CT_Outlet_Enriched`
- Latitude/longitude: enriched outlet fields
- Color: maximum `risk_severity_rank`
- Tooltip: outlet, distinct stockout-risk item count, shortage cost, days cover
  and maximum stockout severity
- Fixed report filter: `risk_severity <> GREEN`
- Use as filter: enabled

The map is valid for the synthetic three-outlet demonstration only. Production
must replace the enriched outlet table with an approved ABNAH reference.

## Priority And Action Views

| Report | Type | Source | Configuration |
| --- | --- | --- | --- |
| `CT_P1_Stockout_Priority_Stack` | Horizontal stacked bar | `FACT_CT_Inventory_Risk` | Y: outlet; X: sum shortage cost value; color: severity; sort severity rank then value |
| `CT_P1_Action_Center` | Tabular | `FACT_CT_Inventory_Risk` | action ID, outlet, item, severity, shortage, recommended action, owner and due band |
| `CT_P1_Stockout_Risk_Detail` | Tabular | `FACT_CT_Inventory_Risk` | item, stock, forecast, safety requirement, inbound, shortage, days cover, cost and severity |
| `CT_P1_Menu_Impact_Detail` | Tabular | `FACT_CT_Menu_Impact` | ingredient, menu item, severity, forecast menu quantity, allocated sales at risk |
| `CT_P1_Expiry_Risk_Detail_Demo` | Tabular | `FACT_CT_Expiry_Risk` | outlet, item, batch, receipt date, GRN, PO, vendor, receipt-source status, item closing quantity, FIFO tranche, expected consumption, quantity/value at risk, estimated date, severity and method |
| `CT_P1_Vendor_PO_Risk` | Tabular | `FACT_CT_Risky_PO` | PO, vendor, expected date, remaining quantity, liability, severity |

For `CT_P1_Action_Center`, filter out green rows and sort:

1. Severity rank descending
2. Total risk value descending
3. Due band ascending

Enable **View Underlying Data**.

## Page 1 Layout

```text
Row 1: five KPI widgets
Row 2: India risk map (7 columns) | risk priority stack (5 columns)
Row 3: action center (12 columns)
Row 4: stockout detail (6) | menu impact (6)
Row 5: expiry demo detail (6) | vendor/PO risk (6)
```

# Page 2 - Procurement, Vendor & Capital Control

## KPI Widgets

| Report | Source | Measure |
| --- | --- | --- |
| `CT_P2_KPI_Monthly_Purchase` | `SUM_CT_Procurement_Funnel` | sum ordered value |
| `CT_P2_KPI_Closing_Inventory` | `SUM_CT_SCM_Monthly` | sum closing stock value |
| `CT_P2_KPI_Open_PO_Liability` | `SUM_CT_Procurement_Funnel` | sum pending value |
| `CT_P2_KPI_Working_Capital` | `SUM_CT_SCM_Monthly` | sum closing stock value + sum open PO value |
| `CT_P2_KPI_Open_PO_Count` | `SUM_CT_Procurement_Funnel` | sum open PO count |
| `CT_P2_KPI_Fill_Rate` | `FACT_CT_PO_Receipt_Line` | PO Fill Rate % |
| `CT_P2_KPI_OTIF` | `FACT_CT_PO_Receipt_Line` | Formula demo only; production blocked by sparse PO-to-GRN linkage |

Label monthly purchase as **Ordered Gross Value** until ABNAH approves ordered,
received or invoiced value as the production basis.

## Procurement Flow

Report: `CT_P2_Procurement_Funnel`

- Type: Funnel
- Source: `SUM_CT_Procurement_Funnel`
- Stage values:
  - Ordered: sum ordered value
  - Processed: sum processed value
  - Pending: sum pending value
  - Delayed: sum delayed value
- Tooltip: PO count and open PO count

If the report designer cannot use four measure names as stages, create a small
four-row reporting table from the same summary or use a grouped horizontal bar.
Do not use an unsupported custom chart.

## Vendor And PO Reports

| Report | Type | Source | Configuration |
| --- | --- | --- | --- |
| `CT_P2_PO_Status_Distribution` | Stacked bar | `FACT_CT_Purchase_Order` | X: PO status; Y: distinct PO count and open liability |
| `CT_P2_Pending_By_Vendor` | Horizontal bar | `SUM_CT_Procurement_Funnel` | Y: vendor; X: pending value; sort descending |
| `CT_P2_Pending_Ingredient_Risk` | Tabular | `FACT_CT_Risky_PO` | PO, vendor, ingredient, remaining quantity/value, expected date and severity; link the ingredient drill to Page 1 menu impact |
| `CT_P2_Expected_Delivery_Breach` | Tabular | `FACT_CT_Purchase_Order` | filter delayed flag=1; show PO, vendor, item, expected date, remaining qty/value |
| `CT_P2_Vendor_Performance_Matrix` | Bubble | `FACT_CT_PO_Receipt_Line` | Group by vendor; X: Vendor OTIF % aggregate formula; Y: average Eligible Lead Time Deviation Days; size: sum open PO value; text: vendor |
| `CT_P2_Vendor_Scorecard` | Tabular | `FACT_CT_PO_Receipt_Line` | Group by vendor; purchase, open liability, Vendor OTIF %, PO Fill Rate %, average eligible lead deviation and delayed lines |
| `CT_P2_Ingredient_Price_Trend` | Line | `FACT_CT_Purchase_Receipt` | X: source period; Y: weighted unit price; color: item; vendor as user filter |
| `CT_P2_Vendor_Price_Comparison` | Grouped bar | `FACT_CT_Purchase_Receipt` | X: vendor; Y: weighted unit price; require one item and one UOM |
| `CT_P2_Top_Price_Movement` | Divergent or horizontal bar | `SUM_CT_Price_Movement` | Y: combined outlet + vendor + item + UOM label; X: price change%; color positive/negative; sort absolute change |
| `CT_P2_Inventory_Value` | Stacked bar | `STD_CT_Inventory_Snapshot` | X: outlet; Y: closing value; color: category |
| `CT_P2_High_Value_Slow_Stock` | Tabular | `FACT_CT_Inventory_Risk` | closing value, days cover, forecast demand and severity; sort closing value descending then days cover descending |
| `CT_P2_Observed_Wastage` | Column | `SUM_CT_Financial_Leakage` | X: period; Y: observed wastage value |
| `CT_P2_Expiry_Exposure_Demo` | Column | `FACT_CT_Expiry_Risk` | X: period; Y: expiry risk value; subtitle must state synthetic estimate |

Build the two cross-outlet vendor performance reports from Query 24, not by
averaging Query 30 percentages. Query 30 remains valid when outlet is shown as
an explicit row/group or exactly one outlet is selected.

Vendor return rate and vendor-return leakage are intentionally omitted while
`Enterprise Stock Return` remains header-only. Do not display `0%` or `INR 0`
as a performance result; restore these measures only after populated return
evidence passes the PO/GRN/item linkage check.

Keep OTIF and lead-time deviation visibly marked as synthetic formula
demonstrations. Do not present them as feasible actual-data KPIs until PO number
coverage in Enterprise Entry materially improves beyond the audited 2 of 562
rows.

Do not add a standing-PO tracker until standing and release PO identifiers are
available.

## Page 2 Layout

```text
Row 1: seven KPI widgets
Row 2: procurement funnel (5) | vendor performance matrix (7)
Row 3: PO status (4) | pending by vendor (4) | expected breach (4)
Row 4: pending ingredient risk (6) | vendor price comparison (6)
Row 5: vendor scorecard (12)
Row 6: price trend (7) | top price movement (5)
Row 7: inventory value (6) | high-value/ageing stock (6)
Row 8: observed wastage (6) | expiry exposure demo (6)
```

# Page 3 - Consumption Variance & Menu Profitability

## KPI Widgets

| Report | Source | Measure |
| --- | --- | --- |
| `CT_P3_KPI_Net_Sales` | `FACT_CT_Menu_Profitability` | Net Sales |
| `CT_P3_KPI_Quantity_Sold` | `FACT_CT_Menu_Profitability` | Quantity Sold |
| `CT_P3_KPI_Theoretical_COGS` | `FACT_CT_Menu_Profitability` | Theoretical COGS |
| `CT_P3_KPI_Consumption_Leakage` | `FACT_CT_Consumption_Variance` | Consumption Leakage Value |
| `CT_P3_KPI_Menu_Gross_Margin` | `FACT_CT_Menu_Profitability` | Menu Gross Margin % |

Use value, not a mixed-UOM total quantity, for the all-item leakage widget.

## Consumption Reports

| Report | Type | Source | Configuration |
| --- | --- | --- | --- |
| `CT_P3_Consumption_Bridge` | Combination | `FACT_CT_Actual_Consumption` | Require one UOM; X: period; bars: opening, receipt, transfer in, signed transfer out, signed return, signed closing; line: calculated actual consumption |
| `CT_P3_Theoretical_Consumption_Detail` | Tabular | `FACT_CT_Theoretical_Consumption` | outlet, ingredient, theoretical quantity/value, UOM and average cost |
| `CT_P3_Actual_vs_Theoretical` | Grouped bar | `FACT_CT_Consumption_Variance` | X: ingredient; Y: actual qty and theoretical qty; require one UOM filter |
| `CT_P3_Consumption_Leakage_Rank` | Horizontal bar | `FACT_CT_Consumption_Variance` | Y: ingredient; X: leakage value; sort descending |
| `CT_P3_Low_Consumption_Check` | Tabular | `FACT_CT_Consumption_Variance` | filter low consumption qty>0; show outlet, ingredient, actual, theoretical, delta and UOM |

Title the last report as a **data/process check**, not a favorable saving.

## Menu Profitability Reports

| Report | Type | Source | Configuration |
| --- | --- | --- | --- |
| `CT_P3_Menu_BCG` | Bubble | `SUM_CT_Menu_Profitability` | Keep outlet as an explicit grouping; X: sold qty; Y: gross margin%; size: net sales; text: outlet + menu item; color: quadrant |
| `CT_P3_Menu_COGS_Detail` | Tabular | `FACT_CT_Menu_Profitability` | menu item, sold quantity, theoretical cost per unit, COGS, net sales and margin |
| `CT_P3_Menu_Margin_Rank` | Horizontal bar | `SUM_CT_Menu_Profitability` | Y: menu item; X: gross margin value; tooltip COGS and margin% |
| `CT_P3_Sales_Trend` | Line | `FACT_CT_Sales` | X: sales date; Y: net sales and sold qty |
| `CT_P3_Category_Contribution` | Stacked bar or ring | `FACT_CT_Menu_Profitability` | category contribution to net sales |
| `CT_P3_Top_Slow_Menu_Ranking` | Horizontal bar | `SUM_CT_Menu_Profitability` | menu item ranked by selected sold quantity, net sales, COGS or margin metric |
| `CT_P3_Outlet_Item_Heatmap` | Heat map | `FACT_CT_Menu_Profitability` | X: menu item or category; Y: outlet; color: net sales or sold qty |

BCG thresholds in the synthetic query are demo thresholds. Move them to approved
variables or formula rules before production publication.

The supplied workbook requests a veg/non-veg split. Do not build it yet because
the active profitability fact has no approved veg/non-veg classification.
Restore that visual only after an exact menu-master flag is validated.

## Page 3 Layout

```text
Row 1: five KPI widgets
Row 2: consumption bridge (7) | actual vs theoretical (5)
Row 3: theoretical consumption detail (6) | low-consumption check (6)
Row 4: leakage rank (6) | menu COGS detail (6)
Row 5: menu BCG (7) | menu margin rank (5)
Row 6: sales trend (4) | category contribution (4) | top/slow ranking (4)
Row 7: outlet-item heatmap (12)
```

# Page 4 - SCM Descriptive Explorer & Data Quality

## Descriptive KPI Widgets

| Report | Source | Measure |
| --- | --- | --- |
| `CT_P4_KPI_Closing_Stock` | `SUM_CT_SCM_Monthly` | closing stock value |
| `CT_P4_KPI_Open_PO` | `SUM_CT_SCM_Monthly` | open PO value |
| `CT_P4_KPI_Net_Sales` | `SUM_CT_SCM_Monthly` | net sales |
| `CT_P4_KPI_Actual_Consumption` | `SUM_CT_SCM_Monthly` | actual consumption value |
| `CT_P4_KPI_Consumption_Variance` | `FACT_CT_Consumption_Variance` | Signed Consumption Variance Value; keep leakage as a separate tooltip/control |
| `CT_P4_KPI_Quantity_Sold` | `FACT_CT_Sales` | sum sold quantity |
| `CT_P4_KPI_Active_Menu_Items` | `FACT_CT_Sales` | distinct menu item code |
| `CT_P4_KPI_Open_PO_Lines` | `FACT_CT_Purchase_Order` | count lines with `is_open_po = 1`; show pending quantity only in UOM-filtered detail |
| `CT_P4_KPI_GRN_Value` | `FACT_CT_Purchase_Receipt` | sum receipt total |
| `CT_P4_KPI_Active_Vendors` | `FACT_CT_Purchase_Order` | distinct vendor name in the selected period/outlet |

These are descriptive totals. Do not attach action severity to high values by
default.

## Trend And Explorer

| Report | Type | Source | Configuration |
| --- | --- | --- | --- |
| `CT_P4_SCM_Monthly_Trend` | Combination | `SUM_CT_SCM_Monthly` | X: period; bars: stock and open PO; lines: sales and actual consumption |
| `CT_P4_Consumption_Variance_Trend` | Bar/line | `FACT_CT_Consumption_Variance` | X: period; Y: signed variance value and leakage value |
| `CT_P4_Descriptive_Explorer` | Pivot or tabular | `SUM_CT_SCM_Monthly` plus drill reports | period, outlet, metric, value; enable export |
| `CT_P4_Sales_Explorer` | Tabular | `FACT_CT_Sales` | date, outlet, menu item/category, sold quantity, net sales and realized unit price |
| `CT_P4_Item_Explorer` | Tabular | `FACT_CT_Inventory_Risk` | outlet, item, category, stock, cost, forecast, PO and severity |
| `CT_P4_PO_Explorer` | Tabular | `FACT_CT_PO_Receipt_Line` | PO, vendor, item, ordered, received, remaining, expected, actual and status |
| `CT_P4_GRN_Explorer` | Tabular | `FACT_CT_Purchase_Receipt` | receipt date, GRN, PO, vendor, item, received quantity, subtotal, tax/total and return-source status |
| `CT_P4_Vendor_Explorer` | Tabular | `SUM_CT_Vendor_Scorecard` | vendor, ordered/received value, open liability, fill, eligible OTIF, lead deviation and delayed lines |
| `CT_P4_Expiry_Explorer_Demo` | Tabular | `FACT_CT_Expiry_Risk` | outlet, item, scenario inputs, estimated date, quantity/value and production-use label |

## Data-Quality Tiles

Create six KPI widgets from `FACT_CT_Data_Quality_Exception`. For each widget,
use `sum(exception_count)` and filter one `exception_type`:

1. `NEGATIVE_STOCK`
2. `ZERO_STOCK_WITH_DEMAND`
3. `SOLD_ITEM_MISSING_RECIPE`
4. `OPERATIONAL_ITEM_MISSING_MASTER`
5. `UOM_MISMATCH_WITHOUT_CONVERSION`
6. `OPEN_PO_MISSING_EXPECTED_DELIVERY`

Create `CT_P4_Data_Quality_Detail` as a tabular report with:

- exception type
- period
- outlet
- record key
- item code
- PO/reference number
- definition

Enable underlying data and export. Clicking a tile must filter this table to the
same exception type.

## Page 4 Layout

```text
Row 1: sales, sold quantity, menu item, stock and open-PO KPI widgets
Row 2: consumption, variance, pending quantity, GRN and vendor KPI widgets
Row 3: monthly trend (7) | variance trend (5)
Row 4: six data-quality tiles
Row 5: data-quality detail (12)
Row 6: sales explorer (6) | item explorer (6)
Row 7: PO explorer (4) | GRN explorer (4) | vendor explorer (4)
Row 8: descriptive/export explorer (12)
Row 9: expiry scenario explorer (12)
```

# Supplied Reference Coverage

| Reference requirement | Delivery decision |
| --- | --- |
| Four pages, KPI strips, map, funnel, vendor matrix, price trend, consumption bridge, BCG, heatmap and data-quality explorer | Build with native Zoho reports and dashboard tabs |
| Expiry map/detail/value | Build from Query 38 as a synthetic batch-linked demonstrator scenario with a permanent source warning; it is an at-risk tranche register, not a complete POSIST batch ledger |
| Multi-outlet geography and new/matured filters | Build from Query 37 for the three synthetic outlets; replace before production |
| OTIF and lead-time deviation | Formula demonstration only until actual PO-to-GRN linkage improves |
| Whole-page Stockout/Expiry/Vendor source toggle | Keep Query 27 stockout, Query 38 expiry and vendor/PO reports separate in native Zoho; exact source-switching needs a custom embedded shell |
| Standing PO tracker | Defer because standing/release PO identifiers are unavailable |
| Veg/non-veg split | Defer because no approved classification is present in the active fact |
| Vendor return rate | Defer because Enterprise Stock Return is header-only |
| Exact expiry or batch ageing | Defer until a populated expiry/batch source is validated |

# Dashboard Implementation Sequence

Build in this order even though the final tab order starts with Page 1:

1. **Foundation**: import the two new AUX files, replace Query 27, create
   Queries 37-38, create lookups, formulas and the two global filters.
2. **Page 4**: build descriptive totals, trends and data-quality drill tables.
   This proves the model before any action-oriented interpretation.
3. **Page 3**: build menu sales/margin first, then theoretical versus actual
   consumption, then variance and BCG.
4. **Page 2**: build PO and receipt totals first, then funnel, pending/delay,
   vendor performance and price movement.
5. **Page 1**: build the stockout action table first, then commercial menu
   impact, the separate expiry demo detail, risky PO detail and finally the
   stockout map.
6. **Assembly**: place the saved reports into the four final tabs and test
   global/page filters.

At every page gate:

1. Reconcile the unfiltered `month_03` total to the corresponding truth CSV.
2. Test OUT001, OUT002 and OUT003 separately.
3. Clear all page filters and confirm the two global filters work on mapped
   components while excluded trends and Query 34 remain unchanged.
4. Click each report-as-filter component and confirm it affects only the
   intended reports.
5. Export the detail behind one KPI and trace it to the Query Table.

Do not begin final styling until all four page gates pass.

# Assemble The Four-Tab Dashboard

1. Click **Create**.
2. Select **New Dashboard**.
3. Name it `ABNAH Supply Chain Control Tower v2`.
4. Add four tabs with the exact page names.
5. Drag the saved reports into each tab using the layouts above.
6. Keep the KPI row at a stable height.
7. Give tables more vertical space than charts.
8. Enable smart alignment.
9. Do not place explanatory text cards between working reports.
10. Save after completing each tab.

Zoho supports multi-tab dashboards and common user filters. Current filter
documentation:
https://www.zoho.com/analytics/help/dashboard/filter.html

## Global Filters

Create only two dashboard-global controls. Add each control once, then customize
which saved reports respond to it. **Do not map either filter blindly to every
component.**

| Filter | Configuration | Application |
| --- | --- | --- |
| As-of source period | Single-select; default `month_03`; map by `source_period_code` or the equivalent forecast period | Apply to current-state KPI, action and detail reports. Do not apply it to the designated historical trend reports or Query 34 data-quality reports. |
| Outlet | Multi-select; default All; map by `outlet_code`, not display name | Apply to reports with a genuine outlet-grain key, including historical trends. Do not apply it to Query 34 because some model-wide controls deliberately use `outlet_code = 'ALL'`. |

Steps:

1. Open the dashboard in edit mode.
2. Open **User Filters**.
3. Add `source_period_code`.
4. Map it to current-state reports using the exact exceptions below.
5. Make it single-select and set `month_03` as the default.
6. Add outlet and map `outlet_code` only to reports with a genuine outlet key.
7. Select **Make User Filters Global** and choose **Make Common Filters as
   Global**. Do not choose **Make Current Tab Filters as Global**, because that
   option would remove the tab-specific filter design.
8. For each saved report, open dashboard **Options**, keep **Apply Dashboard
   Filters** enabled, select **Customize**, and map only the global filters
   allowed by the table below.
9. Test every mapped component under each outlet and period before adding page
   filters. Confirm that excluded trend and data-quality reports remain
   intentionally unchanged.

Do not make category, vendor, PO status, risk type, severity, UOM, region or
new/matured global. Those fields are absent or have different meanings in some
facts and will blank unrelated widgets.

### Exact Global-Filter Exceptions

| Tab | As-of source period | Outlet |
| --- | --- | --- |
| Page 1 | Apply to every Page 1 component. | Apply to every Page 1 component through `outlet_code`. |
| Page 2 | Apply to current KPIs and current PO/vendor/inventory reports. Exclude `CT_P2_Ingredient_Price_Trend`, `CT_P2_Observed_Wastage` and `CT_P2_Expiry_Exposure_Demo` so they retain all three periods. | Apply to every Page 2 report that exposes `outlet_code`. |
| Page 3 | Apply to current KPIs, comparison, leakage, profitability, BCG, contribution, ranking and heat-map reports. Exclude `CT_P3_Consumption_Bridge` and `CT_P3_Sales_Trend`. | Apply to every Page 3 report through `outlet_code`. |
| Page 4 | Apply to current KPI and explorer reports. Exclude `CT_P4_SCM_Monthly_Trend`, `CT_P4_Consumption_Variance_Trend`, all six Query 34 quality tiles and `CT_P4_Data_Quality_Detail`. | Apply to Page 4 current, trend and explorer reports that have a genuine outlet key. Exclude all Query 34 quality reports. |

For each excluded historical chart, optionally add a tab-local **Trend
periods** multi-select mapped only to those historical charts, with
`month_01`, `month_02` and `month_03` selected by default. The global As-of
period remains `month_03` for current-state cards and details.

Query 34 contains both outlet/period rows and model-wide controls encoded with
`source_period_code = 'ALL'` and `outlet_code = 'ALL'`. Mapping either global
filter to Query 34 would hide those model-wide checks. Keep its six tiles and
detail table outside both global-filter mappings.

## Page And Report Filter Matrix

Create these controls only on the named tab. For every control, open each
component's dashboard **Options > Apply Dashboard Filters > Customize** and
map only the compatible reports listed below. A control that is not mapped to a
component must leave that component unchanged.

| Scope | Tab-local user filter | Apply only to | Do not map to |
| --- | --- | --- | --- |
| Page 1 | Region; new/matured | Query 27 stockout, Query 28 menu impact, Query 36 risky PO and Query 38 expiry components through the Query 37 outlet lookup | Reports without the outlet lookup |
| Page 1 | Stockout severity | Query 27 stockout map, priority, action and detail plus Query 28 stockout menu impact | Query 38 expiry severity or Query 36 vendor/PO severity |
| Page 1 | Action owner | Query 27 action-center and stockout action/detail reports | Menu impact, expiry and risky-PO reports |
| Page 1 | Ingredient category | Query 27, Query 28, Query 36 and Query 38 reports that resolve through the item/ingredient lookup | Reports without an ingredient key |
| Page 2 | Region | Every Page 2 component with the Query 37 outlet lookup | Components without an outlet key |
| Page 2 | Vendor | PO, receipt, risky-PO, procurement funnel, vendor scorecard and price reports sourced from Queries 22, 23, 24, 29, 30, 31 and 36 | Inventory, working-capital, stock-risk and wastage reports |
| Page 2 | Ingredient category; item | PO/receipt line, risky-PO, price, inventory-value and high-value stock reports with an item lookup | Procurement funnel and vendor scorecard summaries that have no item grain |
| Page 2 | PO status | `CT_P2_PO_Status_Distribution` and `CT_P2_Expected_Delivery_Breach` from Query 22 | Funnel, vendor, price, inventory and fixed-open risky-PO reports |
| Page 3 | Region | Every Page 3 component through its outlet lookup | Reports without an outlet key |
| Page 3 | Menu category; menu item | Sales, menu-profitability, BCG, contribution, ranking and heat-map reports from Queries 18, 25 and 32 | Ingredient consumption and variance reports |
| Page 3 | Ingredient category; ingredient | Theoretical, actual, variance, leakage and low-consumption reports from Queries 19, 20 and 21 | Sales and menu-profitability reports |
| Page 3 | Canonical UOM | Consumption bridge, theoretical detail, actual-versus-theoretical and low-consumption quantity reports | Currency leakage, sales, margin, BCG and menu reports |
| Page 4 | Region | Current/trend/explorer reports with the Query 37 outlet lookup | Every Query 34 data-quality tile and detail report |
| Page 4 | Ingredient item | Consumption variance, inventory, PO-line, GRN and expiry ingredient reports | Sales/menu-item and vendor-summary reports |
| Page 4 | Menu item | Sales explorer and menu-sales reports | Ingredient, inventory, PO, GRN and data-quality reports |
| Page 4 | Vendor | PO, GRN and vendor explorer reports sourced from Queries 22, 23, 24 and 30 | Sales, consumption, inventory and data-quality reports |
| Page 4 | Exception type | `CT_P4_Data_Quality_Detail` only | The six quality tiles, because each tile already has a fixed exception type |

Region and new/matured come from the lookup to
`37_dim_ct_outlet_enriched.sql`. They are synthetic demonstrator attributes.

Do not create **Explorer source** as a common user filter. Native Zoho cannot
use one field to switch unrelated sales, item, PO, GRN and vendor report
sources. Keep those explorer reports as separate visible sections.

### Risk Toggle Boundary

The supplied HTML uses one toggle to replace Stockout, Expiry and Vendor
content. Native Zoho user filters cannot safely switch unrelated report data
sources. Query 27 supplies stockout map/action views, Query 38 supplies the
visibly synthetic expiry views, and the vendor/PO facts supply vendor risk.
Keep those sections visibly separate. A true whole-page source-switching toggle
requires a custom embedded shell and is outside the native dashboard.

### Filters That Must Stay Inside Reports

- Keep `risk_severity <> GREEN` inside action reports so clearing a user filter
  cannot turn the action page into a healthy-item listing.
- Keep `is_open_po = 1` and `delayed_po_flag = 1` inside their PO reports; PO
  status remains a page user filter for narrower analysis.
- Keep one-UOM enforcement inside quantity charts. Do not apply a UOM filter to
  currency widgets.
- Keep each data-quality tile's exception type fixed. Clicking the tile may
  filter the shared detail table, but a global exception filter must not alter
  unrelated pages.
- Keep `is_estimated = 1` and the demo source label visible on every expiry
  report.

## Report-As-Filter Behavior

Enable **Use as Filter** for:

- Page 1 risk map and priority stack
- Page 2 vendor matrix and price movement
- Page 3 menu BCG and heatmap
- Page 4 data-quality tiles

Keep the user able to clear the selection. Do not enable report filtering on
every component; that creates unpredictable cross-filter chains.

## RAG And Styling

Use one consistent severity palette:

| State | Color |
| --- | --- |
| Purple | `#6C3B8C` |
| Red | `#C63D3D` |
| Amber | `#D49A22` |
| Green | `#2E7D5B` |
| Grey/no data | `#7C8793` |

Use a neutral dashboard background and reserve severity colors for actual
states. Do not color descriptive Page 4 values red merely because they are
large.

## JavaScript Boundary

Do not attempt to inject JavaScript into the native dashboard to recolor or
rebuild charts. Use native chart settings and conditional formatting first.

Zoho's JavaScript API controls reports embedded in an external application:
https://www.zoho.com/analytics/js-api/

If a later custom portal is approved, embed the published dashboard there and
use the API for host-controlled filters, refresh and export. That is a separate
delivery from the native Zoho dashboard.
