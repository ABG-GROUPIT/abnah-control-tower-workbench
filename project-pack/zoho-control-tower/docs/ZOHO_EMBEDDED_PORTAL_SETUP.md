# Zoho Portal Integration Setup

## Current Architecture

The filename is retained for compatibility, but the production portal does not embed Zoho reports or dashboards.

```text
GitHub Pages custom UI
        |
        v
Supabase OAuth and data gateway
        |
        v
Zoho Analytics Query Table API
```

The custom portal owns the visual layout, filters, KPI cards, charts and tables.
Zoho remains the governed analytics model and native validation surface.

## What To Build In Zoho

Build and reconcile the required chart, summary and tabular views, plus the
four native dashboards:

1. `CT_PAGE_1_Risk_Action_Center`
2. `CT_PAGE_2_Procurement_Vendor_Capital`
3. `CT_PAGE_3_Consumption_Menu_Profitability`
4. `CT_PAGE_4_SCM_Explorer_Data_Quality`

These objects validate formulas and allow normal Zoho drilldown. Their Share
URLs are not required by the custom portal.

## Runtime Data

The Supabase Edge Function:

1. verifies the user's Zoho account;
2. verifies access to the configured ABNAH workspace;
3. resolves allowlisted Query Table IDs from metadata;
4. starts asynchronous JSON exports for the selected page and date range;
5. returns rows without persisting them.

Page 1 and Page 2 Query Table names and date fields are listed in
`ZOHO_PORTAL_RUNTIME.md`.

## Authentication

The portal exposes no report data before successful Zoho OAuth. The callback
and token exchange happen in Supabase, not in GitHub Pages. The browser keeps
only an opaque portal-session handle.

## Optional QA Links

Dashboard and report URLs may be stored locally in:

```text
config/zoho-reference-links.local.json
```

Start from `config/zoho-reference-links.example.json`. The local file is
ignored by Git and is only for side-by-side QA.

## Do not use:

- public `open-view` links as an authentication boundary;
- iframe URLs as the source of the custom UI;
- `ZOHO_CRITERIA` against cross-origin embedded reports;
- Zoho passwords, OAuth tokens, client secrets or operational rows in GitHub;
- the deprecated v4 URL handoff as the production runtime.
