# ABNAH Control Tower v2 - Zoho Execution Runbook

## Decision

The synthetic demonstrator can be built in Zoho now.

Do not describe the model as production-validated yet. The current actual-data
audit proves exact CSV schema alignment for 20 current-UAT reports and retains
the exact historical `Vendor Report` contract. It gives populated evidence for
the main PO, receipt, inventory, sales, recipe, transfer and wastage sources.
Production publication is still gated by:

- ABNAH-approved item/UOM enrichment and vendor lead-time/SLA/vendor-item
  mappings not supplied by the historical `Vendor Report`;
- an approved demand forecast and model version;
- approved theoretical-consumption method;
- a populated Enterprise Stock Return export or approved fallback;
- PO status, receipt-linkage and eligible closed-line definitions;
- Restroworks definitions for margin, valuation, tax, rounding and sign rules;
- aligned production periods and final KPI owner sign-off.

The two decisions must remain separate:

| Decision | State |
| --- | --- |
| Build the three-month synthetic Control Tower in Zoho | Ready |
| Build and test the production-shaped RAW/STD/DIM/FACT/SUM model | Ready |
| Publish actual-data KPIs as production truth | Not ready |

## Migration Rule

Do not delete the old raw tables before the replacement model works.

Zoho states that re-importing into the same table preserves dependent reports,
while deleting a table and importing a new one breaks those dependencies:
https://www.zoho.com/analytics/help/import-data/files-feeds.html

Use this controlled migration:

1. Export or duplicate the current workspace as a rollback snapshot.
2. Prefer a separate workspace named `ABNAH Control Tower v2 Build`.
3. If the existing workspace must be used, keep the old tables and load the new
   landing tables under the exact `RAWN_CT_*-Copy` and `AUX_*-Copy` names.
   Save each Query Table with its exact numbered SQL filename, including the
   `.sql` suffix.
4. Build and validate the complete v2 dependency chain in parallel.
5. Build a new dashboard named `ABNAH Supply Chain Control Tower v2`.
6. Reconcile KPI totals and drill rows against the truth pack.
7. Switch users to v2 only after acceptance.
8. Archive the old model after the rollback window; do not delete it during the
   build.

## Phase 0 - Freeze The Build Inputs

Use:

```text
exports/control_tower_zoho/_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv
docs/zoho_control_tower_v2_sql/QUERY_TABLE_MANIFEST.csv
docs/zoho_control_tower_v2_sql/*.sql
```

The active manifest names the exact 14 files to import. The broader
`_CONTROL_TOWER_IMPORT_MANIFEST.csv` is evidence inventory, not an import list.
Keep `RAW_CT_*.csv` local as exact-header evidence. Do not import the three
`SCHEMA_CAPTURE_CT_*` files as production authorities.

Before opening Zoho, record:

```text
pack generation date
expected row count per file
expected column count per file
source period range
outlet count
derived item-reference rule version
forecast/model version
```

## Phase 1 - Import The 14 Required Landing Tables

Import in this order. The order puts business dimensions first, then observed
operational sources, then model-derived features.

| Order | Zoho table | Source file |
| ---: | --- | --- |
| 1 | `RAWN_CT_vendor_report-Copy` | `normalized/RAWN_CT_vendor_report.csv` |
| 2 | `RAWN_CT_gross_net_margin-Copy` | `normalized/RAWN_CT_gross_net_margin.csv` |
| 3 | `RAWN_CT_item_recipe_report-Copy` | `normalized/RAWN_CT_item_recipe_report.csv` |
| 4 | `RAWN_CT_enterprise_variance_normal-Copy` | `normalized/RAWN_CT_enterprise_variance_normal.csv` |
| 5 | `RAWN_CT_closing_stock-Copy` | `normalized/RAWN_CT_closing_stock.csv` |
| 6 | `RAWN_CT_enterprise_purchase_order-Copy` | `normalized/RAWN_CT_enterprise_purchase_order.csv` |
| 7 | `RAWN_CT_enterprise_entry-Copy` | `normalized/RAWN_CT_enterprise_entry.csv` |
| 8 | `RAWN_CT_enterprise_transfer_from-Copy` | `normalized/RAWN_CT_enterprise_transfer_from.csv` |
| 9 | `RAWN_CT_enterprise_transfer_to-Copy` | `normalized/RAWN_CT_enterprise_transfer_to.csv` |
| 10 | `RAWN_CT_enterprise_wastage_normal-Copy` | `normalized/RAWN_CT_enterprise_wastage_normal.csv` |
| 11 | `AUX_Menu_Demand_Forecast-Copy` | `AUX_Menu_Demand_Forecast.csv` |
| 12 | `AUX_Theoretical_Consumption-Copy` | `AUX_Theoretical_Consumption.csv` |
| 13 | `AUX_Outlet_Master-Copy` | `AUX_Outlet_Master.csv` |
| 14 | `AUX_Expiry_Estimate-Copy` | `AUX_Expiry_Estimate.csv` |

The last two files are scenario-only demonstrator references. Keep
`is_synthetic`, `source_evidence` and `production_use_status` visible in their
drill reports. Do not import `AUX_Item_Master` or `AUX_Vendor_Master`.

Before importing `RAWN_CT_vendor_report`, run the documented local vendor
cleaner. Stop if phone-number overflow, address continuation, extra cells, or
invalid compliance-ID formats remain unresolved.

Keep `RAWN_CT_enterprise_stock_return.csv` as gated schema evidence. Its audited
UAT contract and synthetic mirror are header-only, so it is not an active
landing dependency and must not produce a zero return-rate KPI.

For every first import:

1. Use **Create > New Table / Import Data > Files & Feeds > Local Drive**.
2. Use the exact table name above.
3. Set **First row contains column names** to Yes.
4. Keep identifiers as text.
5. Set ISO dates to `yyyy-MM-dd`.
6. Keep quantities and amounts as decimal.
7. Set **On Import Error** to **Don't Import the data**.
8. Compare imported rows to `_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv`.
9. Stop on any unexplained rejected row, shifted column or renamed header.

For a later full refresh, use **Import Data into this table > Delete existing
records and add**. Do not delete and recreate the table.

## Phase 2 - Build The 38 Active Query Tables

Zoho supports a maximum of three Query Table levels over an existing Query
Table. This pack stays within that limit:
https://www.zoho.com/analytics/help/query-tables.html

Build in the exact order below. Do not use alphabetical order.

### Checkpoint A - Standardized Tables

1. `01_std_ct_sales_item.sql`
2. `02_std_ct_recipe.sql`
3. `03_std_ct_theoretical_consumption.sql`
4. `04_std_ct_inventory_period.sql`
5. `05_std_ct_inventory_snapshot.sql`
6. `06_std_ct_inventory_movement.sql`
7. `07_std_ct_purchase_order.sql`
8. `08_std_ct_purchase_receipt.sql`
9. `09_std_ct_wastage.sql`
10. `10_std_ct_vendor_report.sql`
11. `11_std_ct_menu_forecast.sql`
`STD_CT_Vendor_Return` is deliberately gated until Enterprise Stock Return has
populated, audited rows.

Stop and validate dates, identifiers, UOMs, signs, PO status, row counts and the
model-output source labels.

### Checkpoint B - Dimensions

12. `12_dim_ct_date.sql`
13. `13_dim_ct_outlet.sql`
14. `14_dim_ct_item.sql`
15. `15_dim_ct_menu_item.sql`
16. `16_dim_ct_vendor.sql`
17. `17_dim_ct_recipe_effective.sql`

Stop if any operational item lacks a canonical item/UOM mapping or if a vendor
or outlet dimension is non-unique at its approved grain.

### Checkpoint C - Reusable Facts

18. `18_fact_ct_sales.sql`
19. `19_fact_ct_theoretical_consumption.sql`
20. `20_fact_ct_actual_consumption.sql`
21. `21_fact_ct_consumption_variance.sql`
22. `22_fact_ct_purchase_order.sql`
23. `23_fact_ct_purchase_receipt.sql`
24. `24_fact_ct_po_receipt_line.sql`
25. `25_fact_ct_menu_profitability.sql`
26. `26_fact_ct_forecast_ingredient_demand.sql`
27. `27_fact_ct_inventory_risk.sql`
28. `28_fact_ct_menu_impact.sql`

At this checkpoint, prove:

- sales reconciles to the selected raw authority;
- actual consumption follows the approved bridge;
- actual minus theoretical equals signed variance;
- PO, outlet and item keys survive receipt linkage;
- OTIF excludes open or ineligible lines;
- menu COGS comes from effective recipes;
- Query 27 stockout risks retain forecast, stock, inbound, evidence and
  owner/action fields;
- exact expiry remains unavailable, and the explicitly synthetic expiry
  scenario is isolated in Query 38.

### Checkpoint D - Summaries And Action Facts

29. `29_sum_ct_procurement_funnel.sql`
30. `30_sum_ct_vendor_scorecard.sql`
31. `31_sum_ct_price_movement.sql`
32. `32_sum_ct_menu_profitability.sql`
33. `33_sum_ct_scm_monthly.sql`
34. `34_fact_ct_data_quality_exception.sql`
35. `35_sum_ct_financial_leakage.sql`
36. `36_fact_ct_risky_po.sql`

### Checkpoint E - Demo Reference Extensions

37. `37_dim_ct_outlet_enriched.sql`
38. `38_fact_ct_expiry_risk.sql`

If Query Tables 01-36 are already complete, replace/save the current
stockout-only Query 27, then create 37 and 38. Query 37 reads the existing
Query 13 rather than the outlet AUX import. Query 38 reads the expiry AUX
table; Query 27 does not. Do not resave any other existing Query Table.

Use `docs/zoho_control_tower_v2_sql/QUERY_TABLE_MANIFEST.csv` for the exact SQL
file and source dependencies for every step.

The unnumbered uppercase names used later in this runbook are logical model
labels. In Zoho, select the corresponding numbered `.sql` Query Table.

## Phase 3 - Add Aggregate Formulas And Lookups

Use the standalone pre-dashboard configuration runbook:

```text
docs/ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md
```

It contains the exact physical parent and child tables, uniqueness gates,
lookup matrices, row formulas, aggregate formulas, direct aggregations,
single-period and single-UOM restrictions, truth values and the final
pre-dashboard checklist. Do not start Phase 4 until that checklist passes.

## Phase 4 - Build And Reconcile The 39 Saved Views

The external ABNAH portal uses individual Zoho saved views:

```text
20 KPI views + 19 chart/table/map views
```

Build them in this order:

1. `SCM Descriptive Explorer & Data Quality`
2. `Consumption Variance & Menu Profitability`
3. `Procurement, Vendor & Capital Control`
4. `Risk Action Center`

This order proves source totals and drill detail before the executive action
page is assembled.

Use the exact report names, sources, chart types, shelves, filters and expected
results in:

```text
docs/zoho_control_tower_v2_dashboard_click_by_click.md
docs/ZOHO_DASHBOARD_EXPECTED_RESULTS.md
```

After each saved view reconciles, generate its secured-with-login individual
embed URL and connect that exact slot using:

```text
docs/ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md
```

Do not wait for one complete Zoho dashboard before connecting the portal.
Unconfigured slots remain as blueprints while completed views go live.

Use **consumption**, not yield, on Page 3.

## Phase 5 - Match The Supplied Control Tower Visual

The ABNAH portal owns the four-page composition, navigation, page filters,
outer card frames, spacing and responsive layout. Zoho owns the rendered
content inside each secured iframe.

Match the supplied HTML in this order:

1. KPI/report meaning and number format in Zoho;
2. chart type and reading direction in Zoho;
3. severity colors, legends and labels in Zoho;
4. tooltip, drill and underlying-data behavior in Zoho;
5. page hierarchy, spacing and filter placement in the portal;
6. cross-device rendering and secured-login behavior.

The portal cannot restyle cross-origin Zoho iframe content. Apply all
chart-internal colors and number formats before generating the embed URL.

The portal applies tab-specific controls only to compatible views through
URL-encoded `ZOHO_CRITERIA`. Current-state period filters do not alter
historical trend views, and model-wide data-quality checks are not given
outlet criteria.

Zoho documents secured individual-view embedding and URL criteria:
https://www.zoho.com/analytics/help/publishing/embed-reports.html

## Phase 6 - Optional Native Zoho Dashboard

After all 39 saved views reconcile and work in the custom portal, optionally
assemble them into one native four-tab dashboard named:

```text
ABNAH Supply Chain Control Tower v2
```

This is a Zoho-only fallback and an acceptance comparison surface. The custom
portal does not depend on it.

Zoho supports dashboard tabs and mapped user filters:
https://www.zoho.com/analytics/help/dashboard/filter.html
| Pixel-level custom shell around embedded reports | Separate custom application |
| Arbitrary restyling of native Zoho dashboard internals | Not a supported plan |

Start with native Zoho. Approve a custom embedded shell only if the native result
cannot meet a specific signed-off presentation requirement.

## Phase 6 - Train Ask Zia

Train Ask Zia only after the dashboard calculations pass.

Zoho supports table, column and data synonyms, table/column priority and default
functions:
https://www.zoho.com/analytics/help/train-ask-zia.html

### Tables To Prioritize

Set these High:

```text
FACT_CT_Inventory_Risk
FACT_CT_Menu_Impact
FACT_CT_Risky_PO
SUM_CT_Procurement_Funnel
SUM_CT_Vendor_Scorecard
SUM_CT_Price_Movement
FACT_CT_PO_Receipt_Line
FACT_CT_Consumption_Variance
SUM_CT_Menu_Profitability
SUM_CT_SCM_Monthly
FACT_CT_Data_Quality_Exception
```

Exclude all `RAWN_CT_*` tables from Ask Zia. Set `STD_CT_*` and technical
dimensions Low unless a controlled question needs them.

### Minimum Synonyms

| Business phrase | Canonical field/table |
| --- | --- |
| revenue, net revenue, sales | `net_sales` |
| stockout risk, shortage risk | `FACT_CT_Inventory_Risk.shortage_qty` |
| expiry risk | `FACT_CT_Expiry_Risk.expiry_risk_value`; synthetic demo estimate only, never exact batch truth |
| working capital | `closing_stock_value + open_po_value` |
| open PO liability | `open_po_value` |
| fill rate | aggregate `received_qty / ordered_qty` |
| OTIF, on time in full | eligible aggregate OTIF formula |
| vendor return rate | aggregate return-rate formula |
| actual consumption | `calculated_actual_consumption_qty` |
| theoretical consumption | `theoretical_qty` |
| consumption leakage | `leakage_value` |
| menu margin | aggregate `gross_margin_value / net_sales` |
| data quality issue | `exception_type` / `exception_count` |

Do not add synonyms such as audited profit, exact expiry or causal impact unless
the required evidence and definition are approved.

### Acceptance Questions

1. Which outlets have stockout risk this month?
2. Which risky menu items have the highest forecast sales at risk?
3. Which vendors have the highest open PO liability?
4. Show eligible vendor OTIF and fill rate.
5. Which ingredients have the highest consumption leakage value?
6. Show menu items by gross margin value and quantity sold.
7. Show closing stock and open PO value by outlet.
8. List open POs missing expected delivery dates.

For every answer, verify the selected table, filters, aggregation and total
against the dashboard before adding more synonyms.

## Final Cutover Gate

Switch to the v2 dashboard only when all items are true:

- all 14 active landing tables imported with expected rows and types;
- all 38 active Query Tables built in manifest order;
- no dependency exceeds level 3;
- source-to-fact reconciliations pass;
- all four tabs match the approved KPI definitions;
- report drill rows support each published number;
- Ask Zia passes the controlled question bank;
- data-quality and estimated-value labels remain visible;
- no actual-data formula warning is presented as a confirmed source error
  without business-definition sign-off;
- rollback workspace or export is retained.
