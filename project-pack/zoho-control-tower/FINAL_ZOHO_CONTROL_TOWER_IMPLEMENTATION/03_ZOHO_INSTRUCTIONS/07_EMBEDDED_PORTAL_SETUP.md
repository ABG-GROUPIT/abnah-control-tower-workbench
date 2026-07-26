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

## What To Share And Embed

| Zoho object | Build action | Share separately? | Portal action |
| --- | --- | --- | --- |
| Chart, pivot, summary or tabular view | Save the view, validate it, then add it to the matching page dashboard | Optional for QA or direct access only | Do not paste its individual URL into the current portal |
| KPI Widget | Create it inside the matching page dashboard | No; it has no independent Share action | It arrives through the page-dashboard embed |
| Page dashboard | Add its five KPI objects, all saved views and mapped User Filters | Yes, using secured **Access with Login** | Paste this one dashboard iframe `src` into the matching page |

Therefore, build every planned chart/report as a saved view, but the current
production handoff contains only four URLs. Sharing a chart separately does
not make it participate in one common page filter outside its dashboard.

Chart views can have report-level User Filters when those filters are created
in the report designer. Inside a dashboard, prefer the page's Dashboard User
Filters and map them to each compatible report through **More > Options >
Apply Dashboard Filters > Customize**. Enable **Show Report Specific User
Filter** only when a control should affect that one report and nothing else.

## What The Embedded Page Looks Like

The outer portal keeps the ABNAH header, sign-in preflight, page navigation and
Blueprint/Live switch. In **Live dashboard** mode, the complete content area is
the Zoho dashboard iframe. It therefore uses the layout, typography, controls
and chart rendering configured inside Zoho; it does not become the
pixel-identical custom Blueprint UI.

The Zoho dashboard should be formatted to match the approved ABNAH colors,
hierarchy and spacing as closely as Zoho permits. Browser code cannot inject
CSS into the cross-origin Zoho iframe.

Retaining the exact custom Blueprint UI with live values is a separate advanced
integration: individual report embeds, synchronized JavaScript/API filtering
for every view, and separately rendered KPI values. It is not the current
backend-free Pro-plan implementation.

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
