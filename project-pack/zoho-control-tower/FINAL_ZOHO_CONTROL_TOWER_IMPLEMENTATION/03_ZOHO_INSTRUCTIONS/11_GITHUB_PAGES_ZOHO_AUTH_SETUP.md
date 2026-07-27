# GitHub Pages Control Tower Runtime

The deployable frontend and backend source lives in
`ABG-GROUPIT/abnah-control-tower-workbench`. Run the setup commands from that
repository. This personal repository retains the same runbook for implementation
handoff and review.

## Final Product Boundary

The production frontend is only:

`https://abg-groupit.github.io/abnah-control-tower-workbench/portal/`

It is a custom ABNAH interface. It does not place the Zoho dashboard, Zoho
tables, or Zoho filters inside an iframe.

GitHub Pages serves static HTML, CSS and JavaScript. A Supabase Edge Function is
the only backend. It performs Zoho sign-in, verifies access to the approved
workspace, exports allowlisted Query Tables through the Zoho Analytics API, and
returns rows to the custom UI.

Pages 1 and 2 are implemented. Pages 3 and 4 deliberately show `Coming soon`.

## What Each Layer Does

| Layer | Responsibility | Sensitive material |
|---|---|---|
| GitHub Pages | Custom filters, cards, map, charts, tables and navigation | Opaque session handle in tab `sessionStorage` |
| Edge Function | Zoho OAuth, workspace check, token refresh, allowlisted data export | Client secret and encrypted Zoho tokens |
| Supabase Postgres | One-time OAuth states and encrypted sessions | No POSist/Zoho report rows |
| Zoho Analytics | Governed Query Tables and workspace membership | Operational analytics data |

The browser never receives the Zoho client secret, refresh token, database
service-role key, or token-encryption key. The gateway does not persist exported
report rows.

## Live Data Contract

Page 1 reads exactly:

| Portal dataset | Zoho Query Table | Date |
|---|---|---|
| Inventory risk | `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| Menu impact | `28_fact_ct_menu_impact.sql` | `snapshot_date` |
| Expiry risk | `38_fact_ct_expiry_risk.sql` | `as_of_date` |
| Risky PO | `36_fact_ct_risky_po.sql` | `as_of_date` |

Page 2 reads exactly:

| Portal dataset | Zoho Query Table | Date |
|---|---|---|
| Purchase orders | `22_fact_ct_purchase_order.sql` | `as_of_date` |
| PO/receipt lines | `24_fact_ct_po_receipt_line.sql` | `as_of_date` |
| Purchase receipts | `23_fact_ct_purchase_receipt.sql` | `receipt_date` |
| Price movement | `31_sum_ct_price_movement.sql` | `price_as_of_date` |

Each page refresh starts four asynchronous JSON exports. The function resolves
Query Table IDs from Zoho metadata instead of committing IDs to Git. The Zoho
account must be able to view all required Query Tables.

The visible **From** and **To** controls are part of this contract. Pressing
**Apply** sends the selected range back to the gateway and starts fresh,
date-bounded exports for the active page. It is not limited to the synthetic
`source_period_code` window. The gateway rejects ranges longer than 366 days.

## Authentication Flow

1. The portal checks `/status`.
2. `Sign in with Zoho` opens `/auth/start`.
3. The backend stores a one-time state hash and redirects to Zoho India OAuth.
4. Zoho returns the authorization code to `/auth/callback`.
5. The backend exchanges the code and verifies
   `ZOHO_ALLOWED_WORKSPACE_ID`.
6. Zoho tokens are encrypted before being stored.
7. A random, unrelated portal-session handle is returned in the URL fragment.
8. The browser moves that handle to tab `sessionStorage` and removes it from the
   address bar.
9. Every `/session` and `/data` request must present that handle.
10. Logout revokes the stored session.

There is no production bypass. A local synthetic preview is available only on
`localhost` or `127.0.0.1` when the backend URL is still a placeholder.

## Plan Check

Zoho Analytics API access is included in paid plans. API units depend on the
account plan, so confirm the current allowance under **Subscription** before
production load testing. This portal uses metadata reads plus JSON bulk exports;
it does not require Enterprise-only white-label embedding.

## One-Time Setup

Complete the steps in order.

### 1. Create the Supabase project

1. Sign in to Supabase.
2. Click **New project**.
3. Choose the company-approved organization.
4. Set the project name to `abnah-control-tower`.
5. Choose the nearest permitted region.
6. Generate and store a strong database password in the company password
   manager.
7. Click **Create new project**.
8. On **Project Settings > General**, copy the **Reference ID**. This guide calls
   it `<PROJECT_REF>`.

Do not copy an anon key, publishable key, service-role key, or database password
into this repository.

### 2. Register the Zoho server-based OAuth client

1. Open the Zoho API Console in the same India data centre as the Analytics
   account.
2. Click **Add Client**.
3. Select **Server-based Applications**.
4. Set the client name to `ABNAH Supply Chain Control Tower`.
5. Set the homepage to:
   `https://abg-groupit.github.io/abnah-control-tower-workbench/portal/`
6. Set this exact authorized redirect URI:

   `https://<PROJECT_REF>.supabase.co/functions/v1/abnah-portal/auth/callback`

7. Create the client.
8. Store the displayed Client ID and Client Secret in the company password
   manager.

The redirect URI must match character-for-character. Do not add a trailing
slash.

The function requests:

- `ZohoAnalytics.metadata.read`
- `ZohoAnalytics.data.read`
- `ZohoAnalytics.embed.read`
- `profile.userinfo.READ`

### 3. Create the local secret file

From the repository root, create `supabase/.env.production`. It is ignored by
Git. Use:

```dotenv
ZOHO_OAUTH_CLIENT_ID=<CLIENT_ID>
ZOHO_OAUTH_CLIENT_SECRET=<CLIENT_SECRET>
ZOHO_ALLOWED_WORKSPACE_ID=333330000004099001
ZOHO_TOKEN_ENCRYPTION_KEY=<RANDOM_KEY>
PORTAL_ALLOWED_ORIGIN=https://abg-groupit.github.io
PORTAL_RETURN_URL=https://abg-groupit.github.io/abnah-control-tower-workbench/portal/
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.in
ZOHO_ANALYTICS_API_BASE_URL=https://analyticsapi.zoho.in
ZOHO_PROFILE_BASE_URL=https://profile.zoho.in
ZOHO_OAUTH_REDIRECT_URI=https://<PROJECT_REF>.supabase.co/functions/v1/abnah-portal/auth/callback
```

Generate the random encryption key in PowerShell:

```powershell
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
[Convert]::ToBase64String($bytes)
$rng.Dispose()
```

Paste the resulting Base64 value only into `supabase/.env.production`.

Do not add `SUPABASE_URL` or `SUPABASE_SERVICE_ROLE_KEY` to the production
secret file. Supabase provides those reserved values to deployed functions.

### 4. Deploy the database and function

From the repository root:

```powershell
npx supabase@latest login
npx supabase@latest link --project-ref <PROJECT_REF>
npx supabase@latest db push
npx supabase@latest secrets set --env-file supabase/.env.production --project-ref <PROJECT_REF>
npx supabase@latest functions deploy abnah-portal --project-ref <PROJECT_REF>
npx supabase@latest secrets list --project-ref <PROJECT_REF>
```

The migration creates:

- `abnah_portal_oauth_states`
- `abnah_portal_sessions`
- `abnah_zoho_portal_config` for backward-compatible configuration only

RLS is enabled. Browser roles receive no table privileges.

### 5. Connect GitHub Pages to the function

Open `config/supabase-portal.json` and replace only `YOUR_PROJECT_REF`:

```json
{
  "functionBaseUrl": "https://<PROJECT_REF>.supabase.co/functions/v1/abnah-portal",
  "returnUrl": "https://abg-groupit.github.io/abnah-control-tower-workbench/portal/"
}
```

This URL is public and safe to commit. It is not a key.

Run:

```powershell
npm run typecheck
npm test
git add .
git commit -m "configure ABNAH control tower runtime"
git push abg main
```

The existing GitHub Actions workflow builds and deploys GitHub Pages.

### 6. Verify the backend before opening the portal

Run:

```powershell
Invoke-RestMethod `
  "https://<PROJECT_REF>.supabase.co/functions/v1/abnah-portal/status"
```

Required response:

```json
{
  "configured": true
}
```

If `configured` is false, read `missingEnvironment` and add only those values in
**Supabase > Edge Functions > Secrets** or with `supabase secrets set`.

### 7. Verify access enforcement

1. Open the GitHub Pages `/portal/` URL in an InPrivate window.
2. Confirm no KPI or report data is visible before sign-in.
3. Click **Sign in with Zoho**.
4. Sign in with an account that has access to workspace
   `333330000004099001`.
5. Confirm Page 1 loads.
6. Click **Refresh** and confirm the updated time changes.
7. Switch to Page 2 and confirm it loads independently.
8. Sign out and confirm the data disappears.
9. Repeat with a Zoho account that does not have workspace access; it must be
   rejected.

## Product Behavior

The deployed product does not display infrastructure names or setup
instructions. Users see only:

- approved Zoho sign-in;
- control-tower filters and operational views;
- refresh and sign-out actions;
- clear unavailable or empty states;
- Pages 3 and 4 marked `Coming soon`.

Technical setup remains only in this developer runbook.

## Expected Page 1 Validation

For 01 March 2026 through 31 March 2026:

| KPI | Expected |
|---|---:|
| Restaurants at risk | 3 |
| Menu items impacted | 110 |
| Stockout risk | INR 411,695.50 |
| Expiry risk | INR 271,399.12 |
| Open actions | 6 |

See `docs/PAGE_1_AND_PAGE_2_CORRECTIONS.md` for the Query 28 and Zoho Timeline
Filter correction.

## Operational Notes

- Recommendations and owners are control-tower decision rules, not POSist
  instruction fields.
- Opening-stock expiry estimates legitimately have no receipt-linked PO or
  vendor.
- Negative source stock is preserved as a warning but displayed as zero in
  presentation quantities.
- A Page 1 or Page 2 refresh can partially succeed. An unavailable Query Table
  produces an empty panel plus a status message; it does not substitute
  synthetic data in production.
- Monitor Zoho API units during UAT. Increase cache duration or add scheduled
  server-side refresh only after real usage is known.

## Release Checklist

1. Query 28 correction has been saved in Zoho.
2. Queries 29-31 contain their date columns.
3. `config/supabase-portal.json` contains the actual project reference.
4. `/status` returns `configured: true`.
5. Allowed and rejected Zoho accounts behave correctly.
6. Page 1 and Page 2 load from live Query Tables.
7. No screenshots, operational exports, tokens or credentials are committed.
8. `npm run typecheck`, `npm test`, and GitHub Pages deployment pass.
