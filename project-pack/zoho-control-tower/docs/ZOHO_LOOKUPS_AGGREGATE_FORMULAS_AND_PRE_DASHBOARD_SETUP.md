# ABNAH Control Tower v2 - Lookups, Formulas And Pre-Dashboard Setup

## Purpose

Use this runbook after all 38 Query Tables have executed and been saved, but
before creating any dashboard reports.

This is the authoritative pre-dashboard configuration guide for the current
synthetic ABNAH Control Tower v2 build. It covers:

- parent-key and data-type checks;
- every lookup relationship required by the dashboard model;
- SQL-derived physical dashboard columns;
- the four reusable aggregate formulas that genuinely require report-time
  aggregation;
- direct report aggregations that do not need custom formulas;
- filter and grain restrictions;
- table-specific setup for all 38 Query Tables;
- reconciliation checks before dashboard construction.

If all 38 Query Tables, lookups and the earlier formula catalog are already
complete, do not repeat this runbook. Continue from
`ZOHO_CURRENT_WORKSPACE_MIGRATION.md`.

The physical Zoho table names in this build are the numbered SQL filenames,
including the `.sql` suffix. For example:

```text
27_fact_ct_inventory_risk.sql
```

Do not substitute the logical label `FACT_CT_Inventory_Risk` when selecting a
table in Zoho.

## Current Build Boundary

This runbook applies to:

```text
14 imported landing tables
38 successfully saved Query Tables
3 synthetic outlets
3 source periods
90 sales dates
```

The expiry layer is a synthetic estimate because POSIST batch-expiry evidence
is unavailable. Vendor returns remain unavailable because the captured Stock
Return report has no operational rows. Neither limitation may be represented
as actual ABNAH performance.

Every Query 38 report title or subtitle must contain:

```text
Synthetic demo estimate - no POSIST batch/expiry source
```

## Required Execution Order

Complete the work in this exact order:

1. Freeze and back up the 38 successful Query Tables.
2. Validate dimension uniqueness and key data types.
3. Create the required lookup relationships.
4. Verify the SQL-derived dashboard columns.
5. Create the four required aggregate formulas.
6. Validate direct aggregations and table-specific restrictions.
7. Reconcile formulas to the synthetic truth reference.
8. Mark the final readiness checklist complete.
9. Only then start creating dashboard reports.

Do not create dashboard reports while lookups or formulas are only partially
configured. A partially configured model can cause Zoho to use inconsistent
filter paths across reports.

# Phase 0 - Freeze The Completed Query Layer

## Step 0.1 - Confirm The Query Baseline

In the Zoho workspace, confirm:

- Query Tables `01` through `38` exist;
- every table has been saved under its exact numbered `.sql` filename;
- each table opens in View Mode without a parser or missing-column error;
- Query 27 is the current stockout-only version;
- Query 37 is the enriched outlet dimension;
- Query 38 is the synthetic expiry-risk fact;
- no older unnumbered duplicate is being used by a new report.

## Step 0.2 - Record A Rollback Point

Before changing column types:

1. Export or duplicate the workspace.
2. Record the backup date and owner.
3. Use the SQL files from the current final package.
4. If the five dashboard-support columns below are absent, replace and save
   Queries `20`, `21`, `24`, `31` and `33` from the current package in that
   order.

This correction is required because Zoho's direct KPI Widget editor asks for a
physical **Data Column**. Aggregate formulas are report-layer metrics and are
not reliable substitutes for physical row-level fields in that dropdown.

# Phase 1 - Validate Parent Tables And Data Types

## Canonical Parent Tables

Use only these five tables as lookup parents:

| Dimension role | Physical Zoho parent table | Parent key | Expected synthetic rows |
| --- | --- | --- | ---: |
| Outlet | `37_dim_ct_outlet_enriched.sql` | `outlet_code` | 3 |
| Ingredient/item | `14_dim_ct_item.sql` | `item_code` | 43 |
| Menu item | `15_dim_ct_menu_item.sql` | `menu_item_code` | 110 |
| Vendor | `16_dim_ct_vendor.sql` | `vendor_name` | 70 |
| Calendar date | `12_dim_ct_date.sql` | `calendar_date` | 90 |

Do not use `13_dim_ct_outlet.sql` as the dashboard lookup parent. Query 37
supersedes it and adds region, city, market area, coordinates and
new/matured status.

## Step 1.1 - Verify Parent-Key Uniqueness

For each parent table:

1. Open the table in View Mode.
2. Confirm the expected row count above.
3. Create a temporary Summary View or Pivot View.
4. Put the parent key on Rows.
5. Add `count(parent key)` as the measure.
6. Filter the count to values greater than `1`.
7. Confirm that no records remain.
8. Check that the parent key has no null or blank value.
9. Delete the temporary validation view after recording the result.

Stop if a duplicate or blank parent key exists. Do not create a lookup until
the parent is unique.

## Step 1.2 - Verify Key Data Types

Before converting a child column to a lookup, confirm that its type matches the
parent:

| Key | Required type |
| --- | --- |
| `outlet_code` | Plain Text |
| `item_code` | Plain Text |
| `ingredient_code` | Plain Text |
| `menu_item_code` | Plain Text |
| Sales fact `item_code` | Plain Text |
| `vendor_name` | Plain Text |
| `calendar_date` and `sales_date` | Date |

If a child key has a different type:

1. Correct the ordinary column data type before creating the lookup.
2. Recheck a sample of values after conversion.
3. Create the lookup only after the types match.

Zoho does not permit an ordinary data-type change while the column is a lookup.
Remove the lookup first if a later type correction is required.

## Step 1.3 - Verify Query 38 Types

Query 38 deliberately uses direct projection to avoid Zoho parser failures.
Confirm these types manually:

| Query 38 fields | Required type |
| --- | --- |
| `as_of_date`, `receipt_date`, `estimated_expiry_date` | Date |
| `latitude`, `longitude` | Decimal Number |
| Quantity and value fields | Decimal Number or Currency as appropriate |
| `shelf_life_days_assumption`, `days_to_expiry`, `risk_severity_rank` | Number |
| Identifiers, statuses and evidence fields | Plain Text |

Do not change `expiry_qty_at_risk` into a currency field. Do not change
`expiry_risk_value` into a quantity field.

# Phase 2 - Create Lookup Relationships

## How To Convert An Existing Column To A Lookup

Repeat these steps for every relationship listed in the matrices below:

1. Open the child Query Table in Zoho.
2. Locate the child key column.
3. Right-click the column or use **More**.
4. Select **Change to Lookup Column**.
5. Select the exact numbered parent table.
6. Select the exact parent key.
7. Confirm and save.
8. Verify that Zoho displays the lookup indicator on the child column.
9. Open a temporary tabular report and add one parent attribute to prove the
   relationship resolves.

Use **Change to Lookup Column** for these existing fields. Do not add a second
duplicate lookup column.

## 2A - Outlet Lookups

Parent:

```text
37_dim_ct_outlet_enriched.sql.outlet_code
```

Convert `outlet_code` to this lookup on:

| Order | Child table |
| ---: | --- |
| 05 | `05_std_ct_inventory_snapshot.sql` |
| 18 | `18_fact_ct_sales.sql` |
| 19 | `19_fact_ct_theoretical_consumption.sql` |
| 20 | `20_fact_ct_actual_consumption.sql` |
| 21 | `21_fact_ct_consumption_variance.sql` |
| 22 | `22_fact_ct_purchase_order.sql` |
| 23 | `23_fact_ct_purchase_receipt.sql` |
| 24 | `24_fact_ct_po_receipt_line.sql` |
| 25 | `25_fact_ct_menu_profitability.sql` |
| 26 | `26_fact_ct_forecast_ingredient_demand.sql` |
| 27 | `27_fact_ct_inventory_risk.sql` |
| 28 | `28_fact_ct_menu_impact.sql` |
| 29 | `29_sum_ct_procurement_funnel.sql` |
| 30 | `30_sum_ct_vendor_scorecard.sql` |
| 31 | `31_sum_ct_price_movement.sql` |
| 32 | `32_sum_ct_menu_profitability.sql` |
| 33 | `33_sum_ct_scm_monthly.sql` |
| 35 | `35_sum_ct_financial_leakage.sql` |
| 36 | `36_fact_ct_risky_po.sql` |
| 38 | `38_fact_ct_expiry_risk.sql` |

Do not create this lookup on Query 34. That exception table intentionally
contains `outlet_code = 'ALL'` for model-wide exceptions.

## 2B - Ingredient/Item Lookups

Parent:

```text
14_dim_ct_item.sql.item_code
```

Convert `item_code` to this lookup on:

| Order | Child table |
| ---: | --- |
| 05 | `05_std_ct_inventory_snapshot.sql` |
| 19 | `19_fact_ct_theoretical_consumption.sql` |
| 20 | `20_fact_ct_actual_consumption.sql` |
| 21 | `21_fact_ct_consumption_variance.sql` |
| 22 | `22_fact_ct_purchase_order.sql` |
| 23 | `23_fact_ct_purchase_receipt.sql` |
| 24 | `24_fact_ct_po_receipt_line.sql` |
| 26 | `26_fact_ct_forecast_ingredient_demand.sql` |
| 27 | `27_fact_ct_inventory_risk.sql` |
| 31 | `31_sum_ct_price_movement.sql` |
| 36 | `36_fact_ct_risky_po.sql` |
| 38 | `38_fact_ct_expiry_risk.sql` |

Query 28 uses a differently named item key:

```text
28_fact_ct_menu_impact.sql.ingredient_code
    -> 14_dim_ct_item.sql.item_code
```

Do not create an item lookup on Query 34. Blank item keys are valid for some
exception types, and missing-master rows must remain visible rather than being
forced through the parent dimension.

## 2C - Menu-Item Lookups

Parent:

```text
15_dim_ct_menu_item.sql.menu_item_code
```

Create these relationships:

| Child table | Child key | Important meaning |
| --- | --- | --- |
| `18_fact_ct_sales.sql` | `item_code` | This sales key is a menu item, not an ingredient |
| `25_fact_ct_menu_profitability.sql` | `menu_item_code` | Menu profitability grain |
| `26_fact_ct_forecast_ingredient_demand.sql` | `menu_item_code` | Forecast menu item |
| `28_fact_ct_menu_impact.sql` | `menu_item_code` | Impacted menu item |
| `32_sum_ct_menu_profitability.sql` | `menu_item_code` | Menu BCG summary |

Do not connect `18_fact_ct_sales.sql.item_code` to the ingredient dimension.

## 2D - Vendor Lookups

Parent:

```text
16_dim_ct_vendor.sql.vendor_name
```

Convert `vendor_name` to this lookup on:

| Order | Child table |
| ---: | --- |
| 22 | `22_fact_ct_purchase_order.sql` |
| 23 | `23_fact_ct_purchase_receipt.sql` |
| 24 | `24_fact_ct_po_receipt_line.sql` |
| 29 | `29_sum_ct_procurement_funnel.sql` |
| 30 | `30_sum_ct_vendor_scorecard.sql` |
| 31 | `31_sum_ct_price_movement.sql` |
| 36 | `36_fact_ct_risky_po.sql` |

Query 38 may contain a blank vendor on synthetic opening-stock fallback rows.
Keep `vendor_name` as plain text for the first dashboard build. It can be
converted to the vendor lookup later only after confirming that Zoho preserves
the blank fallback rows.

## 2E - Date Lookup

Parent:

```text
12_dim_ct_date.sql.calendar_date
```

Create:

```text
18_fact_ct_sales.sql.sales_date
    -> 12_dim_ct_date.sql.calendar_date
```

This relationship supports calendar attributes for daily sales trends. Do not
create date lookups for PO expected dates, receipt dates or estimated expiry
dates because those dates can extend beyond the sales-derived calendar range.

## Relationships Not To Create

Do not create lookups for:

- `source_period_code`;
- `source_period_label`;
- `category_name` or `super_category_name`;
- `canonical_uom`;
- `po_number` or `grn_number`;
- status, risk, action or evidence fields;
- Query 34 `outlet_code` or `item_code`;
- raw landing tables;
- every standardized table merely because a matching field exists.

The dashboard common filter will map `source_period_code` across reports. It is
not a dimension lookup.

# Phase 3 - Verify SQL-Derived Physical Columns

Do not try to create these as Zoho formula columns. They now come directly from
the numbered Query Table SQL and therefore appear as selectable fields in the
report designer and KPI Widget editor.

## Step 3.1 - Apply The Dashboard-Support SQL Correction

Replace and save only these Query Tables, in this order:

1. `20_fact_ct_actual_consumption.sql`
2. `21_fact_ct_consumption_variance.sql`
3. `24_fact_ct_po_receipt_line.sql`
4. `31_sum_ct_price_movement.sql`
5. `33_sum_ct_scm_monthly.sql`

Queries `21` and `33` are listed after `20` because they depend on Query `20`.
No other Query Table needs to be re-created for this correction.

## Step 3.2 - Verify The New Columns

Open each Query Table in View Mode and confirm the exact physical columns:

| Query Table | Physical column | Dashboard use |
| --- | --- | --- |
| `20_fact_ct_actual_consumption.sql` | `bridge_transfer_out_qty` | Negative transfer-out bridge bar |
| `20_fact_ct_actual_consumption.sql` | `bridge_return_qty` | Negative return bridge bar |
| `20_fact_ct_actual_consumption.sql` | `bridge_closing_qty` | Negative closing-stock bridge bar |
| `21_fact_ct_consumption_variance.sql` | `signed_consumption_variance_value` | Signed variance KPI and trend |
| `21_fact_ct_consumption_variance.sql` | `consumption_variance_direction` | Exact Individual Values filter for over/under/matched rows |
| `24_fact_ct_po_receipt_line.sql` | `eligible_lead_time_deviation_days` | Average lead-time deviation for eligible closed lines |
| `31_sum_ct_price_movement.sql` | `price_comparison_key` | Unambiguous outlet/vendor/item/UOM label |
| `31_sum_ct_price_movement.sql` | `absolute_unit_price_change_percent` | Sort by movement magnitude |
| `31_sum_ct_price_movement.sql` | `price_movement_direction` | Increase/decrease/no-change color and filter |
| `33_sum_ct_scm_monthly.sql` | `working_capital_value` | Direct Working Capital KPI Widget |

The signed bridge columns do not replace
`calculated_actual_consumption_qty`. The signed variance is positive when
actual consumption exceeds theoretical consumption and negative when it is
below theoretical consumption.

# Phase 4 - Create Reusable Aggregate Formulas

Only the four ratio or weighted-rate metrics in this phase require Aggregate
Formulas. All sums and counts in the dashboard guide use physical columns and
the report/widget aggregation control.

An Aggregate Formula is available in the report designer, but it is not added
as a physical column to the Query Table. Therefore:

- do not search for an Aggregate Formula name in a direct KPI Widget's
  **Data Column** list;
- use a direct KPI Widget only when the guide names a physical column;
- build each Aggregate Formula KPI as a compact saved Summary View and place
  that saved report on the dashboard;
- never create a second formula just to rename a physical sum or count.

## How To Add An Aggregate Formula

For each formula below:

1. Open the specified physical Query Table.
2. Select **Add > Aggregate Formula**.
3. Enter the exact formula name.
4. Paste the formula expression.
5. Select the recommended output type.
6. Set count fields to zero decimals.
7. Set currency fields to INR with two decimals.
8. Set percentages to two decimals.
9. Save.
10. Create a temporary Summary View with no grouping and compare it with the
    validation values in Phase 8.

Aggregate formulas respond to the grouping and filters in each report. Rates
must therefore divide aggregated numerators by aggregated denominators.

## 4A - Weighted Unit Price

Table:

```text
23_fact_ct_purchase_receipt.sql
```

```text
Name: Weighted Unit Price
Formula: if(sum("received_qty") <> 0, sum("receipt_subtotal") / sum("received_qty"), null)
Type: Currency
```

Never average row unit prices. A weighted price must divide total receipt
subtotal by total received quantity.

## 4B - PO Fill Rate And OTIF

Table:

```text
24_fact_ct_po_receipt_line.sql
```

```text
Name: PO Fill Rate %
Formula: if(sum("ordered_qty") <> 0, sum("received_qty") / sum("ordered_qty") * 100, null)
Type: Percentage
```

```text
Name: Vendor OTIF %
Formula: if(sum("eligible_closed_line_flag") <> 0, sum("otif_success_flag") / sum("eligible_closed_line_flag") * 100, null)
Type: Percentage
```

Validate that the unfiltered synthetic results display approximately `83.25%`
and `51.67%`. If Zoho's selected percentage format renders `8,325%` or
`5,167%`, retain the Percentage type but remove `* 100` from the formulas.
The displayed result, not the storage convention, must be `83.25%` and
`51.67%`.

Return null when the denominator is zero. Do not convert an absent eligible
population into `0%`.

## 4C - Menu Profitability

Table:

```text
25_fact_ct_menu_profitability.sql
```

```text
Name: Menu Gross Margin %
Formula: if(sum("net_sales") <> 0, sum("gross_margin_value") / sum("net_sales") * 100, null)
Type: Percentage
```

The unfiltered synthetic result must display approximately `82.02%`. Do not
average the row-level `gross_margin_percent` column.

## 4D - Aggregate Formula Inventory Check

After completing Phase 4, the required catalog is exactly:

| Query Table | Aggregate Formula |
| --- | --- |
| `23_fact_ct_purchase_receipt.sql` | `Weighted Unit Price` |
| `24_fact_ct_po_receipt_line.sql` | `PO Fill Rate %` |
| `24_fact_ct_po_receipt_line.sql` | `Vendor OTIF %` |
| `25_fact_ct_menu_profitability.sql` | `Menu Gross Margin %` |

If additional formulas from an earlier draft already exist, they do not need
to be deleted, but do not use them in the direct KPI Widget instructions.

# Phase 5 - Direct Report Aggregations

The following fields already exist at the correct grain. Select the stated
aggregation in the report designer. Do not create redundant aggregate formulas
unless the same display label is required across many reports.

| Table | Field | Report aggregation | Restriction |
| --- | --- | --- | --- |
| `05_std_ct_inventory_snapshot.sql` | `closing_value` | Sum | One source period for current stock |
| `18_fact_ct_sales.sql` | `net_sales` | Sum | Additive |
| `18_fact_ct_sales.sql` | `sold_qty` | Sum | Additive |
| `19_fact_ct_theoretical_consumption.sql` | `theoretical_consumption_value` | Sum | Additive value |
| `20_fact_ct_actual_consumption.sql` | `calculated_actual_consumption_value` | Sum | Additive value |
| `20_fact_ct_actual_consumption.sql` | `bridge_transfer_out_qty`, `bridge_return_qty`, `bridge_closing_qty` | Sum | Single UOM only |
| `21_fact_ct_consumption_variance.sql` | `leakage_value` | Sum | Additive value |
| `21_fact_ct_consumption_variance.sql` | `signed_consumption_variance_value` | Sum | Additive signed value |
| `22_fact_ct_purchase_order.sql` | `gross_order_value` | Sum | Ordered gross basis |
| `22_fact_ct_purchase_order.sql` | `open_po_value` | Sum | Open liability |
| `23_fact_ct_purchase_receipt.sql` | `receipt_total` | Sum | Received total basis |
| `25_fact_ct_menu_profitability.sql` | `net_sales` | Sum | Additive |
| `25_fact_ct_menu_profitability.sql` | `sold_qty` | Sum | Additive |
| `25_fact_ct_menu_profitability.sql` | `theoretical_cogs` | Sum | Additive |
| `25_fact_ct_menu_profitability.sql` | `gross_margin_value` | Sum | Additive |
| `27_fact_ct_inventory_risk.sql` | `shortage_cost_value` | Sum | Stockout exposure only |
| `27_fact_ct_inventory_risk.sql` | `total_risk_value` | Sum | Same stockout-only value in current Query 27 |
| `28_fact_ct_menu_impact.sql` | `allocated_forecast_net_sales_at_risk` | Sum | Allocated field only |
| `29_sum_ct_procurement_funnel.sql` | Value fields | Sum | Do not count rows as POs |
| `30_sum_ct_vendor_scorecard.sql` | `monthly_purchase_value` | Sum | Additive value |
| `30_sum_ct_vendor_scorecard.sql` | `open_po_value` | Sum | Additive value |
| `33_sum_ct_scm_monthly.sql` | All five value measures, including `working_capital_value` | Sum | Current snapshot widgets require one period |
| `35_sum_ct_financial_leakage.sql` | `leakage_value` | Sum | Observed wastage only |
| `36_fact_ct_risky_po.sql` | `open_po_value` | Sum | Risky open liability |
| `38_fact_ct_expiry_risk.sql` | `expiry_risk_value` | Sum | Synthetic estimate only |

For counts in direct KPI Widgets, select the physical identifier and choose
**Count Distinct**. Examples are `outlet_code`, `menu_item_code`, `po_number`
and `vendor_name`. Do not search for a business label such as `Open Risky PO
Count` in the Data Column list.

Do not use row count as PO count. One PO can contain multiple item lines.

## Values That Must Not Be Aggregated Directly

Do not sum or average:

- Query 24 row flags as a percentage without the approved numerator and
  denominator formulas;
- Query 25 row `gross_margin_percent`;
- Query 28 unallocated `forecast_net_sales_at_risk`;
- Query 30 `otif_percent` or `fill_rate_percent` across outlets;
- Query 31 `unit_price_change_percent` across items or UOMs;
- Query 32 `bcg_quadrant`;
- quantities across kg, litre and pieces;
- inventory snapshots across multiple periods for a current-state KPI.

Category contribution does not need a table aggregate formula. In the category
report, use `sum(net_sales)` and configure **Show Values As > % of Total**.

# Phase 6 - Table-Specific Configuration Register

Use this register as the final pass across all 38 Query Tables.

| No. | Physical Query Table | Pre-dashboard action |
| ---: | --- | --- |
| 01 | `01_std_ct_sales_item.sql` | Upstream only. No lookup or formula required. |
| 02 | `02_std_ct_recipe.sql` | Upstream only. Preserve menu-item to ingredient recipe grain. |
| 03 | `03_std_ct_theoretical_consumption.sql` | Upstream only. Do not expose as a final actual-consumption source. |
| 04 | `04_std_ct_inventory_period.sql` | Upstream period bridge only. No dashboard aggregation. |
| 05 | `05_std_ct_inventory_snapshot.sql` | Create outlet and item lookups. Use one source period for current stock. |
| 06 | `06_std_ct_inventory_movement.sql` | Upstream only. Quantities require a single UOM if shown. |
| 07 | `07_std_ct_purchase_order.sql` | Upstream only. Use Query 22 for reports. |
| 08 | `08_std_ct_purchase_receipt.sql` | Upstream only. Use Query 23 for reports. |
| 09 | `09_std_ct_wastage.sql` | Upstream only. Use Query 35 for observed financial leakage. |
| 10 | `10_std_ct_vendor_report.sql` | Vendor master evidence only. Historical source limitations remain. |
| 11 | `11_std_ct_menu_forecast.sql` | Upstream model input. Forecast is synthetic and versioned. |
| 12 | `12_dim_ct_date.sql` | Validate 90 unique dates. Use as parent for Query 18 sales date only. |
| 13 | `13_dim_ct_outlet.sql` | Base dimension only. Do not use as the dashboard lookup parent. |
| 14 | `14_dim_ct_item.sql` | Validate 43 unique item codes. Blank enrichment fields are unavailable source attributes, not zero values. |
| 15 | `15_dim_ct_menu_item.sql` | Validate 110 unique menu-item codes. Use as sales/menu parent. |
| 16 | `16_dim_ct_vendor.sql` | Validate 70 unique vendor names. Vendor names without vendor codes remain valid observed vendors. |
| 17 | `17_dim_ct_recipe_effective.sql` | Effective recipe bridge only. No lookup or formula required. |
| 18 | `18_fact_ct_sales.sql` | Create outlet, sales-date and menu-item lookups. Use physical sales fields; count distinct `item_code` for active menu items. |
| 19 | `19_fact_ct_theoretical_consumption.sql` | Create outlet and item lookups. Use value for mixed-UOM summaries. |
| 20 | `20_fact_ct_actual_consumption.sql` | Create outlet and item lookups. Verify the three physical signed bridge columns. |
| 21 | `21_fact_ct_consumption_variance.sql` | Create outlet/item lookups. Verify physical signed variance; sum physical leakage and variance fields. |
| 22 | `22_fact_ct_purchase_order.sql` | Create outlet/item/vendor lookups. Use physical value/flag fields and distinct PO/vendor identifiers. |
| 23 | `23_fact_ct_purchase_receipt.sql` | Create outlet/item/vendor lookups. Add only the Weighted Unit Price aggregate formula; count distinct `grn_number` when needed. |
| 24 | `24_fact_ct_po_receipt_line.sql` | Create outlet/item/vendor lookups. Add fill-rate and OTIF formulas. Keep formula-demo label until actual linkage is approved. |
| 25 | `25_fact_ct_menu_profitability.sql` | Create outlet/menu lookups. Add aggregate gross-margin percentage. Never average row margin percentage. |
| 26 | `26_fact_ct_forecast_ingredient_demand.sql` | Create outlet/item/menu lookups. Treat forecast fields as model output, not observed demand. |
| 27 | `27_fact_ct_inventory_risk.sql` | Create outlet/item lookups. Use physical `risk_type` in the report Filter shelf and distinct physical identifiers for counts. |
| 28 | `28_fact_ct_menu_impact.sql` | Create outlet, ingredient and menu lookups. Sum allocated sales-at-risk only. |
| 29 | `29_sum_ct_procurement_funnel.sql` | Create outlet/vendor lookups. Use value measures as separate funnel stages. |
| 30 | `30_sum_ct_vendor_scorecard.sql` | Create outlet/vendor lookups. Percentages are native period-outlet-vendor results; do not combine them across outlets. |
| 31 | `31_sum_ct_price_movement.sql` | Create outlet/item/vendor lookups. Use the physical comparison key and absolute-change sort field. Compare one item and one UOM. |
| 32 | `32_sum_ct_menu_profitability.sql` | Create outlet/menu lookups. Force one source period and one outlet for a BCG view, or retain outlet as a visible grouping. |
| 33 | `33_sum_ct_scm_monthly.sql` | Create outlet lookup. Sum physical `working_capital_value`; current-state KPI cards require one source period. |
| 34 | `34_fact_ct_data_quality_exception.sql` | Sum physical `exception_count`. Do not add outlet/item lookups because `ALL` and blank keys are intentional. |
| 35 | `35_sum_ct_financial_leakage.sql` | Create outlet lookup. Label as observed wastage, not total financial leakage. |
| 36 | `36_fact_ct_risky_po.sql` | Create outlet/item/vendor lookups and count distinct physical `po_number`. |
| 37 | `37_dim_ct_outlet_enriched.sql` | Validate 3 unique outlets and coordinates. This is the canonical outlet parent. |
| 38 | `38_fact_ct_expiry_risk.sql` | Validate types; create outlet/item lookups; use physical expiry fields; retain explicit synthetic-estimate label. |

# Phase 7 - Filter And Grain Contract

## Source Period

For current-state inventory, risk and working-capital visuals:

```text
Control type: single-select
Default value: month_03
```

This applies to Query 05, Query 27, Query 33 and Query 38. Summing all three
inventory checkpoints would treat separate month-end states as simultaneous
stock.

Historical trend reports may intentionally allow multiple periods.

## Outlet

Use `outlet_code` as the common filter key. Use attributes from Query 37 for:

- outlet display name;
- region;
- city;
- market area;
- new/matured flag.

Do not use `super_category_name` as the company or outlet identifier.

## UOM

Require exactly one `canonical_uom` before displaying:

- actual versus theoretical quantities;
- low-consumption quantity;
- shortage quantity across multiple items;
- expiry quantity across multiple items.

Currency values may be combined across UOMs when the valuation basis is the
same.

## Vendor Percentages

Query 30 percentages are already calculated at:

```text
source period + outlet + vendor
```

Do not sum or average them across outlets. For a cross-outlet vendor view,
calculate fill rate and OTIF from Query 24 using their aggregate formulas.

## Price Movement

Query 31 is at:

```text
source period + outlet + vendor + item + UOM
```

Do not aggregate its percentage across items. Use the absolute formula only for
sorting and display the signed change.

## Menu BCG

Query 32 is at:

```text
source period + outlet + menu item
```

The quadrant uses synthetic demo thresholds. A BCG visual must either:

- select one source period and one outlet; or
- retain outlet as an explicit grouping.

# Phase 8 - Reconciliation Before Dashboards

## Parent-Key Checks

Record:

| Check | Expected |
| --- | ---: |
| Query 37 distinct outlets | 3 |
| Query 14 distinct items | 43 |
| Query 15 distinct menu items | 110 |
| Query 16 distinct vendors | 70 |
| Query 12 distinct calendar dates | 90 |

## All-Period Formula Checks

For this one validation only, clear the source-period and outlet filters. These
are all-period synthetic truth-pack values, not the final current-state
dashboard filter state.

| Formula or measure | Expected result |
| --- | ---: |
| Outlets At Stockout Risk | 3 |
| Stockout Risk Item Count | 16 |
| Menu Items At Risk | 110 |
| Stockout Sales At Risk | INR 976,271.72 |
| Query 27 stockout shortage exposure | INR 61,735.03 |
| Expiry Risk Value - Demo Estimate | INR 628,131.99 |
| Combined presentation reference only | INR 689,867.02 |
| Open Risky PO Count | 1 |
| Working Capital Locked | INR 7,702,923.62 |
| Open PO Count | 79 |
| Delayed PO Count | 65 |
| PO Fill Rate | 83.2529% |
| Vendor OTIF | 51.6704% |
| Net Sales | INR 6,027,041.45 |
| Quantity Sold | 23,319 |
| Active Menu Items | 110 |
| Theoretical COGS | INR 1,083,602.04 |
| Signed Consumption Variance Value | INR -37,258.56 |
| Consumption Leakage Value | INR 59,388.51 |
| Menu Gross Margin | INR 4,943,439.41 |
| Menu Gross Margin % | 82.021% |

The stockout controls above use Query 27 and Query 36 only. The earlier
combined-risk draft produced 221 actions and 53 risky POs by treating Query 38
expiry rows as stockout rows; those values are invalid for the final split
model.

The combined presentation reference is:

```text
Query 27 stockout shortage exposure + Query 38 synthetic expiry exposure
```

Do not implement it as a cross-fact aggregate formula or another Query Table.
Keep the two KPI cards separate so their evidence levels remain visible.

## Data-Quality Formula Checks

Filter Query 34 by each `exception_type` and validate:

| Exception type | Expected count |
| --- | ---: |
| `NEGATIVE_STOCK` | 1 |
| `ZERO_STOCK_WITH_DEMAND` | 2 |
| `SOLD_ITEM_MISSING_RECIPE` | 0 |
| `OPERATIONAL_ITEM_MISSING_MASTER` | 0 |
| `UOM_MISMATCH_WITHOUT_CONVERSION` | 0 |
| `OPEN_PO_MISSING_EXPECTED_DELIVERY` | 3 |

Do not hide a zero-count exception type from the final data-quality design.
Zero means the check ran and found no exception in the synthetic baseline.

# Phase 9 - Final Readiness Checklist

Do not start dashboard construction until every item is complete.

| Check | Required result | Status |
| --- | --- | --- |
| Query Tables 01-38 saved | No errors | NOT STARTED |
| Query 37 parent-key validation | 3 unique outlet codes | NOT STARTED |
| Query 14 parent-key validation | 43 unique item codes | NOT STARTED |
| Query 15 parent-key validation | 110 unique menu-item codes | NOT STARTED |
| Query 16 parent-key validation | 70 unique vendor names | NOT STARTED |
| Query 12 parent-key validation | 90 unique dates | NOT STARTED |
| Outlet lookup matrix | All listed child tables complete | NOT STARTED |
| Item lookup matrix | All listed child tables complete | NOT STARTED |
| Menu lookup matrix | All five relationships complete | NOT STARTED |
| Vendor lookup matrix | Seven required relationships complete | NOT STARTED |
| Sales date lookup | Complete | NOT STARTED |
| Query 20 physical bridge columns | Three fields validated | NOT STARTED |
| Query 21 physical signed variance/direction | Two fields validated | NOT STARTED |
| Query 24 eligible lead deviation | Field validated | NOT STARTED |
| Query 31 physical comparison/sort/direction fields | Three fields validated | NOT STARTED |
| Query 33 physical working capital | Field validated | NOT STARTED |
| Aggregate formula catalog | Exactly four required formulas saved | NOT STARTED |
| Percentage display convention | 83.25%, 51.67%, 82.02% | NOT STARTED |
| All-period reconciliation | Matches Phase 8 | NOT STARTED |
| Query 34 exception checks | Matches Phase 8 | NOT STARTED |
| Default current-state period | `month_03` recorded | NOT STARTED |
| Expiry wording | Synthetic-estimate disclaimer approved | NOT STARTED |
| Vendor-return widgets | Omitted | NOT STARTED |

# Troubleshooting

## A Lookup Option Is Unavailable

Check:

1. The parent key is unique.
2. Parent and child data types match.
3. The child is not already a lookup.
4. You opened the child table, not the parent table.
5. You selected the exact numbered Query Table.

## A Lookup Hides Rows

Remove the lookup and inspect unmatched child values. Do not create substitute
dimension rows merely to make a lookup pass. Query 34 and blank Query 38 vendor
values are documented exceptions.

## A Percentage Is 100 Times Too Large

Zoho percentage display behavior can depend on the selected formatting mode.
The accepted results are `83.25%`, `51.67%` and `82.02%`. If the displayed
result is 100 times larger, remove `* 100` while retaining the Percentage
format.

## A PO Count Is Too High

Confirm the formula uses `distinctcount("po_number")`. Row count and
`sum(is_open_po)` measure PO lines, not distinct POs.

## Stock Or Working Capital Is Too High

Confirm the dashboard is filtered to one source period. The default
current-state period is `month_03`.

## Sales At Risk Is Too High

Confirm the report uses:

```text
sum("allocated_forecast_net_sales_at_risk")
```

Do not sum `forecast_net_sales_at_risk`.

## Margin Percentage Does Not Reconcile

Confirm the report uses:

```text
sum("gross_margin_value") / sum("net_sales")
```

Do not average `gross_margin_percent`.

# Official Zoho References

- Working with tables and lookup columns:
  https://www.zoho.com/analytics/help/table/working-with-tables.html
- Aggregate formulas:
  https://www.zoho.com/analytics/help/analyze-data/aggregate-formula.html
- Aggregate functions:
  https://www.zoho.com/analytics/help/analyze-data/aggregate-functions.html

After this runbook passes, continue with:

```text
docs/zoho_control_tower_v2_dashboard_click_by_click.md
```
