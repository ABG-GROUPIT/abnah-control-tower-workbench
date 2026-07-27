# Page 1 and Page 2 Correction Guide

This is the smallest safe correction sequence for the Page 1 dashboard already
built in Zoho and the Page 2 dashboard now being completed. Do not delete the
dashboard, rebuild the 38-table model, or remove the existing Aggregate
Formulas.

## What The Live Page 1 Review Found

The reviewed dashboard rendered correctly, but three values were not using the
intended reporting scope or grain:

| Area | Live result | Correct March demo truth | Cause |
| --- | ---: | ---: | --- |
| Menu items at risk | 79 | 110 | Query 28 tested recipe-path shortages instead of the ingredient's total required quantity |
| Stockout sales at risk | INR 286,563.67 | INR 411,695.50 | The same Query 28 grain issue excluded valid impacted menu items |
| Expiry risk | about INR 600,000 | INR 271,399.12 | `source_period_code` did not reliably restrict the expiry widget to March |

The following reviewed values were already correct for March:

| KPI | Expected |
| --- | ---: |
| Outlets at stockout risk | 3 |
| Open actions | 6 |
| Vendor PO risk rows | 0 |

The zero Vendor PO risk result is valid for March. It must not silently pull a
January PO merely to keep the table non-empty.

## Part A - Replace Query 28

1. In Zoho Analytics, open **Data**.
2. Open `28_fact_ct_menu_impact.sql`.
3. Select **Edit Design**.
4. Replace the SQL with the complete contents of:
   `02_QUERY_TABLES/28_fact_ct_menu_impact.sql`.
5. Click **Execute Query**.
6. Confirm that the preview has rows and no parsing or invalid-column error.
7. Click **Save**.
8. Wait for the dependent reports to finish refreshing.

Only Query 28 must be replaced for the Page 1 value correction. Queries 1-27
do not need to be re-saved.

## Part B - Refresh The Three Query 28 Views

Open and refresh these existing Page 1 elements:

1. **Menu Items At Risk**
2. **Stockout Sales At Risk**
3. **Menu Impact Detail**

Keep their report settings:

| Element | Data column / measure | Display |
| --- | --- | --- |
| Menu Items At Risk | `menu_item_code` | Count Distinct |
| Stockout Sales At Risk | `allocated_forecast_net_sales_at_risk` | Sum |
| Menu Impact Detail | Query 28 detail columns | Sort allocated value descending |

Do not sum `forecast_net_sales_at_risk`. It repeats when one menu item depends
on multiple risky ingredients. Only the allocated field is additive.

## Part C - Replace Source Period With A Date Range

The synthetic `month_01` to `month_03` codes are lineage fields. They are not
the final business-facing time control.

1. Open the Page 1 dashboard in **Edit Design**.
2. Remove the visible **Source Period** user filter from the page.
3. Click **Add User Filters**.
4. Choose **Timeline Filter**.
5. Set its label to **Date Range**.
6. Use a custom start/end range and select March for the current validation.
7. Open the filter's **Map Filter to Reports** or equivalent mapping screen.
8. Map each report to the physical date column below.

| Query Table | Date column |
| --- | --- |
| `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `28_fact_ct_menu_impact.sql` | `snapshot_date` |
| `38_fact_ct_expiry_risk.sql` | `as_of_date` |
| `36_fact_ct_risky_po.sql` | `as_of_date` |

Do not map the filter to `source_period_code`.

For the Zoho Page 1 dashboard, keep only the controls that can be mapped
reliably:

1. Date Range
2. Outlet
3. Ingredient Category
4. Action Owner

Region and risk severity remain available in the custom portal, where the
gateway filters the returned rows consistently. They do not need to be forced
into the Zoho dashboard if Zoho cannot map them to every report.

## Part D - Validate Page 1

Select the March date range and no outlet/category/owner restriction. Confirm:

| Check | Expected |
| --- | ---: |
| Query 28 rows | 302 |
| Distinct menu items at risk | 110 |
| Stockout sales at risk | INR 411,695.50 |
| Expiry risk value | INR 271,399.12 |
| Open actions | 6 |
| Vendor PO risk rows | 0 |

Minor display rounding is acceptable. A materially different total is not.

### Why Some Expiry Vendor And PO Cells Are Blank

The March expiry demo has 68 rows:

- 26 receipt-linked rows, worth INR 130,382.35, can carry GRN, PO and vendor
  lineage.
- 42 opening-stock estimate rows, worth INR 141,016.77, have no captured
  receipt lineage, so vendor and PO are intentionally blank.

Do not fill those cells with synthetic vendor or PO identifiers. Show
`Opening stock estimate` or `Not traceable to receipt` in the custom interface.
Expiry remains explicitly labelled as a synthetic estimate because the POSIST
batch/expiry module is unavailable.

### Where The Recommended Actions Come From

`recommended_action`, `action_owner`, `due_band`, and similar instructions are
model outputs created by CASE rules in Queries 27, 36 and 38. They are not
fields supplied by POSIST. The UI labels them as model recommendations so they
cannot be mistaken for source-system instructions.

## Part E - Prepare Page 2

Re-save only these updated files, in order:

1. `29_sum_ct_procurement_funnel.sql`
2. `30_sum_ct_vendor_scorecard.sql`
3. `31_sum_ct_price_movement.sql`

Do this for each file:

1. Open the Query Table in **Data**.
2. Click **Edit Design**.
3. Select all existing SQL and replace it with the complete matching file from
   `02_QUERY_TABLES`.
4. Click **Execute Query**.
5. Confirm that the preview contains the new columns listed below.
6. Click **Save**.
7. Wait for dependent views to refresh before continuing.

| Query Table | Columns that must now be visible |
| --- | --- |
| Query 29 | `po_date`, `po_status`, `item_code`, `item_name`, `category_name`, `canonical_uom` |
| Query 30 | the same filter columns, plus `otif_success_line_count`, `eligible_closed_line_count`, `received_qty`, `ordered_qty`, `eligible_lead_time_deviation_days_total`, `eligible_lead_time_line_count` |
| Query 31 | `current_purchase_qty`, `current_purchase_value`, `previous_unit_price`, `current_unit_price`, `price_change_amount`, `price_change_percent`, `absolute_price_change_percent`, `price_change_value_impact`, `price_movement_direction` |

`price_comparison_key` is no longer required. The Top Price Movement report is
a table built from the visible business fields in Query 31.

Keep every Aggregate Formula you already created. Add only these three formulas
to Query 30 for the vendor scorecard:

```text
Q30 Vendor OTIF %
if(sum("eligible_closed_line_count") <> 0, sum("otif_success_line_count") / sum("eligible_closed_line_count") * 100, null)
```

```text
Q30 PO Fill Rate %
if(sum("ordered_qty") <> 0, sum("received_qty") / sum("ordered_qty") * 100, null)
```

```text
Q30 Avg Lead Deviation Days
if(sum("eligible_lead_time_line_count") <> 0, sum("eligible_lead_time_deviation_days_total") / sum("eligible_lead_time_line_count"), null)
```

Use Percentage for the first two and Decimal Number for the third. If Zoho
renders a ratio 100 times too large, remove `* 100` but keep Percentage format.

## Part F - Configure Page 2 Filters

Open `CT_PAGE_2_Procurement_Vendor_Capital` in **Edit Design**.

Delete these duplicate report-only controls from the dashboard filter bar:

- the extra Raw Material control sourced only from Query 23;
- the extra Vendor control sourced only from Query 23;
- the extra UOM control sourced only from Query 23;
- `As-of Source Period`.

Keep UOM as a control inside the Ingredient Price Trend report only. It must not
pretend to filter the whole page.

Create these dashboard user filters in this order:

1. **Date Range** - Timeline Filter
2. **Region** - Multi Select
3. **Outlet** - Multi Select
4. **Ingredient Category** - Multi Select
5. **Vendor** - Multi Select
6. **Raw Material** - Multi Select or Search
7. **PO Status** - Multi Select

For **Date Range**, open **Map Filter to Reports** and map:

| Query Table | Date column |
| --- | --- |
| `29_sum_ct_procurement_funnel.sql` | `po_date` |
| `30_sum_ct_vendor_scorecard.sql` | `po_date` |
| `31_sum_ct_price_movement.sql` | `price_as_of_date` |
| `22_fact_ct_purchase_order.sql` | `po_date` |
| `24_fact_ct_po_receipt_line.sql` | `po_date` |
| `23_fact_ct_purchase_receipt.sql` | `receipt_date` |
| `36_fact_ct_risky_po.sql` | `po_date` |
| `05_std_ct_inventory_snapshot.sql` | `snapshot_date` |
| `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `35_sum_ct_financial_leakage.sql` | `as_of_date` |
| `38_fact_ct_expiry_risk.sql` | `as_of_date` |

Map the remaining Page 2 filters exactly:

| Report source | Outlet | Region | Category | Vendor | Raw Material | PO Status |
| --- | --- | --- | --- | --- | --- | --- |
| Query 29 | `outlet_code` | outlet lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 30 | `outlet_code` | outlet lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 31 | `outlet_code` | outlet lookup `region` | `category_name` | `vendor_name` | `item_code` | leave unmapped |
| Query 22 | `outlet_code` | outlet lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 24 | `outlet_code` | outlet lookup `region` | `category_name` | `vendor_name` | `item_code` | `po_status` |
| Query 23 | `outlet_code` | outlet lookup `region` | `category_name` | `vendor_name` | `item_code` | leave unmapped |

If the Query Table does not expose a field, leave that report unmapped. Do not
map a similarly named but semantically different column.

### Rebuild `CT_P2_Top_Price_Movement`

The existing R04 definition is invalid until Query 31 has been re-saved.

1. Click **Create > New Report > Tabular View**.
2. Select `31_sum_ct_price_movement.sql`.
3. Name it `CT_P2_Top_Price_Movement`.
4. Add columns in this order:
   `item_name`, `vendor_name`, `canonical_uom`, `previous_unit_price`,
   `current_unit_price`, `price_change_amount`, `price_change_percent`,
   `price_change_value_impact`.
5. Open **Filters**.
6. Add `price_movement_direction`.
7. Choose **Individual Values**.
8. Include only `INCREASE`, `DECREASE`, and `NO_CHANGE`.
9. Do not include `NO_BASELINE`.
10. Sort `absolute_price_change_percent` descending.
11. Format Previous, Current, Change and Value Impact as INR.
12. Format Change % as percentage with two decimals.
13. Save and add this view to Page 2.

No Aggregate Formula is required for this table.

### Keep these report-specific settings

| View | Fixed/report-only setting |
| --- | --- |
| `CT_P2_Expected_Delivery_Breach` | `delayed_po_flag`: Individual Values, include `1` |
| `CT_P2_Ingredient_Price_Trend` | choose exactly one Raw Material and one UOM inside the report |
| `CT_P2_Top_Price_Movement` | exclude `NO_BASELINE`; rank by `absolute_price_change_percent` |
| Price Watch KPI | Count Distinct `item_code`; do not exclude `NO_BASELINE` |

## Part G - Validate Page 2

Select 01 March 2026 through 31 March 2026 and clear every other filter.

| KPI | Expected |
| --- | ---: |
| Ordered gross value | INR 1,565,981.32 |
| Open PO liability | INR 177,145.39 |
| Delayed PO value | INR 156,529.83 |
| Vendor OTIF | 53.70% |
| Price Watch | 42 ingredients |

Price Watch includes all 42 current ingredient price observations. Of these,
39 have a comparable prior-period series and 3 are `NO_BASELINE`. Exclude
`NO_BASELINE` rows from top price increase/decrease rankings, but do not exclude
them from the Price Watch count.

Then test one filter at a time:

1. Select one Outlet. All five KPIs and all six Page 2 reports must refresh.
2. Select one Category. The three PO KPIs, OTIF, Price Watch, and all applicable
   reports must refresh.
3. Select one Vendor. All five KPIs and all vendor-applicable reports must
   refresh.
4. Select one PO Status. Query 29, Query 30, Query 22 and Query 24 views must
   refresh; Query 23 and Query 31 views must remain unchanged.
5. Select one Raw Material. Every item-aware view must refresh.
6. Change the Date Range. No table may continue showing rows outside that range.

The live dashboard audit that produced these corrections is documented in
`docs/LIVE_P2_DASHBOARD_AUDIT_2026-07-27.md`.

## Final Build Boundary

Zoho remains the governed analytics and data-refresh layer. The GitHub Pages
portal renders the ABNAH presentation from allowlisted Query Table rows through
the secured gateway. It does not embed the Zoho dashboard UI.

The complete production authentication and deployment procedure is in
`11_GITHUB_PAGES_ZOHO_AUTH_SETUP.md` inside the final implementation pack.
