# ABNAH Zoho Build, Filter And Runtime Handoff Sequence

## Resume Point

The 38 numbered Query Tables already exist. Queries 28, 29, 30 and 31 have
already been corrected and re-saved. The three Query 30 scorecard formulas have
also been added.

Do not re-save another Query Table and do not delete an Aggregate Formula. The
next action is the named Page 1 Timeline mapping correction, followed by the
Page 2 filter cleanup.

Keep the four existing Aggregate Formulas:

| Query | Formula |
| --- | --- |
| Query 23 | `Weighted Unit Price` |
| Query 24 | `PO Fill Rate %` |
| Query 24 | `Vendor OTIF %` |
| Query 25 | `Menu Gross Margin %` |

The three Query 30 formulas listed in `PAGE_1_AND_PAGE_2_CORRECTIONS.md` should
now remain unchanged.

## Final Architecture

```text
Zoho Query Tables
        |
        +-- authenticated metadata + asynchronous JSON exports
        v
Supabase Edge Function
        |
        +-- approved rows and secured visual URL handoff
        v
GitHub Pages hybrid control tower
        |
        +-- custom KPI, action, evidence and detail surfaces
        +-- selected Zoho-native map, bar and line views
```

Zoho dashboards remain native validation and fallback surfaces. The production
portal does not place a whole dashboard iframe behind each custom page. It
embeds selected individual views where Zoho rendering is stronger and uses API
rows for the custom operational surfaces.

KPI Widgets remain dashboard-only. Saved chart, pivot, summary and tabular
views should still be created because they validate the business logic in Zoho,
but their Share URLs are not runtime dependencies.

## Current Build Order

1. In Page 1, explicitly map `snapshot_date` on `Menu Items Impacted`,
   `Stockout Risk (Net Sales)` and `CT_P1_Menu_Impact_Detail`.
2. Confirm Page 1 March Stockout Risk changes from the all-period `9.76L` to
   `INR 411,695.55`.
3. Remove the exact four obsolete Page 2 controls named in
   `PAGE_1_AND_PAGE_2_CORRECTIONS.md`.
4. Add the Page 2 Date Range Timeline Filter.
5. Map every named Page 2 KPI/report to its exact physical date column.
6. Merge Outlet, Category, Vendor, Raw Material and PO Status by selecting the
   exact table columns in **Edit Column Mapping**.
7. Rebuild only `CT_P2_Top_Price_Movement` if it is not already present.
8. Reconcile the Page 1 and Page 2 acceptance values.
9. Fill the ignored handoff file in `portal-handoff`.
10. Configure Supabase and Zoho OAuth.
11. Verify the custom GitHub Pages portal against the same date/filter cases.

## Governing Guides

Keep these open:

1. `PAGE_1_AND_PAGE_2_CORRECTIONS.md`
2. `zoho_control_tower_v2_dashboard_click_by_click.md`
3. `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`
4. `ZOHO_DASHBOARD_EXPECTED_RESULTS.md`
5. `ZOHO_PORTAL_RUNTIME.md`

## KPI Widget Rule

For an additive KPI:

1. Add a KPI Widget inside the Zoho dashboard.
2. Select the exact numbered Query Table.
3. Select the physical field named in the guide.
4. Choose Sum, Count or Count Distinct as documented.
5. Leave Group By empty.
6. Apply only the documented fixed report filter.
7. Map dashboard user filters from the dashboard editor.

For OTIF and other ratio metrics, use the saved Summary View built from the
approved Aggregate Formula. Do not search for an Aggregate Formula in a direct
KPI Widget's Data Column list.

## Filter Rule

Page 1 and Page 2 use Date Range and Outlet as their common controls. Page 3
and Page 4 retain `source_period_code` only where their current synthetic
design requires it.

For Date Range:

1. Edit the Timeline Filter.
2. Expand **Timeline Filter Column Mapping**.
3. Select one physical date column per table.
4. Open **More > Options** on each named KPI/report.
5. Use **Mapping Timeline Filter** or **Customize** to select that object's
   exact date column from
   `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`.
6. Do not type a table name or column name.

For dimension controls:

1. Edit the merged User Filter.
2. Click **Edit Column Mapping**.
3. Select the exact fields from the mapping matrix.
4. Leave incompatible reports unmapped.
5. Apply fixed definitions in the report Filter shelf with
   **Individual Values > Include**.
6. Never type SQL comparison expressions into the dashboard filter UI.

## URL Handoff

The Query Table API is sufficient for KPI cards, custom action queues and
underlying-data tables. The hybrid native visual slots additionally require
secured Zoho view URLs.

1. Share each saved view with **Access with Login** for the approved viewer.
2. Copy
   `portal-handoff/ABNAH_PORTAL_HANDOFF_TEMPLATE.json` to the ignored
   `ABNAH_PORTAL_HANDOFF.local.json`.
3. Fill the runtime URLs, OAuth placeholders, all 19 report slots and four
   dashboard fallback slots in that one local file.
4. Run the validator command in `portal-handoff/README.md`.
5. Store the completed visual URL section through the authenticated Supabase `/config`
   endpoint; keep the committed template blank.
6. The portal embeds `p1-risk-map`, `p2-funnel` and `p2-price-trend`.
7. Other report URLs open from evidence drilldowns; dashboard URLs remain
   external page fallbacks.

Do not commit public `open-view` links or use them as the authentication
boundary. The `abnah-zoho-view-handoff/v4` contract is the production visual
handoff; it contains URLs only, never credentials or report rows.

## Authentication

1. The user opens the GitHub Pages portal.
2. The portal calls the Supabase backend status endpoint.
3. **Sign in with Zoho** redirects to Zoho India OAuth.
4. Supabase exchanges the code server-side.
5. Supabase verifies access to the configured ABNAH workspace.
6. Supabase stores encrypted Zoho tokens and returns an opaque portal session.
7. The browser requests allowlisted Page 1 or Page 2 Query Table data.
8. Logout revokes the portal session.

The frontend never receives the Zoho client secret, refresh token, Supabase
service-role key or token-encryption key.

## Stop Gate

Do not present Page 1 or Page 2 as complete until:

- all five KPI values match the March acceptance guide;
- Date Range uses physical date fields and no row leaks outside the range;
- Outlet changes every applicable KPI and report;
- Category, Vendor, Item and PO Status change every compatible object;
- Price Watch includes no-baseline observations;
- Top Price Movement excludes no-baseline observations and uses the visible
  Query 31 business fields;
- the GitHub Pages portal exposes no data before successful Zoho sign-in;
- no screenshot, operational export, credential or public report link has been
  committed.
