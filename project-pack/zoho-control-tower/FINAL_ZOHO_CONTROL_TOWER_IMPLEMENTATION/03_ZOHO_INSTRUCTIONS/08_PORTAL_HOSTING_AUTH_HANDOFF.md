# Zoho Portal Hosting, Authentication And Handoff

## Final MVP Decision

Use this architecture for the ABNAH demonstration:

```text
GitHub Pages or private Sites
        |
        | static portal shell, navigation and blueprint
        v
Four secured-login Zoho Analytics dashboard iframes
        |
        | Zoho session, sharing permissions, filters and refreshed data
        v
Approved 38-Query-Table Control Tower model
```

Open the delivery portal as a separate page:

```text
/portal/
```

The Schema Atlas contains only a launch link. The delivery portal is not an
Atlas tab and does not inherit the Atlas editing interface.

## What GitHub Pages Can Handle

GitHub Pages can host:

- the portal shell and four-page navigation;
- the ABNAH reference layout, labels and color system;
- secured Zoho iframe embeds;
- browser-local import of the four embed URLs;
- static help, fallback and presentation content;
- client-side construction of documented `ZOHO_CRITERIA` URLs when each
  target view has an approved table/column mapping.

The embedded Zoho dashboard handles:

- current data retrieval;
- data refreshes;
- Zoho dashboard filters;
- drilldown, tooltip and underlying-data interactions exposed by Zoho;
- Zoho user login and dashboard sharing permissions.

Changing or refreshing data in Zoho does not require rebuilding GitHub Pages.
The iframe loads the current Zoho view whenever the portal is loaded or
refreshed.

## What GitHub Pages Cannot Handle

GitHub Pages is not a backend. It cannot securely:

- store a Zoho OAuth client secret or refresh token;
- mint short-lived embed URLs;
- proxy private Zoho API responses;
- enforce a company-email allowlist for the outer portal shell;
- securely run custom APIs for the action queue or waterfall;
- validate an outer-shell login session.

Never put a password, OAuth access token, refresh token, client secret or raw
ABNAH report row in JavaScript, JSON committed to Git, browser local storage,
GitHub Actions variables exposed to the client, or SharePoint page markup.

## Zoho Login Behavior

The MVP uses **secured/with-login embeds**.

1. Share each dashboard with the exact company email registered for the Zoho
   account.
2. Give that account Viewer/read-only access.
3. Generate the dashboard iframe with the secured/with-login option.
4. Sign in to `https://analytics.zoho.in/` with that account.
5. Reload the separate portal and open **Live Zoho**.

This protects the embedded data. It does not authenticate the outer GitHub
Pages shell. A person may see the empty shell or blueprint, but Zoho refuses
the data view unless the signed-in account has access.

Some corporate browsers restrict third-party cookies in iframes. If an iframe
sign-in loops:

1. open Zoho Analytics in a normal tab;
2. complete sign-in;
3. keep that tab/session open;
4. reload the portal;
5. ask IT to allow the Zoho Analytics domain if policy still blocks it.

The portal must not pretend that it can detect the Zoho login state across
origins. The iframe is the enforcement boundary.

## Pro-Plan Gate

Do not infer entitlement from the word `Pro` alone because Zoho plan naming
can vary by edition, bundle and contract.

The required MVP capability is confirmed when the workspace UI exposes:

```text
Share > Embed > Access with Login / secured login
```

If that option works, no OAuth key or server is required for the MVP.

Do not assume these are available on the current plan:

- private no-login permalinks;
- portal/white-label add-ons;
- short-lived Embed URL API entitlement.

Zoho documents the short-lived Embed URL API for Embedded Analytics
customers. It needs a backend, organization/workspace/view IDs, OAuth scope
`ZohoAnalytics.embed.read`, and server-held credentials. General API access on
a paid plan does not by itself prove this embed entitlement.

## One-File Handoff

No key file is required for secured-login iframe delivery. The only handoff
values are the four iframe `src` URLs.

Start with:

```text
config/zoho-secured-embed-handoff.example.json
```

The file has this shape:

```json
{
  "schema": "abnah-zoho-secured-embed-handoff/v1",
  "authMode": "zoho_secured_login",
  "dashboards": {
    "p1": {
      "dashboardViewName": "CT_PAGE_1_Risk_Action_Center",
      "securedEmbedUrl": ""
    },
    "p2": {
      "dashboardViewName": "CT_PAGE_2_Procurement_Vendor_Capital",
      "securedEmbedUrl": ""
    },
    "p3": {
      "dashboardViewName": "CT_PAGE_3_Consumption_Menu_Profitability",
      "securedEmbedUrl": ""
    },
    "p4": {
      "dashboardViewName": "CT_PAGE_4_SCM_Explorer_Data_Quality",
      "securedEmbedUrl": ""
    }
  }
}
```

Handoff procedure:

1. In Zoho, generate a secured-login iframe for each complete dashboard.
2. Copy only each iframe's `src` URL.
3. Paste the four URLs into one handoff JSON file.
4. On the standalone portal, choose **Configure > Import**.
5. Select the JSON file.
6. The portal validates HTTPS and the approved Zoho Analytics hosts.
7. The URLs are saved only in that browser profile.
8. Choose **Handoff** to export the current four-URL file for another approved
   laptop.

The file contains view identifiers, not authentication credentials. Do not
email or commit it unless ABG accepts exposure of those identifiers. Zoho
sharing still controls access to the data.

## Filter And Refresh Flow

For the MVP, keep `filterStrategy` set to `native_dashboard`.

```text
User changes filter inside Zoho iframe
        -> Zoho maps it to selected reports
        -> Zoho Query Tables return the filtered results
        -> Zoho redraws the KPI/chart
```

Configure each Zoho user filter against the individual reports it is allowed
to affect. Historical trend reports must ignore the current-period filter.
Query 34 model-wide exceptions must ignore current-period and outlet filters
when their valid key is `ALL`.

Do not expect controls in the outer static shell to manipulate a cross-origin
iframe. External controls require one of:

- documented `ZOHO_CRITERIA` on each secured view, with exact physical table
  and column mapping;
- a Zoho-supported embed API entitlement and backend;
- a custom server API plus custom-rendered chart.

## Custom-Code Boundary

The 38 Query Tables already perform the business transformations. The portal
must not recalculate stockout exposure, expiry value, OTIF, consumption,
variance, leakage, COGS or gross margin.

The custom layer may render:

- the exact ABNAH action-card queue over approved Query 27 rows;
- the exact ABNAH consumption waterfall over approved Query 20 aggregates.

For production custom rendering, add a small company-approved backend such as
an Azure Function, Cloudflare Worker or internal API. It must:

1. authenticate the company user;
2. keep Zoho OAuth credentials server-side;
3. request only approved aggregate/row fields;
4. return the minimum response to the portal;
5. reconcile output to the relevant Query Table.

Until that backend and entitlement are approved, use the native Zoho table and
combination-chart fallbacks documented in the capability matrix.

## GitHub Pages Versus SharePoint

### Keep GitHub Pages for the current demonstration when

- a public outer shell is acceptable;
- the Zoho data itself must remain login protected;
- easy Git-based transfer and presentation are priorities;
- no server-side OAuth/API work is required.

### Use SharePoint when

- the outer shell itself must be visible only to company users;
- ABG wants the Entra/SharePoint access gate;
- the Microsoft 365 administrator approves the iframe domains.

SharePoint is still not the Zoho backend. Its standard Embed web part accepts
HTTPS iframe content but does not provide arbitrary script execution. A custom
portal may need SPFx or another approved hosting method. Before migration, ask
IT to allow:

```text
https://analytics.zoho.in
https://abg-groupit.github.io
https://abnah-schema-workspace.cfsckksbk4.chatgpt.site
```

Use only the hosts that ABG approves. Test the secured iframe before moving the
shell; otherwise SharePoint may add policy friction without solving a data or
API problem.

## Company-Laptop Acceptance Checklist

- The standalone `/portal/` page opens.
- `analytics.zoho.in` opens in a normal tab.
- The exact company email can sign in.
- Each dashboard has been shared to that account as Viewer.
- The four-URL handoff imports successfully.
- Each page switches to **Live Zoho**.
- Native filters update only their mapped reports.
- Refreshing the page loads current Zoho data.
- No password, OAuth token, client secret or operational row is in the
  handoff file or browser console.

## Local Report Reviewer

The report reviewer is intentionally separate from the hosted portal because
it contains full local operational rows.

`127.0.0.1` means **this same laptop**. A company laptop cannot open a reviewer
running on the personal laptop.

On the company laptop:

1. keep the complete local auditor folder and audit output on that laptop;
2. run `run_local_report_viewer.bat`;
3. leave the terminal window open;
4. open `http://127.0.0.1:8765/`;
5. verify `http://127.0.0.1:8765/health`.

If it fails, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\diagnose_local_report_viewer.ps1
```

`Connection refused` means no process is listening at that address. It does
not mean that port 8765 is inherently insecure.

## Reference Coverage

The delivery mapping covers:

- all 4 ABNAH reference pages;
- all 20 KPI cards;
- all 19 requested visual/report sections;
- all page-specific reference filters.

The page accents are:

- Page 1: purple `#5b2d82` and gold `#9a8559`;
- Page 2: blue `#4164d9`;
- Page 3: gold `#9a8559` and navy `#162552`;
- Page 4: red `#e44b51` and charcoal `#424b56`.

Risk severity remains consistent:

- purple `#6f2dbd`;
- red `#e24950`;
- amber `#d29a2d`;
- green `#168d61`;
- grey `#9a9a9a`.

Zoho report formatting must be set to the same colors manually. The outer
portal cannot restyle the content inside a cross-origin Zoho iframe.

## Official References

- [Zoho secured embedding and URL criteria](https://www.zoho.com/analytics/help/publishing/embed-reports.html)
- [Zoho publishing and live embedded views](https://www.zoho.com/analytics/help/publishing/)
- [Zoho Analytics pricing and plan capabilities](https://www.zoho.com/analytics/help/pricing.html)
- [Zoho short-lived Embed URL API](https://www.zoho.com/analytics/api/v2/embed-api/embed-url.html)
- [SharePoint iframe domain controls](https://support.microsoft.com/en-US/SharePoint/sites-pages/allow-or-restrict-the-ability-to-embed-content-on-sharepoint-pages)
- [SharePoint Embed web part](https://support.microsoft.com/en-US/SharePoint/sites-pages/add-content-to-your-page-using-the-embed-web-part)
