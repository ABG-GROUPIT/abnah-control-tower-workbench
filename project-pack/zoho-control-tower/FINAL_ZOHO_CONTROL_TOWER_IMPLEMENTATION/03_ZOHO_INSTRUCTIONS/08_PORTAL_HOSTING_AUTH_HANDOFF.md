# Zoho Portal Hosting, Authentication And Handoff

## Final Architecture

```text
GitHub Pages custom ABNAH portal
        |
        | OAuth/session/config API
        v
Supabase Edge Function + private Postgres tables
        |
        | verifies workspace membership
        v
Zoho Analytics India
        |
        | 19 secured report views + 4 dashboard fallbacks
        v
Approved 38-Query-Table model
```

GitHub Pages is the only frontend host. The delivery portal is the separate
`/portal/` route linked from the Atlas; it is not an Atlas tab. No ChatGPT-hosted
or SharePoint-hosted copy is part of the production design.

## Responsibilities

GitHub Pages owns:

- the custom four-page visual shell and navigation;
- external page filters and `ZOHO_CRITERIA` generation;
- 19 individual chart, pivot, summary, or tabular view slots;
- four links to complete Zoho dashboards as native fallbacks;
- a configuration drawer for the URL-only v4 handoff.

Supabase owns:

- the Zoho OAuth callback and client secret;
- allowed-workspace verification;
- encrypted Zoho access/refresh tokens;
- opaque portal sessions;
- the shared, versioned URL-only handoff.

Zoho owns:

- Query Table execution and refreshed analytics data;
- saved report rendering, drills, tooltips, and exports;
- native dashboard KPI Widgets and Dashboard User Filters;
- report and dashboard sharing permissions.

Supabase stores no POSist rows, screenshots, dashboard values, or report
exports. GitHub stores no secrets.

## Verified Sign-In

1. `/portal/` checks the Supabase `/status` endpoint.
2. **Continue with Zoho** opens the Edge Function `/auth/start` route.
3. Supabase stores a one-time state hash and redirects to Zoho India OAuth.
4. Zoho returns to the Supabase `/auth/callback` route.
5. Supabase exchanges the code and calls the Zoho workspace metadata API.
6. The account must be able to access `ZOHO_ALLOWED_WORKSPACE_ID`.
7. Supabase redirects to GitHub Pages with an opaque session in the URL
   fragment.
8. The browser moves the handle to `sessionStorage` and clears the fragment.

There is no **Continue after sign-in** bypass and the frontend cannot mark
itself authenticated.

## Supabase Deployment

The repository root contains:

- `supabase/migrations/20260727000100_abnah_portal.sql`;
- `supabase/functions/abnah-portal/`;
- `supabase/.env.example`;
- `config/supabase-portal.json`;
- `docs/ZOHO_PORTAL_RUNTIME.md`.

Register this callback in the Zoho server-based OAuth client:

```text
https://<PROJECT_REF>.supabase.co/functions/v1/abnah-portal/auth/callback
```

Keep these in Supabase Edge Function Secrets:

- `ZOHO_OAUTH_CLIENT_ID`
- `ZOHO_OAUTH_CLIENT_SECRET`
- `ZOHO_ALLOWED_WORKSPACE_ID`
- `ZOHO_TOKEN_ENCRYPTION_KEY`
- `PORTAL_ALLOWED_ORIGIN`
- `PORTAL_RETURN_URL`
- optional `ZOHO_PORTAL_ADMIN_EMAILS`

The full deployment commands are in the root
`docs/ZOHO_PORTAL_RUNTIME.md`.

## V4 URL Handoff

Use:

```text
config/zoho-secured-embed-handoff.example.json
```

Schema:

```text
abnah-zoho-view-handoff/v4
```

The file has:

- 19 individual secured report-view URL slots;
- four secured complete-dashboard fallback URL slots;
- exact expected Zoho view names;
- no credentials, tokens, passwords, or report rows.

The configuration drawer saves the handoff centrally through Supabase. The
browser keeps a URL-only read-through cache for temporary backend outages.

## Live Filters

The custom portal's page controls remain outside Zoho. Applying a filter sends
an encoded `ZOHO_CRITERIA` expression only to report views with a compatible
field mapping in `app/lib/zoho-report-embed-contract.ts`.

Native Dashboard User Filters remain inside each complete-dashboard fallback.
They use `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`.

Do not send a filter to a report whose source grain does not contain the mapped
field. Historical trends remain excluded from current-period criteria where
the contract says so.

## KPI Boundary

Zoho KPI Widgets are dashboard-only objects and have no independent Share
contract. The custom KPI cards therefore remain explicitly labelled synthetic
validation baselines until a governed Zoho data-API measure endpoint is
activated. Dashboard pages are never scraped for KPI values.

Use the complete dashboard fallback to demonstrate native live KPI Widgets.
Use the custom page to demonstrate the approved external visual composition.

## Visual Boundary

The custom portal controls page composition, navigation, filters, labels,
spacing, and its baseline KPI cards. Zoho controls every pixel inside each
cross-origin report iframe.

Configure internal report colors in Zoho:

- purple `#6F2DBD`;
- red `#E24950`;
- amber `#D29A2D`;
- green `#168D61`;
- grey `#9A9A9A`.

## Company-Laptop Acceptance

- GitHub Pages `/portal/` opens.
- Supabase `/status` returns `configured: true`.
- a permitted Zoho account signs in and a non-member is rejected;
- all 19 individual views and four dashboard fallbacks reload across browsers;
- external filters affect only compatible report views;
- logout revokes the opaque session;
- no credential or operational row is present in Git or the handoff.

## Local Report Reviewer

The local reviewer remains separate because it can contain operational rows.
`127.0.0.1` means **this same laptop**. Run the viewer on the laptop that opens
it, leave the terminal active, and use `http://127.0.0.1:8765/`.

`Connection refused` means no process is listening on that laptop. It does not
mean port 8765 is inherently insecure.

## Official References

- [Zoho Analytics API prerequisites](https://www.zoho.com/analytics/api/v2/prerequisites.html)
- [Zoho workspace metadata API](https://www.zoho.com/analytics/api/v2/metadata-api/all-workspace.html)
- [Zoho dashboard filters](https://www.zoho.com/analytics/help/dashboard/filter.html)
- [Zoho KPI Widgets](https://www.zoho.com/analytics/help/dashboard/kpi-widgets.html)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [Supabase Edge Function secrets](https://supabase.com/docs/guides/functions/secrets)
