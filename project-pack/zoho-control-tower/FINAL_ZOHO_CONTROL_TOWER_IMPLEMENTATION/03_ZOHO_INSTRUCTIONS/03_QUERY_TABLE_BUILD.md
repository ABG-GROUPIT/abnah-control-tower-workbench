# Zoho Control Tower v2 - Query Table Build

## Platform Constraint

Zoho Analytics allows a maximum of three Query Table levels over imported
tables. The generated pack contains:

- 16 level-1 Query Tables
- 12 level-2 Query Tables
- 10 level-3 Query Tables
- 38 active Query Tables total

The builder fails if any dependency would become level 4.

Official Query Table guidance:
https://www.zoho.com/analytics/help/query-tables.html

## Generate The Pack

```powershell
python scripts/build_control_tower_v2_sql.py
```

Use:

```text
docs/zoho_control_tower_v2_sql/QUERY_TABLE_MANIFEST.csv
```

as the exact implementation checklist. Do not rely on alphabetical order.

## Incremental Extension After The First 36 Tables

If Query Tables 01-36 already exist and execute, do **not** rebuild them.
Complete only this sequence:

1. Keep `AUX_Outlet_Master.csv` as packaged reference evidence if it is already
   imported. The current Query 37 does not depend on that table.
2. Import `AUX_Expiry_Estimate.csv` as `AUX_Expiry_Estimate-Copy`. If the
   earlier item-level version already exists, replace its data and columns;
   never append the corrected 206-row batch-tranche scenario.
3. Replace and save only `27_fact_ct_inventory_risk.sql`. The current version
   is a stockout/days-cover fact with no CTEs and no expiry join. Its forecast
   and open-PO inputs are independent one-level aggregations for Zoho parser
   compatibility.
4. Create `37_dim_ct_outlet_enriched.sql`. It reads the already-built
   `13_dim_ct_outlet.sql` and adds the visibly synthetic demo geography without
   casts or an AUX-table dependency.
5. Create `38_fact_ct_expiry_risk.sql`, or replace and save it if the earlier
   version already exists. The current version projects the imported fields
   directly and derives severity from `risk_status`; it uses no casts,
   concatenation or numeric filter.

Queries 1-26 and 28-37 do not need to be re-saved. Query 38 remains the
separate expiry scenario fact. If only Query 27 is failing to parse, do not
re-import any CSV and do not replace Query 38.

## Query Table Naming Contract

Save each Query Table with the exact SQL filename shown in
`query_table_name`, including the numeric prefix and `.sql` suffix. For
example, save the sales standardization table as
`01_std_ct_sales_item.sql`.

The SQL pack uses those exact physical Zoho names in every downstream `FROM`
and `JOIN`. The unnumbered `STD_CT_*`, `DIM_CT_*`, `FACT_CT_*`, and `SUM_CT_*`
names are logical model labels only.

## Repair An Earlier Partial Build

If Query Tables 01-14 were created from a pack generated before this naming
and output-column contract was enforced:

1. Replace and save the SQL for Query Tables 01-11.
2. Leave Query Tables 12 and 13 unchanged if their source names were already
   corrected manually and both execute successfully.
3. Replace and save Query Table 14.
4. Create Query Table 15 from the revised file and continue in numeric order.

Queries 01-11 now alias every downstream field explicitly. Query 14 explicitly
aliases `item_code`. This prevents Zoho from exposing source-dependent column
labels such as the one that caused Query Table 15 to reject `item_code`.

If Query Table 24 reports `Invalid column 'outlet_code'` after 01-14 have
already been rebuilt, replace only Query Table 24 with the current SQL. Its
internal receipt aggregation now explicitly publishes all four join keys:
period, outlet, PO and item. No earlier table needs to be rebuilt for that
specific correction.

If Query Table 27 reports that subqueries are unsupported within CTEs or shows
the generic `Parsing Of query Failed` message, replace only Query Table 27 with
the current SQL. It has no `WITH` clause, no nested subquery and no expiry
dependency. The two independent aggregate joins are each one level deep.
Query Tables 28 and 36 also follow Zoho's limits: no subquery inside a CTE and
no more than three CTEs per query.

If Query Table 34 reports that more than one level of `FROM` subqueries is not
allowed, replace only Query Table 34 with the current SQL. The UOM exception
branch is now flattened to a single derived-table level. The generator rejects
any future SQL that exceeds this depth.

If Query Table 37 fails to parse, reports an invalid cast, or cannot find the
outlet AUX table, replace only Query Table 37 with the current SQL. It reads
`13_dim_ct_outlet.sql`, which already exists in a completed 01-36 build, and
adds the three demo map locations through direct `CASE` expressions. No CSV
re-import and no earlier Query Table re-save is required.

If Query Table 38 shows the generic `Parsing Of query Failed` message, replace
only Query Table 38 with the current SQL. It has no `CAST`, `CONCAT`, CTE,
subquery or numeric `WHERE` expression. The packaged expiry input already
contains only positive at-risk rows, and its `risk_status` field directly
drives severity, action and due band. Confirm the source table is named exactly
`AUX_Expiry_Estimate-Copy`; no earlier Query Table needs to be changed.

## Create Each Query Table

For each manifest row:

1. Confirm every table in the `sources` column already exists.
2. In Zoho Analytics, click **Create**.
3. Click **New Query Table**.
4. Open the SQL file shown in `sql_file`.
5. Paste the complete SQL into the editor.
6. Click **Execute Query**.
7. Check the preview has rows and the expected columns.
8. Click **Save**.
9. Enter the exact `query_table_name` from the manifest.
10. Add the manifest purpose as the table description.
11. Save the table.
12. Record its row count and dependency level in the build checklist.

Do not rename a Query Table after downstream tables have been created.

## Build Checkpoints

### Checkpoint A - Standardized Tables

Build orders 1-11.

Verify:

- Dates parse as dates.
- Identifier columns remain text.
- Quantities and values are numeric.
- PO status produces a sensible `is_open_po` flag.
- Transfer and wastage signs are correct.
- `STD_CT_Vendor_Report` contains one structurally repaired row per vendor
  master record.
- Exact expiry remains unavailable until the POSIST module is enabled and a
  populated export is validated. Query 27 contains no expiry fields. The
  visibly synthetic expiry scenario is isolated in Query 38.

Stop if any required row count is zero unexpectedly.

`STD_CT_Vendor_Return` is not in the active manifest because Enterprise Stock
Return is header-only. Do not create it or a return KPI until populated evidence
passes the local audit.

### Checkpoint B - Dimensions

Build orders 12-17.

Verify:

- Three active outlets exist.
- Every operational item maps to `DIM_CT_Item`.
- Recipe rows have ingredient code and canonical UOM.
- `canonical_recipe_qty` is numeric and non-null.
- Vendor names are unique at the expected master grain.
- Transaction-only vendor names are retained with
  `source_evidence = observed_in_po_or_entry_only` and investigated as source
  coverage exceptions.

The item/UOM dimension is a publication gate. Do not continue with quantity,
price, theoretical COGS or variance charts if conversion coverage is incomplete.

### Checkpoint C - Reusable Facts

Build orders 18-28.

Verify:

- Sales net value reconciles to the raw landing table.
- Actual consumption reproduces the inventory bridge.
- Consumption variance equals actual minus theoretical.
- PO receipt lines retain outlet, PO number and item code.
- OTIF eligibility excludes open lines and missing expected dates.
- Menu profitability uses `theoretical_cost_per_menu_unit`, not the source
  purchase-value column as the final COGS authority.
- Inventory risk has stockout `risk_severity`, action, owner and due band.
- Expiry severity and exposure are kept separately in Query 38 so the demo
  estimate cannot be mistaken for POSIST production truth.
- Menu impact has `allocated_forecast_net_sales_at_risk`.

### Checkpoint D - KPI Summaries

Build orders 29-36.

Verify:

- Procurement funnel totals reconcile to PO line totals.
- Vendor scorecard ratios use eligible denominators.
- Price movement compares only matching item, vendor, outlet and UOM.
- Page 4 monthly summary has one row per period and outlet.
- Data-quality summary has six exception types.
- Financial leakage distinguishes `observed` from `estimated`.
- Risky PO fact retains exact PO number and only non-green ingredient lines.

### Checkpoint E - Demo Reference Extensions

Build orders 37-38.

Verify:

- Query 37 has exactly three unique outlet codes, valid latitude/longitude and
  `is_synthetic = 1`.
- Query 38 has only positive expiry quantities, quantity at risk never exceeds
  its estimated batch tranche, the tranche never exceeds item closing stock,
  batch allocation IDs are unique, and every row has
  `production_use_status = demo_only_no_posist_batch_or_expiry_source`.
- `sum(expiry_qty_at_risk * average_unit_cost)` reconciles to
  `sum(expiry_risk_value)` within rounding tolerance.
- Rows tied to a synthetic GRN retain batch, receipt, PO and vendor lineage.
  Fallback rows are explicitly marked
  `synthetic_near_expiry_opening_tranche`.
- No expiry value is described as a POSIST batch fact.

## Why Four Conceptual Views Are Not Query Tables

These names remain part of the logical architecture but are implemented in the
report layer:

| Conceptual view | Implementation |
| --- | --- |
| `FACT_CT_Vendor_Performance` | Use `FACT_CT_PO_Receipt_Line` directly |
| `FACT_CT_Action_Queue` | Use action fields embedded in `FACT_CT_Inventory_Risk` |
| `SUM_CT_Risk_Action` | KPI widgets over Inventory Risk and Menu Impact |
| `SUM_CT_Consumption_Variance` | Reports over `FACT_CT_Consumption_Variance` |

Creating them as additional Query Tables would add unnecessary layers and can
exceed Zoho's limit.

## Aggregate Formulas

Create formulas from the indicated table using **Add > Aggregate Formula**.
Zoho aggregate formulas are evaluated at report grouping grain, so ratio KPIs
must divide aggregate numerators by aggregate denominators.

Official formula guidance:
https://www.zoho.com/analytics/help/analyze-data/aggregate-formula.html

### `FACT_CT_Inventory_Risk`

```text
Outlets At Stockout Risk
distinctcount(if("risk_severity" <> 'GREEN', "outlet_code", null))

Stockout Risk Item Count
distinctcount(if("risk_severity" <> 'GREEN', "action_id", null))

Shortage Cost Value
sum("shortage_cost_value")

Stockout Inventory Exposure
sum("total_risk_value")
```

In Query 27, `total_risk_value` intentionally equals shortage cost only. Show
stockout exposure from Query 27 and the visibly labelled expiry estimate from
Query 38 as separate KPI cards. Do not add the two sources in another Query
Table, and keep forecast menu revenue at risk as a separate commercial-impact
measure.

### `FACT_CT_Expiry_Risk`

```text
Expiry Risk Value - Demo Estimate
sum("expiry_risk_value")

Expiry Items At Risk - Demo Estimate
distinctcount("action_id")

Outlets With Expiry Risk - Demo Estimate
distinctcount("outlet_code")

Expiry Quantity At Risk - Single UOM Only
sum("expiry_qty_at_risk")
```

Always retain **Demo estimate - no POSIST batch/expiry source** in the report
title or subtitle. Show the quantity formula only when one canonical UOM is
fixed.

### `FACT_CT_Menu_Impact`

```text
Menu Items At Risk
distinctcount("menu_item_code")

Stockout Risk Value
sum("allocated_forecast_net_sales_at_risk")
```

Query 28 contains only risk rows. Do not sum `forecast_net_sales_at_risk`
directly. It repeats when one menu item depends on several risky ingredients.

### `FACT_CT_Risky_PO`

```text
Open Risky PO Count
distinctcount("po_number")

Open Risky PO Liability
sum("open_po_value")
```

### `FACT_CT_PO_Receipt_Line`

```text
PO Fill Rate %
if(sum("ordered_qty") <> 0,
sum("received_qty") / sum("ordered_qty") * 100,
null)

Vendor OTIF %
if(sum("eligible_closed_line_flag") <> 0,
sum("otif_success_flag") / sum("eligible_closed_line_flag") * 100,
null)
```

Return null or show no data when a denominator is zero. Do not convert an absent
eligible population to 0%.

Vendor return rate is gated and intentionally absent from the active formula
set while the Enterprise Stock Return contract has no rows.

### `FACT_CT_Menu_Profitability`

```text
Net Sales
sum("net_sales")

Quantity Sold
sum("sold_qty")

Theoretical COGS
sum("theoretical_cogs")

Menu Gross Margin
sum("gross_margin_value")

Menu Gross Margin %
if(sum("net_sales") <> 0,
sum("gross_margin_value") / sum("net_sales") * 100,
null)
```

### `FACT_CT_Consumption_Variance`

```text
Consumption Leakage Value
sum("leakage_value")

Low Consumption Check Quantity
sum("low_consumption_qty")
```

Show quantity only at one canonical UOM or item/category grain. Across mixed UOM
scope, use value rather than adding kg, litre and pieces.

### `SUM_CT_SCM_Monthly`

```text
Working Capital Locked
sum("closing_stock_value") + sum("open_po_value")
```

Keep `closing_stock_value` and `open_po_value` as separate widgets beside the
combined formula so the composition remains auditable.

### `FACT_CT_Purchase_Receipt`

```text
Weighted Unit Price
if(sum("received_qty") <> 0,
sum("receipt_subtotal") / sum("received_qty"),
null)
```

Never use a simple average of row unit prices for the price-trend chart.

## Production PO Gate

The latest `RAWN_CT_enterprise_purchase_order` sample is populated and matches
the validated contract. It can replace the earlier header-only assumption, but
it does not by itself approve PO KPIs:

1. Link PO lines to `RAWN_CT_enterprise_entry` using exact PO, outlet and item
   keys.
2. Approve normalized status semantics and the eligible closed-line denominator.
3. Keep OTIF and overdue PO draft until expected dates and receipt evidence pass.
4. Use `RAWN_CT_purchase_detail` only as sparse reconciliation evidence; the
   captured sample has PO fields on 2 of 288 rows.
5. Do not create fake PO rows or silently fill delivery/status fields.

The synthetic Enterprise Purchase Order file demonstrates the intended model
while these production linkage and semantic gates are resolved.
