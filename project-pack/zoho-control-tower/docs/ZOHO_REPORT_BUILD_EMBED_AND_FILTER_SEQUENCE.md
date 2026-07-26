# Zoho Report URL Handoff and Custom Portal Sequence

Follow `04_DASHBOARD_BUILD.md` for every Zoho click. This file begins only
after a saved report or page dashboard is working.

## What to Send for Each Saved Report

1. Open the saved report in **View Mode**.
2. Click **Share**.
3. Click **Embed** or **URL / Permalink**.
4. Choose secured **Access with Login**.
5. Keep interactive mode enabled.
6. Copy the report URL or iframe `src`.
7. Paste it beside the exact report name in
   `zoho-secured-embed-handoff.example.json`.

Do not send:

- screenshots;
- exported client rows;
- passwords;
- access tokens;
- refresh tokens;
- client secrets.

## What to Send for Each Page Dashboard

1. Open the page dashboard in **View Mode**.
2. Click **Share**.
3. Click **Embed**.
4. Choose secured **Access with Login**.
5. Keep Dashboard User Filters enabled.
6. Copy the dashboard URL or iframe `src`.
7. Paste it beside the exact `CT_PAGE_...` dashboard name.

The four dashboard URLs are native Zoho validation and fallback views. They
are not the intended final custom UI.

## Required URL List

### Page 1

```text
CT_PAGE_1_Risk_Action_Center
CT_P1_Outlet_Risk_Map
CT_P1_Action_Center
CT_P1_Stockout_Risk_Detail
CT_P1_Menu_Impact_Detail
CT_P1_Expiry_Risk_Detail_Demo
CT_P1_Vendor_PO_Risk
```

### Page 2

```text
CT_PAGE_2_Procurement_Vendor_Capital
CT_P2_Procurement_Funnel
CT_P2_Vendor_Scorecard
CT_P2_Ingredient_Price_Trend
CT_P2_Top_Price_Movement
CT_P2_Pending_By_Vendor
CT_P2_Expected_Delivery_Breach
```

### Page 3

```text
CT_PAGE_3_Consumption_Menu_Profitability
CT_P3_Consumption_Bridge
CT_P3_Consumption_Variance
CT_P3_Menu_BCG
CT_P3_Outlet_Item_Heatmap
```

### Page 4

```text
CT_PAGE_4_SCM_Explorer_Data_Quality
CT_P4_SCM_Monthly_Trend
CT_P4_Data_Quality_Detail
CT_P4_Descriptive_Explorer
```

## Custom Portal Architecture

The final portal will not place one complete Zoho dashboard iframe in the
middle of the custom page.

```text
Custom ABNAH page layout
        |
        +-- custom page filter bar
        |
        +-- individual Zoho report slots
        |       |
        |       +-- Zoho JavaScript API user-filter calls
        |
        +-- custom KPI cards
                |
                +-- secure server call to final Zoho Query Tables
```

The individual report URLs are placed only inside their matching chart or
table slots. The custom portal owns:

- page navigation;
- headings;
- ABNAH colors;
- KPI-card design;
- filter controls;
- Risk Type section switching;
- responsive layout;
- loading and error states.

Zoho retains:

- report calculations;
- chart rendering for individually embedded Zoho reports;
- drilldown;
- tooltip;
- underlying-data permission;
- secured-login access.

## Custom Filter Operation

The portal will create one filter state per page. When a user changes a custom
filter:

1. the portal reads the selected value;
2. it checks which report slots support that filter;
3. it sends the value to each compatible Zoho view through the Zoho JavaScript
   API;
4. it leaves incompatible views unchanged;
5. it requests refreshed KPI values from the backend;
6. it updates the custom KPI cards.

The filter mapping is exactly the mapping in
`05_DASHBOARD_FILTER_MAPPING.md`.

## KPI Limitation and Required Production Setup

Dashboard KPI Widgets do not have individual report URLs. Therefore report and
dashboard URLs alone are sufficient for the custom layout and individually
filtered chart/table embeds, but they are not sufficient for fully custom,
live KPI numbers.

For live custom KPI cards, use one of these two paths:

1. **Preferred production path:** a secure server-side Zoho API connection
   reads the final Query Tables and returns only KPI aggregates.
2. **URL-only fallback:** create one saved Summary View for every KPI and
   provide its secured report URL.

Do not create the 20 additional Summary Views now. Complete the four native
Zoho dashboards first. After the first report URL is tested in the custom
portal, the integration test will determine whether the paid-plan API route is
available. Only use the Summary View fallback if that API route is unavailable.

## Backend Rule

GitHub Pages cannot store Zoho OAuth secrets or run secure server code.
Therefore:

- the GitHub Pages build remains a static Atlas and presentation fallback;
- the live custom portal runs on the ABG application deployment with a server
  route;
- Zoho client secrets and refresh tokens are environment variables;
- secrets never enter the repository or URL handoff file;
- the server exposes only approved KPI/report endpoints;
- browser requests never contain arbitrary SQL.

Supabase is not required for the first implementation. The existing ABG app
server can perform the Zoho API calls and cache the resulting aggregates.

## First Integration Test

Before collecting every URL:

1. Finish `CT_P2_Ingredient_Price_Trend`.
2. Add its `Raw Material`, `Vendor`, and `UOM` report User Filters.
3. Create its secured-with-login individual report URL.
4. Send that one URL first.
5. The app will embed it in one custom Page 2 panel.
6. The app will call the Zoho JavaScript filter function from custom controls.
7. Test the URL while signed into the intended company Zoho account.
8. If the report updates correctly, collect the remaining URLs.

## Final Handoff Check

Before marking a page ready:

1. Its five native Zoho KPI objects match
   `04A_DASHBOARD_EXPECTED_RESULTS.md`.
2. Every required saved report opens in View Mode.
3. Every dashboard User Filter has been tested.
4. The historical trends still show all three periods.
5. Every individual report URL opens after Zoho login.
6. The page dashboard URL opens after Zoho login.
7. The URL handoff JSON contains no credentials or client rows.
