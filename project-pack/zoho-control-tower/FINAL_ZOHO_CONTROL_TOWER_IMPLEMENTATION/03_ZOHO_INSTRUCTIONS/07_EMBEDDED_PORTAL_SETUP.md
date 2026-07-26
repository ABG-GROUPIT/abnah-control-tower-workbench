# Zoho Embedded Portal Setup

## Current Architecture

The live portal embeds four complete secured Zoho dashboards, one for each
ABNAH page.

```text
4 secured Zoho dashboard embeds
  = 4 page dashboards
  = 20 dashboard KPI Widgets
  + saved chart, pivot, summary and tabular reports
```

KPI Widgets remain inside Zoho because they are dashboard-only elements.
Dashboard User Filters update both KPI Widgets and mapped reports.

## Portal Responsibilities

The portal provides:

- the separate `/portal/` route;
- Zoho sign-in preflight;
- four-page ABNAH navigation and blueprint views;
- one secured dashboard URL slot per page;
- browser-local import/export of the four URLs;
- no passwords, tokens, secrets or operational rows.

In Live mode, Zoho owns the page dashboard layout, KPI rendering, filters,
chart interactions and drill behavior. The outer portal cannot restyle pixels
inside the cross-origin iframe.

## Build In Zoho

Create:

1. `CT_PAGE_1_Risk_Action_Center`
2. `CT_PAGE_2_Procurement_Vendor_Capital`
3. `CT_PAGE_3_Consumption_Menu_Profitability`
4. `CT_PAGE_4_SCM_Explorer_Data_Quality`

Place the planned KPI Widgets and saved reports inside their matching
dashboard. Add dashboard User Filters using:

```text
ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md
```

## Connect Without Editing Code

Use:

```text
config/zoho-secured-embed-handoff.example.json
```

The file uses:

```text
abnah-zoho-dashboard-embed-handoff/v3
```

On the portal:

1. Choose **Configure**.
2. Select Page 1, 2, 3 or 4.
3. Paste the matching dashboard's secured-with-login iframe `src` URL.
4. Choose **Save locally**.
5. Switch that page to **Live dashboard**.
6. Use **Handoff** to transfer all four page URLs to another approved laptop.

## Sign-In

The viewer opens Zoho Analytics, signs in with an account that has access to
the four dashboards, returns to the portal and continues. The iframe reuses the
Zoho browser session.

The outer portal cannot inspect or bypass Zoho authentication. Access fails if
the dashboard was not shared with the signed-in account.

## Security

Use secured **Access with Login**.

Do not use:

- Public Access;
- private without-login links;
- client-side OAuth;
- secrets in the handoff JSON;
- actual POSIST rows in the site.

Dashboard filters are presentation controls, not row-level security.

## Troubleshooting

### KPI cannot be shared individually

This is expected. Add the KPI Widget to its page dashboard and share/embed the
dashboard.

### Filter does not change one object

Open that object's **More > Options > Apply Dashboard Filters** setting. Map the
exact field from `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`, or deliberately
exclude the object if its grain does not contain that filter.

### Historical chart collapses to one period

Disable the As-of Source Period dashboard filter for that chart.

### Query 34 controls disappear

Disable period and outlet dashboard filters for Query 34 tiles and detail.

### Sign-in loop or blank iframe

1. Open `https://analytics.zoho.in/` in a normal tab.
2. Complete sign-in.
3. Confirm the dashboard was shared with that account.
4. Return to the portal and reload.
5. Ask IT to allow Zoho embedded content if company policy blocks it.

Official references:

- [Dashboard filters](https://www.zoho.com/analytics/help/dashboard/filter.html)
- [KPI Widgets](https://www.zoho.com/analytics/help/dashboard/kpi-widgets.html)
- [Secured embedding](https://www.zoho.com/analytics/help/publishing/embed-reports.html)
