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

Queries 29 and 30 expose `as_of_date` for the Timeline Filter. Query 31 exposes
`price_as_of_date`, keeps ingredient category, compares like UOM with like UOM,
and retains new price observations as `NO_BASELINE`.

Existing Page 2 reports do not need to be recreated after these queries are
saved. Refresh them and verify their selected columns.

## Part F - Configure Page 2 Filters

Create one **Date Range** Timeline Filter and map it as follows:

| Query Table | Date column |
| --- | --- |
| `29_sum_ct_procurement_funnel.sql` | `as_of_date` |
| `30_sum_ct_vendor_scorecard.sql` | `as_of_date` |
| `31_sum_ct_price_movement.sql` | `price_as_of_date` |
| `22_fact_ct_purchase_order.sql` | `as_of_date` |
| `24_fact_ct_po_receipt_line.sql` | `as_of_date` |
| `23_fact_ct_purchase_receipt.sql` | `receipt_date` |
| `36_fact_ct_risky_po.sql` | `as_of_date` |
| `05_std_ct_inventory_snapshot.sql` | `snapshot_date` |
| `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `35_sum_ct_financial_leakage.sql` | `as_of_date` |
| `38_fact_ct_expiry_risk.sql` | `as_of_date` |

Use these Page 2 controls:

1. Date Range
2. Outlet
3. Vendor
4. Ingredient Category
5. Item
6. PO Status

Map a control only to reports whose source table contains the corresponding
column. Leaving a report unmapped is better than mapping an unrelated field.

## Part G - Validate Page 2

For the March demo selection, the custom portal baseline is:

| KPI | Expected |
| --- | ---: |
| Ordered gross value | about INR 1.57M |
| Delayed PO value | about INR 180K |
| Open PO liability | about INR 160K |
| PO fill rate | about 53.7% |
| Price Watch | 42 ingredients |

Price Watch includes all 42 current ingredient price observations. Of these,
39 have a comparable prior-period series and 3 are `NO_BASELINE`. Exclude
`NO_BASELINE` rows from top price increase/decrease rankings, but do not exclude
them from the Price Watch count.

## Final Build Boundary

Zoho remains the governed analytics and data-refresh layer. The GitHub Pages
portal renders the ABNAH presentation from allowlisted Query Table rows through
the secured gateway. It does not embed the Zoho dashboard UI.

The complete production authentication and deployment procedure is in
`11_GITHUB_PAGES_ZOHO_AUTH_SETUP.md` inside the final implementation pack.
