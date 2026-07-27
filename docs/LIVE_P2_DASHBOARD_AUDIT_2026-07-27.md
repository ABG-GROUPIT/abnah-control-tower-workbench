# Live Page 2 Dashboard Audit - 27 July 2026

## Scope

The live Zoho dashboard `CT_PAGE_2_Procurement_Vendor_Capital` was reviewed
interactively. Every visible filter was opened and tested separately against
the KPI cards and report views.

No screenshot or operational row extract is stored in this repository. This
document records only the schema behavior, aggregate results and correction
decisions understood from the review.

## Baseline Seen In Zoho

With the dashboard in its original all-period state:

| KPI | Displayed |
| --- | ---: |
| Ordered Value | INR 16L |
| Open PO | INR 2L |
| Delayed PO | INR 2L |
| Avg Vendor OTIF | 51.7% |
| Items to Price Watch | 43 |

These are not the March validation values. They combine periods because several
views were not mapped to the active period control.

## Filters Actually Present

| Visible label | Source field | Observed scope |
| --- | --- | --- |
| As-of Source Period | Query 29 `source_period_code` | Procurement Funnel only |
| Raw Material | Query 23 `item_code` | Ingredient Price Trend only |
| Vendor | Query 23 `vendor_name` | Ingredient Price Trend only |
| UOM | Query 23 `canonical_uom` | Ingredient Price Trend only |
| Region | Query 37 `region` | only `North` exists in the demo |
| Raw Material Category | Query 22 `category_name` | PO detail views; KPI cards did not change |
| Vendor Name (Global) | Query 24 `vendor_name` | OTIF and scorecard; other KPIs did not change |
| PO Status | Query 22 `po_status` | PO detail views; KPI cards did not change |
| Raw Material (Global) | Query 22 `item_code` | PO detail views; KPI cards did not change |
| Outlet | Query 22 `outlet_code` | PO KPIs and detail; Price Watch did not change |

The duplicated Raw Material and Vendor controls are not equivalent. Three
controls are report-specific but visually appear global.

## Tested Behavior

| Test | Result |
| --- | --- |
| Outlet `OUT001` | Ordered INR 6L, Open INR 1L, Delayed INR 1L and OTIF 56.1%; Price Watch stayed 43 |
| Category `Dairy` | PO detail filtered; all five KPI cards stayed unchanged |
| Vendor `FreshDairy Foods NCR` | OTIF changed to 42.9% and scorecard reduced to one vendor; PO KPIs and Price Watch stayed unchanged |
| PO Status `Pending` | PO detail filtered; KPI cards stayed unchanged |
| Raw Material `ING001` | PO detail reduced to the item; KPI cards stayed unchanged |
| Source Period `month_01` / `month_02` / `month_03` | Procurement Funnel changed; OTIF, Price Watch and detail tables remained all-period |
| Trend-only Raw Material, Vendor and UOM | only Ingredient Price Trend changed |

The Expected Delivery Breach table showed January rows while `month_03` was
selected. Pending By Vendor contained January, February and March rows under
the same selection.

## Root Causes

1. Queries 29 and 30 grouped away `po_date`, item, category and PO status before
   dashboard filtering.
2. Query 31 did not expose the plain business columns expected by the R04
   instructions in the user's current saved version.
3. `source_period_code` was presented as a business time filter even though it
   was mapped to only one report.
4. Report-specific filters were placed beside global controls without a visual
   distinction.
5. The Top Price Movement requirement was interpreted as a chart with a
   composite key. ABNAH's reference and KPI workbook specify a ranked table
   showing previous price, current price, change and change percentage.

## Approved Corrections

1. Re-save Queries 29, 30 and 31 from the corrected SQL pack.
2. Use one Date Range Timeline Filter.
3. Map PO-based views to `po_date`, receipt views to `receipt_date`, and price
   movement to `price_as_of_date`.
4. Keep only one global Outlet, Region, Category, Vendor, Raw Material and PO
   Status control.
5. Keep UOM inside Ingredient Price Trend because it is not applicable to every
   Page 2 view.
6. Build Top Price Movement as a Tabular View from Query 31.
7. Include `NO_BASELINE` in Price Watch, but exclude it from movement ranking.

## March Acceptance Baseline

For 01 March 2026 through 31 March 2026 with all other filters cleared:

| KPI | Expected |
| --- | ---: |
| Ordered gross value | INR 1,565,981.32 |
| Open PO exposure | INR 177,145.39 |
| Delayed PO value | INR 156,529.83 |
| Vendor OTIF | 53.70% |
| Price Watch | 42 |

Price movement contains 39 comparable ingredients and 3 records without a
prior-period baseline.

## Acceptance Rule

A filter passes only when every applicable KPI and report changes and every
non-applicable report remains intentionally unmapped. A report fails if it
continues showing a row whose physical date is outside the selected Date Range.
