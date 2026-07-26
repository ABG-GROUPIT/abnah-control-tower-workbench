# Zoho Embedded Portal Setup

## Current Architecture

The live portal keeps the custom ABNAH four-page layout. It embeds 19
individual secured Zoho report views in the named visual slots and retains one
complete secured Zoho dashboard per page as a native fallback.

```text
19 secured individual report views
  + 4 secured dashboard fallbacks
  + Supabase-verified Zoho access
  = GitHub Pages custom Control Tower
```

## What To Share

| Zoho object | Build action | Portal action |
| --- | --- | --- |
| Chart, pivot, summary, or tabular view | Save, reconcile, share with login | Paste its secured URL into the matching report slot |
| KPI Widget | Create inside its native page dashboard | Do not paste; it has no independent Share action |
| Page dashboard | Add native KPI Widgets, saved views, and Dashboard User Filters | Paste as the page's **Native fallback** |

The production handoff contains 19 report URLs and four fallback dashboard
URLs. The fallback does not replace the custom page.

## Build In Zoho

Build the saved views listed in
`ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md`, then build:

1. `CT_PAGE_1_Risk_Action_Center`
2. `CT_PAGE_2_Procurement_Vendor_Capital`
3. `CT_PAGE_3_Consumption_Menu_Profitability`
4. `CT_PAGE_4_SCM_Explorer_Data_Quality`

The dashboards remain the native validation and fallback surfaces. Apply their
User Filters using `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`.

## Connect The Custom Portal

Use:

```text
config/zoho-secured-embed-handoff.example.json
```

The file uses:

```text
abnah-zoho-view-handoff/v4
```

After the Supabase/Zoho runtime is configured:

1. Open GitHub Pages `/portal/`.
2. Select **Continue with Zoho** and complete verified sign-in.
3. Choose **Configure**.
4. Select a page.
5. Paste each secured individual report URL into its exact named slot.
6. Paste the complete page dashboard into **Native fallback**.
7. Save the shared handoff.
8. Switch to **Live** and test every filter.
9. Export the v4 JSON as a transfer backup.

Do not enter a Zoho password, OAuth token, client secret, iframe HTML, or report
row. Paste only the secured HTTPS Zoho Analytics URL.

## Filters

The custom page controls construct `ZOHO_CRITERIA` for each compatible report.
The source-field contract decides which controls apply to each view. A report
without outlet, period, vendor, category, item, UOM, status, or exception grain
does not receive that criterion.

The complete dashboard fallback continues to use native Dashboard User
Filters. Its filter state is not synchronized with the custom page controls.

## KPI Cards

KPI Widgets stay inside the fallback dashboards. The custom cards display
labelled synthetic acceptance baselines until live KPI values are returned by
the approved Zoho data API. A one-value Summary View can be used as a bounded
fallback after validation.

## Authentication

The outer portal is not a fake sign-in preflight. Supabase completes Zoho OAuth,
checks the configured workspace, stores encrypted Zoho tokens, and issues an
opaque portal session. GitHub Pages receives no backend secret.

See:

```text
ZOHO_PORTAL_HOSTING_AUTH_HANDOFF.md
```

and the repository root:

```text
docs/ZOHO_PORTAL_RUNTIME.md
```

## Security

Use secured **Access with Login** URLs. Do not use:

- public or without-login report links;
- credentials or tokens in JSON;
- actual POSist rows in GitHub or Supabase;
- a browser-only continue button as proof of authentication;
- dashboard scraping for KPI values.

## Acceptance

- 19/19 report slots connect.
- 4/4 dashboard fallbacks open.
- Zoho workspace membership is verified before the page loads.
- every custom filter affects only its contracted views;
- the visual stays within the custom page grid at desktop and mobile sizes;
- no report iframe causes horizontal page overflow;
- logout and expired sessions return to the access gate.
