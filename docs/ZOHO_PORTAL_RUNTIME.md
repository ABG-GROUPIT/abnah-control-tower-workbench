# Zoho Portal Runtime

## Purpose

The `/portal` surface is the executive-facing ABNAH Control Tower. It preserves
the custom four-page UI while using governed Zoho Analytics views as its report
rendering source.

## Runtime Boundary

The secured portal requires the Worker/Sites deployment. GitHub Pages remains a
static Atlas and project-pack distribution surface; it cannot perform OAuth
callbacks, protect sessions, verify workspace membership, or persist the shared
URL handoff in D1.

## Authentication

1. The portal calls `/api/zoho-auth/session`.
2. An unauthenticated user selects `Continue with Zoho`.
3. `/api/zoho-auth/start` begins Zoho's authorization-code flow.
4. `/api/zoho-auth/callback` exchanges the code server-side.
5. The server calls the Zoho Analytics workspace metadata API and requires
   access to `ZOHO_ALLOWED_WORKSPACE_ID`.
6. Only then is an encrypted, HttpOnly, SameSite session cookie issued.

There is no browser-side `Continue after sign-in` bypass.

Required server environment variables are listed in `.env.example`:

- `ZOHO_OAUTH_CLIENT_ID`
- `ZOHO_OAUTH_CLIENT_SECRET`
- `ZOHO_SESSION_SECRET`
- `ZOHO_ALLOWED_WORKSPACE_ID`

`ZOHO_PORTAL_ADMIN_EMAILS` optionally limits who may edit the shared URL map.
When it is empty, any Zoho user verified against the allowed workspace may
maintain the map.

## URL Handoff

Use the portal's `Configure` drawer or import
`config/zoho-secured-embed-handoff.example.json`.

Each page accepts:

- one secured full-dashboard URL as a native fallback;
- one secured URL for every individual chart, pivot, summary, or tabular view.

The full dashboard is not inserted into the custom UI. Individual report URLs
fill the named slots, while the dashboard opens separately through
`Native fallback`.

The central mapping is versioned in D1. A browser-local copy is only a
read-through cache when the authenticated runtime temporarily cannot load D1.
The handoff never contains passwords, OAuth credentials, tokens, or report
rows.

## Filters

The custom page controls remain outside Zoho. Selecting `Apply` adds a
URL-encoded `ZOHO_CRITERIA` expression to each configured report URL.
`app/lib/zoho-report-embed-contract.ts` decides exactly which filters and source
columns apply to each report, so incompatible filters are not sent.

The native dashboard fallback continues to use its own Zoho dashboard filters.

## KPI Cards

Zoho dashboard KPI widgets do not provide the same independent share contract
as saved report views. Therefore:

- the current custom KPI cards display clearly labelled synthetic validation
  baselines;
- dashboard URLs are never scraped for KPI values;
- production live KPI values must be returned server-side through the Zoho
  Analytics data API, using the same verified OAuth session and the governed
  query-table measures.

No extra KPI URL is required when the API measure endpoint is activated. A
one-value saved Summary View can be used as a bounded fallback where needed.

## Handoff Checklist

1. Register a Zoho server-based OAuth client.
2. Register the exact production callback:
   `<production-origin>/api/zoho-auth/callback`.
3. Configure the runtime environment variables.
4. Confirm the allowed workspace ID.
5. Sign in through `/portal`.
6. Paste each dashboard fallback and individual report URL in `Configure`.
7. Save the shared handoff and verify all four page connection counts.
8. Test outlet, period, category, vendor, item, status, UOM, and exception
   filters against their mapped reports.
