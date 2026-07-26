# ABNAH Zoho Dashboard Build, Filter, Embed And Handoff Sequence

## Resume Point

The 38 numbered Query Tables, lookups and earlier Aggregate Formulas already
exist. Do not restart that work.

Keep and use these four Aggregate Formulas:

| Query | Aggregate Formula |
| --- | --- |
| `23_fact_ct_purchase_receipt.sql` | `Weighted Unit Price` |
| `24_fact_ct_po_receipt_line.sql` | `PO Fill Rate %` |
| `24_fact_ct_po_receipt_line.sql` | `Vendor OTIF %` |
| `25_fact_ct_menu_profitability.sql` | `Menu Gross Margin %` |

Other earlier formulas may remain unused. Do not delete them while reports may
still depend on them.

## Correct Delivery Architecture

Build every chart, pivot, summary, and tabular object as a saved secured view.
The custom portal places 19 of those views into its own layout. Also build and
secure these four complete dashboards as native validation/fallback surfaces:

```text
CT_PAGE_1_Risk_Action_Center
CT_PAGE_2_Procurement_Vendor_Capital
CT_PAGE_3_Consumption_Menu_Profitability
CT_PAGE_4_SCM_Explorer_Data_Quality
```

```text
38 Query Tables
        |
        v
saved chart / pivot / summary / tabular reports
        |
        +-----------------------------+
        |                             |
        v                             v
19 individual secured views    4 complete dashboards
        |                             |
        | custom ZOHO_CRITERIA        | native filters/KPI Widgets
        v                             v
custom GitHub Pages layout      native fallbacks
```

Do not create 20 standalone KPI embed URLs. KPI Widgets remain dashboard-only.
The v4 portal handoff contains 19 saved-report URLs and four dashboard fallback
URLs.

Saved chart, pivot, summary and tabular views are still required: build,
validate, share, and add each one to its page dashboard. Paste each individual
secured URL into the exact matching custom portal slot.

The custom portal synchronizes only compatible individual report views. The
complete dashboards preserve native filtering and live KPI Widgets, but open
separately as fallbacks. Cross-origin Zoho iframe pixels remain under Zoho
control.

## Governing Guides

Keep these open:

1. `zoho_control_tower_v2_dashboard_click_by_click.md`
2. `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`
3. `ZOHO_DASHBOARD_EXPECTED_RESULTS.md`
4. `ABNAH_REFERENCE_TO_ZOHO_CAPABILITY_MATRIX.md`

## Build Order

Build Page 4 first, then Page 3, Page 2 and Page 1. This validates descriptive
sources before executive action logic.

For each page:

1. Create the saved chart, pivot, summary and tabular reports listed in the
   click-by-click guide.
2. Validate each report at `month_03 / All outlets`.
3. Create the page dashboard with the exact `CT_PAGE_...` name.
4. Add the saved reports to the dashboard.
5. Create the five KPI Widgets inside the dashboard.
6. Add and map the dashboard User Filters.
7. Reconcile All outlets, `OUT001`, `OUT002` and `OUT003`.
8. Apply colors, number formats and layout only after values reconcile.
9. Share each saved view and the complete page dashboard.
10. Connect the individual views and dashboard fallback in the portal.

## KPI Widget Rule

For additive values:

1. Add a KPI Widget from inside the dashboard.
2. Select the exact numbered Query Table.
3. Select the exact physical Data Column.
4. Use Sum, Count or Count Distinct as documented.
5. Leave Group By empty.
6. Apply fixed business filters in the KPI design where specified.
7. Let dashboard User Filters provide the togglable period/outlet scope.

For `Vendor OTIF %` and `Menu Gross Margin %`, create a saved Summary View from
the Aggregate Formula and place that view in the dashboard. Do not search for
an Aggregate Formula in the KPI Widget physical Data Column list.

## Filter Rule

Dashboard User Filters are the live controls inside native fallbacks. A KPI
Widget does not need or provide its own togglable filter.

For every placed KPI/report:

1. Open **More > Options**.
2. Keep **Apply Dashboard Filters** enabled only when the object has a valid
   mapped field.
3. Use **Customize/Map Columns** to select the exact field.
4. Disable current-period filtering for historical trends.
5. Disable period/outlet filtering for Query 34 model-wide quality objects.

Use the complete per-query matrix in:

```text
ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md
```

Only As-of Source Period and Outlet are broadly shared. Category, item, vendor,
PO status, UOM and exception filters are scoped to compatible facts. A filter
that does not exist at a summary table's grain must not be faked.

For the custom page, use the same field/grain rule. The portal adds
`ZOHO_CRITERIA` only to the saved views mapped in its report contract.

## Fixed Filters

These remain fixed inside reports/widgets:

| Object family | Field | Include |
| --- | --- | --- |
| Page 1 stockout KPIs/map/action/detail | `risk_type` | `STOCKOUT` |
| Page 2 Expected Delivery Breach | `delayed_po_flag` | `1` |
| Page 3 Leakage Rank | `consumption_variance_direction` | `OVER_CONSUMPTION` |
| Page 3 Low Consumption Check | `consumption_variance_direction` | `UNDER_CONSUMPTION` |
| Each Page 4 quality tile | `exception_type` | Its assigned exception code |

Do not type SQL comparison syntax into the dashboard filter interface. Select
the physical field and tick the required value.

## Share And Embed

For each of the 19 saved report views:

1. Open the view in View Mode.
2. Share it with the company Zoho viewer account.
3. Generate secured **Access with Login**.
4. Copy only the secured HTTPS URL.
5. Paste it into the matching named portal report slot.

For each complete page dashboard:

1. Share it with the same viewer.
2. Generate secured **Access with Login**.
3. Keep it interactive so native User Filters work.
4. Paste it into that page's **Native fallback** slot.
5. Save the shared handoff through the verified portal.

The handoff format is:

```text
config/zoho-secured-embed-handoff.example.json
abnah-zoho-view-handoff/v4
```

It stores 19 report URLs, four dashboard fallback URLs, and no credentials or
rows.

## Authentication

The viewer selects **Continue with Zoho**. The Supabase Edge Function completes
OAuth, verifies access to the configured Zoho workspace, and issues an opaque
portal session. Zoho still enforces access to each secured report/dashboard.

Do not use:

- public access;
- without-login links on the Pro-plan POC;
- passwords, OAuth tokens or client secrets in browser configuration;
- raw operational rows in GitHub or the portal.

## Stop Gate

Do not embed a page until:

- all five KPI values match the acceptance guide;
- the outlet selector changes every compatible KPI/report;
- scoped filters affect only mapped objects;
- historical trends retain all three periods;
- Query 34 model-wide rows remain visible;
- one Canonical UOM is used for quantity comparisons;
- the dashboard opens for the intended Zoho viewer account.

After these checks, connect its individual report URLs and secured dashboard
fallback, then continue to the next page.
