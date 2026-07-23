# ABNAH Zoho Analytics Corporate Dashboard Blueprint

Use this document after:

- all 18 RAW FastAPI feed tables are connected in Zoho Analytics,
- all 37 Query Tables are created,
- lookup relationships have been completed,
- the workspace is ready for final dashboard design.

This is the corporate dashboard blueprint for the ABNAH Cafe Intelligence synthetic demo. It is not only a chart checklist. It defines the dashboard story, visual choices, executive information hierarchy, chart purpose, axes, measures, filters, drilldowns, final page arrangement, and the exact Zoho build steps for creating the reports and dashboards.

If you are actively clicking inside Zoho, use this file first:

```text
docs/zoho_dashboard_click_by_click_build.md
```

That file is the practical build manual. It gives one KPI/chart at a time with exact source table, field, filter, aggregation, and save name.

## 1. Dashboard Vision

The dashboard should tell a simple executive story:

```text
ABNAH can ingest operational cafe reports through a controlled FastAPI feed layer,
model them inside Zoho Analytics,
and produce outlet-aware dashboards that connect sales, menu mix, vendors,
inventory, events, and competitor context.
```

The core message is not that this is a final production forecasting system. The core message is that ABNAH can build a reliable analytics foundation from operational reports and then extend it toward forecasting, inventory planning, event intelligence, and vendor control.

The dashboard suite must help leadership answer:

1. Which outlet is performing best?
2. Why is one outlet outperforming another?
3. Which menu items and categories drive sales?
4. Which vendors and materials drive spend?
5. Which inventory items need attention?
6. Which events or holidays explain sales spikes?
7. Which competitor pricing positions need review?
8. Does the same model update when Month 2 and Month 3 data is refreshed?

## 2. Audience And Tone

Design for an executive / operations leadership audience.

The dashboard should feel:

- operational,
- structured,
- decision-oriented,
- credible,
- easy to scan in a review meeting.

Avoid a decorative or marketing-style dashboard. Use restrained charts, clear hierarchy, short titles, and tables where operational detail matters.

Recommended tone for chart titles:

- direct,
- business-friendly,
- not overly technical.

Examples:

| Weak title | Better corporate title |
|---|---|
| `Sales Chart` | `Daily Net Sales Trend` |
| `Vendor Data` | `Top Vendors By Ordered Value` |
| `Low Stock` | `Inventory Pressure By Item` |
| `Events` | `Event Sales Lift And Spike Explanation` |
| `Competitors` | `Competitor Price Positioning By Market` |

## 3. Final Dashboard Suite

Build five dashboard modules:

| Dashboard | Scope | Purpose |
|---|---|---|
| `01_Executive_Outlet_Health` | Cross-outlet | Executive comparison of Connaught Place, Hauz Khas, and Saket Premium |
| `02_Sales_Menu_Intelligence` | Outlet-specific | Sales trend, category mix, item performance, premium item context |
| `03_Vendor_Procurement_Analytics` | Outlet-specific | Vendor share, PO status, receipt value, pending/partial PO follow-up |
| `04_Inventory_Consumption_Intelligence` | Outlet-specific | Inventory pressure, stock value, theoretical recipe consumption |
| `05_Calendar_Event_Competitor_Intelligence` | Outlet / market-specific | Event lift, spike explanation, holiday context, competitor price positioning |

If Zoho allows locked dashboard filters, keep one reusable dashboard per module and lock/filter by `outlet_code`.

If filter locking is weak, duplicate outlet-specific pages:

```text
01_Executive_Outlet_Health

02_Sales_Menu_OUT001
02_Sales_Menu_OUT002
02_Sales_Menu_OUT003

03_Procurement_OUT001
03_Procurement_OUT002
03_Procurement_OUT003

04_Inventory_OUT001
04_Inventory_OUT002
04_Inventory_OUT003

05_Calendar_Competitor_OUT001
05_Calendar_Competitor_OUT002
05_Calendar_Competitor_OUT003
```

Outlet mapping:

| Outlet code | Outlet name | Market area |
|---|---|---|
| `OUT001` | `ABNAH Cafe Connaught Place` | `Connaught Place` |
| `OUT002` | `ABNAH Cafe Hauz Khas` | `Hauz Khas` |
| `OUT003` | `ABNAH Cafe Saket Premium` | `Saket` |

## 4. Current Data Model State

The Zoho model is complete at this stage:

| Layer | Count | Description |
|---|---:|---|
| RAW feed tables | 18 | Outlet-specific operational feeds plus static/global feeds |
| STD Query Tables | 10 | Standardized cleaned layer |
| DIM Query Tables | 8 | Lookup/filter dimensions |
| FACT Query Tables | 10 | Analysis-grade fact layer |
| SUM Query Tables | 9 | Dashboard-ready summary layer |
| Lookup relationships | Completed | Used for filters, drilldowns, and cross-table navigation |

Use `FACT_*` and `SUM_*` tables for dashboards. Use RAW tables only for audit drill-through if necessary.

## 5. Chart Selection Philosophy

Use chart types based on decision purpose.

| Business need | Best chart type | Why |
|---|---|---|
| Executive headline number | KPI card / number tile | Fastest way to read status |
| Outlet comparison | Horizontal bar / clustered bar | Easy comparison across three outlets |
| Daily movement | Line chart | Shows trend and seasonality |
| Category contribution | Bar chart or 100% stacked bar | Better than pie for comparison |
| Share of small number of categories | Donut only if categories are few | Acceptable for quick mix, not detailed analysis |
| Vendor ranking | Horizontal bar | Vendor names are long; horizontal labels read better |
| Inventory pressure list | Table with conditional formatting | Operational users need exact item details |
| Event explanation | Table / bar + table | Events need context, not only a chart |
| Price position vs sales | Scatter plot | Shows relationship between price index and sales |
| PO follow-up | Table | Actionable operational list |
| Recipe-to-ingredient analysis | Pivot / matrix | Best for menu item x ingredient relationships |

Avoid overusing:

- pie charts,
- 3D charts,
- gauges,
- decorative visuals,
- raw row tables as primary visuals.

## 6. Global Dashboard Controls

Create a filter strip at the top of every dashboard.

| Filter | Source | Field | Applies to |
|---|---|---|---|
| Month | `DIM_Date` | `month_key` | All modules |
| Date range | `DIM_Date` or source fact | `date_value`, `sales_date`, `activity_date`, `po_date`, `receipt_date`, `inventory_date` | All modules |
| Outlet | `DIM_Outlet` | `outlet_code`, `outlet_name` | All outlet-specific modules |
| Market area | `DIM_Outlet`, competitor tables | `market_area`, `outlet_market_area` | Competitor module |
| Category | Sales/menu tables | `category`, `super_category` | Sales, menu, event, competitor |
| Vendor | `FACT_Vendor_Spend` | `vendor_name` | Procurement |
| Ingredient | `DIM_Ingredient` | `ingredient_name`, `ingredient_code` | Inventory/consumption |
| Event type | `DIM_Event` / event summaries | `event_type` | Calendar/event module |
| Competitor | `DIM_Competitor` | `competitor_name` | Competitor module |

Filter behavior:

- Dashboard 1: outlet filter optional.
- Dashboards 2-5: outlet filter required.
- Competitor visuals: market area filter required if outlet lookup does not cascade cleanly.
- Date/month filter should be visible on every page.
- Dropdown filters should use `List only relevant values` so downstream choices are limited by upstream choices.
- Build dropdown filters from the dashboard's primary fact table wherever possible. Example: Dashboard 3 vendor/material filters should come from `FACT_Vendor_Spend`, not from `DIM_Vendor`.

## 7. Corporate Layout Standard

Use this layout on every dashboard:

1. Header: dashboard name + short business purpose.
2. Filter strip: date/month/outlet/category/vendor/event as relevant.
3. KPI row: 3 to 6 KPI cards.
4. Primary decision row: one or two main charts.
5. Diagnostic row: supporting breakdown charts.
6. Detail row: operational table or pivot.
7. Caveat note: only where needed, especially inventory, competitor, event lift.

Recommended visual sizing:

| Component | Width | Height |
|---|---|---|
| KPI cards | 4 to 6 cards across | compact |
| Main trend chart | half or full width | medium |
| Ranking chart | half width | medium |
| Detail table | full width | taller |
| Caveat text | full width | short |

## 8. Dashboard 1: Executive / Outlet Comparison / Outlet Health

Scope: all outlets.

Purpose: give leadership one page to compare outlet performance, sales trend, inventory pressure, event exposure, and broad operational health.

Primary source tables:

- `FACT_Outlet_Daily_Health`
- `SUM_Outlet_Health`
- `SUM_Event_Impact`
- `SUM_Event_Markers`

### 8.1 Header

Title:

```text
Executive Outlet Health
```

Subtitle:

```text
Cross-outlet view of sales, procurement, receipts, inventory pressure, and event exposure.
```

### 8.2 Filters

Create these filters first:

1. `Date Range`
   - Source table: `FACT_Outlet_Daily_Health`
   - Field: `activity_date`
   - Use on: executive KPI cards and executive charts.

2. `Outlet`
   - Source table: `FACT_Outlet_Daily_Health`
   - Field: `outlet_name`
   - Default: `All`.

3. `Event Type`
   - Source table: `SUM_Event_Impact`
   - Field: `event_type`
   - Use on: event lift KPI and event explanation charts.

Do not add `Month` first. Add `Month` only after `Date Range` works and the `FACT_Outlet_Daily_Health.activity_date -> DIM_Date.date_value` lookup is confirmed.

### 8.3 Executive KPI Row

Do not use vague executive labels such as `Total Quantity Sold`. That number only means customer-facing menu units sold, and it belongs in the Sales/Menu dashboard, not the executive dashboard.

Use these executive KPI cards:

1. `Net Sales Revenue`
   - Meaning: total sales revenue for the selected period.
   - Build from: `FACT_Outlet_Daily_Health.net_sales`.
   - Calculation: `SUM`.

2. `Average Daily Revenue`
   - Meaning: sales run-rate per active business day.
   - Build from: aggregate formula `AF_Average_Daily_Revenue`.
   - Formula: `SUM(net_sales) / DISTINCTCOUNT(activity_date)`.

3. `Procurement Spend`
   - Meaning: purchase-order value raised in the selected period.
   - Build from: `FACT_Outlet_Daily_Health.po_value`.
   - Calculation: `SUM`.

4. `Purchase-To-Sales Ratio`
   - Meaning: procurement spend as a percentage of sales.
   - Build from: aggregate formula `AF_Purchase_To_Sales_Ratio`.
   - Formula: `SUM(po_value) / SUM(net_sales) * 100`.

5. `Revenue Per Inventory Rupee`
   - Meaning: sales generated per rupee of average inventory value.
   - Build from: aggregate formula `AF_Revenue_Per_Inventory_Rupee`.
   - Formula: `SUM(net_sales) / AVG(inventory_value)`.

6. `Inventory Pressure Item-Days`
   - Meaning: count of low-stock inventory observations across outlet-days.
   - Build from: `FACT_Outlet_Daily_Health.low_stock_item_count`.
   - Calculation: `SUM`.

7. `Event-Linked Sales Lift %`
   - Meaning: average directional sales lift during mapped event windows.
   - Build from: `SUM_Event_Impact.sales_lift_pct`.
   - Calculation: `AVG`.

8. `Best Performing Outlet`
   - Meaning: outlet with highest net sales in the selected period.
   - Build as: a Top 1 table, not a normal KPI number.
   - Source: `FACT_Outlet_Daily_Health`.
   - Row: `outlet_name`.
   - Measure: `SUM(net_sales)`.
   - Sort: descending, Top 1.

Profit note:

The current 37-table model supports profit-pressure proxies such as `Purchase-To-Sales Ratio` and `Revenue Per Inventory Rupee`. It does not yet support audited profit because labour, rent, wastage, delivery commission, and actual COGS are not in the source reports. Only call a profit metric `Estimated Gross Profit` after creating and validating an additional cost-estimation query table from recipe BOM plus inventory average price.

### 8.4 Main Charts

| Chart | Recommended type | Source | X-axis | Y-axis | Series/color | Sort | Purpose |
|---|---|---|---|---|---|---|---|
| Outlet Sales Ranking | Horizontal bar | `SUM_Outlet_Health` | `outlet_name` | `SUM(total_net_sales)` | `outlet_health_band` | Desc by sales | Shows best-performing outlet |
| Daily Sales Trend By Outlet | Line chart | `FACT_Outlet_Daily_Health` | `activity_date` | `SUM(net_sales)` | `outlet_name` | Date ascending | Shows movement over time |
| Sales vs Purchase vs Receipt | Clustered bar | `SUM_Outlet_Health` | `outlet_name` | `SUM(total_net_sales)`, `SUM(total_po_value)`, `SUM(total_receipt_value)` | Measure name | Outlet order | Compares commercial and procurement activity |

### 8.5 Diagnostic Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Purpose |
|---|---|---|---|---|---|---|
| Inventory Pressure By Outlet | Bar | `SUM_Outlet_Health` | `outlet_name` | `SUM(low_stock_item_days)` | `outlet_health_band` | Identifies pressure by outlet |
| Event Exposure By Outlet | Bar | `SUM_Outlet_Health` | `outlet_name` | `SUM(event_day_markers)` | `market_area` | Shows event-affected outlet activity |
| Outlet Health Band | Stacked bar or donut | `SUM_Outlet_Health` | `outlet_health_band` | `COUNT(outlet_code)` | none | Summarizes health state |

### 8.6 Detail Tables

| Table | Source | Rows / dimensions | Measures |
|---|---|---|---|
| Outlet Health Detail | `SUM_Outlet_Health` | `outlet_code`, `outlet_name`, `market_area`, `outlet_health_band` | `total_net_sales`, `avg_daily_net_sales`, `total_sold_qty`, `total_po_value`, `total_receipt_value`, `avg_inventory_value`, `low_stock_item_days`, `event_day_markers` |
| Spike Explanation Panel | `SUM_Event_Markers` | `event_date`, `outlet_name`, `event_name`, `event_type`, `affected_category`, `affected_items`, `confidence_level` | `event_day_sales`, `baseline_sales`, `sales_lift_percentage` |

### 8.7 Corporate Notes

Use this dashboard first in the demo. It proves the model is outlet-aware and leadership-ready.

Do not overload this page with item-level or vendor-level detail. Keep it executive.

## 9. Dashboard 2: Sales And Menu Intelligence

Scope: selected outlet only.

Purpose: explain sales performance through daily trend, category mix, menu-item ranking, realized unit price, and event/item sensitivity.

Primary source tables:

- `FACT_Sales`
- `SUM_Menu_Item_Performance`
- `SUM_Event_Impact`

Build date-sensitive sales/category visuals from `FACT_Sales`. Do not use `SUM_Sales_Category_Mix` for dashboard charts that must respond to `Date Range`, because that summary table has no `sales_date` column.

### 9.1 Header

Title:

```text
Sales And Menu Intelligence - Selected Outlet
```

Subtitle:

```text
Menu performance, category contribution, realized pricing, and event-sensitive items.
```

### 9.2 Filters

| Filter | Field |
|---|---|
| Outlet required | `outlet_code` / `outlet_name` |
| Month | `DIM_Date.month_key` |
| Date range | `FACT_Sales.sales_date` |
| Category | `category` |
| Super category | `super_category` |
| Menu item | `item_name` |
| Event type | `SUM_Event_Impact.event_type` |

### 9.3 KPI Row

| KPI title | Source | Measure | Purpose |
|---|---|---|---|
| Net Sales | `FACT_Sales` | `SUM(net_sale)` | Selected outlet revenue |
| Menu Units Sold | `FACT_Sales` | `SUM(qty)` | Customer-facing menu item units sold, not ingredients |
| Average Realized Unit Price | `FACT_Sales` | `AVG(net_sale_per_qty)` | Blended realized price |
| Active Menu Items | `FACT_Sales` | `COUNTD(item_number)` | Menu breadth |
| Highest Sales Item | `SUM_Menu_Item_Performance` | Top item by `total_net_sale` | Quick winner identification |

### 9.4 Main Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Sort | Purpose |
|---|---|---|---|---|---|---|---|
| Daily Net Sales Trend | Line | `FACT_Sales` | `sales_date` | `SUM(net_sale)` | optional `category` | Date ascending | Shows daily sales movement |
| Category Revenue Mix | Horizontal bar | `FACT_Sales` | `category` | `SUM(net_sale)` | `super_category` | Desc by revenue | Shows category contribution for selected date/outlet filters |
| Super Category Share | 100% stacked bar or donut | `FACT_Sales` | `super_category` | `SUM(net_sale)` | none | Desc by revenue | Shows food/beverage/dessert mix for selected date/outlet filters |

### 9.5 Menu Performance Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Filters | Purpose |
|---|---|---|---|---|---|---|---|
| Top Items By Net Sales | Horizontal bar | `SUM_Menu_Item_Performance` | `item_name` | `SUM(total_net_sale)` | `category` | Top 10/15 | Identifies revenue winners |
| Top Items By Quantity | Horizontal bar | `SUM_Menu_Item_Performance` | `item_name` | `SUM(total_qty)` | `category` | Top 10/15 | Identifies volume winners |
| Realized Unit Price By Item | Bar or dot plot | `SUM_Menu_Item_Performance` | `item_name` | `AVG(avg_realized_unit_price)` | `category` | Category/item filter | Compares price realization |
| Premium Item Performance | Scatter | `SUM_Menu_Item_Performance` | `avg_price_index` | `total_net_sale` | `price_position`; size `total_qty` | Category/filter | Finds premium items that still sell |

### 9.6 Detail Tables

| Table | Source | Rows / dimensions | Measures |
|---|---|---|---|
| Menu Item Detail | `SUM_Menu_Item_Performance` | `item_number`, `item_name`, `super_category`, `category`, `performance_note` | `total_qty`, `total_net_sale`, `avg_realized_unit_price`, `avg_price_index` |
| Event Item Lift | `SUM_Event_Impact` | `event_name`, `event_type`, `item_name`, `category`, `confidence_level` | `event_day_sales`, `baseline_sales`, `sales_lift_value`, `sales_lift_pct` |

### 9.7 Corporate Notes

This module should help an operations user decide which items to promote, review, or protect during high-demand events.

Avoid claiming event lift is causal. Use "directional lift" or "event-associated lift".

## 10. Dashboard 3: Vendor And Procurement Analytics

Scope: selected outlet only.

Purpose: explain procurement behavior through vendor share, ordered value, receipt value, PO status, pending/partial PO lines, and material/vendor mapping.

Primary source tables:

- `FACT_Purchase_Order`
- `FACT_Entry_Receipt`
- `FACT_PO_Receipt_Comparison`
- `FACT_Vendor_Spend`

Use `FACT_Vendor_Spend` for the main procurement KPI cards and vendor-share charts. It combines PO raised value and receipt booked value into one outlet/date/vendor/material grain, so the same outlet, date, vendor, and material filters can affect both sides consistently.

### 10.1 Header

Title:

```text
Vendor And Procurement Analytics - Selected Outlet
```

Subtitle:

```text
Vendor share, order value, receipt value, and PO follow-up visibility.
```

### 10.2 Filters

| Filter | Field |
|---|---|
| Outlet required | `outlet_code` / `outlet_name` |
| Month | `DIM_Date.month_key` |
| Procurement date range | `FACT_Vendor_Spend.activity_date` |
| Vendor | `FACT_Vendor_Spend.vendor_name` |
| PO status | `FACT_Vendor_Spend.po_status` |
| Ingredient/material | `FACT_Vendor_Spend.item_name`, `FACT_Vendor_Spend.item_code` |
| Category | `category_name`, `super_category_name` |

Set dropdown filters to `List only relevant values` and place them in this order:

```text
Outlet -> Procurement Date Range -> Vendor -> Material -> PO Status
```

This makes the vendor dropdown show only vendors available for the selected outlet.

### 10.3 KPI Row

| KPI title | Source | Measure | Purpose |
|---|---|---|---|
| PO Raised Value | `FACT_Vendor_Spend` | `SUM(ordered_value)` | PO value raised in the selected period/vendor/outlet |
| Receipt Booked Value | `FACT_Vendor_Spend` | `SUM(received_value)` | Receipt/entry value booked in the selected period/vendor/outlet |
| PO vs Receipt Value Gap | `FACT_Vendor_Spend` | `SUM(ordered_value) - SUM(received_value)` | Difference between PO value raised and receipt value booked in the selected scope |
| Open / Partial PO Status Count | `FACT_Vendor_Spend` | `SUM(open_or_partial_po_count)` | Status follow-up count under the same outlet/date/vendor/material filters |
| Active Vendors In Selected Outlet | `FACT_Vendor_Spend` | `COUNTD(vendor_name)` | Vendor base for selected outlet/date/material; usually do not apply the vendor filter to this card |
| Pending / Partial Lines | `FACT_PO_Receipt_Comparison` | `SUM(pending_or_partial_flag)` | PO risk queue |

`Receipt Booked Value` can be higher or lower than `PO Raised Value` for a selected date range because receipts can be booked for POs raised earlier or later. Treat them as two operational movements, not as a strict same-period accounting reconciliation.

`Open / Partial PO Status Count` is not a value-gap metric. It counts PO lines that are Pending, Partially Received, or have a positive remaining quantity. Use `PO vs Receipt Value Gap` when the demo question is about why PO raised value and receipt booked value differ.

### 10.4 Vendor Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Sort | Purpose |
|---|---|---|---|---|---|---|---|
| Vendor PO Raised Share | Horizontal bar | `FACT_Vendor_Spend` | `vendor_name` | `SUM(ordered_value)` | optional `market_area` | Desc by ordered value | Identifies top vendors by PO value under current filters |
| Vendor Receipt Booked Share | Horizontal bar | `FACT_Vendor_Spend` | `vendor_name` | `SUM(received_value)` | optional `market_area` | Desc by received value | Identifies top vendors by receipts under current filters |
| Vendor Share Percent | Bar | `FACT_Vendor_Spend` | `vendor_name` | percent of `SUM(ordered_value)` if Zoho chart supports percent-of-total labels | none | Desc by share | Shows dependency concentration |
| Vendor Spend Trend | Multi-line or combo | `FACT_Vendor_Spend` | `activity_date` | `SUM(ordered_value)`, `SUM(received_value)` | Measure name or vendor | Date ascending | Tracks ordering and receipt movement |

### 10.5 PO Status Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Purpose |
|---|---|---|---|---|---|---|
| PO Status Value | Stacked bar | `FACT_Purchase_Order` | `po_status` | `SUM(total_item_cost)` | `vendor_name` or `category_name` | Shows value held by status |
| PO Status Count | Bar | `FACT_Purchase_Order` | `po_status` | `COUNTD(po_number)` | none | Shows number of POs by status |
| Processed vs Remaining Value | Clustered bar | `FACT_Purchase_Order` | `vendor_name` | `SUM(processed_value_est)`, `SUM(remaining_value_est)` | Measure name | Shows fulfillment gap |

### 10.6 Detail Tables

| Table | Source | Rows / dimensions | Measures |
|---|---|---|---|
| Pending / Partial PO Detail | `FACT_PO_Receipt_Comparison` | `po_number`, `vendor_name`, `item_name`, `po_status`, `po_date`, `expected_delivery_date` | `ordered_qty`, `processed_qty`, `matched_received_qty`, `unmatched_order_qty`, `remaining_qty`, `total_item_cost` |
| Vendor Material Matrix | `FACT_Purchase_Order` | Rows: `vendor_name`; columns: `item_name` or `category_name` | `SUM(total_item_cost)` |
| Receipt Detail | `FACT_Entry_Receipt` | `receipt_date`, `vendor_name`, `transaction_number`, `invoice_number`, `item_name` | `received_qty`, `grand_total`, `realized_receipt_unit_cost` |

### 10.7 Corporate Notes

This dashboard is about operational procurement visibility, not audited accounts payable.

The PO-to-receipt comparison is approximate because the entry report does not contain direct PO number.

## 11. Dashboard 4: Inventory And Consumption Intelligence

Scope: selected outlet only.

Purpose: connect current stock position, low-stock pressure, category inventory value, and theoretical recipe consumption from menu sales.

Primary source tables:

- `FACT_Inventory_Closing`
- `FACT_Theoretical_Consumption`
- `FACT_Outlet_Daily_Health`
- `SUM_Inventory_Risk`

### 11.1 Header

Title:

```text
Inventory And Consumption Intelligence - Selected Outlet
```

Subtitle:

```text
Inventory pressure, stock value, and recipe-based material demand.
```

### 11.2 Filters

| Filter | Field |
|---|---|
| Outlet required | `outlet_code` / `outlet_name` |
| Month | `DIM_Date.month_key` |
| Inventory date | `inventory_date` |
| Sales date | `sales_date` |
| Ingredient/material | `ingredient_name`, `item_name`, `item_code` |
| Inventory category | `category_name`, `super_category_name` |
| Pressure band | `inventory_pressure_band` |

### 11.3 KPI Row

| KPI title | Source | Measure | Purpose |
|---|---|---|---|
| Inventory Value | `SUM_Inventory_Risk` | `SUM(total_amt)` | Current stock value |
| Low Stock Item Count | `SUM_Inventory_Risk` | `SUM(low_stock_flag)` | Pressure count |
| Closing Inventory Quantity | `SUM_Inventory_Risk` | `SUM(total_qty)` | Closing stock quantity for inventory items |
| Theoretical Ingredient Demand | `FACT_Theoretical_Consumption` | `SUM(theoretical_ingredient_qty)` | Recipe demand implied by sales |
| Event Days With Pressure | `FACT_Outlet_Daily_Health` | `SUM(event_count)` where `low_stock_item_count > 0` | Event-linked pressure context |

### 11.4 Inventory Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Sort | Purpose |
|---|---|---|---|---|---|---|---|
| Inventory Value By Category | Bar | `SUM_Inventory_Risk` | `category_name` | `SUM(total_amt)` | `super_category_name` | Desc by value | Shows latest stock value concentration |
| Inventory Pressure Band | Stacked bar or donut | `SUM_Inventory_Risk` | `inventory_pressure_band` | `COUNT(item_code)` | none | Band order | Summarizes stock pressure |
| Top Inventory Value Items | Horizontal bar | `SUM_Inventory_Risk` | `item_name` | `SUM(total_amt)` | `category_name` | Desc by value | Identifies high-value stock |
| Low Stock Items | Horizontal bar | `SUM_Inventory_Risk` | `item_name` | `SUM(low_stock_flag)` | `inventory_pressure_band` | Low-stock first | Highlights pressure items |

### 11.5 Consumption Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Purpose |
|---|---|---|---|---|---|---|
| Theoretical Consumption Trend | Line | `FACT_Theoretical_Consumption` | `sales_date` | `SUM(theoretical_ingredient_qty)` | `ingredient_name` | Shows ingredient demand over time |
| Top Theoretical Ingredients | Horizontal bar | `FACT_Theoretical_Consumption` | `ingredient_name` | `SUM(theoretical_ingredient_qty)` | `ingredient_unit` | Identifies demand-heavy ingredients |
| Menu Item To Ingredient Demand | Pivot / matrix | `FACT_Theoretical_Consumption` | Rows: `menu_item_name`; columns: `ingredient_name` | `SUM(theoretical_ingredient_qty)` | Explains material demand by recipe |

### 11.6 Detail Tables

| Table | Source | Rows / dimensions | Measures |
|---|---|---|---|
| Low Stock Detail | `SUM_Inventory_Risk` | `item_code`, `item_name`, `category_name`, `inventory_pressure_band`, `risk_note` | `total_qty`, `total_amt`, `total_theoretical_qty`, `low_stock_flag` |
| Event Day Inventory Pressure | `FACT_Outlet_Daily_Health` | `activity_date`, `outlet_name`, `health_note` | `net_sales`, `inventory_value`, `low_stock_item_count`, `event_count` |

### 11.7 Corporate Notes

Use "inventory pressure" language.

Do not call it final stockout prediction. Production-grade prediction would require reorder levels, lead times, wastage, transfers, opening stock, and actual consumption postings.

## 12. Dashboard 5: Calendar, Event, And Competitor Intelligence

Scope: selected outlet or selected market area.

Purpose: explain event-linked sales movement, holiday context, and competitor price positioning.

Primary source tables:

- `SUM_Event_Impact`
- `SUM_Event_Markers`
- `FACT_Event_Sales_Impact`
- `FACT_Competitor_Price_Position`
- `SUM_Competitor_Positioning`
- `DIM_Event`
- `DIM_Holiday`
- `DIM_Competitor`

### 12.1 Header

Title:

```text
Calendar, Event, And Competitor Intelligence - Selected Outlet / Market
```

Subtitle:

```text
Event lift, spike explanation, holiday context, and competitor price position.
```

### 12.2 Filters

| Filter | Field |
|---|---|
| Outlet required | `outlet_code`, `outlet_name` |
| Market area required for competitor charts | `market_area`, `outlet_market_area` |
| Month | `DIM_Date.month_key` |
| Event type | `event_type` |
| Event name | `event_name` |
| Competitor | `competitor_name` |
| Category | `category`, `competitor_category` |
| Price position | `price_position`, `price_position_band` |

### 12.3 KPI Row

| KPI title | Source | Measure | Purpose |
|---|---|---|---|
| Event Day Sales | `SUM_Event_Impact` | `SUM(event_day_sales)` | Event-linked sales |
| Baseline Sales | `SUM_Event_Impact` | `AVG(baseline_sales)` | Baseline comparison |
| Average Event Lift % | `SUM_Event_Impact` | `AVG(sales_lift_pct)` | Directional lift |
| Manual Event Count | `DIM_Event` | `COUNTD(event_id)` | Event coverage |
| Premium Context Sales | `SUM_Competitor_Positioning` | `SUM(premium_context_sales_lines)` | Premium items with mapped sales |

### 12.4 Event Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Sort | Purpose |
|---|---|---|---|---|---|---|---|
| Event Sales By Event | Bar | `SUM_Event_Impact` | `event_name` | `SUM(event_day_sales)` | `event_type` | Desc by sales | Shows highest event-linked sales |
| Event Lift % By Event | Bar | `SUM_Event_Impact` | `event_name` | `AVG(sales_lift_pct)` | `confidence_level` | Desc by lift | Shows strongest directional lift |
| Event Sales Trend | Line | `SUM_Event_Markers` | `event_date` | `SUM(event_day_sales)` | `event_name` | Date ascending | Shows timing of event spikes |
| Holiday Sales Trend | Line | `FACT_Sales` | `sales_date` | `SUM(net_sale)` | `holiday_type` or `holiday_name` | Date ascending | Shows sales around holiday markers |

### 12.5 Competitor Charts

| Chart | Type | Source | X-axis | Y-axis | Series/color | Sort | Purpose |
|---|---|---|---|---|---|---|---|
| Competitor Price Index | Bar | `SUM_Competitor_Positioning` | `competitor_name` | `AVG(avg_price_index)` | `competitor_category` | Desc by index | Shows ABNAH relative price position |
| ABNAH Vs Competitor Difference | Bar | `SUM_Competitor_Positioning` | `competitor_category` | `AVG(avg_price_difference)` | `price_position_band` | Desc by difference | Shows category price gap |
| Price Position Sales | Stacked bar | `SUM_Competitor_Positioning` | `price_position_band` | `SUM(mapped_net_sale)` | `competitor_category` | Band order | Shows sales by relative price position |
| Premium Item Performance | Scatter | `FACT_Competitor_Price_Position` | `price_index` | `SUM(net_sale)` | `price_position_band`; size `SUM(qty)` | Market/outlet | Shows premium items still selling |

### 12.6 Detail Tables

| Table | Source | Rows / dimensions | Measures |
|---|---|---|---|
| Spike Explanation Panel | `SUM_Event_Markers` | `event_date`, `outlet_name`, `event_name`, `event_type`, `affected_category`, `affected_items`, `confidence_level` | `event_day_sales`, `baseline_sales`, `sales_lift_percentage` |
| Premium Overperformance Table | `FACT_Competitor_Price_Position` | `abnah_item_name`, `competitor_name`, `competitor_category`, `price_position`, `price_position_band` | `price_index`, `price_difference`, `SUM(net_sale)`, `SUM(qty)` |
| Competitor Positioning Detail | `SUM_Competitor_Positioning` | `outlet_name`, `competitor_name`, `competitor_category`, `price_position_band`, `positioning_note` | `avg_price_index`, `avg_price_difference`, `mapped_sales_qty`, `mapped_net_sale`, `premium_context_sales_lines` |

### 12.7 Corporate Notes

Competitor pricing is contextual.

Do not claim competitor prices caused sales changes. The correct statement is:

```text
The dashboard shows whether ABNAH sold items while positioned above, below, or near competitor pricing in the same market area.
```

## 13. Cross-Dashboard Navigation

Recommended drill path:

```text
Executive Outlet Health
-> selected outlet
-> Sales/Menu module
-> selected item/category
-> Event/Competitor module
```

Procurement drill path:

```text
Executive Outlet Health
-> selected outlet
-> Vendor/Procurement module
-> selected vendor
-> pending/partial PO detail
```

Inventory drill path:

```text
Executive Outlet Health
-> selected outlet
-> Inventory/Consumption module
-> low stock item
-> theoretical consumption / recipe demand
```

## 14. Conditional Formatting Standards

Use conditional formatting sparingly but consistently.

| Field | Suggested rule |
|---|---|
| `sales_lift_pct` | Green above 10%, neutral between -10% and 10%, red below -10% |
| `low_stock_flag` | Red when 1 |
| `inventory_pressure_band` | Red for pressure/low, amber for watch, green for stable |
| `pending_or_partial_flag` | Red when 1 |
| `price_index` | Amber above 1.05, blue below 0.95, neutral near parity |
| `outlet_health_band` | Green stable, amber event-sensitive, red pressure |

Do not make the entire dashboard red/green. Use status colors only where action is required.

## 15. Month Refresh Demonstration

The dashboard must demonstrate that the same Zoho model updates after feed refresh.

### Month 1 Baseline

Expected sales rows:

| Table | Rows |
|---|---:|
| `RAW_Sales_Report_OUT001` | 1,529 |
| `RAW_Sales_Report_OUT002` | 1,595 |
| `RAW_Sales_Report_OUT003` | 1,731 |
| `STD_Sales_Report` | 4,855 |

### Month 2

Run:

```powershell
python manage_demo.py load-month 2
```

Refresh all RAW feeds in Zoho.

Expected sales rows:

| Table | Rows |
|---|---:|
| `RAW_Sales_Report_OUT001` | 3,003 |
| `RAW_Sales_Report_OUT002` | 3,088 |
| `RAW_Sales_Report_OUT003` | 3,325 |
| `STD_Sales_Report` | 9,416 |

### Month 3

Run:

```powershell
python manage_demo.py load-month 3
```

Refresh all RAW feeds in Zoho.

Expected sales rows:

| Table | Rows |
|---|---:|
| `RAW_Sales_Report_OUT001` | 4,623 |
| `RAW_Sales_Report_OUT002` | 4,747 |
| `RAW_Sales_Report_OUT003` | 5,206 |
| `STD_Sales_Report` | 14,576 |

### Reset

Run:

```powershell
python manage_demo.py reset-to-month 1
```

Refresh Zoho again. Dashboard values should return to Month 1 baseline.

If values do not reset, fix the RAW import refresh behavior before changing dashboards.

## 16. Final Dashboard QA Checklist

Before the demo:

1. All five dashboards open without broken charts.
2. Dashboard 1 compares all three outlets.
3. Dashboards 2-5 require outlet or market-area filtering.
4. All charts use `FACT_*` or `SUM_*` tables unless intentionally using audit detail.
5. KPI numbers match source Query Tables.
6. Chart titles are business-readable.
7. Long vendor/item names are readable, preferably with horizontal bars or tables.
8. Date filters affect all relevant charts.
9. Outlet filters affect all relevant outlet-specific charts.
10. Competitor charts filter by market area.
11. Inventory charts use pressure/risk language.
12. Event charts use directional/explanatory language.
13. No chart claims production forecasting.
14. No chart claims competitor pricing caused sales.
15. Month 2, Month 3, and reset refresh tests have been performed.

## 17. Executive Demo Flow

Use this flow:

1. Start on `01_Executive_Outlet_Health`.
2. Explain that all three outlets are being compared on the same model.
3. Show outlet sales ranking and daily trend.
4. Drill into one selected outlet, preferably `OUT001` first.
5. Open `02_Sales_Menu_Intelligence`.
6. Show top category and top menu item.
7. Open `03_Vendor_Procurement_Analytics`.
8. Show vendor share and pending/partial PO table.
9. Open `04_Inventory_Consumption_Intelligence`.
10. Show low-stock/pressure table and theoretical consumption.
11. Open `05_Calendar_Event_Competitor_Intelligence`.
12. Show event lift and competitor price positioning.
13. Load Month 2 or Month 3.
14. Refresh Zoho feeds.
15. Show that the same dashboard updates without changing the model.

## 18. Caveats To Keep Ready

Use these caveats if asked:

- The dataset is synthetic.
- Neon simulates a POSIST-like backend.
- FastAPI feed import is the intended architecture.
- Direct Neon-to-Zoho is only a fallback/test path.
- Sales rows are daily outlet-item aggregates, not individual bills.
- Vendor spend is demo spend share, not audited accounts payable.
- PO-to-receipt matching is approximate because entry rows do not carry PO number.
- Theoretical consumption is recipe math, not actual variance.
- Inventory pressure is heuristic, not final stockout prediction.
- Event lift is directional, not causal proof.
- Competitor pricing is market context, not causal attribution.

## 19. Recommended Final Page Order In Zoho

Use this order in the dashboard folder:

```text
01_Executive_Outlet_Health
02_Sales_Menu_Intelligence
03_Vendor_Procurement_Analytics
04_Inventory_Consumption_Intelligence
05_Calendar_Event_Competitor_Intelligence
```

If duplicating by outlet:

```text
01_Executive_Outlet_Health
02_Sales_Menu_OUT001
02_Sales_Menu_OUT002
02_Sales_Menu_OUT003
03_Procurement_OUT001
03_Procurement_OUT002
03_Procurement_OUT003
04_Inventory_OUT001
04_Inventory_OUT002
04_Inventory_OUT003
05_Calendar_Competitor_OUT001
05_Calendar_Competitor_OUT002
05_Calendar_Competitor_OUT003
```

## 20. One-Line Corporate Summary

Use this line when introducing the dashboard:

```text
This Zoho workspace converts ABNAH-style operational reports into an outlet-aware executive and operations dashboard suite, connecting sales, menu performance, procurement, inventory pressure, event lift, and competitor pricing context through one refreshable FastAPI feed model.
```

## 21. Exact Zoho Dashboard Build Procedure

Use this section while actually building inside Zoho Analytics.

The earlier sections explain what the dashboard should communicate. This section explains exactly what to click, which source table to select, which fields to use, which aggregate to apply, how to save each chart, and how to place the chart on the final dashboard.

### 21.1 Recommended Build Order

Build in this order:

1. Confirm all RAW tables refresh successfully.
2. Confirm all 37 Query Tables exist.
3. Confirm lookup relationships are completed.
4. Create a folder named `ABNAH Dashboard Source Views`.
5. Create all chart views and pivot/table views listed below.
6. Create the five dashboards.
7. Add the saved chart views to the dashboards.
8. Add dashboard-level filters.
9. Test each dashboard using `OUT001`, `OUT002`, and `OUT003`.
10. Run the Month 2 / Month 3 refresh test.

Do not build charts directly from RAW tables. Use `FACT_*` and `SUM_*` tables unless this document explicitly says otherwise.

### 21.2 Standard Zoho Report Creation Steps

For every chart in this section, use this base workflow:

1. Go to the Zoho workspace.
2. Open `Explorer`.
3. Click `+ New`.
4. Choose `Chart View`.
5. Select the source Query Table listed in the chart table below.
6. Choose the chart type listed in the chart table below.
7. Drag the listed field into `X-axis`.
8. Drag the listed measure into `Y-axis`.
9. Set the aggregation listed in the chart table, usually `SUM`, `AVG`, `COUNT`, or `COUNT DISTINCT`.
10. Drag the listed field into `Color`, `Series`, or `Legend` if provided.
11. Add the listed report filters.
12. Set the listed sort order.
13. Rename the report exactly as shown in the `Save as` column.
14. Save it inside `ABNAH Dashboard Source Views`.

If Zoho shows different shelf names, use the closest equivalent:

| This guide says | Zoho may call it |
|---|---|
| `X-axis` | Columns, X Axis, Dimension |
| `Y-axis` | Rows, Y Axis, Measure |
| `Series/color` | Color, Legend, Break By, Group By |
| `Filter` | Filters, User Filters, Criteria |
| `Sort` | Sort By, Ranking, Top/Bottom |

### 21.3 Exact KPI Label Widget Creation Steps

Zoho calls KPI cards `KPI Widgets`. For our dashboard, use the simple single-number version, usually shown as `Label Widget` or `Single Label Widget`.

There are two different things inside one KPI widget:

| Part | What it means | Example |
|---|---|---|
| KPI value | The number calculated from the data column | `1,245,000` |
| KPI label | The text displayed on the widget | `Net Sales Revenue` |

Do not make a separate chart just for the KPI label. The label is typed inside the KPI widget settings.

#### 21.3.1 One Worked Example: `Net Sales Revenue`

Use this exact example first. After this works, repeat the same pattern for the other KPI cards.

Goal:

```text
Show one KPI card labelled Net Sales Revenue.
The number should be SUM(net_sales) from FACT_Outlet_Daily_Health.
This is the executive revenue card, not a quantity/volume card.
```

Steps:

1. Open dashboard `01_Executive_Outlet_Health`.
2. Click `Edit Design` or the pencil/edit button.
3. Click `Widget` from the dashboard toolbar.
4. Choose `KPI Widget`.
5. Choose `Label Widget`.
6. Choose `Single Label` / `Single Number`.
7. In the widget editor, go to the `Data` tab.
8. For `Table`, choose `FACT_Outlet_Daily_Health`.
9. For `Data Column`, choose `net_sales`.
10. For calculation / show value as, choose `SUM`.
11. Leave `Group By` empty.
12. Add dashboard filters if available:

```text
activity_date = dashboard date range
outlet_name = selected outlet only if you want an outlet-specific executive view
```

13. Go to the `Settings` tab.
14. Open `Values`, `Label`, or `Primary Value`, depending on the Zoho screen.
15. In the label text box, type exactly:

```text
Net Sales Revenue
```

16. Format the value:
    - number type: currency or number,
    - decimal places: 0,
    - thousand separator: on,
    - prefix: `INR` if Zoho allows it.
17. Optional tooltip text:

```text
Total net sales revenue for the selected date range and outlet scope.
```

18. Click `Apply` or `Done`.
19. Drag the widget into the first KPI row.
20. Resize it to match the other KPI cards.
21. Click `Save` on the dashboard.

If the card shows many rows or multiple values, the problem is usually that `Group By` is not empty.

If the card does not change when the dashboard date filter changes, edit the dashboard filter mapping and make sure the filter is connected to `FACT_Outlet_Daily_Health.activity_date`.

#### 21.3.2 KPI Widget Fields Explained

Use this interpretation when Zoho's wording differs:

| Zoho field | What to fill |
|---|---|
| Widget type | `Label Widget` / `Single Label` / `Single Number` |
| Table | The source table from the KPI table below |
| Data Column | The numeric field to calculate |
| Show Value As / Calculation | `SUM`, `AVG`, `COUNT`, or `COUNT DISTINCT` |
| Group By | Usually leave empty for one KPI number |
| Filter / Criteria | Use this to isolate the metric or outlet |
| Label | The exact display text on the card |
| Secondary value | Leave blank for now |
| Indicator | Leave off for now |
| Target | Leave blank for now |
| Tooltip / Widget Info | Optional short explanation |

#### 21.3.3 Executive Dashboard KPI Labels To Type

Use this exact order. Do not start by making all charts.

##### A. Make These Dashboard Filters First

Create only these filters first. Add more later.

Filter 1: `Date Range`

1. Open `01_Executive_Outlet_Health`.
2. Click `Edit Design`.
3. Click `Add User Filter`.
4. Choose source table `FACT_Outlet_Daily_Health`.
5. Choose column `activity_date`.
6. Filter display type: `Date Range`.
7. Filter label to type:

```text
Date Range
```

8. Default: full available date range.
9. Apply this filter to every KPI/chart built from `FACT_Outlet_Daily_Health`.

Filter 2: `Outlet`

1. Click `Add User Filter`.
2. Choose source table `FACT_Outlet_Daily_Health`.
3. Choose column `outlet_name`.
4. Filter display type: dropdown.
5. Selection type: multi-select or single-select.
6. Filter label to type:

```text
Outlet
```

7. Default: `All`.
8. Apply this filter to every KPI/chart that has `outlet_name`.

Filter 3: `Event Type`

1. Click `Add User Filter`.
2. Choose source table `SUM_Event_Impact`.
3. Choose column `event_type`.
4. Filter display type: dropdown.
5. Filter label to type:

```text
Event Type
```

6. Default: `All`.
7. Apply this only to event charts and the `Event-Linked Sales Lift %` KPI.

Important filter mapping:

- For KPIs/charts from `FACT_Outlet_Daily_Health`, map `Date Range` to `activity_date`.
- For KPIs/charts from `FACT_Outlet_Daily_Health`, map `Outlet` to `outlet_name`.
- For `Event-Linked Sales Lift %`, map `Outlet` to `SUM_Event_Impact.outlet_name`.
- For `Event-Linked Sales Lift %`, map `Event Type` to `SUM_Event_Impact.event_type`.
- If Zoho asks for a date field for `SUM_Event_Impact`, use `start_date`. If that is awkward, leave the event-lift KPI controlled by outlet and event type only for the first build.

Do not use `SUM_Executive_KPIs` for these executive KPI cards. It is not as clear for dashboard filtering.

##### B. Verify Lookup Connections

You said lookups are done, but check these if a dashboard filter does not apply.

Connection 1:

```text
FACT_Outlet_Daily_Health.outlet_code
-> DIM_Outlet.outlet_code
```

Connection 2:

```text
FACT_Outlet_Daily_Health.activity_date
-> DIM_Date.date_value
```

Connection 3:

```text
SUM_Event_Impact.outlet_code
-> DIM_Outlet.outlet_code
```

How to verify a lookup in Zoho:

1. Open the source table.
2. Click `Edit Design`.
3. Click the source column, for example `outlet_code`.
4. Confirm the column is a lookup to the target table.
5. If not, change the column type to `Lookup Column`.
6. Select the target table and target column listed above.
7. Save.

If Zoho does not allow lookup on that table, use direct filter mapping from the source table column instead.

##### C. Create These Aggregate Formulas

Open table `FACT_Outlet_Daily_Health`.

Create formula 1:

```text
Formula name:
AF_Average_Daily_Revenue

Formula:
SUM("net_sales") / DISTINCTCOUNT("activity_date")

Format:
Currency / INR
```

Create formula 2:

```text
Formula name:
AF_Purchase_To_Sales_Ratio

Formula:
SUM("po_value") / SUM("net_sales") * 100

Format:
Percentage
```

Create formula 3:

```text
Formula name:
AF_Revenue_Per_Inventory_Rupee

Formula:
SUM("net_sales") / AVG("inventory_value")

Format:
Decimal number
```

If Zoho does not accept `DISTINCTCOUNT`, use Zoho's formula helper and select `Distinct Count` for `activity_date`.

##### D. Build KPI 1: Net Sales Revenue

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Data column: `net_sales`.
5. Calculation: `SUM`.
6. Group By: blank.
7. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
8. Label text:

```text
Net Sales Revenue
```

9. Format: Currency / INR.

##### E. Build KPI 2: Average Daily Revenue

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Value: `AF_Average_Daily_Revenue`.
5. Group By: blank.
6. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Label text:

```text
Average Daily Revenue
```

8. Format: Currency / INR.

##### F. Build KPI 3: Procurement Spend

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Data column: `po_value`.
5. Calculation: `SUM`.
6. Group By: blank.
7. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
8. Label text:

```text
Procurement Spend
```

9. Format: Currency / INR.

##### G. Build KPI 4: Purchase-To-Sales Ratio

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Value: `AF_Purchase_To_Sales_Ratio`.
5. Group By: blank.
6. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Label text:

```text
Purchase-To-Sales Ratio
```

8. Format: Percentage.

##### H. Build KPI 5: Revenue Per Inventory Rupee

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Value: `AF_Revenue_Per_Inventory_Rupee`.
5. Group By: blank.
6. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Label text:

```text
Revenue Per Inventory Rupee
```

8. Format: decimal number.

##### I. Build KPI 6: Inventory Pressure Item-Days

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Data column: `low_stock_item_count`.
5. Calculation: `SUM`.
6. Group By: blank.
7. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
8. Label text:

```text
Inventory Pressure Item-Days
```

9. Format: number.

##### J. Build KPI 7: Event-Linked Sales Lift %

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `SUM_Event_Impact`.
4. Data column: `sales_lift_pct`.
5. Calculation: `AVG`.
6. Group By: blank.
7. Apply filters:
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
   - optional date filter -> `start_date`
8. Label text:

```text
Event-Linked Sales Lift %
```

9. Format: percentage.

##### K. Build Card 8: Best Performing Outlet

This is a small table, not a KPI widget.

1. Click `+ New`.
2. Choose `Table View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Add column: `outlet_name`.
5. Add measure: `net_sales`.
6. Aggregation for `net_sales`: `SUM`.
7. Sort: `SUM(net_sales)` descending.
8. If Zoho supports row limit, set Top 1.
9. Save as:

```text
CARD_Best_Performing_Outlet
```

10. Add it to dashboard row 3.
11. Apply filters:
    - `Date Range` -> `activity_date`
    - optional `Outlet` -> `outlet_name`

##### Profit KPI Reality Check

Do not label anything as true profit yet.

The current model has revenue, purchase orders, receipts, inventory value, recipe BOM, and theoretical ingredient consumption. It does not have labour, rent, wastage, delivery commissions, overhead allocation, or audited actual COGS.

Use these immediately:

| Profit-style proxy | Source | Why it is allowed |
|---|---|---|
| `Purchase-To-Sales Ratio` | `FACT_Outlet_Daily_Health` | Spend pressure compared with sales |
| `Revenue Per Inventory Rupee` | `AF_Revenue_Per_Inventory_Rupee` | Inventory productivity proxy |

Only build `Estimated Gross Profit` later after adding an extra cost-estimation Query Table that connects:

```text
FACT_Theoretical_Consumption.ingredient_name
-> FACT_Inventory_Closing.item_name
-> latest average_price
```

Then the estimate would be:

```text
Estimated Ingredient Cost = theoretical_ingredient_qty * latest average_price
Estimated Gross Profit = net_sale - Estimated Ingredient Cost
Estimated Gross Margin % = Estimated Gross Profit / net_sale * 100
```

Call this `Estimated Gross Profit`, not `Profit`, because it is recipe-cost based and not audited profit.

#### 21.3.4 Sales Dashboard KPI Labels To Type

Create these KPI widgets on `02_Sales_Menu_Intelligence`.

For all widgets, add dashboard/user filter or widget criteria for the selected outlet:

```text
outlet_code = selected outlet
```

| KPI label to type | Source table | Data column | Show value as | Group by | Suggested format |
|---|---|---|---|---|---|
| `Net Sales` | `FACT_Sales` | `net_sale` | `SUM` | blank | Currency / INR |
| `Menu Units Sold` | `FACT_Sales` | `qty` | `SUM` | blank | Number |
| `Average Realized Unit Price` | `FACT_Sales` | `net_sale_per_qty` | `AVG` | blank | Currency / INR |
| `Active Menu Items` | `FACT_Sales` | `item_number` | `COUNT DISTINCT` | blank | Number |

For `Highest Sales Item`, do not use a normal single-number KPI unless Zoho supports top-dimension labels cleanly. Use this easier method:

1. Create a table view from `SUM_Menu_Item_Performance`.
2. Add columns:
   - `item_name`
   - `total_net_sale`
3. Filter to selected outlet.
4. Sort `total_net_sale` descending.
5. Keep only Top 1 if Zoho offers row limit.
6. Title the table:

```text
Highest Sales Item
```

7. Place it beside the KPI cards as a compact single-row table.

#### 21.3.5 Procurement Dashboard KPI Labels To Type

Create these KPI widgets on `03_Vendor_Procurement_Analytics`.

Add selected outlet and procurement date filters to every widget. Add vendor/material filters to the two value cards. Do not add the vendor filter to `Active Vendors In Selected Outlet` if that card should keep showing the available supplier base.

| KPI label to type | Source table | Data column | Show value as | Group by | Suggested format |
|---|---|---|---|---|---|
| `PO Raised Value` | `FACT_Vendor_Spend` | `ordered_value` | `SUM` | blank | Currency / INR |
| `Receipt Booked Value` | `FACT_Vendor_Spend` | `received_value` | `SUM` | blank | Currency / INR |
| `PO vs Receipt Value Gap` | `FACT_Vendor_Spend` | aggregate formula `SUM(ordered_value) - SUM(received_value)` | formula value | blank | Currency / INR |
| `Open / Partial PO Status Count` | `FACT_Vendor_Spend` | `open_or_partial_po_count` | `SUM` | blank | Number |
| `Active Vendors In Selected Outlet` | `FACT_Vendor_Spend` | `vendor_name` | `COUNT DISTINCT` | blank | Number |
| `Pending / Partial Lines` | `FACT_PO_Receipt_Comparison` | `pending_or_partial_flag` | `SUM` | blank | Number |

#### 21.3.6 Inventory Dashboard KPI Labels To Type

Create these KPI widgets on `04_Inventory_Consumption_Intelligence`.

Add selected outlet filter to every widget.

| KPI label to type | Source table | Data column | Show value as | Group by | Suggested format |
|---|---|---|---|---|---|
| `Inventory Value` | `SUM_Inventory_Risk` | `total_amt` | `SUM` | blank | Currency / INR |
| `Low Stock Item Count` | `SUM_Inventory_Risk` | `low_stock_flag` | `SUM` | blank | Number |
| `Closing Inventory Quantity` | `SUM_Inventory_Risk` | `total_qty` | `SUM` | blank | Number |
| `Theoretical Ingredient Demand` | `FACT_Theoretical_Consumption` | `theoretical_ingredient_qty` | `SUM` | blank | Number |
| `Event Days With Pressure` | `FACT_Outlet_Daily_Health` | `event_count` | `SUM` | blank | Number |

For `Event Days With Pressure`, add this extra filter:

```text
low_stock_item_count > 0
```

#### 21.3.7 Event And Competitor Dashboard KPI Labels To Type

Create these KPI widgets on `05_Calendar_Event_Competitor_Intelligence`.

Add selected outlet or selected market-area filter as appropriate.

| KPI label to type | Source table | Data column | Show value as | Group by | Suggested format |
|---|---|---|---|---|---|
| `Event Day Sales` | `SUM_Event_Impact` | `event_day_sales` | `SUM` | blank | Currency / INR |
| `Baseline Sales` | `SUM_Event_Impact` | `baseline_sales` | `AVG` | blank | Currency / INR |
| `Average Event Lift %` | `SUM_Event_Impact` | `sales_lift_pct` | `AVG` | blank | Percentage |
| `Manual Event Count` | `DIM_Event` | `event_id` | `COUNT DISTINCT` | blank | Number |
| `Premium Context Sales` | `SUM_Competitor_Positioning` | `premium_context_sales_lines` | `SUM` | blank | Number |

#### 21.3.8 KPI Label Troubleshooting

| What you see | Likely issue | Fix |
|---|---|---|
| The card says the column name instead of the business label | Label text was not changed | Edit widget, go to `Settings`, change `Label` / `Primary Value Label` |
| Executive KPI does not change with date filter | Dashboard filter is not connected to the KPI source table | Map the date filter to `FACT_Outlet_Daily_Health.activity_date` or use direct widget criteria |
| The KPI shows a list instead of one number | `Group By` was filled | Remove `Group By` |
| The KPI is blank | Wrong table, wrong data column, formula error, or filter mismatch | Re-check table, column, formula, and filter mapping |
| Currency does not show INR label | Number format not set | In Settings, set value format or prefix to `INR` |
| Outlet-specific KPI is too high | It is combining all outlets | Add dashboard filter or widget criteria for `outlet_code` |

If Zoho does not offer KPI widgets in your plan/screen, fallback:

1. Create a `Summary View`.
2. Select the same source table and measure.
3. Add the same filter criteria.
4. Save the view using the KPI label as the report name.
5. Add that summary view to the dashboard.

### 21.4 Dashboard-Level Filter Setup

Create these filters after the charts are added to a dashboard.

Use `Add User Filter` in dashboard edit mode.

| Filter name | Preferred field | Filter type | Default | Apply to |
|---|---|---|---|---|
| Month | `month_key` from `DIM_Date` if available through lookup | Dropdown / multi-select | Current loaded month | All charts that support date lookup |
| Date Range | Chart source date field | Date range | Full available range | All time-based charts |
| Outlet | `outlet_name` or `outlet_code` | Dropdown / single-select | Required on Dashboards 2-5 | All outlet-specific charts |
| Category | `category` | Dropdown / multi-select | All | Sales, menu, event, competitor |
| Vendor | `vendor_name` | Dropdown / multi-select | All | Procurement |
| Ingredient | `ingredient_name` or `item_name` | Dropdown / search | All | Inventory and consumption |
| Event Type | `event_type` | Dropdown / multi-select | All | Event charts |
| Competitor | `competitor_name` | Dropdown / multi-select | All | Competitor charts |
| Market Area | `market_area` or `outlet_market_area` | Dropdown / single-select | Match selected outlet | Competitor charts |

Important:

- If a lookup filter does not apply to a chart, add the same filter directly on the chart source table.
- For Dashboards 2-5, do not leave `Outlet` as optional during the final demo.
- If dashboard filters cannot be locked, duplicate outlet dashboards and add fixed chart filters:
  - `outlet_code = OUT001`
  - `outlet_code = OUT002`
  - `outlet_code = OUT003`

### 21.5 Dashboard 1 Build: `01_Executive_Outlet_Health`

Create the dashboard:

1. Click `+ New`.
2. Choose `Dashboard`.
3. Name it `01_Executive_Outlet_Health`.
4. Add a top text widget:

```text
Executive Outlet Health
Cross-outlet view of sales, procurement, receipts, inventory pressure, and event exposure.
```

5. Add only these filters first:
   - `Date Range`: source `FACT_Outlet_Daily_Health.activity_date`
   - `Outlet`: source `FACT_Outlet_Daily_Health.outlet_name`
   - `Event Type`: source `SUM_Event_Impact.event_type`

Do not add a `Month` filter until the Date Range filter is working. Month filters are optional and depend on the date lookup to `DIM_Date`.

#### 21.5.1 KPI Cards

Build these cards using the exact steps in section `21.3.3`.

Primary KPI row:

1. `Net Sales Revenue`
2. `Average Daily Revenue`
3. `Procurement Spend`
4. `Purchase-To-Sales Ratio`

Secondary KPI row:

1. `Revenue Per Inventory Rupee`
2. `Inventory Pressure Item-Days`
3. `Event-Linked Sales Lift %`
4. `CARD_Best_Performing_Outlet`

Do not create `Total Quantity Sold` on this page.

#### 21.5.2 Executive Chart Views

Create and save these chart views before adding them to the dashboard.

Use `FACT_Outlet_Daily_Health` for the main executive charts so the `Date Range` and `Outlet` filters work cleanly.

Build chart `CH01_Outlet_Sales_Ranking`:

1. Create `Chart View`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Chart type: horizontal bar.
4. X-axis: `outlet_name`.
5. Y-axis: `net_sales`.
6. Aggregation: `SUM`.
7. Sort: `SUM(net_sales)` descending.
8. Filters to apply:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
9. Save as:

```text
CH01_Outlet_Sales_Ranking
```

Build chart `CH02_Daily_Sales_Trend_By_Outlet`:

1. Create `Chart View`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Chart type: line chart.
4. X-axis: `activity_date`.
5. Y-axis: `net_sales`.
6. Aggregation: `SUM`.
7. Color/series: `outlet_name`.
8. Sort: `activity_date` ascending.
9. Filters to apply:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
10. Save as:

```text
CH02_Daily_Sales_Trend_By_Outlet
```

Build chart `CH03_Sales_Purchase_Receipt_Comparison`:

1. Create `Chart View`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Chart type: clustered bar.
4. X-axis: `outlet_name`.
5. Y-axis measure 1: `net_sales`, aggregation `SUM`.
6. Y-axis measure 2: `po_value`, aggregation `SUM`.
7. Y-axis measure 3: `receipt_value`, aggregation `SUM`.
8. Series/color: measure name, if Zoho asks.
9. Filters to apply:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
10. Save as:

```text
CH03_Sales_Purchase_Receipt_Comparison
```

Build chart `CH04_Inventory_Pressure_By_Outlet`:

1. Create `Chart View`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Chart type: bar.
4. X-axis: `outlet_name`.
5. Y-axis: `low_stock_item_count`.
6. Aggregation: `SUM`.
7. Color/series: `health_note`.
8. Sort: `SUM(low_stock_item_count)` descending.
9. Filters to apply:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
10. Save as:

```text
CH04_Inventory_Pressure_By_Outlet
```

Build chart `CH05_Event_Exposure_By_Outlet`:

1. Create `Chart View`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Chart type: bar.
4. X-axis: `outlet_name`.
5. Y-axis: `event_count`.
6. Aggregation: `SUM`.
7. Sort: `SUM(event_count)` descending.
8. Filters to apply:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
9. Save as:

```text
CH05_Event_Exposure_By_Outlet
```

Build chart `CH06_Outlet_Health_Note_Mix`:

1. Create `Chart View`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Chart type: stacked bar or donut.
4. X-axis/category: `health_note`.
5. Y-axis: `activity_date`.
6. Aggregation: `COUNT`.
7. Color/series: `outlet_name`, if using stacked bar.
8. Filters to apply:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
9. Save as:

```text
CH06_Outlet_Health_Note_Mix
```

Build table `TB01_Outlet_Health_Detail`:

1. Create `Table View`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Row/detail columns:
   - `activity_date`
   - `outlet_name`
   - `market_area`
   - `health_note`
4. Measure columns:
   - `net_sales`
   - `sold_qty`
   - `po_value`
   - `receipt_value`
   - `inventory_value`
   - `low_stock_item_count`
   - `event_count`
5. Filters to apply:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
6. Sort: `activity_date` ascending, then `outlet_name` ascending.
7. Save as:

```text
TB01_Outlet_Health_Detail
```

Build table `TB02_Spike_Explanation_Panel`:

1. Create `Table View`.
2. Source table: `SUM_Event_Markers`.
3. Row/detail columns:
   - `event_date`
   - `outlet_name`
   - `event_name`
   - `event_type`
   - `affected_category`
   - `affected_items`
   - `confidence_level`
4. Measure columns:
   - `event_day_sales`
   - `baseline_sales`
   - `sales_lift_percentage`
5. Filters to apply:
   - `Date Range` -> `event_date`
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
6. Sort: `event_date` ascending.
7. Save as:

```text
TB02_Spike_Explanation_Panel
```

#### 21.5.3 Dashboard Placement

Arrange the page like this:

| Row | Placement |
|---|---|
| Row 1 | Title text and filters |
| Row 2 | Primary KPI cards: `Net Sales Revenue`, `Average Daily Revenue`, `Procurement Spend`, `Purchase-To-Sales Ratio` |
| Row 3 | Secondary KPI cards: `Revenue Per Inventory Rupee`, `Inventory Pressure Item-Days`, `Event-Linked Sales Lift %`, `Best Performing Outlet` |
| Row 4 left | `CH01_Outlet_Sales_Ranking` |
| Row 4 right | `CH02_Daily_Sales_Trend_By_Outlet` |
| Row 5 left | `CH03_Sales_Purchase_Receipt_Comparison` |
| Row 5 middle | `CH04_Inventory_Pressure_By_Outlet` |
| Row 5 right | `CH05_Event_Exposure_By_Outlet` |
| Row 6 left | `CH06_Outlet_Health_Note_Mix` |
| Row 7 full width | `TB01_Outlet_Health_Detail` |
| Row 8 full width | `TB02_Spike_Explanation_Panel` |

### 21.6 Dashboard 2 Build: `02_Sales_Menu_Intelligence`

Create the dashboard:

1. Click `+ New`.
2. Choose `Dashboard`.
3. Name it `02_Sales_Menu_Intelligence`.
4. Add a top text widget:

```text
Sales And Menu Intelligence
Menu performance, category contribution, realized pricing, and event-sensitive items.
```

5. Add filters:
   - `Outlet` using `outlet_code` or `outlet_name`
   - `Date Range` using `sales_date`
   - `Category`
   - `Super Category`
   - `Menu Item`
   - `Event Type`

For the demo, set `Outlet` to one outlet at a time. Start with `OUT001`.

#### 21.6.1 KPI Cards

| KPI title | Source table | Measure | Aggregation | Criteria |
|---|---|---|---|---|
| Net Sales | `FACT_Sales` | `net_sale` | `SUM` | selected outlet |
| Menu Units Sold | `FACT_Sales` | `qty` | `SUM` | selected outlet |
| Average Realized Unit Price | `FACT_Sales` | `net_sale_per_qty` | `AVG` | selected outlet |
| Active Menu Items | `FACT_Sales` | `item_number` | `COUNT DISTINCT` | selected outlet |
| Highest Sales Item | `SUM_Menu_Item_Performance` | `total_net_sale` | top value by `item_name` | selected outlet |

For `Highest Sales Item`, if Zoho cannot display the top dimension in a KPI card, create a compact table sorted by `total_net_sale` descending and show only the first row.

#### 21.6.2 Sales And Menu Chart Views

| Save as | Source table | Chart type | X-axis | Y-axis | Aggregation | Series/color | Filter | Sort |
|---|---|---|---|---|---|---|---|---|
| `CH07_Daily_Net_Sales_Trend` | `FACT_Sales` | Line | `sales_date` | `net_sale` | `SUM` | optional `category` | selected outlet, date range | `sales_date` ascending |
| `CH08_Category_Revenue_Mix` | `FACT_Sales` | Horizontal bar | `category` | `net_sale` | `SUM` | `super_category` | selected outlet, date range, category | `SUM(net_sale)` descending |
| `CH09_Super_Category_Share` | `FACT_Sales` | 100% stacked bar or donut | `super_category` | `net_sale` | `SUM` | none | selected outlet, date range | `SUM(net_sale)` descending |
| `CH10_Top_Items_By_Net_Sales` | `SUM_Menu_Item_Performance` | Horizontal bar | `item_name` | `total_net_sale` | `SUM` | `category` | selected outlet, top 10 or top 15 | `total_net_sale` descending |
| `CH11_Top_Items_By_Quantity` | `SUM_Menu_Item_Performance` | Horizontal bar | `item_name` | `total_qty` | `SUM` | `category` | selected outlet, top 10 or top 15 | `total_qty` descending |
| `CH12_Realized_Unit_Price_By_Item` | `SUM_Menu_Item_Performance` | Bar or dot plot | `item_name` | `avg_realized_unit_price` | `AVG` | `category` | selected outlet, selected category | `avg_realized_unit_price` descending |
| `CH13_Premium_Item_Performance` | `SUM_Menu_Item_Performance` | Scatter | `avg_price_index` | `total_net_sale` | X as `AVG`, Y as `SUM` | `price_position`; size by `total_qty` | selected outlet | `total_net_sale` descending if ranking is offered |
| `TB03_Menu_Item_Detail` | `SUM_Menu_Item_Performance` | Table | rows: `item_number`, `item_name`, `super_category`, `category`, `performance_note` | `total_qty`, `total_net_sale`, `avg_realized_unit_price`, `avg_price_index` | as imported / `SUM` where needed | none | selected outlet | `total_net_sale` descending |
| `TB04_Event_Item_Lift` | `SUM_Event_Impact` | Table | rows: `event_name`, `event_type`, `item_name`, `category`, `confidence_level` | `event_day_sales`, `baseline_sales`, `sales_lift_value`, `sales_lift_pct` | as imported / `SUM` where needed | none | selected outlet | `sales_lift_pct` descending |

#### 21.6.3 Dashboard Placement

| Row | Placement |
|---|---|
| Row 1 | Title text and filters |
| Row 2 | Five KPI cards |
| Row 3 full width | `CH07_Daily_Net_Sales_Trend` |
| Row 4 left | `CH08_Category_Revenue_Mix` |
| Row 4 right | `CH09_Super_Category_Share` |
| Row 5 left | `CH10_Top_Items_By_Net_Sales` |
| Row 5 right | `CH11_Top_Items_By_Quantity` |
| Row 6 left | `CH12_Realized_Unit_Price_By_Item` |
| Row 6 right | `CH13_Premium_Item_Performance` |
| Row 7 full width | `TB03_Menu_Item_Detail` |
| Row 8 full width | `TB04_Event_Item_Lift` |

### 21.7 Dashboard 3 Build: `03_Vendor_Procurement_Analytics`

Create the dashboard:

1. Click `+ New`.
2. Choose `Dashboard`.
3. Name it `03_Vendor_Procurement_Analytics`.
4. Add a top text widget:

```text
Vendor And Procurement Analytics
Vendor share, PO status, receipt value, and pending or partial purchase follow-up.
```

5. Add filters:
   - `Outlet` from `FACT_Vendor_Spend.outlet_name`
   - `Procurement Date Range` from `FACT_Vendor_Spend.activity_date`
   - `Vendor` from `FACT_Vendor_Spend.vendor_name`
   - `Ingredient / Material` from `FACT_Vendor_Spend.item_name`
   - `PO Status` from `FACT_Vendor_Spend.po_status`
   - `Category` from `FACT_Vendor_Spend.category_name`

Set `Outlet`, `Vendor`, `Ingredient / Material`, and `Category` to `List only relevant values` so the dropdown choices cascade.

#### 21.7.1 KPI Cards

| KPI title | Source table | Measure | Aggregation | Criteria |
|---|---|---|---|---|
| PO Raised Value | `FACT_Vendor_Spend` | `ordered_value` | `SUM` | selected outlet, date, vendor, material |
| Receipt Booked Value | `FACT_Vendor_Spend` | `received_value` | `SUM` | selected outlet, date, vendor, material |
| PO vs Receipt Value Gap | `FACT_Vendor_Spend` | `ordered_value - received_value` aggregate formula | formula value | selected outlet, date, vendor, material; do not map PO status |
| Open / Partial PO Status Count | `FACT_Vendor_Spend` | `open_or_partial_po_count` | `SUM` | selected outlet, date, vendor, material, PO status |
| Active Vendors In Selected Outlet | `FACT_Vendor_Spend` | `vendor_name` | `COUNT DISTINCT` | selected outlet/date/material; exclude vendor filter if you want the supplier-base count |
| Pending / Partial Lines | `FACT_PO_Receipt_Comparison` | `pending_or_partial_flag` | `SUM` | selected outlet |

#### 21.7.2 Procurement Chart Views

| Save as | Source table | Chart type | X-axis | Y-axis | Aggregation | Series/color | Filter | Sort |
|---|---|---|---|---|---|---|---|---|
| `CH14_Vendor_PO_Raised_Share` | `FACT_Vendor_Spend` | Horizontal bar | `vendor_name` | `ordered_value` | `SUM` | optional `market_area` | selected outlet, date, vendor/material optional | `SUM(ordered_value)` descending |
| `CH15_Vendor_Receipt_Booked_Share` | `FACT_Vendor_Spend` | Horizontal bar | `vendor_name` | `received_value` | `SUM` | optional `market_area` | selected outlet, date, vendor/material optional | `SUM(received_value)` descending |
| `CH16_Vendor_Share_Percent` | `FACT_Vendor_Spend` | Bar | `vendor_name` | `ordered_value` | `SUM`, show percent of total if available | none | selected outlet, date | `SUM(ordered_value)` descending |
| `CH17_Vendor_Spend_Trend` | `FACT_Vendor_Spend` | Multi-line or combo | `activity_date` | `ordered_value`, `received_value` | `SUM` for both | measure name or `vendor_name` | selected outlet, vendor optional | `activity_date` ascending |
| `CH18_PO_Status_Value` | `FACT_Purchase_Order` | Stacked bar | `po_status` | `total_item_cost` | `SUM` | `vendor_name` or `category_name` | selected outlet | `total_item_cost` descending |
| `CH19_PO_Status_Count` | `FACT_Purchase_Order` | Bar | `po_status` | `po_number` | `COUNT DISTINCT` | none | selected outlet | count descending |
| `CH20_Processed_vs_Remaining_Value` | `FACT_Purchase_Order` | Clustered bar | `vendor_name` | `processed_value_est`, `remaining_value_est` | `SUM` for both | measure name | selected outlet | `remaining_value_est` descending |
| `TB05_Pending_Partial_PO_Detail` | `FACT_PO_Receipt_Comparison` | Table | rows: `po_number`, `vendor_name`, `item_name`, `po_status`, `po_date`, `expected_delivery_date` | `ordered_qty`, `processed_qty`, `matched_received_qty`, `unmatched_order_qty`, `remaining_qty`, `total_item_cost` | as imported / `SUM` where needed | none | selected outlet, `pending_or_partial_flag = 1` | `expected_delivery_date` ascending |
| `PV01_Vendor_Material_Matrix` | `FACT_Purchase_Order` | Pivot | rows: `vendor_name`; columns: `item_name` or `category_name` | `total_item_cost` | `SUM` | none | selected outlet | `total_item_cost` descending |
| `TB06_Receipt_Detail` | `FACT_Entry_Receipt` | Table | rows: `receipt_date`, `vendor_name`, `transaction_number`, `invoice_number`, `item_name` | `received_qty`, `grand_total`, `realized_receipt_unit_cost` | as imported / `SUM` where needed | none | selected outlet | `receipt_date` descending |

#### 21.7.3 Dashboard Placement

| Row | Placement |
|---|---|
| Row 1 | Title text and filters |
| Row 2 | Five KPI cards |
| Row 3 left | `CH14_Vendor_Ordered_Share` |
| Row 3 right | `CH15_Vendor_Received_Share` |
| Row 4 left | `CH16_Vendor_Share_Percent` |
| Row 4 right | `CH17_Vendor_Spend_Trend` |
| Row 5 left | `CH18_PO_Status_Value` |
| Row 5 middle | `CH19_PO_Status_Count` |
| Row 5 right | `CH20_Processed_vs_Remaining_Value` |
| Row 6 full width | `TB05_Pending_Partial_PO_Detail` |
| Row 7 full width | `PV01_Vendor_Material_Matrix` |
| Row 8 full width | `TB06_Receipt_Detail` |

### 21.8 Dashboard 4 Build: `04_Inventory_Consumption_Intelligence`

Create the dashboard:

1. Click `+ New`.
2. Choose `Dashboard`.
3. Name it `04_Inventory_Consumption_Intelligence`.
4. Add a top text widget:

```text
Inventory And Consumption Intelligence
Inventory pressure, stock value, and recipe-based material demand.
```

5. Add filters:
   - `Outlet`
   - `Inventory Date`
   - `Sales Date`
   - `Ingredient / Material`
   - `Inventory Category`
   - `Pressure Band`

#### 21.8.1 KPI Cards

| KPI title | Source table | Measure | Aggregation | Criteria |
|---|---|---|---|---|
| Inventory Value | `SUM_Inventory_Risk` | `total_amt` | `SUM` | selected outlet |
| Low Stock Item Count | `SUM_Inventory_Risk` | `low_stock_flag` | `SUM` | selected outlet |
| Closing Inventory Quantity | `SUM_Inventory_Risk` | `total_qty` | `SUM` | selected outlet |
| Theoretical Ingredient Demand | `FACT_Theoretical_Consumption` | `theoretical_ingredient_qty` | `SUM` | selected outlet |
| Event Days With Pressure | `FACT_Outlet_Daily_Health` | `event_count` | `SUM` | selected outlet and `low_stock_item_count > 0` |

#### 21.8.2 Inventory And Consumption Chart Views

| Save as | Source table | Chart type | X-axis | Y-axis | Aggregation | Series/color | Filter | Sort |
|---|---|---|---|---|---|---|---|---|
| `CH21_Inventory_Value_By_Category` | `SUM_Inventory_Risk` | Bar | `category_name` | `total_amt` | `SUM` | `super_category_name` | selected outlet; do not map date range | `total_amt` descending |
| `CH22_Inventory_Pressure_Band` | `SUM_Inventory_Risk` | Donut or stacked bar | `inventory_pressure_band` | `item_code` | `COUNT DISTINCT` | none | selected outlet | Low, Watch, OK |
| `CH23_Top_Inventory_Value_Items` | `SUM_Inventory_Risk` | Horizontal bar | `item_name` | `total_amt` | `SUM` | `category_name` | selected outlet, top 10 or top 15 | `total_amt` descending |
| `CH24_Low_Stock_Items` | `SUM_Inventory_Risk` | Horizontal bar | `item_name` | `low_stock_flag` | `SUM` | `inventory_pressure_band` | selected outlet, `low_stock_flag = 1` | `total_qty` ascending |
| `CH25_Theoretical_Consumption_Trend` | `FACT_Theoretical_Consumption` | Line | `sales_date` | `theoretical_ingredient_qty` | `SUM` | `ingredient_name` | selected outlet, selected ingredient optional | `sales_date` ascending |
| `CH26_Top_Theoretical_Ingredients` | `FACT_Theoretical_Consumption` | Horizontal bar | `ingredient_name` | `theoretical_ingredient_qty` | `SUM` | `ingredient_unit` | selected outlet, top 10 or top 15 | `theoretical_ingredient_qty` descending |
| `PV02_Menu_Item_To_Ingredient_Demand` | `FACT_Theoretical_Consumption` | Pivot | rows: `menu_item_name`; columns: `ingredient_name` | `theoretical_ingredient_qty` | `SUM` | none | selected outlet | `theoretical_ingredient_qty` descending |
| `TB07_Low_Stock_Detail` | `SUM_Inventory_Risk` | Table | rows: `item_code`, `item_name`, `category_name`, `inventory_pressure_band`, `risk_note` | `total_qty`, `total_amt`, `total_theoretical_qty`, `low_stock_flag` | as imported / `SUM` where needed | none | selected outlet | `low_stock_flag` descending, `total_qty` ascending |
| `TB08_Event_Day_Inventory_Pressure` | `FACT_Outlet_Daily_Health` | Table | rows: `activity_date`, `outlet_name`, `health_note` | `net_sales`, `inventory_value`, `low_stock_item_count`, `event_count` | as imported / `SUM` where needed | none | selected outlet, `low_stock_item_count > 0` | `activity_date` ascending |

#### 21.8.3 Dashboard Placement

| Row | Placement |
|---|---|
| Row 1 | Title text and filters |
| Row 2 | Five KPI cards |
| Row 3 left | `CH21_Inventory_Value_By_Category` |
| Row 3 right | `CH22_Inventory_Pressure_Band` |
| Row 4 left | `CH23_Top_Inventory_Value_Items` |
| Row 4 right | `CH24_Low_Stock_Items` |
| Row 5 left | `CH25_Theoretical_Consumption_Trend` |
| Row 5 right | `CH26_Top_Theoretical_Ingredients` |
| Row 6 full width | `PV02_Menu_Item_To_Ingredient_Demand` |
| Row 7 full width | `TB07_Low_Stock_Detail` |
| Row 8 full width | `TB08_Event_Day_Inventory_Pressure` |

Add a short text note at the bottom:

```text
Inventory pressure is heuristic and based on closing quantity bands. It is not a production stockout forecast.
```

### 21.9 Dashboard 5 Build: `05_Calendar_Event_Competitor_Intelligence`

Create the dashboard:

1. Click `+ New`.
2. Choose `Dashboard`.
3. Name it `05_Calendar_Event_Competitor_Intelligence`.
4. Add a top text widget:

```text
Calendar, Event, And Competitor Intelligence
Event-linked sales movement, holiday context, and competitor price positioning.
```

5. Add filters:
   - `Outlet`
   - `Market Area`
   - `Date Range`
   - `Event Type`
   - `Category`
   - `Price Position`
   - `Competitor`

#### 21.9.1 KPI Cards

| KPI title | Source table | Measure | Aggregation | Criteria |
|---|---|---|---|---|
| Event Day Sales | `SUM_Event_Impact` | `event_day_sales` | `SUM` | selected outlet |
| Baseline Sales | `SUM_Event_Impact` | `baseline_sales` | `AVG` | selected outlet |
| Average Event Lift % | `SUM_Event_Impact` | `sales_lift_pct` | `AVG` | selected outlet |
| Manual Event Count | `DIM_Event` | `event_id` | `COUNT DISTINCT` | date range if available |
| Premium Context Sales | `SUM_Competitor_Positioning` | `premium_context_sales_lines` | `SUM` | selected outlet or market area |

#### 21.9.2 Event And Competitor Chart Views

| Save as | Source table | Chart type | X-axis | Y-axis | Aggregation | Series/color | Filter | Sort |
|---|---|---|---|---|---|---|---|---|
| `CH27_Event_Sales_By_Event` | `SUM_Event_Impact` | Bar | `event_name` | `event_day_sales` | `SUM` | `event_type` | selected outlet | `event_day_sales` descending |
| `CH28_Event_Lift_By_Event` | `SUM_Event_Impact` | Bar | `event_name` | `sales_lift_pct` | `AVG` | `confidence_level` | selected outlet | `sales_lift_pct` descending |
| `CH29_Event_Sales_Trend` | `SUM_Event_Markers` | Line | `event_date` | `event_day_sales` | `SUM` | `event_name` | selected outlet | `event_date` ascending |
| `CH30_Holiday_Sales_Trend` | `FACT_Sales` | Line | `sales_date` | `net_sale` | `SUM` | `holiday_type` or `holiday_name` | selected outlet, holiday fields not null if desired | `sales_date` ascending |
| `CH31_Competitor_Price_Index` | `SUM_Competitor_Positioning` | Bar | `competitor_name` | `avg_price_index` | `AVG` | `competitor_category` | selected market area / selected outlet | `avg_price_index` descending |
| `CH32_ABNAH_vs_Competitor_Difference` | `SUM_Competitor_Positioning` | Bar | `competitor_category` | `avg_price_difference` | `AVG` | `price_position_band` | selected market area / selected outlet | `avg_price_difference` descending |
| `CH33_Price_Position_Sales` | `SUM_Competitor_Positioning` | Stacked bar | `price_position_band` | `mapped_net_sale` | `SUM` | `competitor_category` | selected market area / selected outlet | band order |
| `CH34_Premium_Item_Performance_Competitor` | `FACT_Competitor_Price_Position` | Scatter | `price_index` | `net_sale` | X as `AVG`, Y as `SUM` | `price_position_band`; size by `qty` | selected market area / selected outlet | none |
| `TB09_Spike_Explanation_Panel` | `SUM_Event_Markers` | Table | rows: `event_date`, `outlet_name`, `event_name`, `event_type`, `affected_category`, `affected_items`, `confidence_level` | `event_day_sales`, `baseline_sales`, `sales_lift_percentage` | as imported / `SUM` where needed | none | selected outlet | `event_date` ascending |
| `TB10_Premium_Overperformance_Table` | `FACT_Competitor_Price_Position` | Table | rows: `abnah_item_name`, `competitor_name`, `competitor_category`, `price_position`, `price_position_band` | `price_index`, `price_difference`, `net_sale`, `qty` | `SUM` for sales/qty, `AVG` for price fields | none | selected market area / selected outlet | `net_sale` descending |
| `TB11_Competitor_Positioning_Detail` | `SUM_Competitor_Positioning` | Table | rows: `outlet_name`, `competitor_name`, `competitor_category`, `price_position_band`, `positioning_note` | `avg_price_index`, `avg_price_difference`, `mapped_sales_qty`, `mapped_net_sale`, `premium_context_sales_lines` | as imported / `SUM` where needed | none | selected market area / selected outlet | `mapped_net_sale` descending |

#### 21.9.3 Dashboard Placement

| Row | Placement |
|---|---|
| Row 1 | Title text and filters |
| Row 2 | Five KPI cards |
| Row 3 left | `CH27_Event_Sales_By_Event` |
| Row 3 right | `CH28_Event_Lift_By_Event` |
| Row 4 full width | `CH29_Event_Sales_Trend` |
| Row 5 full width | `CH30_Holiday_Sales_Trend` |
| Row 6 left | `CH31_Competitor_Price_Index` |
| Row 6 right | `CH32_ABNAH_vs_Competitor_Difference` |
| Row 7 left | `CH33_Price_Position_Sales` |
| Row 7 right | `CH34_Premium_Item_Performance_Competitor` |
| Row 8 full width | `TB09_Spike_Explanation_Panel` |
| Row 9 full width | `TB10_Premium_Overperformance_Table` |
| Row 10 full width | `TB11_Competitor_Positioning_Detail` |

Add a short text note at the bottom:

```text
Event lift and competitor positioning are explanatory context. They do not prove causal impact.
```

### 21.10 If You Duplicate Outlet-Specific Dashboards

If Zoho dashboard filter locking is weak, duplicate Dashboards 2-5 per outlet.

For each duplicate:

1. Open the source dashboard.
2. Click `Duplicate` or `Save As`.
3. Rename using the outlet suffix.
4. Open every chart in edit mode.
5. Add a fixed filter:
   - OUT001 pages: `outlet_code = OUT001`
   - OUT002 pages: `outlet_code = OUT002`
   - OUT003 pages: `outlet_code = OUT003`
6. Save each chart.
7. Test that no chart combines all outlets accidentally.

Use these names:

| Outlet | Sales page | Procurement page | Inventory page | Calendar/competitor page |
|---|---|---|---|---|
| OUT001 | `02_Sales_Menu_OUT001` | `03_Procurement_OUT001` | `04_Inventory_OUT001` | `05_Calendar_Competitor_OUT001` |
| OUT002 | `02_Sales_Menu_OUT002` | `03_Procurement_OUT002` | `04_Inventory_OUT002` | `05_Calendar_Competitor_OUT002` |
| OUT003 | `02_Sales_Menu_OUT003` | `03_Procurement_OUT003` | `04_Inventory_OUT003` | `05_Calendar_Competitor_OUT003` |

### 21.11 Final Dashboard Assembly Checklist

For each dashboard:

1. Title is visible at the top.
2. Filters are immediately under the title.
3. KPI cards are in the first visual row.
4. Main trend/ranking chart is above detailed tables.
5. Detailed tables are at the bottom.
6. Outlet-specific pages have a selected or fixed outlet.
7. Long item/vendor labels use horizontal bars or tables.
8. Currency and quantity fields are formatted consistently.
9. No RAW table is used in a final dashboard visual.
10. No chart mixes all outlets on Dashboards 2-5 unless `outlet_name` is the grouping field.

### 21.12 Month Refresh Test After Dashboard Build

After building the dashboards, test the refresh behavior:

1. Keep Zoho open on `01_Executive_Outlet_Health`.
2. In the local repo, run:

```powershell
python manage_demo.py load-month 2
```

3. In Zoho, refresh all 18 RAW feed tables.
4. Refresh or recompute Query Tables if Zoho does not do it automatically.
5. Check `CH02_Daily_Sales_Trend_By_Outlet`; it should extend with Month 2 dates.
6. Check `CH07_Daily_Net_Sales_Trend`; it should update for the selected outlet.
7. Check KPI cards; sales and quantities should increase from Month 1.
8. Repeat with:

```powershell
python manage_demo.py load-month 3
```

9. Reset if needed:

```powershell
python manage_demo.py reset-to-month 1
```

10. Refresh Zoho again and verify the dashboard returns to Month 1 counts.

### 21.13 Common Zoho Build Mistakes To Avoid

| Mistake | Fix |
|---|---|
| Chart total looks too high | Confirm outlet filter is applied or `outlet_name` is included as a grouping field |
| Chart says invalid column | Check the exact alias in the Query Table; do not use raw report column names |
| Date filter does not affect a chart | Use that chart source table's own date field instead of only `DIM_Date` |
| Competitor chart does not change with outlet | Add `market_area` or `outlet_market_area` filter |
| KPI shows a list instead of one number | Remove `Group By`; KPI cards should use one aggregate value |
| Table is too wide | Keep only operationally relevant columns and move supporting fields to drill-through |
| Event lift looks extreme | Show `confidence_level` and keep the event caveat visible |
| Inventory chart sounds predictive | Rename to inventory pressure, not forecast or stockout prediction |
