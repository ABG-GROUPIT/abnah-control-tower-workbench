# Zoho Current Workspace Migration - 38 Tables Already Complete

## Start State

Use this document only when the workspace already has:

- all 38 numbered Query Tables saved;
- all lookup relationships completed;
- the earlier aggregate-formula list completed;
- no final dashboard reports that need to be preserved.

Do not restart imports. Do not recreate Queries 01-19. Do not redo the full
lookup matrix.

## Final Outcome

The migration changes five Query Tables, verifies only the lookup metadata
that those five saves can affect, keeps four aggregate formulas as active
metrics, retires redundant formulas from dashboard use, and then builds the
reference-first reports.

## Step 1 - Back Up

1. Duplicate or export the Zoho workspace.
2. Record the backup date.
3. Do not delete existing formulas or reports yet.

## Step 2 - Replace Five Query Tables

Use the current SQL files from `02_QUERY_TABLES` and replace/save only:

1. `20_fact_ct_actual_consumption.sql`
2. `21_fact_ct_consumption_variance.sql`
3. `24_fact_ct_po_receipt_line.sql`
4. `31_sum_ct_price_movement.sql`
5. `33_sum_ct_scm_monthly.sql`

The dependency order matters: Query 21 is saved after Query 20.

Do not re-save any other Query Table for this correction.

## Step 3 - Verify New Physical Columns

| Query | Columns that must be visible |
| --- | --- |
| 20 | `bridge_transfer_out_qty`, `bridge_return_qty`, `bridge_closing_qty` |
| 21 | `signed_consumption_variance_value`, `consumption_variance_direction` |
| 24 | `eligible_lead_time_deviation_days` |
| 31 | `price_comparison_key`, `unit_price_change_percent`, `absolute_unit_price_change_percent`, `price_movement_direction` |
| 33 | `working_capital_value` |

If Zoho still shows the old metadata, close and reopen the table/report
designer before changing anything else.

## Step 4 - Check Only Affected Lookups

Saving SQL normally preserves an unchanged output column, but verify the lookup
icon on these columns because Zoho can detach metadata after a query edit:

| Child table | Lookup columns to verify | Parent |
| --- | --- | --- |
| Query 20 | `outlet_code`, `item_code` | Query 37 outlet, Query 14 item |
| Query 21 | `outlet_code`, `item_code` | Query 37 outlet, Query 14 item |
| Query 24 | `outlet_code`, `item_code`, `vendor_name` | Query 37 outlet, Query 14 item, Query 16 vendor |
| Query 31 | `outlet_code`, `item_code`, `vendor_name` | Query 37 outlet, Query 14 item, Query 16 vendor |
| Query 33 | `outlet_code` | Query 37 outlet |

If the icon is still present and a parent attribute resolves, do nothing.
Recreate only a missing relationship in this table. Do not repeat the whole
lookup setup.

## Step 5 - Aggregate Formula Decision Register

### Keep and use

| Table | Formula | Action |
| --- | --- | --- |
| Query 23 | `Weighted Unit Price` | Keep unchanged; use in price reports |
| Query 24 | `PO Fill Rate %` | Keep unchanged; use in Summary Views |
| Query 24 | `Vendor OTIF %` | Keep unchanged; use in Summary Views |
| Query 25 | `Menu Gross Margin %` | Keep unchanged; use in a Summary View |

`<>` is the valid not-equal operator inside a Zoho Aggregate Formula. If these
formulas are already saved and validate, do not change or recreate them. The
earlier problem was typing formula-style comparison logic into a report-filter
interface, not the formula syntax itself.

After Query 24 is re-saved, open its Aggregate Formula list. Recreate its two
formulas only if Zoho removed them.

### Retain temporarily but do not use in the final dashboard

The earlier setup created formula aliases for direct sums and counts. They can
remain without harming the model, but the final direct KPI widgets select
physical fields and the calculation control instead.

| Table | Earlier formula names | Final dashboard replacement |
| --- | --- | --- |
| Query 27 | `Outlets At Stockout Risk`, `Stockout Risk Item Count`, `Shortage Cost Value`, `Stockout Inventory Exposure` | Physical identifier/value fields with Count Distinct or Sum and fixed `risk_type` filter |
| Query 38 | `Expiry Risk Value - Demo Estimate`, `Expiry Items At Risk - Demo Estimate`, `Outlets With Expiry Risk - Demo Estimate`, `Expiry Quantity At Risk - Single UOM Only` | Physical expiry fields; quantity remains single-UOM only |
| Query 28 | `Menu Items At Risk`, `Stockout Risk Value` | `menu_item_code` Count Distinct and `allocated_forecast_net_sales_at_risk` Sum |
| Query 36 | `Open Risky PO Count`, `Open Risky PO Liability` | `po_number` Count Distinct and `open_po_value` Sum |
| Query 25 | `Net Sales`, `Quantity Sold`, `Theoretical COGS`, `Menu Gross Margin` | Direct Sum of the four physical fields |
| Query 21 | `Consumption Leakage Value`, `Low Consumption Check Quantity` | Direct Sum of physical fields; quantity only at one UOM |
| Query 33 | `Working Capital Locked` | Direct Sum `working_capital_value` |

Recommended handling:

1. Do not delete a formula before checking whether an old report depends on it.
2. If Zoho allows renaming without breaking a report, prefix it
   `LEGACY - DO NOT USE -`.
3. Otherwise record it as legacy and leave it untouched.
4. Delete legacy formulas only after the final dashboard passes and no
   dependency remains.

## Step 6 - Validate Four Active Formulas

Use no outlet or source-period filter for this one check:

| Formula | Expected all-period result |
| --- | ---: |
| Weighted Unit Price | Validate per item/vendor/UOM; no single mixed-item total |
| PO Fill Rate % | 83.2529% |
| Vendor OTIF % | 51.6704% |
| Menu Gross Margin % | 82.0210% |

For the final `month_03 / All outlets` state:

| Formula | Expected |
| --- | ---: |
| PO Fill Rate % | 86.3942% |
| Vendor OTIF % | 53.7037% |
| Menu Gross Margin % | 82.0447% |

If a percentage displays 100 times too large, remove `* 100` from that formula
while retaining percentage formatting. Do not change the accepted displayed
value.

## Step 7 - Build The Reference KPI Reports First

Build only these 20 cards before any extended report.

### Page 1

1. `CT_P1_KPI_Outlets_At_Stockout_Risk`
2. `CT_P1_KPI_Menu_Items_At_Risk`
3. `CT_P1_KPI_Stockout_Risk_Value`
4. `CT_P1_KPI_Expiry_Risk_Value_Demo`
5. `CT_P1_KPI_Open_Actions`

### Page 2

1. `CT_P2_KPI_Monthly_Purchase`
2. `CT_P2_KPI_Open_PO_Liability`
3. `CT_P2_KPI_Delayed_PO_Value`
4. `CT_P2_KPI_OTIF`
5. `CT_P2_KPI_Price_Watch`

### Page 3

1. `CT_P3_KPI_Net_Sales`
2. `CT_P3_KPI_Theoretical_COGS`
3. `CT_P3_KPI_Menu_Gross_Margin`
4. `CT_P3_KPI_Menu_Items`
5. `CT_P3_KPI_Consumption_Leakage`

### Page 4

1. `CT_P4_KPI_Closing_Stock`
2. `CT_P4_KPI_Open_PO`
3. `CT_P4_KPI_Net_Sales`
4. `CT_P4_KPI_Actual_Consumption`
5. `CT_P4_KPI_Consumption_Variance`

Use a direct KPI Widget for physical Sum/Count/Count Distinct measures. Use a
saved Summary View for Vendor OTIF and Menu Gross Margin because they are
Aggregate Formulas.

## Step 8 - Build Reference Views In This Order

1. Page 1: Outlet Risk Map, Action Center, Stockout Detail, Menu Impact,
   Expiry Detail Demo, Vendor PO Risk.
2. Page 2: Procurement Funnel, Vendor Scorecard, Ingredient Price Trend,
   Top Price Movement, Pending by Vendor, Expected Delivery Breach.
3. Page 3: Consumption Bridge, Consumption Variance, Menu BCG,
   Outlet-Item Heatmap.
4. Page 4: SCM Monthly Trend, six data-quality tiles, Data Quality Detail,
   Descriptive Explorer.

Validate every object before styling or embedding it.

## Step 9 - Add Filters

1. Add only `As-of Source Period` and `Outlet` as common filters.
2. Map each filter only to a report with the exact compatible field.
3. Exclude historical trend reports from the current-period filter.
4. Exclude Query 34 quality objects from period and outlet filters.
5. Add page-specific filters after the common filters reconcile.
6. Apply fixed conditions through the report Filter shelf using
   **Individual Values > Include**. Do not type SQL comparison expressions in
   the filter UI.

## Step 10 - Stop Gate Before Embedding

Do not generate embed URLs until:

- the five Query Tables open without errors;
- affected lookup icons resolve;
- all four active Aggregate Formulas reconcile;
- the 20 reference KPI cards match the expected-results document;
- Page 1 has 6 stockout action rows at `month_03 / All outlets`;
- trend reports retain all periods;
- Query 34 zero-count checks remain visible;
- every Query 38 title states that it is a synthetic estimate.

Then continue with:

```text
ZOHO_EMBEDDED_PORTAL_SETUP.md
```
