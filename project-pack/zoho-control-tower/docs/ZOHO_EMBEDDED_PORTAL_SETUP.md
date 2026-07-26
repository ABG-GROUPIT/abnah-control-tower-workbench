# Custom ABNAH Portal Setup

The final portal uses the ABNAH custom layout. It does not place a complete
Zoho dashboard iframe inside the page.

## What You Build in Zoho

1. Build the required individual saved reports from
   `04_DASHBOARD_BUILD.md`.
2. Build the four native Zoho dashboards for validation and fallback.
3. Add and test Dashboard User Filters.
4. Generate one secured-with-login URL for every required saved report.
5. Generate one secured-with-login URL for every page dashboard.

## What the Custom Portal Uses

| Zoho object | Custom portal use |
| --- | --- |
| Individual chart, pivot or table URL | Placed in its exact ABNAH visual slot |
| Page dashboard URL | Native Zoho validation and fallback link |
| KPI Widget | Validates the KPI in Zoho; not individually embedded |
| Final Query Table aggregate | Supplies custom KPI cards through the secure backend |

## First Report Test

Do this before collecting all report URLs:

1. Open `CT_P2_Ingredient_Price_Trend`.
2. Confirm it contains report User Filters named:
    - `Raw Material`
    - `Vendor`
    - `UOM`
3. Click **Share**.
4. Click **Embed**.
5. Choose secured **Access with Login**.
6. Keep interactive mode enabled.
7. Copy the iframe `src` or secured report URL.
8. Add it to the Page 2 entry in
   `zoho-secured-embed-handoff.example.json`.
9. Test it in the ABG custom portal.
10. Change the custom Raw Material, Vendor and UOM controls.
11. Confirm the one report changes without displaying the full Zoho
    dashboard.

Collect all remaining URLs only after this test passes.

## Filter Control

The custom page owns the visible filters. Each report is registered with the
filter names it accepts.

Example:

```text
Custom Vendor filter
  -> CT_P2_Vendor_Scorecard
  -> CT_P2_Ingredient_Price_Trend
  -> CT_P2_Top_Price_Movement
  -> CT_P2_Pending_By_Vendor
  -> CT_P2_Expected_Delivery_Breach
```

The portal calls the Zoho JavaScript API `applyUserFilter` on compatible
embedded reports. It does not send a filter to an incompatible report.

The exact compatibility list is in
`05_DASHBOARD_FILTER_MAPPING.md`.

## KPI Cards

Continue creating the five native KPI objects inside each Zoho dashboard.
These provide the acceptance totals.

The final custom KPI cards cannot read a dashboard KPI Widget from its URL.
They require either:

1. the secure ABG backend to retrieve approved aggregates from Zoho; or
2. a saved one-value Summary View URL for each KPI.

Use the backend route if the Zoho paid-plan API test succeeds. Do not create
the additional KPI Summary Views unless that test fails.

## URL Configuration File

Use:

```text
zoho-secured-embed-handoff.example.json
```

Schema:

```text
abnah-zoho-view-handoff/v4
```

The file stores:

- four dashboard URLs;
- every required individual report URL;
- exact Zoho view names.

The file stores no credentials and no report rows.

## Sign-In Test

1. Open `https://analytics.zoho.in/` in a normal browser tab.
2. Sign in with the intended company account.
3. Confirm that account can open the saved report directly.
4. Open the custom portal.
5. Confirm the individual embedded report loads.
6. Reload the custom portal.
7. Confirm the report still loads through the Zoho session.

## Do Not Do These

- Do not use Public Access.
- Do not commit OAuth credentials.
- Do not paste client rows into the URL handoff.
- Do not attempt to restyle a cross-origin Zoho chart using portal CSS.
- Do not use one full-dashboard iframe as the final executive UI.
- Do not collect all URLs before the first JavaScript filter test succeeds.

## Fallback

If an individual view cannot load on the company laptop:

1. open its direct secured URL;
2. confirm it was shared with the signed-in account;
3. confirm the browser permits Zoho embedded content;
4. test the native page-dashboard URL;
5. record the exact browser error;
6. keep the native dashboard as the presentation fallback while the embed
   issue is corrected.
