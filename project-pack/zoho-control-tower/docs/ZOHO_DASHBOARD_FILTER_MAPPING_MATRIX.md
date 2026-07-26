# Zoho Dashboard KPI, User Filter And Embed Contract

## Native Dashboard And Custom Portal Roles

Zoho KPI Widgets are dashboard elements. They are not standalone saved reports
and do not provide an independent Share/Embed action. Build these four secured
Zoho dashboards as native KPI/filter validation and fallback surfaces:

1. `CT_PAGE_1_Risk_Action_Center`
2. `CT_PAGE_2_Procurement_Vendor_Capital`
3. `CT_PAGE_3_Consumption_Menu_Profitability`
4. `CT_PAGE_4_SCM_Explorer_Data_Quality`

Each dashboard contains its five KPI Widgets plus its saved chart, pivot,
summary and tabular reports. The dashboard owns its native user filters.

The custom GitHub Pages portal separately embeds the 19 saved report views into
the approved external composition. Its page controls apply `ZOHO_CRITERIA`
only where the same field/grain mapping is valid. It does not embed a KPI
Widget separately.

Saved chart, pivot, summary and tabular reports must all be added to their
matching page dashboard and shared individually for the custom portal. The v4
handoff contains 19 individual report URLs plus four complete-dashboard
fallbacks.

This delivery correction does not require another SQL change, lookup rebuild,
or Aggregate Formula cleanup.

## Three Different Filter Types

| Type | Where it is created | User can change it | Purpose |
| --- | --- | --- | --- |
| Dashboard User Filter | Dashboard **Add User Filters** | Yes | Changes every explicitly mapped KPI/report on that page |
| Report-specific User Filter | Saved chart/table report | Yes | Optional narrow control shown only with that report |
| Fixed report filter | Report or KPI design | No | Enforces the business definition, such as stockout-only |

A KPI Widget does not need its own user-filter control. Once the widget is
inside a dashboard, the dashboard User Filter applies to it.

For every placed KPI/report, open **More > Options > Apply Dashboard Filters**.
Map the exact column listed below. Uncheck **Apply Dashboard Filters** when the
matrix says **Exclude**.

## Common Values

| Filter | Exact modeled field/value |
| --- | --- |
| As-of Source Period | `source_period_code`: `month_01`, `month_02`, `month_03`; default `month_03` |
| Outlet | `outlet_code`: `OUT001`, `OUT002`, `OUT003`; default All |
| Region | Query 37 lookup `region`; current synthetic value `North` |
| Canonical UOM | `canonical_uom`: `kg`, `litre`, `pcs`; never combine quantities across UOMs |

Use codes as filter keys. Display names may be shown to the user, but do not
map a dashboard filter through `outlet_name`.

# Page 1 - Risk Action Center

## Dashboard User Filters

Add: As-of Source Period, Outlet, Region, Stockout Severity, Ingredient
Category and Action Owner.

Do not add a live `Risk = Stockout/Expiry` toggle. The source families do not
share a complete risk field: Query 28 and Query 36 are already stockout-only,
while Query 38 is the expiry scenario. Keep stockout and expiry sections
visible separately.

| KPI/report family | Query | Period | Outlet | Region | Ingredient category | Severity/owner | Fixed condition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Outlets at risk, Open Actions, Outlet Risk Map, Action Center, Stockout Detail | `27_fact_ct_inventory_risk.sql` | `source_period_code` | `outlet_code` | Query 37 lookup `region` | `category_name` | `risk_severity`; `action_owner` | `risk_type` Include `STOCKOUT` |
| Menu Items at Risk, Stockout Sales at Risk, Menu Impact Detail | `28_fact_ct_menu_impact.sql` | `source_period_code` | `outlet_code` | Query 37 lookup `region` | Query 14 lookup `category_name` through `item_code` | `risk_severity`; owner excluded | None; Query 28 already contains risk rows |
| Expiry Risk Value and Expiry Detail Demo | `38_fact_ct_expiry_risk.sql` | `source_period_code` | `outlet_code` | `region` | `category_name` | `risk_severity`; `action_owner` | None; Query 38 is already the estimated expiry scenario |
| Vendor PO Risk | `36_fact_ct_risky_po.sql` | `source_period_code` | `outlet_code` | Query 37 lookup `region` | inherited `category_name` | `risk_severity`; owner excluded | None; Query 36 already contains open non-green PO rows |

Recommended values:

- Stockout Severity: `PURPLE`, `RED`, `AMBER`.
- Action Owner: `Procurement`, `Supply Chain`.

# Page 2 - Procurement, Vendor & Capital Control

## Dashboard User Filters

Add: As-of Source Period, Outlet, Region and Vendor as the primary controls.
Add Ingredient Category, Ingredient Item and PO Status as scoped controls.

| KPI/report family | Query | Period | Outlet/region | Vendor | Category/item | PO status | Fixed/exclusion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Monthly Purchase, Open PO Exposure, Delayed PO Value, Procurement Funnel, Pending by Vendor | `29_sum_ct_procurement_funnel.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name` | Exclude | Exclude | None |
| Vendor OTIF KPI, Vendor Performance Matrix, Vendor Scorecard | `24_fact_ct_po_receipt_line.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name` | `category_name`, `item_code` | `po_status` | None |
| Price Watch and Top Price Movement | `31_sum_ct_price_movement.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name` | Query 14 `category_name`; `item_code` | Exclude | Top 10 is a chart setting, not a user filter |
| Ingredient Price Trend and Vendor Price Comparison | `23_fact_ct_purchase_receipt.sql` | **Exclude** from current-period filter so all periods remain | `outlet_code`; Query 37 `region` | `vendor_name` | `category_name`, `item_code` | Exclude | Vendor comparison requires one `item_code` and one `canonical_uom` |
| PO Status Distribution and Expected Delivery Breach | `22_fact_ct_purchase_order.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name` | `category_name`, `item_code` | `po_status` | Breach report: `delayed_po_flag` Include `1` |
| Pending Ingredient Risk | `36_fact_ct_risky_po.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name` | `category_name`, `item_code` | `po_status` | Query already limits to open risky lines |
| Extended Vendor Explorer | `30_sum_ct_vendor_scorecard.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name` | Exclude | Exclude | None |

Exact PO Status values currently modeled:

- `Pending`
- `Partially Received`
- `Closed`
- `Cancelled`

The three Query 29 KPI Widgets cannot respond to Ingredient Category, Item or
PO Status because Query 29 is already aggregated to period/outlet/vendor.
Leaving those mappings blank is correct. Do not fake those filters.

# Page 3 - Consumption Variance And Menu Profitability

## Dashboard User Filters

Add As-of Source Period, Outlet and Region as shared controls. Keep menu filters
and ingredient filters visibly separate because they apply to different facts.

| KPI/report family | Query | Period | Outlet/region | Menu scope | Ingredient scope | UOM | Fixed/exclusion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Net Sales, Theoretical COGS, Gross Margin, Menu Items, Menu COGS, Category Contribution, Heatmap | `25_fact_ct_menu_profitability.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `super_category_name`, `category_name`, `menu_item_code` | Exclude | Exclude | None |
| Menu BCG, Margin Rank, Menu Ranking | `32_sum_ct_menu_profitability.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | inherited `super_category_name`, `category_name`, `menu_item_code` | Exclude | Exclude | None |
| Consumption Leakage KPI, Variance, Actual vs Theoretical | `21_fact_ct_consumption_variance.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | Exclude | `category_name`, `item_code` | `canonical_uom` for quantity views only | None |
| Consumption Bridge | `20_fact_ct_actual_consumption.sql` | **Exclude** when the chart must retain all three periods | `outlet_code`; Query 37 `region` | Exclude | inherited `category_name`, `item_code` | `canonical_uom`; require one value | None |
| Theoretical Consumption Detail | `19_fact_ct_theoretical_consumption.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | Exclude | `item_code` and Query 14 `category_name` | `canonical_uom` | None |
| Sales Trend | `18_fact_ct_sales.sql` | **Exclude** so the trend retains all dates/periods | `outlet_code`; Query 37 `region` | `super_category_name`, `category_name`, `item_code` | Exclude | Exclude | None |

Fixed report filters:

- `CT_P3_Consumption_Leakage_Rank`: `consumption_variance_direction` Include `OVER_CONSUMPTION`.
- `CT_P3_Low_Consumption_Check`: `consumption_variance_direction` Include `UNDER_CONSUMPTION`.

Do not map Canonical UOM to currency KPI Widgets. Do not map menu filters to
Queries 19-21. Do not map ingredient filters to Queries 18, 25 or 32.

# Page 4 - SCM Descriptive Explorer And Data Quality

## Dashboard User Filters

Add Current Period and Outlet for current-state SCM objects. Add Exception Type
only for Query 34. Region and the explorer-specific controls are optional.

| KPI/report family | Query | Period | Outlet/region | Detail fields | Exception Type | Fixed/exclusion |
| --- | --- | --- | --- | --- | --- | --- |
| Closing Stock, Open PO, Net Sales, Actual Consumption and Descriptive Explorer | `33_sum_ct_scm_monthly.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | No item/vendor grain | Exclude | None |
| SCM Monthly Trend | `33_sum_ct_scm_monthly.sql` | **Exclude** so all three periods remain | `outlet_code`; Query 37 `region` | No item/vendor grain | Exclude | None |
| Signed Consumption Variance KPI | `21_fact_ct_consumption_variance.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `category_name`, `item_code`, `canonical_uom` | Exclude | None |
| Consumption Variance Trend | `21_fact_ct_consumption_variance.sql` | **Exclude** so all periods remain | `outlet_code`; Query 37 `region` | `category_name`, `item_code`; UOM only for quantities | Exclude | None |
| Six quality tiles and Data Quality Detail | `34_fact_ct_data_quality_exception.sql` | **Exclude** | **Exclude** | Exclude | `exception_type` | Each tile has one fixed exception code |
| Sales Explorer | `18_fact_ct_sales.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `super_category_name`, `category_name`, `item_code` | Exclude | None |
| Item Explorer | `27_fact_ct_inventory_risk.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `category_name`, `item_code` | Exclude | None |
| PO Explorer | `24_fact_ct_po_receipt_line.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name`, `category_name`, `item_code`, `po_status` | Exclude | None |
| GRN Explorer | `23_fact_ct_purchase_receipt.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name`, `category_name`, `item_code` | Exclude | None |
| Vendor Explorer | `30_sum_ct_vendor_scorecard.sql` | `source_period_code` | `outlet_code`; Query 37 `region` | `vendor_name` | Exclude | None |
| Expiry Explorer Demo | `38_fact_ct_expiry_risk.sql` | `source_period_code` | `outlet_code`; `region` | `vendor_name`, `category_name`, `item_code` | Exclude | Estimated scenario only |

Query 34 contains model-wide exception rows with `source_period_code = ALL` and
`outlet_code = ALL`. Applying the period or outlet dashboard filter would hide
those valid controls, so Query 34 must be excluded from both.

Exact Query 34 exception values include:

- `NEGATIVE_STOCK`
- `ZERO_STOCK_WITH_DEMAND`
- `SOLD_ITEM_MISSING_RECIPE`
- `OPERATIONAL_ITEM_MISSING_MASTER`
- `UOM_MISMATCH_WITHOUT_CONVERSION`
- `OPEN_PO_MISSING_EXPECTED_DELIVERY`

# Click Sequence For Each Dashboard

1. Create the dashboard with the exact `CT_PAGE_...` name.
2. Add the saved chart, pivot, summary and tabular reports for that page.
3. Create the five KPI Widgets inside that dashboard.
4. Choose **Add User Filters**.
5. Add only the filters listed for that page.
6. Set the default As-of Source Period to `month_03`.
7. For every placed KPI/report, open **More > Options**.
8. Keep **Apply Dashboard Filters** enabled only for mappings marked Apply.
9. Choose **Customize/Map Columns** and select the exact physical field in the
   matrix.
10. Disable the filter for historical trends and Query 34 as specified.
11. Validate All outlets, `OUT001`, `OUT002` and `OUT003`.
12. Share the complete dashboard, choose secured **Access with Login**, and
    copy only the iframe `src` URL.
13. In the external portal, configure it as the matching page's native
    fallback. Configure the saved report views separately in their named slots.

# Acceptance Checks

Before embedding:

- changing Outlet changes every compatible KPI Widget and report on the page;
- changing a scoped filter changes only the explicitly mapped report families;
- historical trends still show all three periods;
- Query 34 model-wide rows remain visible;
- stockout objects remain stockout-only;
- quantity comparisons use one Canonical UOM;
- no KPI Widget is expected to have its own Share action.

Official Zoho references:

- [Dashboard user filters and column mapping](https://www.zoho.com/analytics/help/dashboard/filter.html)
- [KPI Widgets are dashboard elements](https://www.zoho.com/analytics/help/dashboard/kpi-widgets.html)
- [Secured dashboard embedding](https://www.zoho.com/analytics/help/publishing/embed-reports.html)
