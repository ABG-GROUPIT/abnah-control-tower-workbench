# Zoho Hybrid Portal Setup

## Production Architecture

The GitHub Pages portal is a hybrid control-tower shell:

```text
GitHub Pages custom UI
        |
        +-- Supabase OAuth and data gateway
        |       |
        |       +-- Zoho Query Table API rows
        |
        +-- selected secured Zoho visual views
                |
                +-- map, funnel/bar and price trend
```

The custom portal owns navigation, page hierarchy, filters, KPI cards, action
queues, evidence drawers and custom detail tables. Zoho remains the governed
analytics model and owns visuals that it renders better, including the outlet
map and standard bar/line charts.

The portal does not embed a complete Zoho dashboard as its primary interface.
Each page dashboard remains an external governed fallback.

## Views To Build In Zoho

Build and reconcile all saved chart, summary and tabular views plus:

1. `CT_PAGE_1_Risk_Action_Center`
2. `CT_PAGE_2_Procurement_Vendor_Capital`
3. `CT_PAGE_3_Consumption_Menu_Profitability`
4. `CT_PAGE_4_SCM_Explorer_Data_Quality`

For the current Page 1 and Page 2 hybrid:

| Portal slot | Zoho view | Runtime role |
|---|---|---|
| P1 outlet map | `CT_P1_Outlet_Risk_Map` | Embedded Zoho-native visual |
| P2 procurement funnel | `CT_P2_Procurement_Funnel` | Embedded Zoho-native visual |
| P2 ingredient price trend | `CT_P2_Ingredient_Price_Trend` | Embedded Zoho-native visual |
| Other saved report views | Names in `config/zoho-portal.json` | Open-governed-view drilldown |
| Four page dashboards | Page names above | External fallback and QA |

When a native visual URL is blank, the portal shows a factual local validation
fallback. It never invents a connected view.

## Runtime Data

The Supabase Edge Function:

1. verifies the user's Zoho account and workspace access;
2. resolves allowlisted Query Table IDs from metadata;
3. exports the selected page's rows without persisting them;
4. stores only the encrypted OAuth session and versioned URL handoff;
5. returns secured visual URLs only after a verified portal session.

KPI cards, action queues and evidence tables use Query Table API rows. Clicking
an interactive KPI, vendor, material or PO opens its contributing rows and the
exact saved Zoho view when configured.

## Authentication

The outer portal exposes no operational data before successful Zoho OAuth.
Supabase performs the callback and keeps all secrets server-side.

A secured Zoho iframe can still ask for the user's Zoho browser session because
the iframe is cross-origin. Use **Access with Login** links shared to the same
approved viewer population. OAuth verification and the Zoho iframe session are
related access controls but are not the same browser cookie.

## URL Handoff

Start with:

```text
config/zoho-secured-embed-handoff.example.json
```

Populate the 19 `securedViewUrl` fields and four dashboard fallback fields with
approved HTTPS Zoho Analytics URLs. Save the handoff through the authenticated
Supabase `/config` endpoint. The repository template stays blank.

The current portal embeds only the three native-visual slots listed above.
Other report URLs power **Open governed view** actions in evidence drilldowns.

## Filter Synchronization

The portal appends Zoho's supported, URL-encoded `ZOHO_CRITERIA` parameter to
connected individual views:

- P1 map: `snapshot_date`, `outlet_code`, `category_name`, `action_owner` and
  `risk_type` where compatible;
- P2 funnel: `po_date`, outlet, category, vendor, PO status and material;
- P2 price trend: `receipt_date`, outlet, category, vendor and material.

Region is not sent to these views because it is not a physical field in their
current Query Tables. PO Status is not sent to the receipt-price view. When a
filter cannot be expressed against the target view's physical columns, the
portal leaves it out instead of sending invalid criteria.

Official reference:
https://www.zoho.com/analytics/help/publishing/embed-reports.html

## Do Not Use

- public `open-view` links as an authentication boundary;
- passwords, OAuth tokens, client secrets or operational rows in GitHub;
- a whole-dashboard iframe as the custom portal's primary page;
- custom redrawing of the Zoho map or standard trend charts after their native
  views are connected;
- a filter criterion against a column that the target Zoho view does not
  expose.
