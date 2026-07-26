# Zoho Embedded Portal Setup

## Current Architecture

The current portal uses individual saved Zoho views, not four complete
dashboard iframes.

```text
39 secured Zoho embeds
  = 20 KPI views
  + 19 charts/tables/maps
```

Each view is placed inside its matching ABNAH KPI card or report panel. This
preserves the external page hierarchy, navigation, spacing and color system.
Embedding a complete dashboard would show the native Zoho dashboard layout
inside the page and would not preserve the supplied ABNAH composition.

The complete build sequence is:

```text
ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md
```

## What The Portal Provides

- A separate `/portal/` route.
- A Zoho sign-in preflight before the portal opens.
- Four ABNAH page layouts.
- Twenty KPI slots and nineteen report slots.
- Blueprint and Live reports modes.
- Progressive connection: missing report URLs remain visible as blueprints.
- Tab-specific external filter bars.
- Per-report URL-criteria mappings.
- One-file import/export for all 39 secured embed URLs.
- Browser-local URL storage.

The portal never stores passwords, OAuth tokens, client secrets or report rows.

## What To Create In Zoho

Create every saved view named in:

```text
zoho_control_tower_v2_dashboard_click_by_click.md
```

Use the current reference-first subset listed in:

```text
ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md
```

For each saved view:

1. Build it from the exact numbered Query Table.
2. Apply the documented aggregation and fixed filters.
3. Validate it against `ZOHO_DASHBOARD_EXPECTED_RESULTS.md`.
4. Apply the documented report colors.
5. Share it with the required Zoho Viewer.
6. Generate an interactive **Access with Login** embed.
7. Copy only the iframe `src` URL.
8. Paste it into the matching portal slot.

## Sign-In Behavior

The portal access screen opens Zoho Analytics in a normal browser tab. The
viewer signs in and returns to the portal. Secured iframes then reuse that Zoho
browser session.

The Continue button cannot inspect or bypass Zoho authentication. If the
viewer is not signed in or the saved view was not shared with that account,
Zoho will reject the iframe.

This is the most reliable static-host flow. True automatic company SSO before
the shell opens requires Zoho Directory/Entra configuration or an approved
Embedded Analytics/JWT architecture.

## Connect Views Without Editing Code

Use:

```text
config/zoho-secured-embed-handoff.example.json
```

The file uses schema:

```text
abnah-zoho-report-embed-handoff/v2
```

It contains one blank entry for every KPI/report slot.

On the portal:

1. Choose **Configure**.
2. Select page 1, 2, 3 or 4.
3. Paste the individual saved-view URL beside the exact `CT_...` name.
4. Choose **Save locally**.
5. Repeat as reports are completed.
6. Use **Handoff** to download all current mappings.
7. On another approved laptop, choose **Configure > Import**.

The handoff is browser configuration, not an authentication credential.

## Filter Strategy

The portal owns the visible filter controls. When the user chooses **Apply**,
the portal adds a URL-encoded `ZOHO_CRITERIA` expression to every applicable
individual report URL.

It does not send every filter to every report:

- current-state period does not filter historical trends;
- outlet does not filter Query 34 model-wide checks;
- menu filters do not filter ingredient facts;
- ingredient filters do not filter menu facts;
- UOM applies only to quantity consumption reports;
- exception type applies only to Query 34 detail;
- Page 1 Risk switches the visible stockout/expiry scope.

Zoho documents dynamic embedded-view filtering through the
`ZOHO_CRITERIA` parameter. The portal URL-encodes the expression.

Changing a filter reloads the applicable report frames. Changing source data
or report design in Zoho does not require a portal rebuild.

## Visual Responsibility

The outer portal controls:

- page layout;
- card and panel frames;
- titles and subtitles;
- filter controls;
- page accents;
- navigation;
- responsive behavior.

Zoho controls:

- the rendered chart/table/map;
- chart legends and labels;
- number formatting;
- chart-internal colors;
- drilldown, tooltip and underlying-data behavior.

The outer site cannot restyle content inside a cross-origin iframe. Apply the
documented ABNAH colors to each saved Zoho report before embedding it.

## Security Rules

Use:

```text
Access with Login / secured login
```

Do not use:

- Public Access;
- Access without Login;
- client-side OAuth;
- a password or secret in the handoff JSON;
- actual operational rows in GitHub or the hosted portal.

`ZOHO_CRITERIA` is a presentation filter, not security. Sharing and Zoho login
remain the access-control boundary.

## Troubleshooting

### Sign-in loops

1. Open `https://analytics.zoho.in/` in a normal tab.
2. Complete sign-in.
3. Return to the portal and reload.
4. Confirm the browser allows the Zoho session in embedded content.
5. Ask IT to allow the Zoho domain if company policy blocks it.

### Access denied

The signed-in account was not granted access to that exact saved view. Correct
the share permissions. Do not replace the URL with a public link.

### One slot stays blank

Confirm:

- the URL belongs to that saved `CT_...` view;
- the URL is the iframe `src`, not the complete HTML snippet;
- the host is `analytics.zoho.in` or another approved Zoho Analytics host;
- the report is shared with the signed-in account.

### A filter removes the wrong data

Compare the slot with the filter contract in
`ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md`. Do not change a Query Table
merely to compensate for a report-to-filter mapping error.

## Official References

- [Zoho secured embedding and URL criteria](https://www.zoho.com/analytics/help/publishing/embed-reports.html)
- [Zoho JavaScript API](https://www.zoho.com/analytics/js-api/)
- [Zoho dashboard filter mapping](https://www.zoho.com/analytics/help/dashboard/filter.html)
- [Zoho Directory SSO](https://www.zoho.com/analytics/help/zoho-directory.html)
