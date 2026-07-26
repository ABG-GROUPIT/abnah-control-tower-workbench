# Zoho Portal Runtime

## Production Boundary

The only frontend deployment is:

`https://abg-groupit.github.io/abnah-control-tower-workbench/`

The executive portal is the static `/portal/` route on the same GitHub Pages
site. It preserves the custom four-page ABNAH UI and inserts governed Zoho
Analytics report views into the named slots.

GitHub Pages cannot safely exchange OAuth codes, store secrets, verify workspace
membership, or maintain shared configuration. Those operations are isolated in
the `abnah-portal` Supabase Edge Function. No second frontend deployment is
required or supported.

## Runtime Components

| Component | Responsibility | Data held |
|---|---|---|
| GitHub Pages | Custom UI, filter controls, URL handoff editor, Zoho iframes | Session handle in `sessionStorage`; URL-only cache in `localStorage` |
| Supabase Edge Function | Zoho OAuth, workspace verification, session checks, URL handoff API | Secrets only in function environment |
| Supabase Postgres | One-time OAuth state, encrypted token sessions, versioned URL handoff | No POSist rows, screenshots, report exports, or dashboard values |
| Zoho Analytics | Reports, dashboards, filters, and eventual KPI data API | Governed analytics data |

The browser never receives the Zoho client secret, refresh token, Supabase
service-role key, or token-encryption key.

## Authentication Flow

1. GitHub Pages calls the Supabase function's `/status` endpoint.
2. The user selects `Continue with Zoho`.
3. `/auth/start` stores a one-time state hash and redirects to Zoho India OAuth.
4. Zoho returns to `/auth/callback` on the Supabase function.
5. The function exchanges the code and calls the Zoho Analytics workspace API.
6. Access is accepted only when the account can see
   `ZOHO_ALLOWED_WORKSPACE_ID`.
7. Zoho tokens are encrypted in Postgres and an unrelated random portal session
   is issued.
8. The function redirects to GitHub Pages with that portal session in the URL
   fragment. Fragments are not sent to GitHub's server.
9. The browser moves the handle into `sessionStorage` and immediately removes
   the fragment from the address bar.
10. Subsequent `/session`, `/config`, and `/logout` requests use
    `Authorization: Bearer <opaque-session>`.

There is no browser-side sign-in bypass. Closing the tab clears the browser
handle; logout also revokes the server session.

## Repository Configuration

`config/supabase-portal.json` is public and contains no secret:

```json
{
  "functionBaseUrl": "https://YOUR_PROJECT_REF.supabase.co/functions/v1/abnah-portal",
  "returnUrl": "https://abg-groupit.github.io/abnah-control-tower-workbench/portal/"
}
```

Replace `YOUR_PROJECT_REF` after the Supabase project is created. Commit that
single public URL so GitHub Pages can call the function.

The Edge Function environment template is `supabase/.env.example`. Production
values must be entered as Supabase secrets:

- `ZOHO_OAUTH_CLIENT_ID`
- `ZOHO_OAUTH_CLIENT_SECRET`
- `ZOHO_ALLOWED_WORKSPACE_ID`
- `ZOHO_TOKEN_ENCRYPTION_KEY`
- `PORTAL_ALLOWED_ORIGIN`
- `PORTAL_RETURN_URL`
- optional `ZOHO_PORTAL_ADMIN_EMAILS`

The India endpoints in the template are the defaults. `SUPABASE_URL` and
`SUPABASE_SERVICE_ROLE_KEY` are provided to deployed functions by Supabase.
The service-role key must never be copied into GitHub Pages.

## One-Time Deployment

From the repository root:

```powershell
npx supabase login
npx supabase link --project-ref <PROJECT_REF>
npx supabase db push
npx supabase secrets set --env-file supabase/.env --project-ref <PROJECT_REF>
npx supabase functions deploy abnah-portal --project-ref <PROJECT_REF> --use-api
```

`supabase/.env` is ignored by Git. Generate `ZOHO_TOKEN_ENCRYPTION_KEY` with at
least 32 random bytes and do not reuse a password.

Register this exact redirect URI in the Zoho server-based OAuth client:

`https://<PROJECT_REF>.supabase.co/functions/v1/abnah-portal/auth/callback`

Then update `config/supabase-portal.json`, run `npm test`, commit, and push
`main`. The existing GitHub Pages workflow publishes the portal.

## Database Security

`supabase/migrations/20260727000100_abnah_portal.sql` creates:

- `abnah_portal_oauth_states`;
- `abnah_portal_sessions`;
- `abnah_zoho_portal_config`.

RLS is enabled on all three tables. `anon` and `authenticated` receive no table
permissions. Only the server-side service role used by the Edge Function can
read or write them.

## URL Handoff

Use the portal's `Configure` drawer or import
`config/zoho-secured-embed-handoff.example.json`.

Each page accepts one secured dashboard fallback and one secured URL for every
individual chart, pivot, summary, or tabular view. The custom UI uses the 19
individual views. The four dashboard URLs remain separate native fallbacks.

The handoff is versioned in Supabase. A browser-local URL-only copy is a
read-through cache when the authenticated backend is temporarily unavailable.
The handoff must never contain passwords, OAuth credentials, tokens, report
rows, or dashboard values.

## Filters And KPIs

Custom page controls remain outside Zoho. `Apply` adds an encoded
`ZOHO_CRITERIA` expression only to compatible report views, as defined in
`app/lib/zoho-report-embed-contract.ts`.

Zoho dashboard KPI widgets do not expose the same independent share contract as
saved report views. Until the Zoho data API measure endpoint is implemented,
custom KPI cards stay explicitly labelled as validated synthetic baselines.
Dashboard URLs are never scraped for KPI values.

## Release Check

1. `config/supabase-portal.json` contains the real public function URL.
2. Supabase migration is applied.
3. All required Supabase secrets are present.
4. Zoho callback exactly matches the Edge Function callback.
5. `/status` returns `configured: true`.
6. A permitted Zoho user can sign in and a non-member is rejected.
7. All 19 report slots and four fallbacks save and reload across browsers.
8. Logout revokes the session.
9. `npm test` and the GitHub Pages workflow pass.
