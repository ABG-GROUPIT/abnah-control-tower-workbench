# Zoho Portal Hosting, Authentication And Handoff

## Final Architecture

GitHub Pages is the only frontend host. Supabase is the only backend.

```text
GitHub Pages /portal/
        |
        | OAuth start, session, page-data requests
        v
Supabase Edge Function
        |
        | metadata and asynchronous Query Table exports
        v
Zoho Analytics India
```

The portal is a separate page linked from the Atlas. It is not an Atlas tab,
ChatGPT Site or SharePoint-hosted application.

## Responsibilities

GitHub Pages owns:

- the custom four-page presentation;
- date, outlet and page-specific controls;
- client-side rendering of approved rows;
- refresh, navigation and sign-out.

Supabase owns:

- the Zoho OAuth callback and client secret;
- allowed-workspace verification;
- encrypted access and refresh tokens;
- opaque portal sessions;
- allowlisted Query Table exports.

Zoho owns:

- the 38-Query-Table model;
- governed calculations and refreshed source data;
- native dashboards and saved reports used for validation.

Supabase does not persist exported report rows. GitHub stores no credentials,
screenshots or operational data.

## Verified Sign-In

1. `/portal/` checks the Supabase `/status` endpoint.
2. **Sign in with Zoho** opens `/auth/start`.
3. Supabase stores a one-time state hash and redirects to Zoho India OAuth.
4. Zoho returns to `/auth/callback`.
5. Supabase exchanges the authorization code.
6. Supabase verifies `ZOHO_ALLOWED_WORKSPACE_ID`.
7. Supabase redirects to GitHub Pages with an opaque session handle in the URL
   fragment.
8. The browser moves the handle into tab `sessionStorage` and removes the
   fragment.
9. Every data request must present the session handle.
10. Logout revokes the server-side session.

There is no Continue-after-sign-in bypass.

## Supabase Deployment

Register this exact callback in a Zoho server-based OAuth client:

```text
https://<PROJECT_REF>.supabase.co/functions/v1/abnah-portal/auth/callback
```

Store these as Supabase Edge Function secrets:

- `ZOHO_OAUTH_CLIENT_ID`
- `ZOHO_OAUTH_CLIENT_SECRET`
- `ZOHO_ALLOWED_WORKSPACE_ID`
- `ZOHO_TOKEN_ENCRYPTION_KEY`
- `PORTAL_ALLOWED_ORIGIN`
- `PORTAL_RETURN_URL`

The complete commands and India data-centre URLs are in the root
`docs/ZOHO_PORTAL_RUNTIME.md`.

## Query Table Handoff

The runtime handoff is already represented in code:

- Page 1 and Page 2 Query Table names in
  `supabase/functions/_shared/zoho-data.ts`;
- OAuth and workspace enforcement in
  `supabase/functions/_shared/zoho.ts`;
- public backend location in `config/supabase-portal.json`;
- secrets in Supabase, never GitHub.

No individual report URL, dashboard URL, iframe source or API token must be
pasted into the production frontend.

## Optional Local References

Use `config/zoho-reference-links.local.json` only for developer QA. It means **this same laptop**
or developer checkout, not shared production configuration.
The file is ignored by Git.

## Handoff Checklist

1. Queries 29-31 have been re-saved.
2. Page 1 and Page 2 Date Range mappings pass.
3. `config/supabase-portal.json` contains the real Supabase project reference.
4. Supabase migration, secrets and Edge Function are deployed.
5. `/status` returns `configured: true`.
6. An allowed Zoho user can sign in and load Page 1 and Page 2.
7. A user without workspace access is rejected.
8. Sign-out removes all visible data.
9. No screenshot, row export, credential or public report link is committed.
