# Zoho Zia Training Plan For ABNAH Cafe Intelligence

For the exact click-by-click synonym and Ask Zia setup, start with:

```text
docs/zoho_ask_zia_exact_step_by_step_readme.md
```

That file is written for the current Zoho `Manage Synonyms` screen and explains exactly what to paste into table synonyms, column synonyms, data synonyms, table priority, and default functions.

Use this document after the 18 RAW tables, 37 Query Tables, lookup relationships, and first dashboard views are working.

Goal:

```text
Ask Zia should answer ABNAH business questions in natural language,
use the right curated Query Tables,
understand our cafe/procurement/inventory/event vocabulary,
and generate dashboard insights that explain the business story instead of only restating chart labels.
```

This is not a prompt file. Zoho Zia is trained mainly through metadata: table synonyms, column synonyms, data synonyms, column priority, table priority, default functions, report design, formulas, and Zia Insights settings.

Official Zoho controls used in this plan:

- Ask Zia training: table synonyms, column synonyms, data synonyms, column priority, table priority, default function, and Ask Zia blacklist/exclude behavior.
- Zia Insights: verbosity, Explain by Column, insight categories, and Key Driver Analysis configuration.

Source references are listed at the end.

## 1. Training Strategy

Zia should not be trained on every imported table equally.

If all RAW, STD, DIM, FACT, and SUM tables are visible with equal priority, Ask Zia will sometimes choose the wrong grain. That is the main risk in our workspace.

Our approach:

1. Use curated FACT tables for filter-sensitive answers.
2. Use selected SUM tables only where the business question is explicitly latest/full-period summary.
3. Exclude RAW and STD tables from Ask Zia once the model is validated.
4. Give business synonyms to columns that executives will actually say.
5. Set default functions so Zia sums revenue/spend, averages ratios, counts entities, and does not add already-calculated ratios.
6. Configure Zia Insights chart by chart so it explains the intended story.
7. Validate Zia answers against `docs/month1_truth_tables/dashboard_prediction_pack_month1.csv`.

The guiding rule:

```text
If a question includes date, outlet, category, vendor, material, event, or status filters,
Zia should use a date-safe FACT table, not a month-level SUM table.
```

## 2. Tables To Include Or Exclude From Ask Zia

Open each table in Zoho and use `Edit Design` or column settings to manage Ask Zia settings.

### 2.1 Exclude These Tables

Exclude these from Ask Zia after the dashboards are verified:

| Table group | Action | Reason |
|---|---|---|
| `RAW_*` tables | Exclude / blacklist | Raw feed tables have outlet-split source files and user-unfriendly names. |
| `STD_*` tables | Exclude / low priority | Useful for modeling, not for business answers. |
| `SUM_Executive_KPIs` | Exclude | No date grain; can mislead date-filtered executive questions. |
| `SUM_Sales_Category_Mix` | Exclude or low priority | Month-level; use `FACT_Sales` for date-sensitive category mix. |
| `SUM_Menu_Item_Performance` | Low priority | Useful only for full-month item ranking; can appear static under date filters. |
| `SUM_Vendor_Share` | Exclude or low priority | Use `FACT_Vendor_Spend` for vendor/date/material filters. |
| `DIM_*` tables | Low priority, not excluded | Needed for lookup context, but should not be chosen as metric sources. |

Do not exclude `SUM_Inventory_Risk`; it is useful for latest-stock questions. Train it carefully as a latest snapshot table.

### 2.2 Main Zia Answer Tables

Set these tables as the preferred Zia answer layer.

| Table | Table priority | Table synonyms to add | Use for |
|---|---:|---|---|
| `FACT_Outlet_Daily_Health` | 100 | executive health, outlet health, cafe health, daily performance, outlet scorecard, executive dashboard | Executive KPIs, date-filtered outlet health, revenue run-rate, PO/Sales, inventory pressure item-days |
| `FACT_Sales` | 100 | sales, menu sales, item sales, revenue, menu intelligence, category sales, item performance | Sales trend, category mix, menu item rankings, realized price |
| `FACT_Vendor_Spend` | 100 | procurement, vendor spend, supplier spend, PO and receipts, purchase spend, ordering and receiving | PO raised value, receipt booked value, value gap, vendor/material filters |
| `FACT_Purchase_Order` | 90 | purchase orders, PO status, open PO, partial PO, pending PO | PO status charts, processed vs remaining value |
| `FACT_PO_Receipt_Comparison` | 90 | pending PO detail, PO follow up, receipt comparison, PO receipt matching | PO-level pending/partial detail table |
| `FACT_Inventory_Closing` | 90 | inventory, stock, closing stock, stock value, inventory closing | Date-sensitive inventory value and stock trend |
| `SUM_Inventory_Risk` | 85 | latest inventory, current stock pressure, low stock, inventory risk | Latest low-stock list and current stock pressure |
| `FACT_Theoretical_Consumption` | 85 | recipe consumption, theoretical consumption, ingredient demand, material demand | Recipe BOM x sales ingredient demand |
| `SUM_Event_Impact` | 80 | event lift, event impact, promotion impact, holiday impact | Event lift by event/outlet |
| `SUM_Event_Markers` | 80 | spike explanation, event marker, event day story | Event story tables |
| `SUM_Competitor_Positioning` | 75 | competitor pricing, market pricing, price position, ABNAH vs competitors | Competitor price index and market position |

## 3. Column Synonyms And Default Functions

Set synonyms on the table where Zia should primarily use the column. Do not add every synonym everywhere.

### 3.1 Executive And Outlet Health

Table: `FACT_Outlet_Daily_Health`

| Column | Synonyms to add | Default function | Priority | Business meaning |
|---|---|---|---:|---|
| `net_sales` | revenue, net sales, sales revenue, top line, turnover | Sum | 100 | Sales revenue after source net-sale logic. |
| `activity_date` | date, day, business date, sales date | Date grouping | 100 | Daily time axis. |
| `outlet_name` | outlet, cafe, store, branch, location | Group by / actual | 100 | Cafe identity. |
| `market_area` | market, area, locality, location area | Group by / actual | 80 | Competitor and outlet geography. |
| `sold_qty` | menu units sold, units sold, items sold, customer items | Sum | 65 | Customer-facing menu units, not ingredients. |
| `po_value` | procurement spend, PO value, purchase spend, PO raised, ordered value | Sum | 90 | Purchase-order value raised. |
| `receipt_value` | receipt booked, received value, GRN value, entry value | Sum | 85 | Receipt/entry value booked. |
| `inventory_value` | inventory value, stock value, closing inventory | Average | 85 | Daily outlet stock value; average it for period KPIs. |
| `low_stock_item_count` | inventory pressure, low stock item-days, stock pressure | Sum | 80 | Daily count summed over dates; not current item count. |
| `event_count` | event days, event markers, calendar events | Sum | 70 | Event annotations on outlet-days. |
| `health_note` | outlet status, health status, operating note | Actual | 70 | `Normal`, `Event Day`, `Inventory Pressure`. |

Required aggregate formulas on this table:

| Formula name | Formula | Synonyms | Format |
|---|---|---|---|
| `AF_Average_Daily_Revenue` | `SUM("net_sales") / DISTINCTCOUNT("activity_date")` | average daily sales, revenue run rate, daily run rate | Currency |
| `AF_Purchase_To_Sales_Ratio` | `SUM("po_value") / SUM("net_sales") * 100` | purchase to sales ratio, procurement to sales, spend pressure | Percentage |
| `AF_Revenue_Per_Avg_Inventory_Rupee` | `SUM("net_sales") * DISTINCTCOUNT("activity_date") / SUM("inventory_value")` | revenue per inventory rupee, inventory productivity, inventory turnover rupee | Decimal |

Critical instruction:

```text
Do not let Zia sum Revenue Per Inventory Rupee across outlets.
It must calculate from aggregate numerator and denominator.
```

### 3.2 Sales And Menu

Table: `FACT_Sales`

| Column | Synonyms to add | Default function | Priority | Business meaning |
|---|---|---|---:|---|
| `net_sale` | revenue, net sales, sales, menu revenue, item sales | Sum | 100 | Revenue from menu item sales. |
| `qty` | menu units, units sold, quantity sold, item quantity | Sum | 80 | Customer menu item units sold. |
| `sales_date` | date, sales date, day | Date grouping | 100 | Date filter and trend axis. |
| `outlet_name` | outlet, cafe, store, branch | Group by / actual | 100 | Cafe selected. |
| `super_category` | super category, broad category, food beverage dessert | Group by / actual | 80 | High-level menu category. |
| `category` | category, menu category, product category | Group by / actual | 95 | Category revenue mix. |
| `item_name` | menu item, product, dish, drink, SKU name | Group by / actual | 95 | Menu item. |
| `item_number` | item code, SKU, product code | Actual | 75 | Unique item identifier. |
| `net_sale_per_qty` | realized price, average selling price, ASP, unit price realized | Average | 70 | Row-level realized unit price; better formula is below. |

Required aggregate formula:

| Formula name | Formula | Synonyms | Format |
|---|---|---|---|
| `AF_Avg_Realized_Menu_Price` | `SUM("net_sale") / SUM("qty")` | average realized price, blended ASP, average item price | Currency |

Zia wording rule:

```text
When someone asks "top performing item", interpret performance as SUM(net_sale)
unless the question says "by quantity" or "by units".
```

### 3.3 Vendor And Procurement

Table: `FACT_Vendor_Spend`

| Column | Synonyms to add | Default function | Priority | Business meaning |
|---|---|---|---:|---|
| `ordered_value` | PO raised value, ordered value, purchase order value, procurement raised, PO spend | Sum | 100 | Value of purchase orders raised. |
| `received_value` | receipt booked value, received value, GRN value, booked receipt, goods received value | Sum | 95 | Receipt/entry value booked. |
| `activity_date` | procurement date, PO or receipt date, transaction date | Date grouping | 95 | Unified date for PO and receipt movement. |
| `vendor_name` | vendor, supplier, seller | Group by / actual | 100 | Vendor/supplier name. |
| `item_name` | material, ingredient, procurement item, supply item | Group by / actual | 95 | Purchased material. |
| `category_name` | material category, procurement category, ingredient category | Group by / actual | 80 | Material category. |
| `po_status` | PO status, order status, purchase status | Actual | 70 | Applies only to PO rows, not receipt rows. |
| `open_or_partial_po_count` | open PO count, partial PO count, pending PO count, follow-up count | Sum | 80 | Count of pending/partial/remaining-qty PO lines. |

Required aggregate formula:

| Formula name | Formula | Synonyms | Format |
|---|---|---|---|
| `AF_PO_vs_Receipt_Value_Gap` | `SUM("ordered_value") - SUM("received_value")` | PO receipt gap, ordered vs received gap, value gap, pending value gap | Currency |

Important Zia training notes:

- `Open / Partial PO Status Count` is status/remaining-quantity based.
- `PO vs Receipt Value Gap` is value based.
- A vendor can have a positive value gap and zero open/partial status count. Zia should explain that these are different measures.
- Do not map `PO Status` to `Receipt Booked Value`; receipt rows do not carry PO status.

### 3.4 PO Follow-Up Detail

Table: `FACT_PO_Receipt_Comparison`

| Column | Synonyms to add | Default function | Priority |
|---|---|---|---:|
| `po_number` | PO number, purchase order number, order ID | Actual | 100 |
| `po_date` | PO date, order date, procurement date | Date grouping | 100 |
| `expected_delivery_date` | due date, delivery date, expected delivery | Date grouping | 90 |
| `pending_or_partial_flag` | pending flag, open flag, follow-up flag | Sum | 95 |
| `remaining_qty` | remaining quantity, balance quantity, open quantity | Sum | 90 |
| `unmatched_order_qty` | unmatched quantity, unreceived quantity | Sum | 85 |
| `matched_received_qty` | received quantity, matched receipt quantity | Sum | 85 |

Use this table for questions like:

```text
Which POs need follow-up?
Show pending POs for Connaught Place.
Which vendor has remaining quantity?
```

### 3.5 Inventory And Consumption

Use two separate meanings:

| Question type | Preferred table |
|---|---|
| Current/latest stock pressure | `SUM_Inventory_Risk` |
| Historical inventory trend by date | `FACT_Inventory_Closing` |
| Recipe-based ingredient demand from sales | `FACT_Theoretical_Consumption` |

Table: `SUM_Inventory_Risk`

| Column | Synonyms to add | Default function | Priority |
|---|---|---|---:|
| `total_amt` | current inventory value, latest stock value, stock value | Sum | 95 |
| `total_qty` | current stock quantity, latest stock qty, stock on hand | Sum | 90 |
| `low_stock_flag` | low stock count, current low stock, low stock item count | Sum | 95 |
| `inventory_pressure_band` | pressure band, stock band, risk band | Actual | 90 |
| `risk_note` | stock note, inventory note, risk note | Actual | 70 |

Table: `FACT_Theoretical_Consumption`

| Column | Synonyms to add | Default function | Priority |
|---|---|---|---:|
| `theoretical_ingredient_qty` | ingredient demand, theoretical consumption, recipe demand, material consumption | Sum | 100 |
| `ingredient_name` | ingredient, material, raw material | Group by / actual | 100 |
| `menu_item_name` | menu item, recipe, product | Group by / actual | 85 |
| `sales_date` | date, sales date, consumption date | Date grouping | 90 |

### 3.6 Events And Competitor Context

Table: `SUM_Event_Impact`

| Column | Synonyms to add | Default function | Priority |
|---|---|---|---:|
| `event_day_sales` | event sales, event revenue, promotion sales | Sum | 95 |
| `baseline_sales` | baseline, normal sales, expected sales | Average | 80 |
| `sales_lift_pct` | lift, sales lift, event lift, uplift | Average | 95 |
| `event_name` | event, promotion, holiday | Actual | 100 |
| `event_type` | event type, promotion type, holiday type | Actual | 80 |

Table: `SUM_Competitor_Positioning`

| Column | Synonyms to add | Default function | Priority |
|---|---|---|---:|
| `avg_price_index` | price index, competitor index, premium index | Average | 95 |
| `avg_price_difference` | price difference, premium amount, price gap | Average | 85 |
| `price_position_band` | price position, premium/discounted/equal | Actual | 90 |
| `competitor_name` | competitor, nearby cafe, market competitor | Actual | 85 |
| `competitor_category` | competitor category, mapped category | Actual | 85 |

## 4. Data Synonyms

Data synonyms teach Zia that user language maps to exact values in the data.

Add these under text columns where possible.

### 4.1 Outlet Names

Column: `outlet_name`

| Actual value | Data synonyms |
|---|---|
| `ABNAH Cafe Connaught Place` | CP, Connaught, Connaught Place, office outlet, corporate outlet, central Delhi cafe |
| `ABNAH Cafe Hauz Khas` | HK, Hauz, Hauz Khas, student outlet, youth outlet, college cafe |
| `ABNAH Cafe Saket Premium` | Saket, Saket Premium, mall outlet, premium outlet, leisure outlet |

### 4.2 Menu Categories

Column: `category`

| Actual value examples | Data synonyms |
|---|---|
| `Coffee Classics` | hot coffee, classic coffee, regular coffee |
| `Signature Coffee` | premium coffee, specialty coffee, signature drinks |
| `Cold Coffee` | cold coffee, frappe-style drinks, iced coffee |
| `Cold Brew` | cold brew coffee |
| `Tea` | chai, tea drinks |
| `Desserts` | dessert, sweets, cakes |
| `Baked Goods` | bakery, croissants, baked items |
| `Sandwiches` | sandwiches, lunch sandwiches |
| `Wraps` | wraps, rolls |

### 4.3 Vendors

Column: `vendor_name`

| Actual value | Data synonyms |
|---|---|
| `FreshDairy Foods NCR` | dairy vendor, milk vendor, FreshDairy |
| `Delhi Bakery Supply Co` | bakery vendor, bread supplier, bakery supplier |
| `PackPro Disposables` | packaging vendor, disposables supplier, cups vendor |
| `NorthStar Poultry` | poultry vendor, chicken supplier, egg supplier |
| `BeanCraft Roasters Delhi` | coffee bean vendor, roaster, coffee supplier |
| `TeaLeaf Traders NCR` | tea vendor, matcha supplier, tea supplier |
| `SweetBase Foods` | syrup vendor, sugar syrup supplier |
| `ChocoCraft Ingredients` | chocolate vendor, cocoa supplier |
| `GreenLeaf Produce Delhi` | produce vendor, vegetable supplier |
| `Metro Wholesale Delhi` | fallback vendor, wholesale vendor |

### 4.4 PO Status

Column: `po_status`

| Actual value | Data synonyms |
|---|---|
| `Closed` | completed, fulfilled, received |
| `Partially Received` | partial, partly received, incomplete |
| `Pending` | open, not received, awaiting delivery |
| `Cancelled` | canceled, void, dropped |

## 5. Zia Insights Configuration By Dashboard

Zia Insights should be configured per saved report/chart, not only at the dashboard level.

General settings:

1. Open the saved chart/report.
2. Click `Zia Insights`.
3. Open `Settings`.
4. Set verbosity:
   - Executive charts: `High`
   - Detailed tables: `Medium`
   - Very small KPI cards: `Low` or `Medium`
5. Set `Explain by Column` manually.
6. Enable only the insight categories that fit the report.
7. For important trend charts, review Key Driver Analysis configuration.
8. Save the report after configuration.

### 5.1 Dashboard 1: Executive Outlet Health

Charts:

| Report/chart | Verbosity | Explain by columns | Insight categories | Key driver target | Factors |
|---|---|---|---|---|---|
| `CH02_Daily_Sales_Trend_By_Outlet` | High | `activity_date`, `outlet_name`, `net_sales`, `event_count`, `low_stock_item_count`, `po_value` | Trend, anomaly, contribution, diagnostic | `net_sales` | `outlet_name`, `event_count`, `low_stock_item_count`, `po_value`, `inventory_value` |
| `CH01_Outlet_Sales_Ranking` | Medium | `outlet_name`, `net_sales`, `po_value`, `receipt_value`, `inventory_value` | Contribution, top contributors | `net_sales` | `outlet_name`, `po_value`, `inventory_value` |
| `CH03_Sales_Purchase_Receipt_Comparison` | High | `outlet_name`, `net_sales`, `po_value`, `receipt_value` | Contribution, analysis of measures | `net_sales` | `outlet_name`, `po_value`, `receipt_value` |

Expected Zia story:

```text
Saket Premium leads Month 1 revenue.
Hauz Khas has stronger purchase pressure relative to sales.
Connaught Place is stable corporate coffee-led revenue.
Inventory pressure is visible as item-days, not a current stock count.
```

### 5.2 Dashboard 2: Sales And Menu Intelligence

Charts:

| Report/chart | Verbosity | Explain by columns | Insight categories | Key driver target | Factors |
|---|---|---|---|---|---|
| `CH07_Daily_Net_Sales_Trend` | High | `sales_date`, `outlet_name`, `category`, `net_sale`, `qty` | Trend, anomaly, key drivers | `net_sale` | `category`, `item_name`, `qty`, `outlet_name` |
| `CH08_Category_Revenue_Mix` | High | `category`, `super_category`, `net_sale`, `qty`, `outlet_name` | Contribution, top contributors | `net_sale` | `category`, `super_category`, `qty` |
| `CARD_Top_5_Menu_Winners` | Medium | `category`, `item_name`, `net_sale`, `qty` | Top contributors | `net_sale` | `category`, `item_name`, `qty` |
| `TB03_Menu_Item_Detail_Date_Filtered` | Medium | `item_number`, `item_name`, `category`, `net_sale`, `qty`, `AF_Avg_Realized_Menu_Price` | Contribution, extreme values | `net_sale` | `category`, `item_name`, `qty`, realized price |

Expected Zia story:

```text
Coffee Classics is the main revenue driver in all outlets for Month 1,
but the top menu item differs by outlet.
Connaught Place is classic coffee-led.
Hauz Khas has a colder beverage/social pattern.
Saket Premium carries premium coffee and dessert/mall behavior.
```

### 5.3 Dashboard 3: Vendor And Procurement Analytics

Charts:

| Report/chart | Verbosity | Explain by columns | Insight categories | Key driver target | Factors |
|---|---|---|---|---|---|
| KPI row | Medium | `ordered_value`, `received_value`, `AF_PO_vs_Receipt_Value_Gap`, `open_or_partial_po_count`, `vendor_name`, `item_name` | Analysis of measures, contribution | `ordered_value` | `vendor_name`, `item_name`, `received_value`, `open_or_partial_po_count` |
| `CH14_Vendor_PO_Raised_Share` | High | `vendor_name`, `ordered_value`, `outlet_name`, `item_name`, `category_name` | Contribution, top contributors | `ordered_value` | `vendor_name`, `item_name`, `category_name` |
| `CH15_Vendor_Receipt_Booked_Share` | High | `vendor_name`, `received_value`, `outlet_name`, `item_name`, `category_name` | Contribution, top contributors | `received_value` | `vendor_name`, `item_name`, `category_name` |
| `TB05_Pending_Partial_PO_Detail` | Medium | `po_number`, `po_status`, `vendor_name`, `item_name`, `remaining_qty`, `expected_delivery_date` | Extreme values, diagnostic | `remaining_qty` | `vendor_name`, `item_name`, `po_status`, `expected_delivery_date` |

Expected Zia story:

```text
FreshDairy is the largest PO vendor in all outlets.
Receipt value does not need to equal PO raised value because receipt rows are separate receiving movements.
PO vs Receipt Value Gap explains value difference.
Open / Partial PO Status Count explains operational follow-up status.
```

### 5.4 Dashboard 4: Inventory And Consumption Intelligence

Charts:

| Report/chart | Verbosity | Explain by columns | Insight categories | Key driver target | Factors |
|---|---|---|---|---|---|
| Latest stock pressure card/list | Medium | `outlet_name`, `item_name`, `inventory_pressure_band`, `low_stock_flag`, `total_qty`, `total_amt` | Extreme values, contribution | `low_stock_flag` | `item_name`, `category_name`, `total_qty`, `total_amt` |
| `CH21_Inventory_Value_By_Category` | High | `latest_inventory_date`, `category_name`, `super_category_name`, `total_amt`, `outlet_name` | Contribution, top contributors | `total_amt` | `category_name`, `super_category_name`, `outlet_name` |
| `CH26_Top_Theoretical_Ingredients` | High | `ingredient_name`, `theoretical_ingredient_qty`, `menu_item_name`, `outlet_name`, `sales_date` | Contribution, top contributors | `theoretical_ingredient_qty` | `ingredient_name`, `menu_item_name`, `outlet_name` |

Expected Zia story:

```text
Inventory pressure should be explained as current/heuristic pressure,
not as a stockout forecast.
Theoretical consumption connects menu sales to raw material demand,
especially common packaging and beverage inputs.
```

### 5.5 Dashboard 5: Calendar, Event, And Competitor Intelligence

Charts:

| Report/chart | Verbosity | Explain by columns | Insight categories | Key driver target | Factors |
|---|---|---|---|---|---|
| `CH27_Event_Sales_By_Event` | High | `event_name`, `event_type`, `outlet_name`, `event_day_sales`, `baseline_sales`, `sales_lift_pct` | Contribution, diagnostic | `event_day_sales` | `event_name`, `outlet_name`, `event_type`, `baseline_sales` |
| `CH28_Event_Lift_By_Event` | High | `event_name`, `outlet_name`, `sales_lift_pct`, `confidence_level`, `affected_category` | Extreme values, diagnostic | `sales_lift_pct` | `event_name`, `outlet_name`, `affected_category`, `confidence_level` |
| `CH31_Competitor_Price_Index` | Medium | `market_area`, `competitor_name`, `competitor_category`, `avg_price_index`, `price_position_band` | Contribution, extreme values | `avg_price_index` | `market_area`, `competitor_category`, `competitor_name` |

Expected Zia story:

```text
Coffee Subscription Launch should show positive lift for Connaught Place and Saket.
Republic Day should show leisure upside strongest in Saket and weaker corporate behavior in Connaught Place.
Competitor pricing should be treated as context, not proof of causality.
```

## 6. Natural Language Question Bank

Use these questions to test Ask Zia after training. Compare answers against:

```text
docs/month1_truth_tables/dashboard_prediction_pack_month1.csv
docs/month1_truth_reference_readme.md
```

### 6.1 Executive Questions

| Ask Zia question | Expected answer behavior |
|---|---|
| Which outlet had the highest net sales in Month 1? | Should answer Saket Premium with about `6.92L`. |
| Compare net sales, PO raised value, and receipt booked value by outlet for January 2026. | Should use `FACT_Outlet_Daily_Health` and show three outlets. |
| What is the purchase-to-sales ratio for Hauz Khas in Month 1? | Should calculate about `96.5%`, not all-outlet `83.7%`. |
| Which outlet had the most inventory pressure item-days? | Should answer Hauz Khas with `47`. |
| What happened on the highest sales day for Connaught Place? | Should identify `2026-01-16` around `30.63K` and connect it to event day if possible. |

### 6.2 Sales/Menu Questions

| Ask Zia question | Expected answer behavior |
|---|---|
| What are the top 5 menu items by net sales for Connaught Place in January? | Should use `FACT_Sales`; top item should be `Cappuccino - Medium`. |
| Which category drove revenue for Hauz Khas? | Should answer `Coffee Classics`, with Cold Coffee also important. |
| Show top menu items for Saket Premium by units sold. | Should sort by `SUM(qty)`, not revenue. |
| What is the category revenue mix for selected outlet and date range? | Should use `FACT_Sales`, not static `SUM_Sales_Category_Mix`. |
| What is average realized menu price by item? | Should use aggregate formula `SUM(net_sale) / SUM(qty)`. |

### 6.3 Vendor/Procurement Questions

| Ask Zia question | Expected answer behavior |
|---|---|
| Which vendor has the highest PO raised value for Hauz Khas? | Should answer `FreshDairy Foods NCR`. |
| Which vendor has the highest receipt booked value for Hauz Khas? | Should answer `Delhi Bakery Supply Co`. |
| Why can PO raised be higher than receipt booked but open PO count is zero? | Should explain value gap vs status count difference. |
| Show vendors with positive PO receipt gap and zero open status count. | Should include examples like TeaLeaf Traders NCR and ChocoCraft Ingredients. |
| Which POs need follow-up? | Should use `FACT_PO_Receipt_Comparison` and filter `pending_or_partial_flag = 1`. |

### 6.4 Inventory/Consumption Questions

| Ask Zia question | Expected answer behavior |
|---|---|
| Which outlet has the most latest low stock items? | Should use `SUM_Inventory_Risk`, not historical item-days. |
| Which category has the highest inventory value for Saket? | Should use inventory category value. |
| Which ingredient has the highest theoretical demand from sales? | Should use `FACT_Theoretical_Consumption`. |
| What does inventory pressure mean here? | Should describe heuristic low-stock pressure, not forecasted stockout. |
| Show top materials consumed by Connaught Place menu sales. | Should rank ingredients by theoretical quantity. |

### 6.5 Event/Competitor Questions

| Ask Zia question | Expected answer behavior |
|---|---|
| What was the sales lift from Coffee Subscription Launch? | Should show Connaught Place and Saket lift. |
| Did Republic Day help all outlets equally? | Should show Saket positive, Connaught negative/soft corporate behavior. |
| Which event had the strongest positive lift? | Should use `SUM_Event_Impact.sales_lift_pct`. |
| Which market has premium competitor price positioning? | Should use `SUM_Competitor_Positioning`. |
| Are competitor prices causing sales? | Should say competitor data is contextual and does not prove causality. |

## 7. Complete Business Answer Template

When evaluating Ask Zia answers, judge them against this structure:

```text
1. Direct answer: one sentence with the metric and value.
2. Context: outlet/date/category/vendor/material filters used.
3. Breakdown: top contributors or drivers.
4. Interpretation: what it means operationally.
5. Caveat: synthetic data, proxy metric, or correlation/causality warning if relevant.
6. Suggested next view: chart/table to open for drilldown.
```

Example good answer:

```text
For Month 1, Saket Premium led net sales at about 6.92L.
The result uses FACT_Outlet_Daily_Health with January 1-31 selected.
Coffee Classics and Signature Coffee were the leading sales categories.
This supports the premium mall/leisure story for Saket.
Inventory and competitor context should be reviewed separately before calling this a profit result.
Open the Sales/Menu dashboard and Category Revenue Mix for drilldown.
```

Example bad answer:

```text
Saket is best because it sold the most items.
```

Why it is bad:

- It does not state revenue.
- It confuses sales performance with unit count.
- It does not mention date scope.
- It does not explain the business story.

## 8. Step-By-Step Zia Build Plan In Zoho

Follow this section while Zoho is open. Do not jump straight to asking questions. Train in this order so Zia learns the business language before it sees many possible tables.

If Zoho labels differ slightly, use the closest matching screen:

| This README says | Zoho may call it |
|---|---|
| Ask Zia Settings | Zia Settings / Ask Zia Setup |
| Train Ask Zia | Manage Synonyms / Train Zia / Zia Training |
| Table priority | Table Ranking / Relevance / Priority |
| Column priority | Column Ranking / Importance / Priority |
| Data synonyms | Value Synonyms / Data Value Synonyms |
| Exclude table | Blacklist / Hide from Ask Zia / Do not include |
| Default function | Default Aggregation / Default Summary Function |

### Phase 0: Prepare The Workspace

1. Confirm all dashboards and reports exist or at least the core saved reports exist.
2. Confirm these Query Tables exist:

```text
FACT_Outlet_Daily_Health
FACT_Sales
FACT_Vendor_Spend
FACT_Purchase_Order
FACT_PO_Receipt_Comparison
FACT_Inventory_Closing
SUM_Inventory_Risk
FACT_Theoretical_Consumption
SUM_Event_Impact
SUM_Event_Markers
SUM_Competitor_Positioning
```

3. Open:

```text
docs/month1_truth_tables/dashboard_prediction_pack_month1.csv
```

4. Keep this file open as the answer key.
5. In Zoho, open `Ask Zia`.
6. Ask one baseline question before training:

```text
Which outlet had the highest net sales in January 2026?
```

7. Note the answer mentally. If it is wrong now, that is fine. This is the before-training baseline.

### Phase 1: Open Ask Zia Training Settings

1. In Zoho Analytics, open the ABNAH workspace.
2. Click `Ask Zia` from the left sidebar or top toolbar.
3. Click the `Settings` / gear icon inside Ask Zia.
4. Open `Train Ask Zia` / `Manage Synonyms`.
5. Find the section where tables and columns are listed.
6. Do not edit synonyms yet. First clean the visible table set.

### Phase 2: Exclude RAW And Modeling Tables

Purpose: prevent Zia from choosing raw/source tables instead of curated business tables.

1. In Ask Zia training settings, open the table list.
2. Search:

```text
RAW_
```

3. For every RAW table, set:

```text
Exclude from Ask Zia / Hide / Blacklist
```

4. Search:

```text
STD_
```

5. For every STD table, set:

```text
Exclude from Ask Zia
```

If Zoho does not allow exclusion, set the lowest available priority.

6. Search:

```text
SUM_Executive_KPIs
SUM_Sales_Category_Mix
SUM_Vendor_Share
```

7. Exclude these, or set them to very low priority.
8. Keep `SUM_Menu_Item_Performance` visible only if you want full-month item ranking. Set it to low priority.
9. Keep `SUM_Inventory_Risk`, `SUM_Event_Impact`, `SUM_Event_Markers`, and `SUM_Competitor_Positioning` visible.
10. Save table visibility settings.

Immediate check:

1. Ask Zia:

```text
Show category revenue mix for Connaught Place in January 2026.
```

2. If Zia mentions a RAW or STD table, go back and hide/lower that table.

### Phase 3: Set Table Synonyms And Priorities

Purpose: make Zia choose the correct business table when a user says revenue, menu, vendor, inventory, event, or competitor.

Do the tables in this exact order.

#### 3.1 Train `FACT_Outlet_Daily_Health`

1. In training settings, search:

```text
FACT_Outlet_Daily_Health
```

2. Open table settings.
3. Set table priority to:

```text
100
```

4. Add table synonyms exactly:

```text
executive health
outlet health
cafe health
daily performance
outlet scorecard
executive dashboard
chain performance
outlet comparison
business health
```

5. Save.

#### 3.2 Train `FACT_Sales`

1. Search and open:

```text
FACT_Sales
```

2. Set table priority:

```text
100
```

3. Add table synonyms:

```text
sales
menu sales
item sales
revenue
menu intelligence
category sales
item performance
menu performance
top items
sales trend
```

4. Save.

#### 3.3 Train `FACT_Vendor_Spend`

1. Search and open:

```text
FACT_Vendor_Spend
```

2. Set table priority:

```text
100
```

3. Add table synonyms:

```text
procurement
vendor spend
supplier spend
PO and receipts
purchase spend
ordering and receiving
vendor analytics
procurement dashboard
PO raised
receipt booked
```

4. Save.

#### 3.4 Train Supporting Detail Tables

Set these priorities and synonyms.

| Table | Priority | Synonyms to enter |
|---|---:|---|
| `FACT_Purchase_Order` | 90 | purchase orders, PO status, open PO, partial PO, pending PO, processed quantity, remaining quantity |
| `FACT_PO_Receipt_Comparison` | 90 | pending PO detail, PO follow up, receipt comparison, PO receipt matching, pending purchase orders |
| `FACT_Inventory_Closing` | 90 | inventory, stock, closing stock, stock value, inventory closing, inventory trend |
| `SUM_Inventory_Risk` | 85 | latest inventory, current stock pressure, low stock, inventory risk, current stock |
| `FACT_Theoretical_Consumption` | 85 | recipe consumption, theoretical consumption, ingredient demand, material demand, recipe demand |
| `SUM_Event_Impact` | 80 | event lift, event impact, promotion impact, holiday impact, event sales |
| `SUM_Event_Markers` | 80 | spike explanation, event marker, event day story, event notes |
| `SUM_Competitor_Positioning` | 75 | competitor pricing, market pricing, price position, ABNAH vs competitors, pricing context |

For each table:

1. Search table name.
2. Open table settings.
3. Set priority.
4. Paste synonyms.
5. Save.

### Phase 4: Set Column Synonyms And Default Functions

Purpose: make Zia aggregate metrics correctly.

For every table below:

1. Open table training settings.
2. Open the `Columns` tab/list.
3. Click the column.
4. Add synonyms.
5. Set default function.
6. Set priority if available.
7. Save column.
8. Repeat.

#### 4.1 `FACT_Outlet_Daily_Health` Columns

| Column | Default function | Priority | Synonyms to paste |
|---|---|---:|---|
| `net_sales` | Sum | 100 | revenue, net sales, sales revenue, top line, turnover |
| `activity_date` | Date grouping | 100 | date, day, business date, sales date |
| `outlet_name` | Actual / Group by | 100 | outlet, cafe, store, branch, location |
| `market_area` | Actual / Group by | 80 | market, area, locality, location area |
| `sold_qty` | Sum | 65 | menu units sold, units sold, items sold, customer items |
| `po_value` | Sum | 90 | procurement spend, PO value, purchase spend, PO raised, ordered value |
| `receipt_value` | Sum | 85 | receipt booked, received value, GRN value, entry value |
| `inventory_value` | Average | 85 | inventory value, stock value, closing inventory |
| `low_stock_item_count` | Sum | 80 | inventory pressure, low stock item-days, stock pressure |
| `event_count` | Sum | 70 | event days, event markers, calendar events |
| `health_note` | Actual | 70 | outlet status, health status, operating note |

Check after this table:

```text
What is average daily revenue for Hauz Khas in January?
```

Expected direction:

```text
About 20.21K.
```

#### 4.2 `FACT_Sales` Columns

| Column | Default function | Priority | Synonyms to paste |
|---|---|---:|---|
| `net_sale` | Sum | 100 | revenue, net sales, sales, menu revenue, item sales |
| `qty` | Sum | 80 | menu units, units sold, quantity sold, item quantity |
| `sales_date` | Date grouping | 100 | date, sales date, day |
| `outlet_name` | Actual / Group by | 100 | outlet, cafe, store, branch |
| `super_category` | Actual / Group by | 80 | super category, broad category, food beverage dessert |
| `category` | Actual / Group by | 95 | category, menu category, product category |
| `item_name` | Actual / Group by | 95 | menu item, product, dish, drink, SKU name |
| `item_number` | Actual | 75 | item code, SKU, product code |
| `net_sale_per_qty` | Average | 70 | realized price, average selling price, ASP, unit price realized |

Check:

```text
Top 5 menu items by net sales for Connaught Place in January.
```

Expected top:

```text
Cappuccino - Medium
```

#### 4.3 `FACT_Vendor_Spend` Columns

| Column | Default function | Priority | Synonyms to paste |
|---|---|---:|---|
| `ordered_value` | Sum | 100 | PO raised value, ordered value, purchase order value, procurement raised, PO spend |
| `received_value` | Sum | 95 | receipt booked value, received value, GRN value, booked receipt, goods received value |
| `activity_date` | Date grouping | 95 | procurement date, PO or receipt date, transaction date |
| `vendor_name` | Actual / Group by | 100 | vendor, supplier, seller |
| `item_name` | Actual / Group by | 95 | material, ingredient, procurement item, supply item |
| `category_name` | Actual / Group by | 80 | material category, procurement category, ingredient category |
| `po_status` | Actual | 70 | PO status, order status, purchase status |
| `open_or_partial_po_count` | Sum | 80 | open PO count, partial PO count, pending PO count, follow-up count |

Check:

```text
Which vendor has the highest PO raised value for Hauz Khas in January?
```

Expected:

```text
FreshDairy Foods NCR
```

#### 4.4 `FACT_PO_Receipt_Comparison` Columns

| Column | Default function | Priority | Synonyms to paste |
|---|---|---:|---|
| `po_number` | Actual | 100 | PO number, purchase order number, order ID |
| `po_date` | Date grouping | 100 | PO date, order date, procurement date |
| `expected_delivery_date` | Date grouping | 90 | due date, delivery date, expected delivery |
| `pending_or_partial_flag` | Sum | 95 | pending flag, open flag, follow-up flag |
| `remaining_qty` | Sum | 90 | remaining quantity, balance quantity, open quantity |
| `unmatched_order_qty` | Sum | 85 | unmatched quantity, unreceived quantity |
| `matched_received_qty` | Sum | 85 | received quantity, matched receipt quantity |

Check:

```text
Which POs need follow-up for Connaught Place?
```

Expected behavior:

```text
Zia should use FACT_PO_Receipt_Comparison and pending_or_partial_flag = 1.
```

#### 4.5 Inventory, Consumption, Event, Competitor Columns

Set these after the three main business modules are working.

| Table | Column | Default function | Synonyms |
|---|---|---|---|
| `SUM_Inventory_Risk` | `low_stock_flag` | Sum | low stock count, current low stock, low stock item count |
| `SUM_Inventory_Risk` | `total_amt` | Sum | current inventory value, latest stock value, stock value |
| `SUM_Inventory_Risk` | `inventory_pressure_band` | Actual | pressure band, stock band, risk band |
| `FACT_Theoretical_Consumption` | `theoretical_ingredient_qty` | Sum | ingredient demand, theoretical consumption, recipe demand, material consumption |
| `FACT_Theoretical_Consumption` | `ingredient_name` | Actual / Group by | ingredient, material, raw material |
| `SUM_Event_Impact` | `event_day_sales` | Sum | event sales, event revenue, promotion sales |
| `SUM_Event_Impact` | `sales_lift_pct` | Average | lift, sales lift, event lift, uplift |
| `SUM_Competitor_Positioning` | `avg_price_index` | Average | price index, competitor index, premium index |
| `SUM_Competitor_Positioning` | `price_position_band` | Actual | price position, premium, discounted, equal |

### Phase 5: Create Aggregate Formulas For Zia

Create these formulas before serious Zia testing. Ratio and gap questions should use formulas, not row-level arithmetic.

#### 5.1 Formula: Average Daily Revenue

1. Open table:

```text
FACT_Outlet_Daily_Health
```

2. Click `Add Formula`.
3. Choose `Aggregate Formula`.
4. Name:

```text
AF_Average_Daily_Revenue
```

5. Formula:

```text
SUM("net_sales") / DISTINCTCOUNT("activity_date")
```

6. Format: Currency / INR.
7. Synonyms:

```text
average daily sales
revenue run rate
daily run rate
average daily revenue
```

8. Save.

#### 5.2 Formula: Purchase-To-Sales Ratio

1. Open `FACT_Outlet_Daily_Health`.
2. Add Aggregate Formula.
3. Name:

```text
AF_Purchase_To_Sales_Ratio
```

4. Formula:

```text
SUM("po_value") / SUM("net_sales") * 100
```

5. Format: Percentage.
6. Synonyms:

```text
purchase to sales ratio
procurement to sales
spend pressure
PO to sales
```

7. Save.

#### 5.3 Formula: Revenue Per Average Inventory Rupee

1. Open `FACT_Outlet_Daily_Health`.
2. Add Aggregate Formula.
3. Name:

```text
AF_Revenue_Per_Avg_Inventory_Rupee
```

4. Formula:

```text
SUM("net_sales") * DISTINCTCOUNT("activity_date") / SUM("inventory_value")
```

5. Format: Decimal.
6. Synonyms:

```text
revenue per inventory rupee
inventory productivity
inventory turnover rupee
sales per stock rupee
```

7. Save.

#### 5.4 Formula: Average Realized Menu Price

1. Open `FACT_Sales`.
2. Add Aggregate Formula.
3. Name:

```text
AF_Avg_Realized_Menu_Price
```

4. Formula:

```text
SUM("net_sale") / SUM("qty")
```

5. Format: Currency / INR.
6. Synonyms:

```text
average realized price
blended ASP
average selling price
average item price
```

7. Save.

#### 5.5 Formula: PO vs Receipt Value Gap

1. Open `FACT_Vendor_Spend`.
2. Add Aggregate Formula.
3. Name:

```text
AF_PO_vs_Receipt_Value_Gap
```

4. Formula:

```text
SUM("ordered_value") - SUM("received_value")
```

5. Format: Currency / INR.
6. Synonyms:

```text
PO receipt gap
ordered vs received gap
value gap
pending value gap
PO vs receipt value gap
```

7. Save.

### Phase 6: Add Data Synonyms

Purpose: make normal business language map to exact text values.

#### 6.1 Outlet Data Synonyms

1. Open Ask Zia training.
2. Go to `Data Synonyms` / `Value Synonyms`.
3. Choose table:

```text
FACT_Outlet_Daily_Health
```

4. Choose column:

```text
outlet_name
```

5. Add:

| Actual value | Synonyms |
|---|---|
| `ABNAH Cafe Connaught Place` | CP, Connaught, Connaught Place, office outlet, corporate outlet |
| `ABNAH Cafe Hauz Khas` | HK, Hauz, Hauz Khas, student outlet, youth outlet |
| `ABNAH Cafe Saket Premium` | Saket, Saket Premium, mall outlet, premium outlet |

6. Save.
7. Repeat for `FACT_Sales.outlet_name` and `FACT_Vendor_Spend.outlet_name` if Zoho does not propagate lookup synonyms automatically.

#### 6.2 Vendor Data Synonyms

1. Choose table:

```text
FACT_Vendor_Spend
```

2. Choose column:

```text
vendor_name
```

3. Add:

| Actual value | Synonyms |
|---|---|
| `FreshDairy Foods NCR` | dairy vendor, milk vendor, FreshDairy |
| `Delhi Bakery Supply Co` | bakery vendor, bread supplier, bakery supplier |
| `PackPro Disposables` | packaging vendor, disposables supplier, cups vendor |
| `NorthStar Poultry` | poultry vendor, chicken supplier, egg supplier |
| `BeanCraft Roasters Delhi` | coffee bean vendor, roaster, coffee supplier |
| `TeaLeaf Traders NCR` | tea vendor, matcha supplier, tea supplier |
| `SweetBase Foods` | syrup vendor, sugar syrup supplier |
| `ChocoCraft Ingredients` | chocolate vendor, cocoa supplier |
| `GreenLeaf Produce Delhi` | produce vendor, vegetable supplier |
| `Metro Wholesale Delhi` | fallback vendor, wholesale vendor |

4. Save.

#### 6.3 PO Status Synonyms

1. Choose table:

```text
FACT_Vendor_Spend
```

2. Choose column:

```text
po_status
```

3. Add:

| Actual value | Synonyms |
|---|---|
| `Closed` | completed, fulfilled, received |
| `Partially Received` | partial, partly received, incomplete |
| `Pending` | open, not received, awaiting delivery |
| `Cancelled` | canceled, void, dropped |

4. Save.

### Phase 7: Configure Dashboard-Level Zia Insights

This is the part that makes Zia explain chart stories instead of only answering Ask Zia questions.

For every saved chart:

1. Open the saved chart/report from Explorer.
2. Click `Zia Insights`.
3. Click `Settings`.
4. Set `Verbosity`.
5. Set `Explain by Column`.
6. Enable the correct insight categories.
7. If available, configure Key Driver Analysis.
8. Save chart/report.
9. Return to dashboard and refresh the embedded view.

#### 7.1 Executive Dashboard Insights

Configure these first.

| Chart | Verbosity | Explain by Column | Insight categories | Key driver target |
|---|---|---|---|---|
| `CH02_Daily_Sales_Trend_By_Outlet` | High | `activity_date`, `outlet_name`, `net_sales`, `event_count`, `low_stock_item_count`, `po_value` | Trend, anomaly, contribution, diagnostic | `net_sales` |
| `CH01_Outlet_Sales_Ranking` | Medium | `outlet_name`, `net_sales`, `po_value`, `receipt_value`, `inventory_value` | Contribution, top contributors | `net_sales` |
| `CH03_Sales_Purchase_Receipt_Comparison` | High | `outlet_name`, `net_sales`, `po_value`, `receipt_value` | Contribution, analysis of measures | `net_sales` |

After saving, open dashboard `01_Executive_Outlet_Health` and click `Zia Insights`.

Expected story:

```text
Saket Premium leads Month 1 revenue.
Hauz Khas has stronger purchase pressure relative to sales.
Connaught Place is stable corporate coffee-led revenue.
```

#### 7.2 Sales/Menu Dashboard Insights

| Chart/report | Verbosity | Explain by Column | Insight categories | Key driver target |
|---|---|---|---|---|
| `CH07_Daily_Net_Sales_Trend` | High | `sales_date`, `outlet_name`, `category`, `net_sale`, `qty` | Trend, anomaly, key drivers | `net_sale` |
| `CH08_Category_Revenue_Mix` | High | `category`, `super_category`, `net_sale`, `qty`, `outlet_name` | Contribution, top contributors | `net_sale` |
| `CARD_Top_5_Menu_Winners` | Medium | `category`, `item_name`, `net_sale`, `qty` | Top contributors | `net_sale` |
| `TB03_Menu_Item_Detail_Date_Filtered` | Medium | `item_number`, `item_name`, `category`, `net_sale`, `qty` | Contribution, extreme values | `net_sale` |

Expected story:

```text
Coffee Classics is the main revenue driver, but the top menu item differs by outlet.
```

#### 7.3 Vendor/Procurement Dashboard Insights

| Chart/report | Verbosity | Explain by Column | Insight categories | Key driver target |
|---|---|---|---|---|
| KPI row | Medium | `ordered_value`, `received_value`, `AF_PO_vs_Receipt_Value_Gap`, `open_or_partial_po_count`, `vendor_name`, `item_name` | Analysis of measures, contribution | `ordered_value` |
| `CH14_Vendor_PO_Raised_Share` | High | `vendor_name`, `ordered_value`, `outlet_name`, `item_name`, `category_name` | Contribution, top contributors | `ordered_value` |
| `CH15_Vendor_Receipt_Booked_Share` | High | `vendor_name`, `received_value`, `outlet_name`, `item_name`, `category_name` | Contribution, top contributors | `received_value` |
| `TB05_Pending_Partial_PO_Detail` | Medium | `po_number`, `po_status`, `vendor_name`, `item_name`, `remaining_qty`, `expected_delivery_date` | Extreme values, diagnostic | `remaining_qty` |

Expected story:

```text
FreshDairy is the largest PO vendor in all outlets.
PO vs Receipt Value Gap explains value difference.
Open / Partial PO Status Count explains operational follow-up status.
```

#### 7.4 Inventory/Consumption Dashboard Insights

| Chart/report | Verbosity | Explain by Column | Insight categories | Key driver target |
|---|---|---|---|---|
| Latest stock pressure list | Medium | `outlet_name`, `item_name`, `inventory_pressure_band`, `low_stock_flag`, `total_qty`, `total_amt` | Extreme values, contribution | `low_stock_flag` |
| `CH21_Inventory_Value_By_Category` | High | `latest_inventory_date`, `category_name`, `super_category_name`, `total_amt`, `outlet_name` | Contribution, top contributors | `total_amt` |
| `CH26_Top_Theoretical_Ingredients` | High | `ingredient_name`, `theoretical_ingredient_qty`, `menu_item_name`, `outlet_name`, `sales_date` | Contribution, top contributors | `theoretical_ingredient_qty` |

Expected story:

```text
Inventory pressure is a heuristic pressure signal, not a stockout forecast.
Theoretical consumption connects menu sales to raw material demand.
```

#### 7.5 Event/Competitor Dashboard Insights

| Chart/report | Verbosity | Explain by Column | Insight categories | Key driver target |
|---|---|---|---|---|
| `CH27_Event_Sales_By_Event` | High | `event_name`, `event_type`, `outlet_name`, `event_day_sales`, `baseline_sales`, `sales_lift_pct` | Contribution, diagnostic | `event_day_sales` |
| `CH28_Event_Lift_By_Event` | High | `event_name`, `outlet_name`, `sales_lift_pct`, `confidence_level`, `affected_category` | Extreme values, diagnostic | `sales_lift_pct` |
| `CH31_Competitor_Price_Index` | Medium | `market_area`, `competitor_name`, `competitor_category`, `avg_price_index`, `price_position_band` | Contribution, extreme values | `avg_price_index` |

Expected story:

```text
Coffee Subscription Launch shows positive lift for Connaught Place and Saket.
Republic Day is stronger for leisure/mall behavior than corporate behavior.
Competitor pricing is context, not causality.
```

### Phase 8: Ask Zia Test And Fix Loop

Use this loop after every module, not only at the end.

#### 8.1 Create A QA Log

Create a simple spreadsheet or note with these columns:

```text
question
expected answer
actual answer
source table Zia used
pass/fail
fix applied
retest result
```

Use the expected answer from:

```text
docs/month1_truth_tables/dashboard_prediction_pack_month1.csv
```

#### 8.2 Test Executive Questions First

Ask:

```text
Which outlet had the highest net sales in Month 1?
```

Pass condition:

```text
Saket Premium, about 6.92L.
```

Ask:

```text
What is the purchase-to-sales ratio for Hauz Khas in January 2026?
```

Pass condition:

```text
About 96.5%.
```

If it says `83.7%`, Zia is using all outlets or wrong filter mapping.

Fix:

1. Increase priority of `FACT_Outlet_Daily_Health.outlet_name`.
2. Confirm Hauz Khas data synonym exists.
3. Confirm ratio formula uses aggregate formula.
4. Lower priority of `SUM_Executive_KPIs`.

#### 8.3 Test Sales/Menu Questions

Ask:

```text
Top 5 menu items by net sales for Connaught Place in January.
```

Pass condition:

```text
Cappuccino - Medium should be top.
```

If Zia gives same static table after date filters:

1. Lower priority of `SUM_Menu_Item_Performance`.
2. Increase priority of `FACT_Sales.sales_date`.
3. Add synonym `top performing item` to `FACT_Sales.net_sale`, not to `qty`.

#### 8.4 Test Vendor/Procurement Questions

Ask:

```text
Which vendor has highest PO raised value for Hauz Khas?
```

Pass condition:

```text
FreshDairy Foods NCR.
```

Ask:

```text
Why is PO raised higher than receipt booked but open PO count is zero?
```

Pass condition:

```text
Zia should explain that PO vs receipt value gap and open/partial status count are different metrics.
```

If Zia says it is an error:

1. Add synonyms to `AF_PO_vs_Receipt_Value_Gap`.
2. Add synonyms to `open_or_partial_po_count`.
3. Lower priority of PO status for receipt-value questions.
4. Re-ask with `explain PO vs receipt gap`.

#### 8.5 Test Inventory Questions

Ask:

```text
Which outlet has the most low stock items currently?
```

Pass condition:

```text
Use SUM_Inventory_Risk, not historical item-days.
```

Ask:

```text
Which ingredients have highest theoretical consumption from sales?
```

Pass condition:

```text
Use FACT_Theoretical_Consumption and rank theoretical_ingredient_qty.
```

If Zia uses inventory quantity instead:

1. Increase priority of `FACT_Theoretical_Consumption.theoretical_ingredient_qty`.
2. Add synonyms `ingredient demand`, `recipe demand`, `material demand`.
3. Keep inventory quantity synonyms focused on stock-on-hand.

#### 8.6 Test Event/Competitor Questions

Ask:

```text
What was the sales lift from Coffee Subscription Launch?
```

Pass condition:

```text
Connaught Place and Saket should show positive lift.
```

Ask:

```text
Are competitor prices causing sales?
```

Pass condition:

```text
Zia should say competitor pricing is contextual and does not prove causality.
```

If Zia claims causality:

1. Reduce wording in synonyms that says `caused by competitor`.
2. Use synonyms like `competitor context`, `price positioning`, `market pricing`.
3. Add dashboard text note/caveat near competitor charts.

### Phase 9: Dashboard Story Testing

After Ask Zia questions pass, test Zia Insights on each dashboard.

For each dashboard:

1. Open dashboard.
2. Set filters to full Month 1.
3. Click `Zia Insights`.
4. Read the generated insight.
5. Check whether it covers:
   - top contributor,
   - trend or comparison,
   - business meaning,
   - caveat where needed.
6. Change outlet filter.
7. Click `Zia Insights` again.
8. Confirm story changes.

Pass examples:

| Dashboard | Expected Zia story |
|---|---|
| Executive | Saket leads revenue; Hauz Khas has high procurement pressure; Connaught is corporate coffee-led. |
| Sales/Menu | Coffee Classics leads, but top menu item differs by outlet. |
| Vendor/Procurement | FreshDairy leads PO raised; receipt value and PO value differ by movement timing. |
| Inventory | Current low-stock pressure differs from historical pressure item-days. |
| Event/Competitor | Events are directional lift; competitor pricing is context, not causality. |

### Phase 10: Retest After Month 2 / Month 3 Refresh

After loading new months:

1. Refresh Zoho RAW feeds.
2. Refresh/recompute Query Tables.
3. Ask:

```text
How did net sales change after Month 2?
Which outlet improved most?
Did procurement pressure increase?
Which event created the biggest lift?
```

4. Zia should answer over the selected refreshed date range.
5. If it still answers only Month 1, check:
   - RAW feeds refreshed,
   - Query Tables recomputed,
   - dashboard date filter includes Month 2/3,
   - Zia is using date-safe FACT tables.

## 9. Acceptance Criteria

Zia is ready for demo only when:

| Test | Pass condition |
|---|---|
| Outlet synonyms | CP/HK/Saket all map to correct outlet names. |
| Revenue questions | Zia uses `SUM(net_sales)` or `SUM(net_sale)`, not quantity. |
| Date questions | Zia uses date-safe FACT tables. |
| Ratio questions | Zia uses aggregate formulas, not summed row ratios. |
| Procurement gap | Zia separates value gap from open/partial status count. |
| Receipt questions | Zia does not filter receipt booked value by PO status. |
| Inventory pressure | Zia distinguishes current low stock from historical item-days. |
| Event lift | Zia explains directional lift with causality caveat. |
| Competitor context | Zia does not claim competitor prices caused sales. |
| Dashboard Insights | Each key chart produces a useful story at Medium/High verbosity. |

## 10. What Not To Claim

Do not train or encourage Zia to claim:

- audited profit,
- actual gross margin,
- exact COGS,
- labour/rent-adjusted profitability,
- causal competitor impact,
- stockout prediction,
- PO-to-receipt audit reconciliation by PO number.

Current model supports:

- net sales,
- average daily revenue,
- purchase pressure,
- PO raised value,
- receipt booked value,
- PO vs receipt value gap,
- open/partial PO follow-up,
- inventory pressure,
- theoretical consumption,
- event-associated lift,
- competitor price context.

## 11. Maintenance Checklist

Whenever query tables change:

1. Re-run:

```powershell
python scripts\analyze_month1_truth.py
```

2. Check updated truth files.
3. Update Zia synonyms only if column names or business meanings changed.
4. Re-run the question bank.
5. Re-check Zia Insights settings on affected charts.

Whenever a new dashboard is added:

1. Decide primary fact table.
2. Add table/column synonyms.
3. Add data synonyms if new entities appear.
4. Add 5-10 question bank entries.
5. Add prediction rows to the truth process if the dashboard becomes part of the main demo.

## 12. Official References

- Zoho Analytics Ask Zia training documentation: https://www.zoho.com/analytics/help/train-ask-zia.html
- Zoho Analytics Zia Insights documentation: https://www.zoho.com/analytics/help/zia/insights.html
