# ABNAH Zoho Build, Filter And Runtime Handoff Sequence

## Resume Point

The 38 numbered Query Tables already exist. For the current Page 2 correction,
re-save only:

1. `29_sum_ct_procurement_funnel.sql`
2. `30_sum_ct_vendor_scorecard.sql`
3. `31_sum_ct_price_movement.sql`

Keep the four existing Aggregate Formulas:

| Query | Formula |
| --- | --- |
| Query 23 | `Weighted Unit Price` |
| Query 24 | `PO Fill Rate %` |
| Query 24 | `Vendor OTIF %` |
| Query 25 | `Menu Gross Margin %` |

Add the three Query 30 formulas listed in
`PAGE_1_AND_PAGE_2_CORRECTIONS.md`. Do not delete any formula that an existing
report may still use.

## Final Architecture

```text
Zoho Query Tables
        |
        | authenticated metadata + asynchronous JSON exports
        v
Supabase Edge Function
        |
        | approved rows for selected page and date range
        v
GitHub Pages custom control tower
```

Zoho dashboards remain native validation surfaces. The production custom
portal does not embed the Zoho dashboard, individual reports, KPI Widgets or
Zoho filter UI.

KPI Widgets remain dashboard-only. Saved chart, pivot, summary and tabular
views should still be created because they validate the business logic in Zoho,
but their Share URLs are not runtime dependencies.

## Current Build Order

1. Apply the Page 1 Query 28 correction if it is not already saved.
2. Re-save Page 2 Queries 29, 30 and 31.
3. Add the three Query 30 scorecard formulas.
4. Correct the Page 1 Date Range mapping.
5. Correct the Page 2 Date Range and dimension mappings.
6. Rebuild only `CT_P2_Top_Price_Movement`.
7. Reconcile the Page 1 and Page 2 acceptance values.
8. Configure Supabase and Zoho OAuth.
9. Verify the custom GitHub Pages portal against the same date/filter cases.

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

For every KPI/report:

1. Open the dashboard filter's **Map Filter to Reports** screen.
2. Select the exact physical field from
   `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`.
3. Leave incompatible reports unmapped.
4. Apply fixed definitions in the report Filter shelf with
   **Individual Values > Include**.
5. Never type SQL comparison expressions into the dashboard filter UI.

## URL Handoff

No dashboard or individual-report URL is required for the custom control tower.
Do not commit public `open-view` links as production configuration.

For local QA only:

1. Copy `config/zoho-reference-links.example.json` to
   `config/zoho-reference-links.local.json`.
2. Paste dashboard links or report links into the local file.
3. Use them only to compare Zoho output with the custom portal.
4. Keep the local file uncommitted.

The old `abnah-zoho-view-handoff/v4` files remain backward-compatible developer
artifacts. They are not the final runtime integration.

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
