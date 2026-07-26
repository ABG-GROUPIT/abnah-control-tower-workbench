# ABNAH Reference Control Tower - Zoho Capability Matrix

## Decision

The HTML is the visual reference supplied directly by ABNAH. It is therefore
authoritative for the four-page information architecture, KPI and view naming,
business intent, interaction hierarchy, and target visual treatment. It is not
a calculation source: every final number must come from the approved
38-Query-Table model.

Use these implementation classes:

| Class | Meaning | Build decision |
| --- | --- | --- |
| Zoho native | Zoho can reproduce the requested business view without custom code | Build and embed the Zoho report |
| Zoho enhanced | Zoho's native analytical view is more useful than the reference rendering | Use the better Zoho view while retaining the reference title and business purpose |
| Custom finish | Zoho can provide the data, but not the exact reference interaction or chart geometry | Use the stated native fallback for the MVP; add a custom component only after the Zoho report reconciles |

The ABNAH-provided reference contains hard-coded example values. Page 4 is
especially important: its values must never be copied into the production
dashboard.

Coverage is complete at the requirement level: 4 pages, 20 KPI cards and 19
requested visual/report sections are mapped below. This does not mean every
pixel is native Zoho. The exact action-card queue and exact consumption
waterfall remain the two declared custom finishes.

Use the ABNAH reference palette:

| Meaning | Color |
| --- | --- |
| Page 1 accent | Purple `#5b2d82`, gold `#9a8559` |
| Page 2 accent | Blue `#4164d9` |
| Page 3 accent | Gold `#9a8559`, navy `#162552` |
| Page 4 accent | Red `#e44b51`, charcoal `#424b56` |
| Risk purple | `#6f2dbd` |
| Risk red | `#e24950` |
| Risk amber | `#d29a2d` |
| Risk green | `#168d61` |
| Neutral/unknown | `#9a9a9a` |

Set these colors inside the Zoho chart/report formatting UI. A custom outer
portal cannot restyle pixels inside a cross-origin Zoho iframe.

## Final Page 1 - Risk Action Center

### KPI row

| Reference element | Final Zoho object | Source and calculation | Capability | Decision |
| --- | --- | --- | --- | --- |
| Restaurants at risk | `CT_P1_KPI_Outlets_At_Stockout_Risk` | Query 27, Count Distinct `outlet_code`, fixed `risk_type = STOCKOUT` | Zoho native | Keep the reference title in the external shell; subtitle it `Stockout evidence scope` until a cross-risk production fact exists |
| Menu items impacted | `CT_P1_KPI_Menu_Items_At_Risk` | Query 28, Count Distinct `menu_item_code` | Zoho native | Exact |
| Stockout risk | `CT_P1_KPI_Stockout_Risk_Value` | Query 28, Sum `allocated_forecast_net_sales_at_risk` | Zoho native | Exact commercial-risk interpretation |
| Expiry risk | `CT_P1_KPI_Expiry_Risk_Value_Demo` | Query 38, Sum `expiry_risk_value` | Zoho native | Must display the synthetic-estimate disclaimer |
| Open actions | `CT_P1_KPI_Open_Actions` | Query 27, Count Distinct `action_id`, fixed `risk_type = STOCKOUT` | Zoho native | Replaces the earlier `Open Risky PO` fifth card |

Default `month_03 / All outlets` results are `3`, `110`,
`INR 411,695.55`, `INR 271,399.12`, and `6`.

### Main views

| Reference view | Final Zoho object | Capability | Final treatment |
| --- | --- | --- | --- |
| India outlet-risk map | `CT_P1_Outlet_Risk_Map` | Zoho native | Use a Map Scatter/Bubble view with Query 37 coordinates and Query 27 severity/exposure |
| Priority action queue | `CT_P1_Action_Center` | Custom finish | MVP: sorted Zoho tabular view. Exact card queue/drawer: custom portal component over an approved data endpoint |
| Stockout risk | `CT_P1_Stockout_Risk_Detail` | Zoho native | Exact tabular drilldown |
| Menu impact | `CT_P1_Menu_Impact_Detail` | Zoho native | Exact tabular drilldown |
| Expiry risk | `CT_P1_Expiry_Risk_Detail_Demo` | Zoho native | Exact layout, synthetic evidence warning retained |
| Vendor / PO mitigation | `CT_P1_Vendor_PO_Risk` | Zoho native | Exact tabular drilldown where a risky open PO exists |

## Final Page 2 - Procurement, Vendor & Capital Control

### KPI row

| Reference element | Final Zoho object | Source and calculation | Capability | Decision |
| --- | --- | --- | --- | --- |
| Monthly purchase | `CT_P2_KPI_Monthly_Purchase` | Query 29, Sum `ordered_value` | Zoho native | Label `Ordered Gross Value` until ABNAH approves the purchase-value basis |
| Open PO exposure | `CT_P2_KPI_Open_PO_Liability` | Query 29, Sum `pending_value` | Zoho native | Exact |
| Delayed PO value | `CT_P2_KPI_Delayed_PO_Value` | Query 29, Sum `delayed_value` | Zoho native | Restores the reference KPI omitted from the earlier guide |
| Avg OTIF | `CT_P2_KPI_OTIF` | Query 24, `Vendor OTIF %` Aggregate Formula | Zoho enhanced | Use the weighted eligible-line ratio; do not average vendor percentages |
| Price watch | `CT_P2_KPI_Price_Watch` | Query 31, Count Distinct `item_code` | Zoho native | Counts raw materials with a current price record |

Default results are `INR 1,565,981.32`, `INR 177,145.39`,
`INR 156,529.82`, `53.70%`, and `42`.

### Main views

| Reference view | Final Zoho object | Capability | Final treatment |
| --- | --- | --- | --- |
| Procurement funnel | `CT_P2_Procurement_Funnel` | Zoho native | Try Funnel. If the wide four-measure shape is rejected, use grouped horizontal bars; do not add a dependency-level-4 query merely for geometry |
| Vendor risk scorecard | `CT_P2_Vendor_Scorecard` | Zoho native | Use Query 24 formulas so cross-outlet percentages remain weighted |
| Raw material price trend | `CT_P2_Ingredient_Price_Trend` | Zoho native | Line chart using `Weighted Unit Price` |
| Top price movement | `CT_P2_Top_Price_Movement` | Zoho enhanced | Use a Butterfly or signed horizontal bar; it communicates increases and decreases better than the reference table |
| Pending by vendor | `CT_P2_Pending_By_Vendor` | Zoho native | Horizontal bar with drilldown |
| Expected delivery breach | `CT_P2_Expected_Delivery_Breach` | Zoho native | Table filtered by `delayed_po_flag = 1` through Individual Values |

Closing inventory, working capital, open PO count, fill rate, the vendor
matrix, PO status, inventory value, observed wastage, and the expiry scenario
remain valid extended controls. They do not belong in the five-card reference
row.

## Final Page 3 - Consumption Variance & Menu Profitability

Use **consumption**, not yield, in every title and label.

### KPI row

| Reference element | Final Zoho object | Source and calculation | Capability | Decision |
| --- | --- | --- | --- | --- |
| Net sales | `CT_P3_KPI_Net_Sales` | Query 25, Sum `net_sales` | Zoho native | Exact |
| Theoretical COGS | `CT_P3_KPI_Theoretical_COGS` | Query 25, Sum `theoretical_cogs` | Zoho native | Exact |
| Gross margin | `CT_P3_KPI_Menu_Gross_Margin` | Query 25, `Menu Gross Margin %` Aggregate Formula | Zoho enhanced | Weighted ratio, never Average `gross_margin_percent` |
| Menu items | `CT_P3_KPI_Menu_Items` | Query 25, Count Distinct `menu_item_code` | Zoho native | Replaces `Quantity Sold` in the primary reference row |
| Consumption leakage | `CT_P3_KPI_Consumption_Leakage` | Query 21, Sum `leakage_value` | Zoho native | Renamed from the reference's incorrect yield wording |

Default results are `INR 2,192,475.48`, `INR 393,664.46`, `82.04%`,
`110`, and `INR 38,632.37`.

### Main views

| Reference view | Final Zoho object | Capability | Final treatment |
| --- | --- | --- | --- |
| Consumption bridge | `CT_P3_Consumption_Bridge` | Custom finish | MVP: Zoho Combination chart over Query 20 signed bridge fields. Exact waterfall geometry: custom component after reconciliation |
| Consumption variance | `CT_P3_Consumption_Variance` | Zoho enhanced | Use a Butterfly chart over signed variance; clearer than separate positive-only leakage bars |
| Menu BCG matrix | `CT_P3_Menu_BCG` | Zoho enhanced | Use a Bubble chart: X sold quantity, Y gross-margin percentage, size net sales, color BCG quadrant |
| Item sales heatmap | `CT_P3_Outlet_Item_Heatmap` | Zoho enhanced | Zoho Heat Map provides filtering, tooltips and drilldown |

Quantity sold, actual-versus-theoretical detail, leakage ranking, COGS
detail, margin rank, sales trend, category contribution and slow-item ranking
remain extended analytical reports.

## Final Page 4 - SCM Descriptive Explorer & Data Quality

### KPI row

| Reference element | Final Zoho object | Source and calculation | Capability |
| --- | --- | --- | --- |
| Closing stock value | `CT_P4_KPI_Closing_Stock` | Query 33, Sum `closing_stock_value` | Zoho native |
| Open PO snapshot | `CT_P4_KPI_Open_PO` | Query 33, Sum `open_po_value` | Zoho native |
| Monthly sales | `CT_P4_KPI_Net_Sales` | Query 33, Sum `net_sales` | Zoho native |
| Actual consumption | `CT_P4_KPI_Actual_Consumption` | Query 33, Sum `actual_consumption_value` | Zoho native |
| Variance value | `CT_P4_KPI_Consumption_Variance` | Query 21, Sum `signed_consumption_variance_value` | Zoho native |

Default results are `INR 3,344,237.44`, `INR 177,145.39`,
`INR 2,192,475.48`, `INR 377,620.25`, and `INR -22,106.87`.

| Reference view | Final Zoho object | Capability | Final treatment |
| --- | --- | --- | --- |
| Month-end SCM trend | `CT_P4_SCM_Monthly_Trend` | Zoho native | Combination chart; do not apply the current-period filter |
| Data quality exceptions | Six Query 34 tiles plus `CT_P4_Data_Quality_Detail` | Zoho native | Keep zero-count checks visible |
| SCM descriptive explorer | `CT_P4_Descriptive_Explorer` plus source explorers | Zoho enhanced | Pivot/tabular drilldown and export are stronger than the static reference table |

## Final Filter Architecture

Use native Zoho dashboard filters for the first embedded release. This is the
only approach that reliably maps one visible control to the different physical
tables inside a dashboard.

| Scope | Filters |
| --- | --- |
| Common across pages where mapped | As-of Source Period, Outlet |
| Page 1 | Region, risk type, ingredient category, action owner |
| Page 2 | Region, ingredient category, vendor, PO status, raw material |
| Page 3 | Region, outlet, super category, menu category, menu item, raw material; add Canonical UOM only to quantity views |
| Page 4 | Period/range, region, outlet, ingredient category, exception type on the detail report only |

Historical trends must be excluded from the current-period filter. Query 34
must be excluded from both current-period and outlet filters because valid
model-wide rows use `ALL`.

## Custom-Code Boundary

The custom portal may own:

- the reference navigation and page shell;
- the exact action-card queue and detail drawer;
- the exact waterfall presentation;
- page-level secured Zoho embeds;
- later, approved API-fed custom visuals where native Zoho cannot reproduce a
  signed-off interaction.

It must not calculate business KPIs in browser code. A custom visual consumes
an approved aggregate or row set from Zoho/server APIs and renders it. OAuth
tokens, refresh tokens and client secrets remain server-side.

## Official Zoho Evidence

- [Zoho chart types](https://www.zoho.com/analytics/help/chart/chart-types.html)
- [Zoho dashboard filters](https://www.zoho.com/analytics/help/dashboard/filter.html)
- [Zoho KPI widgets](https://www.zoho.com/analytics/help/dashboard/kpi-widgets.html)
- [Embedding Zoho views](https://www.zoho.com/analytics/help/publishing/embed-reports.html)
