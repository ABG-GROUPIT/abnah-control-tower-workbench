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

Zoho KPI Widgets exist only inside dashboards. They cannot be treated as
standalone shareable report views. Build and secure these four dashboards:

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
        v
5 KPI Widgets + saved reports inside each page dashboard
        |
        | dashboard User Filters
        v
4 secured-with-login dashboard iframe URLs
        |
        v
ABNAH external portal: one complete dashboard per page
```

Do not create 20 standalone KPI embed URLs. The portal handoff contains four
dashboard URLs.

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
9. Share and embed the complete page dashboard.

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

Dashboard User Filters are the live controls. A KPI Widget does not need or
provide its own togglable filter.

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

Repeat once per page dashboard:

1. Open the completed dashboard in View Mode.
2. Choose **Share** and grant the company Zoho viewer account read access.
3. Choose **Embed**.
4. Select secured **Access with Login**.
5. Keep the dashboard interactive so its User Filters work.
6. Copy only the iframe `src` URL.
7. Open the ABNAH portal **Configure** drawer.
8. Select the matching page.
9. Paste the one dashboard URL and save locally.

The handoff format is:

```text
config/zoho-secured-embed-handoff.example.json
abnah-zoho-dashboard-embed-handoff/v3
```

It stores four dashboard URLs and no credentials or rows.

## Authentication

The viewer signs into Zoho Analytics in a normal browser tab and returns to the
portal. The secured dashboard iframe reuses that Zoho session. Zoho remains the
access-control boundary.

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

After these checks, connect its secured dashboard URL and continue to the next
page.
