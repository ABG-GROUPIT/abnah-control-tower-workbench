# Zoho Portal Hosting, Authentication And Handoff

## Final MVP Architecture

```text
Static ABNAH portal shell
        |
        | four secured-with-login Zoho dashboard embeds
        v
4 page dashboards
        |
        | 5 KPI Widgets + saved reports + Dashboard User Filters per page
        v
Approved 38-Query-Table model
```

Zoho KPI Widgets are dashboard-only objects. Do not expect a Share action on
an individual KPI and do not create a separate KPI iframe.

The delivery portal is a separate `/portal/` page. The Schema Atlas links to
it; the live portal is not an Atlas tab.

## Responsibilities

GitHub Pages can host:

- the outer four-page shell and navigation;
- the sign-in preflight;
- blueprint/reference screens;
- four secured Zoho dashboard iframes;
- browser-local import/export of the four dashboard URLs.

Zoho handles:

- viewer authentication and sharing permissions;
- dashboard User Filters and their mapped fields;
- KPI, report, drill and tooltip rendering;
- Query Table execution and refreshed data.

Saving or refreshing data in Zoho does not require rebuilding GitHub Pages.

GitHub Pages is not a backend. It cannot securely store OAuth secrets, mint
short-lived embed URLs, proxy private APIs, verify a Zoho session for the outer
shell or enforce a company-email allowlist. Never commit credentials or actual
ABNAH operational rows.

## Sign-In Flow

1. The viewer chooses **Sign in with Zoho**.
2. Zoho Analytics opens in a normal tab.
3. The viewer signs in with an account granted access to all four dashboards.
4. The viewer returns and chooses **Continue after sign-in**.
5. Each secured dashboard iframe reuses the Zoho browser session.
6. Zoho remains the actual report-access gate.

The static portal cannot inspect Zoho cookies across origins. The Continue
button confirms the sequence, not the login state.

## Pro-Plan Gate

Do not infer entitlement from the plan name. Confirm that a completed
dashboard exposes:

```text
Share > Embed > Access with Login
```

If that works, the MVP requires no client secret, API key or backend. Keep the
dashboard interactive so native User Filters remain available.

## One-File Handoff

Use:

```text
config/zoho-secured-embed-handoff.example.json
```

Schema:

```text
abnah-zoho-dashboard-embed-handoff/v3
```

It contains four entries, each with:

- page ID;
- exact Zoho dashboard name;
- blank or configured secured iframe `src`.

It contains no credential or report row.

Procedure:

1. Generate a secured embed from each completed page dashboard.
2. Copy only the iframe `src`.
3. Open `/portal/` and choose **Configure**.
4. Select the matching page and paste its dashboard URL.
5. Choose **Save locally**.
6. Use **Handoff** to export all four mappings.
7. Import that handoff on another approved browser.

The URLs are saved in that browser profile. Clearing browser site data removes
them.

## Filter And Refresh Flow

```text
Zoho dashboard User Filter
        |
        v
explicit per-object column mapping
        |
        v
compatible KPI Widgets and saved reports update together
```

Use `ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md` for the exact Query Table fields.
Historical trends are excluded from the current-period filter. Query 34
model-wide checks are excluded from period and outlet filters. Scoped item,
vendor, UOM, status and exception filters apply only to compatible objects.

Fixed business conditions remain inside the relevant KPI/report design. The
outer portal does not calculate or filter business values.

## Visual Boundary

The external portal controls navigation, sign-in preflight, page launch and
blueprint/reference screens. Zoho controls every pixel inside the live
cross-origin dashboard iframe, including KPI colors, chart palettes, legends,
labels, number formats and filter layout.

Configure these internal styles in Zoho:

- purple `#6F2DBD`;
- red `#E24950`;
- amber `#D29A2D`;
- green `#168D61`;
- grey `#9A9A9A`.

The mapping covers all four reference pages, 20 KPI objects and 19 requested
visual/report sections.

## GitHub Pages Versus SharePoint

Use GitHub Pages for the demonstration when a public empty shell is acceptable,
Zoho protects all report data and no server-side OAuth is required.

Use SharePoint when the outer shell itself must be company-only and IT has
approved the Zoho iframe domain. SharePoint still does not replace secured
Zoho sharing or become a Zoho backend.

## Company-Laptop Acceptance

- `/portal/` opens.
- `https://analytics.zoho.in/` opens in a normal tab.
- The company account can sign in.
- All four dashboards are shared to that account.
- The v3 handoff imports.
- Dashboard User Filters update mapped KPI/report objects.
- A page refresh loads current Zoho dashboard data.
- No credential or operational row is in the handoff or repository.

## Local Report Reviewer

The local reviewer remains separate because it contains operational rows.
`127.0.0.1` means **this same laptop**. Run the viewer on the laptop that opens
it, leave the terminal active and use `http://127.0.0.1:8765/`.

`Connection refused` means no process is listening on that laptop. It does not
mean port 8765 is inherently insecure.

## Official References

- [Zoho dashboard filters](https://www.zoho.com/analytics/help/dashboard/filter.html)
- [Zoho KPI Widgets](https://www.zoho.com/analytics/help/dashboard/kpi-widgets.html)
- [Zoho secured embedding](https://www.zoho.com/analytics/help/publishing/embed-reports.html)
- [Zoho Directory and Entra SSO](https://www.zoho.com/analytics/help/zoho-directory.html)
