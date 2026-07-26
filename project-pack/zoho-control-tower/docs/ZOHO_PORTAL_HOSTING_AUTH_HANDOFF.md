# Zoho Portal Hosting, Authentication And Handoff

## Final MVP Decision

Use:

```text
Static ABNAH portal shell
        |
        | 39 individual secured-with-login Zoho view embeds
        v
20 KPI views + 19 chart/table/map views
        |
        v
Approved 38-Query-Table model
```

The delivery portal is a separate `/portal/` page. The Schema Atlas contains a
launch link; the live portal is not an Atlas tab.

Do not put one complete Zoho dashboard iframe into each page. Individual view
embeds preserve the external ABNAH page composition.

## GitHub Pages Responsibility

GitHub Pages can host:

- the four-page shell and navigation;
- the supplied ABNAH hierarchy and color system;
- the sign-in preflight screen;
- twenty KPI slots and nineteen report slots;
- secured Zoho iframes;
- browser-local import/export of the view URL handoff;
- external filter controls that generate documented `ZOHO_CRITERIA`.

Zoho handles:

- authentication for report data;
- sharing permissions;
- refreshed data;
- Query Table execution;
- report rendering;
- supported tooltip, drill and underlying-data interactions.

Saving or refreshing data in Zoho does not require rebuilding GitHub Pages.

## Backend Boundary

GitHub Pages is not a backend. It cannot securely:

- keep OAuth client secrets or refresh tokens;
- mint short-lived embed URLs;
- proxy private Zoho APIs;
- verify a Zoho session for the outer shell;
- enforce a company-email allowlist around the shell;
- retrieve Query 27 rows for custom action cards;
- retrieve Query 20 aggregates for a custom waterfall.

Never commit a password, OAuth token, client secret or actual ABNAH report row.

## Sign-In Flow

The portal now presents the Zoho access screen before the control tower.

1. The viewer chooses **Sign in with Zoho**.
2. Zoho Analytics opens in a normal tab.
3. The viewer signs in using the account granted Viewer access.
4. The viewer returns and chooses **Continue after sign-in**.
5. Secured report iframes reuse the Zoho browser session.
6. Zoho checks access to every saved view.

The static portal cannot read Zoho cookies across origins. The Continue button
cannot automatically confirm authentication. It only enforces the correct
sequence. Zoho remains the actual report-access gate.

For true organization SSO before the outer shell opens, configure Zoho
Directory with Microsoft Entra ID or use an approved Embedded Analytics/JWT
architecture. That requires administrator and licensing approval.

## Pro-Plan Gate

Do not infer entitlement from the word `Pro` alone. The required MVP feature is
available when the view UI exposes:

```text
Share > Embed > Access with Login / secured login
```

If that option works for an individual saved report, the MVP needs no API key
or backend.

Do not assume that the current plan includes:

- private no-login permalinks;
- a white-label portal add-on;
- short-lived Embed URL API entitlement;
- JWT embedded SSO.

## One-File Handoff

Use:

```text
config/zoho-secured-embed-handoff.example.json
```

Schema:

```text
abnah-zoho-report-embed-handoff/v2
```

The handoff contains 39 entries:

- saved view name;
- page ID;
- KPI/report slot type;
- blank or configured secured iframe `src`.

It contains no user credential.

Procedure:

1. Generate a secured embed from each saved Zoho view.
2. Copy only the iframe `src`.
3. Open `/portal/`.
4. Choose **Configure**.
5. Select the relevant page.
6. Paste the URL beside the exact `CT_...` view name.
7. Choose **Save locally**.
8. Choose **Handoff** to export all mappings.
9. Use **Configure > Import** on another approved browser.

The URLs are saved in that browser profile. Clearing browser site data removes
them.

## Filter And Refresh Flow

The portal builds a separate filter expression for every applicable saved
view:

```text
Outer filter selection
        |
        v
Per-view table/column contract
        |
        v
URL-encoded ZOHO_CRITERIA
        |
        v
Secured Zoho report reload
```

Historical trends are excluded from the current-period filter. Query 34
model-wide quality checks are excluded from period/outlet filters. Menu,
ingredient, vendor, UOM and status controls are applied only to compatible
sources.

`ZOHO_CRITERIA` is a view filter, not row-level security. Zoho login, sharing
and any approved share criteria enforce security.

The Zoho JavaScript API can later replace reload-based filtering with
`applyUserFilter` if it is validated under the ABNAH plan and every report has
the required named User Filters. The current URL-criteria implementation is
backend-free and officially documented.

## Visual Boundary

The external portal controls:

- page background;
- section hierarchy;
- card/panel frames;
- labels;
- filter layout;
- navigation;
- responsive behavior.

Zoho controls the pixels rendered inside each report iframe. Configure report
palettes, legends, labels, number formats and conditional formatting in Zoho.
The outer portal cannot inject CSS into a cross-origin iframe.

Risk colors:

- purple `#6F2DBD`;
- red `#E24950`;
- amber `#D29A2D`;
- green `#168D61`;
- grey `#9A9A9A`.

The mapping covers all four reference pages, 20 KPI cards and 19 report
sections.

Two exact finishes remain conditional:

- the Page 1 action-card queue needs approved row retrieval for a true custom
  card renderer; the MVP embeds a sorted Zoho table;
- the Page 3 waterfall needs approved aggregate retrieval or a supported Zoho
  waterfall; the MVP embeds the combination chart.

The portal must not recalculate stockout, expiry, OTIF, consumption, variance,
leakage, COGS or margin.

## GitHub Pages Versus SharePoint

Use GitHub Pages for the current demonstration when:

- a public empty shell is acceptable;
- report data stays protected by Zoho;
- easy Git-based handoff is important;
- no server-side OAuth is required.

Use SharePoint when:

- the outer shell must be company-only;
- ABG requires the Entra/SharePoint access gate;
- IT approves the Zoho iframe domain;
- the custom portal is packaged through an approved SharePoint/SPFx route.

SharePoint is still not a Zoho backend. It does not replace secured Zoho
sharing or automatically supply arbitrary client-side scripts through the
standard Embed web part.

## Company-Laptop Acceptance

- `/portal/` opens.
- `https://analytics.zoho.in/` opens in a normal tab.
- The company account can sign in.
- Each configured saved view is shared to that account.
- The v2 handoff imports.
- Live reports preserve the external layout.
- Period and outlet filters skip the documented exclusions.
- A page refresh loads current Zoho views.
- No credential or operational row is in the handoff or repository.

## Local Report Reviewer

The local reviewer remains separate because it contains operational rows.

`127.0.0.1` means **this same laptop**. Run the viewer on the company laptop
that opens it:

1. Run `run_local_report_viewer.bat`.
2. Leave the terminal open.
3. Open `http://127.0.0.1:8765/`.
4. Check `http://127.0.0.1:8765/health`.

Diagnostic:

```powershell
powershell -ExecutionPolicy Bypass -File .\diagnose_local_report_viewer.ps1
```

`Connection refused` means no process is listening. It does not mean port 8765
is inherently insecure.

## Official References

- [Zoho secured embedding and URL criteria](https://www.zoho.com/analytics/help/publishing/embed-reports.html)
- [Zoho JavaScript API](https://www.zoho.com/analytics/js-api/)
- [Zoho applyUserFilter](https://www.zoho.com/analytics/js-api/apply-user-filter.html)
- [Zoho dashboard filters](https://www.zoho.com/analytics/help/dashboard/filter.html)
- [Zoho Directory and Entra SSO](https://www.zoho.com/analytics/help/zoho-directory.html)
- [Zoho short-lived Embed URL API](https://www.zoho.com/analytics/api/v2/embed-api/embed-url.html)
- [SharePoint iframe domain controls](https://support.microsoft.com/en-US/SharePoint/sites-pages/allow-or-restrict-the-ability-to-embed-content-on-sharepoint-pages)
- [SharePoint Embed web part](https://support.microsoft.com/en-US/SharePoint/sites-pages/add-content-to-your-page-using-the-embed-web-part)
