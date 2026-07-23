# Zoho Ask Zia Exact Step-By-Step Training Manual

Use this after the final dashboard charts are built.

This README is written for the Zoho Analytics screen shown in the final screenshots:

```text
Ask Zia -> Manage Synonyms -> Synonyms Settings: <table name or column name>
```

The goal is not just to make Ask Zia understand words. The goal is to make Ask Zia use a controlled semantic layer that sits on top of the same final business model that the dashboards use:

```text
RAW feed tables -> STD cleaned tables -> FACT/SUM dashboard tables -> ZIA semantic query tables -> Ask Zia
```

Current project decision:

```text
Dashboards continue to use the existing FACT/SUM query tables.
Ask Zia should primarily use the new ZIA_* query tables in docs/zoho_ask_zia_query_table_sql.
```

This change is necessary because Ask Zia was selecting event/baseline/inventory fields for plain sales questions. The ZIA layer exposes fewer, clearer, business-named columns.

Build and train the new layer from:

```text
docs/zoho_ask_zia_query_table_sql/README.md
```

## 1. Final Dashboard Scope

Train Ask Zia for these final dashboards only:

| Dashboard | Final visuals Ask Zia must understand |
|---|---|
| Executive Outlet Health | KPI row, Outlet Performance Summary, Daily Sales Trend By Outlet, Sales Purchase Receipt Comparison, Outlet Sales Ranking |
| Sales And Menu Intelligence | KPI row, Daily Net Sales Trend, Category Revenue Mix, Top Items By Net Sales, Top Items By Quantity, Revenue Vs Quantity, Realized Price Vs Menu Rate, Category Trend, Days Of Week HeatMap, Top 5 Menu Winners, Menu Item Detail |
| Vendor And Procurement Analytics | KPI row, Vendor PO Raised Share, Vendor Receipt Booked Share, Vendor Spend Trend, PO Status Value, PO VS Receipt Gap By Vendor, Pending Quantity By Material, Vendor Material Concentration, Pending Partial PO Detail, Receipt Booking Trend |
| Inventory And Consumption Intelligence | KPI row, Top Inventory Value Items By Category, Current Stock Pressure Band Chart, Inventory Trend, Theoretical Demand Trend (Packaging), Top Theoretical Ingredients (Recipe), Top Theoretical Materials (Packaging), Theoretical Demand Trend (Recipe) |

Do not train Event/Competitor as a main final-dashboard area unless that optional page is actually being shown in the demo. If those tables remain in Zoho, set them Low or exclude them from Ask Zia.

## 2. What Ask Zia Should Do

There are two layers.

### 2.1 Layer 1: Replace Manual Filtering

Instead of manually setting filters like:

```text
Outlet = Hauz Khas
Date = January 2026
Measure = Net Sale
Group By = Category
```

the user should ask:

```text
Show category wise net sales for Hauz Khas in January 2026
```

Ask Zia should generate a report from:

```text
ZIA_Sales_Menu_Daily_Category
```

using:

```text
Rows / X-axis = category
Measure / Y-axis = SUM(net_sales)
Filters = outlet_name contains Hauz Khas, business_date in January 2026
```

### 2.2 Layer 2: Extra Business Processing

Ask Zia can also answer questions that are more flexible than fixed charts:

```text
Which items sell high quantity but weak revenue?
Which vendor has high PO raised value but low receipt booked value?
Which materials have the highest pending quantity?
Which ingredient demand is highest from recipe consumption?
Which weekday performs best for Connaught Place?
Which outlet has the highest purchase-to-sales pressure?
```

This works only if:

1. `ZIA_*` tables have High priority.
2. RAW, STD, event, competitor, and old dashboard FACT/SUM tables are excluded or low priority for Ask Zia.
3. Metric columns have correct synonyms and default functions.
4. Outlet, vendor, category, item, and PO status values have data synonyms.
5. Ratio metrics are aggregate formulas or prebuilt safe columns, not normal row-level formulas.

### 2.3 What Ask Zia Must Not Claim

Ask Zia should not claim these because the current raw data does not contain enough information:

```text
audited profit
true gross margin
labour cost impact
rent impact
customer-level behavior
stockout prediction
causal competitor impact
audited COGS
```

It can talk about:

```text
sales revenue
menu units
average realized price
procurement raised value
receipt booked value
PO receipt gap
current inventory value
current low-stock/watch materials
theoretical ingredient demand from menu sales
weekday/category/item patterns
```

## 3. Data Baseline Guardrail Before Training

Before judging Ask Zia, first confirm the data is not duplicated.

Use these Month 1 sanity checks after raw table cleanup/refetch:

| Check | Expected Month 1 baseline |
|---|---:|
| All-outlet Executive Net Sales Revenue | about `19.45L` |
| Connaught Place Net Sales | about `6.26L` |
| Hauz Khas Net Sales | about `6.27L` |
| Saket Premium Net Sales | about `6.92L` |
| Current total inventory value | about `18.92L` |
| Current inventory value - Connaught Place | about `6.13L` |
| Current inventory value - Hauz Khas | about `6.77L` |
| Current inventory value - Saket Premium | about `6.02L` |

If dashboard values are much higher, do not "fix" Ask Zia first. Fix the raw import/refetch duplication first. Ask Zia will only explain the data it sees.

## 4. Zoho Screen Navigation

Use this exact path:

1. Open the Zoho Analytics workspace.
2. Click `Ask Zia` from the left sidebar.
3. Open `Manage Synonyms`.
4. In the left panel, use search to find the table.
5. Click the table name itself to edit table-level synonyms and table priority.
6. Click the arrow beside the table name to expand columns.
7. Click a column name to edit column-level synonyms, default function, and column priority.
8. For text columns, open the value/data synonyms area if Zoho shows it.
9. Click `Save` after each table or column update.

Important screen rule:

```text
Selected table name = table synonyms and table priority.
Selected column name = column synonyms, default function, column priority, and data synonyms.
```

## 5. Table Priority Plan

Set table priority before adding detailed synonyms.

### 5.1 High Priority Ask Zia Semantic Tables

| Table | Priority | Paste into Table Synonyms |
|---|---|---|
| `ZIA_Executive_Outlet_Daily` | High | daily outlet health, daily executive scorecard, outlet daily sales, daily cafe performance |
| `ZIA_Executive_Outlet_Month` | High | monthly outlet health, monthly executive scorecard, outlet monthly sales, net sales by outlet, purchase to sales by outlet |
| `ZIA_Sales_Menu_Daily_Item` | High | menu item sales, item sales, daily item revenue, top menu items, item quantity |
| `ZIA_Sales_Menu_Daily_Category` | High | category sales, category revenue, menu category mix, category trend |
| `ZIA_Sales_Menu_Item_Summary` | High | menu winners, menu item performance, revenue versus quantity, realized price, menu rate |
| `ZIA_Sales_Weekday_Category` | High | weekday sales, day of week sales, weekday heatmap, category by weekday |
| `ZIA_Procurement_Daily_Vendor_Material` | High | procurement daily, vendor spend daily, material purchase, PO and receipt movement |
| `ZIA_Procurement_Monthly_Vendor` | High | vendor monthly scorecard, top vendors, PO receipt gap, receipt coverage |
| `ZIA_Pending_PO_Detail` | High | pending PO detail, partial PO detail, PO follow up, pending quantity |
| `ZIA_Current_Inventory_Snapshot` | High | current inventory, latest stock, current stock pressure, low stock, watch materials |
| `ZIA_Inventory_Daily_Trend` | High | inventory trend, daily inventory value, stock value trend |
| `ZIA_Theoretical_Demand_Daily` | High | daily theoretical demand, recipe demand daily, packaging demand daily, ingredient demand trend |
| `ZIA_Theoretical_Demand_Summary` | High | top ingredients, top packaging materials, theoretical demand summary, recipe demand summary |

### 5.2 Low Priority Existing Dashboard Tables

| Table | Priority | Why |
|---|---|---|
| Existing `FACT_*` tables | Low | They still drive dashboards, but Ask Zia should prefer the ZIA semantic layer. |
| Existing `SUM_*` tables | Low | They can confuse Ask Zia with old summary grains. |
| `DIM_*` tables | Low | Helpful as lookup context, but not primary answer tables. |

### 5.3 Exclude Or Low Priority Import/Event Tables

| Table group | Priority | Reason |
|---|---|---|
| `RAW_*` | Exclude if possible; otherwise Low | Raw feeds are import staging tables. They can contain duplicate refetches and confusing column names. |
| `STD_*` | Exclude if possible; otherwise Low | Standardization layer is for modelling, not final business answers. |
| `FACT_Event_Sales_Impact`, `SUM_Event_Impact`, `SUM_Event_Markers` | Exclude/Low | These caused Ask Zia to answer normal sales questions with event sales, baseline sales, and sales lift. |
| `FACT_Competitor_Price_Position`, `SUM_Competitor_Positioning` | Exclude/Low | Only train if competitor demo is active. |

Detailed ZIA table build order, synonyms, and expected answers are in:

```text
docs/zoho_ask_zia_query_table_sql/README.md
```

## 6. Column Training: Exact Values To Fill

Primary column training should be done on the `ZIA_*` tables using:

```text
docs/zoho_ask_zia_query_table_sql/README.md
```

The FACT/SUM column guidance below is fallback/reference only. Do not keep old FACT/SUM tables High priority after the `ZIA_*` tables are created.

For each table:

1. Expand the table in the left panel.
2. Click the column.
3. Paste the synonyms exactly.
4. Set the default function.
5. Set the priority.
6. Save.

### 6.1 `FACT_Outlet_Daily_Health`

Use this table for the Executive Outlet Health dashboard.

Final visuals covered:

```text
KPI row
Outlet Performance Summary
Daily Sales Trend By Outlet
Sales Purchase Receipt Comparison
Outlet Sales Ranking
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `activity_date` | date, day, business date, sales date, activity date, report date | Actual / Date | 100 |
| `outlet_name` | outlet, cafe, store, branch, location, restaurant | Actual / Group by | 100 |
| `market_area` | market, area, locality, location area | Actual / Group by | 80 |
| `net_sales` | revenue, net sales, sales revenue, top line, turnover, outlet sales | Sum | 100 |
| `sold_qty` | menu units sold, units sold, menu quantity, customer items sold | Sum | 65 |
| `po_value` | procurement spend, PO value, purchase spend, PO raised, ordered value, purchase order value | Sum | 95 |
| `receipt_value` | receipt booked, received value, GRN value, entry value, goods received value | Sum | 90 |
| `inventory_value` | inventory value, stock value, closing inventory, closing stock value | Average | 85 |
| `low_stock_item_count` | inventory pressure, low stock item-days, stock pressure, pressure item days, watch item days | Sum | 80 |
| `event_count` | event days, event markers, calendar events, promotion days | Sum | 50 |
| `health_note` | outlet status, health status, operating note, performance note | Actual | 70 |

Aggregate formulas to create or confirm:

| Formula name | Formula expression | Synonyms |
|---|---|---|
| `AF_Average_Daily_Revenue` | `SUM("net_sales") / DISTINCTCOUNT("activity_date")` | average daily sales, average daily revenue, revenue run rate, daily run rate |
| `AF_Purchase_To_Sales_Ratio` | `SUM("po_value") / SUM("net_sales") * 100` | purchase to sales ratio, procurement to sales, spend pressure, PO to sales |
| `AF_Revenue_Per_Avg_Inventory_Rupee` | `SUM("net_sales") / AVG("inventory_value")` | revenue per average inventory rupee, sales per inventory rupee, inventory productivity |

Do not set purchase-to-sales ratio as Sum. It must be an aggregate formula.

### 6.2 `FACT_Sales`

Use this table for date-sensitive Sales And Menu Intelligence.

Final visuals covered:

```text
KPI row
Daily Net Sales Trend
Category Revenue Mix
Top Items By Net Sales
Top Items By Quantity
Category Trend
Days Of Week HeatMap
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `sales_date` | date, sales date, day, business date | Actual / Date | 100 |
| `outlet_name` | outlet, cafe, store, branch, location | Actual / Group by | 100 |
| `market_area` | market, area, locality | Actual / Group by | 80 |
| `net_sale` | revenue, net sales, sales, menu revenue, item sales, sales value | Sum | 100 |
| `qty` | menu units, units sold, quantity sold, item quantity, volume | Sum | 80 |
| `category` | category, menu category, product category | Actual / Group by | 95 |
| `super_category` | super category, broad category, food beverage dessert | Actual / Group by | 80 |
| `item_name` | menu item, product, dish, drink, SKU name, item | Actual / Group by | 95 |
| `item_number` | item code, SKU, product code, menu code | Actual | 75 |
| `day_of_week_name` | day of week, weekday, week day, Monday Tuesday, weekday name, sales weekday | Actual / Group by | 95 |
| `day_of_week_sort` | weekday sort, day sort, weekday number, day number | Actual | 40 |
| `net_sale_per_qty` | realized price, average selling price, ASP, unit price realized | Average | 70 |

Aggregate formula to create or confirm:

| Formula name | Formula expression | Synonyms |
|---|---|---|
| `AF_Avg_Realized_Menu_Price` | `SUM("net_sale") / SUM("qty")` | average realized price, blended ASP, average selling price, average item price |

Important rule:

```text
"Top performing menu item" means rank by SUM(net_sale).
"Most sold item" means rank by SUM(qty).
```

### 6.3 `SUM_Menu_Item_Performance`

Use this table for full-period menu item comparison visuals.

Final visuals covered:

```text
Revenue Vs Quantity
Realized Price Vs Menu Rate
Top 5 Menu Winners
Menu Item Detail
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `outlet_name` | outlet, cafe, store, branch, location | Actual / Group by | 100 |
| `item_number` | item code, SKU, product code, menu code | Actual | 80 |
| `item_name` | menu item, product, dish, drink, item | Actual / Group by | 100 |
| `super_category` | super category, broad category | Actual / Group by | 80 |
| `category` | category, menu category, product category | Actual / Group by | 95 |
| `total_qty` | total units sold, menu units sold, total quantity, units sold | Sum | 85 |
| `total_net_sale` | total net sales, item revenue, menu item revenue, sales value | Sum | 100 |
| `avg_realized_unit_price` | realized price, average selling price, ASP, achieved price | Average | 90 |
| `menu_rate` | menu rate, listed rate, listed price, standard menu price | Average | 80 |
| `avg_price_index` | price index, realized price index, price realization index | Average | 75 |
| `price_position` | price position, premium, discounted, above menu, below menu | Actual | 70 |
| `performance_note` | performance note, item note, menu note | Actual | 70 |

Use this table for item detail lists and scatter/bubble charts. Use `FACT_Sales` when the user asks for a specific date range.

### 6.4 `FACT_Vendor_Spend`

Use this for Vendor And Procurement Analytics.

Final visuals covered:

```text
KPI row
Vendor PO Raised Share
Vendor Receipt Booked Share
Vendor Spend Trend
PO Status Value
PO VS Receipt Gap By Vendor
Vendor Material Concentration
Receipt Booking Trend
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `activity_date` | procurement date, PO or receipt date, transaction date, purchase date | Actual / Date | 95 |
| `outlet_name` | outlet, cafe, store, branch, location | Actual / Group by | 100 |
| `vendor_name` | vendor, supplier, seller, procurement partner | Actual / Group by | 100 |
| `item_name` | material, ingredient, procurement item, supply item, inventory item | Actual / Group by | 95 |
| `category_name` | material category, procurement category, ingredient category | Actual / Group by | 80 |
| `super_category_name` | material super category, procurement super category | Actual / Group by | 70 |
| `po_status` | PO status, order status, purchase status | Actual | 80 |
| `ordered_value` | PO raised value, ordered value, purchase order value, procurement raised, PO spend | Sum | 100 |
| `received_value` | receipt booked value, received value, GRN value, booked receipt, goods received value | Sum | 95 |
| `open_or_partial_po_count` | open PO count, partial PO count, pending PO count, follow-up count | Sum | 80 |

Aggregate formula to create or confirm:

| Formula name | Formula expression | Synonyms |
|---|---|---|
| `AF_PO_vs_Receipt_Value_Gap` | `SUM("ordered_value") - SUM("received_value")` | PO receipt gap, ordered vs received gap, value gap, pending value gap |

Important rule:

```text
PO Raised Value is the value of orders raised.
Receipt Booked Value is the value of received/booked goods.
Open or Partial PO Count is a status/count measure.
These three will not always move together.
```

### 6.5 `FACT_PO_Receipt_Comparison`

Use this for pending and partial PO operational detail.

Final visuals covered:

```text
Pending Quantity By Material
Pending Partial PO Detail
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `po_number` | PO number, purchase order number, order ID | Actual | 100 |
| `po_date` | PO date, order date, procurement date | Actual / Date | 100 |
| `expected_delivery_date` | due date, delivery date, expected delivery | Actual / Date | 90 |
| `outlet_name` | outlet, cafe, store, branch, location | Actual / Group by | 100 |
| `vendor_name` | vendor, supplier | Actual / Group by | 95 |
| `item_name` | material, ingredient, supply item | Actual / Group by | 90 |
| `po_status` | PO status, order status | Actual | 95 |
| `pending_or_partial_flag` | pending flag, open flag, follow-up flag | Sum | 95 |
| `remaining_qty` | remaining quantity, balance quantity, open quantity, pending quantity | Sum | 90 |
| `matched_received_qty` | received quantity, matched receipt quantity | Sum | 85 |
| `unmatched_order_qty` | unmatched quantity, unreceived quantity | Sum | 85 |

### 6.6 `SUM_Inventory_Risk`

Use this for dashboard Zia Insights or fallback inventory training only. For typed Ask Zia questions after the new semantic layer is built, use `ZIA_Current_Inventory_Snapshot` instead.

Final visuals covered:

```text
Inventory Value KPI
Low Stock Item Count KPI
Current Watch Material Count KPI
Top Inventory Value Items By Category
Current Stock Pressure Band Chart
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `outlet_name` | outlet, cafe, store, branch | Actual / Group by | 100 |
| `latest_inventory_date` | latest date, stock date, inventory date, current date | Actual / Date | 95 |
| `item_name` | inventory item, ingredient, material, stock item | Actual / Group by | 100 |
| `category_name` | inventory category, material category, ingredient category | Actual / Group by | 80 |
| `super_category_name` | inventory super category, material super category | Actual / Group by | 70 |
| `total_amt` | current inventory value, latest stock value, stock value, inventory value | Sum | 95 |
| `total_qty` | current stock quantity, latest stock qty, stock on hand, inventory quantity | Sum | 90 |
| `low_stock_flag` | low stock count, current low stock, low stock item count | Sum | 95 |
| `inventory_pressure_band` | pressure band, stock band, risk band, watch material, current watch material, stock pressure | Actual | 95 |
| `risk_note` | stock note, inventory note, risk note | Actual | 70 |

Important rule:

```text
For typed Ask Zia "current inventory value" questions, use ZIA_Current_Inventory_Snapshot.
For dashboard Zia Insights on saved inventory charts, SUM_Inventory_Risk can still explain the existing dashboard visuals.
Do not use FACT_Inventory_Closing unless the user asks for a date trend.
```

### 6.7 `FACT_Inventory_Closing`

Use this for daily inventory trend over time.

Final visuals covered:

```text
Inventory Trend
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `inventory_date` | inventory date, stock date, closing date, date | Actual / Date | 100 |
| `outlet_name` | outlet, cafe, store, branch | Actual / Group by | 100 |
| `item_name` | inventory item, ingredient, material, stock item | Actual / Group by | 95 |
| `category_name` | inventory category, material category, ingredient category | Actual / Group by | 85 |
| `super_category_name` | inventory super category, material super category | Actual / Group by | 75 |
| `total_amt` | inventory value, stock value, closing value, daily inventory value | Sum | 95 |
| `qty` or `total_qty` | stock quantity, inventory quantity, closing quantity | Sum | 85 |

If the visual is a daily trend, using Sum across `inventory_date` is fine because each date is a snapshot point. If the visual is a current KPI, use `SUM_Inventory_Risk`.

### 6.8 `FACT_Theoretical_Consumption`

Use this for recipe and packaging demand generated from menu sales.

Final visuals covered:

```text
Theoretical Ingredient Demand from Menu Sales KPI
Theoretical Demand Trend (Packaging)
Top Theoretical Ingredients (Recipe)
Top Theoretical Materials (Packaging)
Theoretical Demand Trend (Recipe)
```

| Column | Synonyms to paste | Default function | Priority |
|---|---|---|---:|
| `sales_date` | date, sales date, consumption date | Actual / Date | 90 |
| `outlet_name` | outlet, cafe, store, branch | Actual / Group by | 100 |
| `menu_item_name` | menu item, recipe, product, sold item | Actual / Group by | 85 |
| `ingredient_name` | ingredient, material, raw material, supply item | Actual / Group by | 100 |
| `demand_component_type` | recipe or packaging, demand type, component type, packaging component, recipe ingredient | Actual / Group by | 100 |
| `item_tab_type` | BOM type, item tab type, recipe type, base recipe | Actual | 60 |
| `theoretical_ingredient_qty` | ingredient demand, theoretical consumption, recipe demand, material consumption, theoretical demand | Sum | 100 |

Important rule:

```text
Recipe demand and packaging demand are both theoretical demand.
Use demand_component_type to separate them.
```

## 7. Data Synonyms: Exact Values To Add

Data synonyms are for exact text values.

In Zoho:

1. Open `Manage Synonyms`.
2. Expand the table.
3. Click the text column, for example `outlet_name`.
4. Open the data/value synonym area if Zoho shows it.
5. Select one actual value.
6. Add comma-separated synonyms for that value.
7. Save.
8. Repeat on the same column in other high-priority tables if Zoho does not reuse value synonyms automatically.

### 7.1 Outlet Data Synonyms

Add these for `outlet_name` in:

```text
FACT_Outlet_Daily_Health
FACT_Sales
SUM_Menu_Item_Performance
FACT_Vendor_Spend
FACT_PO_Receipt_Comparison
SUM_Inventory_Risk
FACT_Inventory_Closing
FACT_Theoretical_Consumption
```

| Actual value | Synonyms to paste |
|---|---|
| `ABNAH Cafe Connaught Place` | CP, Connaught, Connaught Place, office outlet, corporate outlet, central Delhi cafe |
| `ABNAH Cafe Hauz Khas` | HK, Hauz, Hauz Khas, student outlet, youth outlet, college cafe |
| `ABNAH Cafe Saket Premium` | Saket, Saket Premium, mall outlet, premium outlet, leisure outlet |

### 7.2 Vendor Data Synonyms

Add these for `vendor_name` in:

```text
FACT_Vendor_Spend
FACT_Purchase_Order
FACT_PO_Receipt_Comparison
FACT_Entry_Receipt
```

| Actual value | Synonyms to paste |
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

### 7.3 PO Status Data Synonyms

Add these for `po_status` in:

```text
FACT_Vendor_Spend
FACT_Purchase_Order
FACT_PO_Receipt_Comparison
```

| Actual value | Synonyms to paste |
|---|---|
| `Closed` | completed, fulfilled, received |
| `Partially Received` | partial, partly received, incomplete |
| `Pending` | open, not received, awaiting delivery |
| `Cancelled` | canceled, void, dropped |

### 7.4 Menu Category Data Synonyms

Add these for `category` in:

```text
FACT_Sales
SUM_Menu_Item_Performance
```

| Actual value | Synonyms to paste |
|---|---|
| `Coffee Classics` | hot coffee, classic coffee, regular coffee |
| `Signature Coffee` | premium coffee, specialty coffee, signature drinks |
| `Cold Coffee` | cold coffee, iced coffee |
| `Cold Brew` | cold brew coffee |
| `Tea` | chai, tea drinks |
| `Desserts` | dessert, sweets, cakes |
| `Baked Goods` | bakery, croissants, baked items |
| `Sandwiches` | sandwiches, lunch sandwiches |
| `Wraps` | wraps, rolls |
| `Shake` | shakes, milkshakes |

### 7.5 Demand Type Data Synonyms

Add these for `demand_component_type` in:

```text
FACT_Theoretical_Consumption
```

| Actual value | Synonyms to paste |
|---|---|
| `Recipe Ingredient` | recipe, ingredient, raw material demand, recipe demand |
| `Packaging Consumable` | packaging, consumable, cups, napkin, lid, straw, packaging demand |

### 7.6 Weekday Data Synonyms

If `day_of_week_name` values are stored as text, add obvious short forms:

| Actual value | Synonyms to paste |
|---|---|
| `Monday` | Mon |
| `Tuesday` | Tue, Tues |
| `Wednesday` | Wed |
| `Thursday` | Thu, Thur, Thurs |
| `Friday` | Fri |
| `Saturday` | Sat |
| `Sunday` | Sun |

## 8. Zia Insights Setup For Final Dashboard Stories

Ask Zia and Zia Insights are different:

```text
Ask Zia = typed natural-language questions.
Zia Insights = automatic explanation of a saved chart/dashboard.
```

This section is only for the `Zia Insights` panel inside each dashboard's settings. It explains which existing chart reports Zoho should summarize when you click `Zia Insights` on the dashboard.

Do not use this section to set Ask Zia table priority. For natural-language Ask Zia questions, keep the `ZIA_*` query tables from `docs/zoho_ask_zia_query_table_sql` as High priority, and keep the older `FACT_*` / `SUM_*` dashboard source tables Low.

There are two places to configure Zia Insights:

```text
Dashboard Settings panel
Zia Insights -> Customize panel
```

Your Zoho screen only shows charts/tables in `Explain By Reports`. KPI widgets do not appear there. That is okay. Do not try to force KPI widgets into Zia Insights. KPI cards are handled through Ask Zia table/column synonyms and the question bank.

### 8.1 Dashboard Settings Panel

Open the dashboard and click:

```text
Settings icon -> Settings panel
```

Fill the visible settings like this:

| Setting in Zoho | What to set | Why |
|---|---|---|
| `Enable Reports to act as Filters` | OFF for now | Dashboard already has user filters. Chart-click filtering can make testing confusing. |
| `Change Date function based on Time Slicer` | OFF for now | We are using explicit dashboard date filters. |
| `Show Sort Menu in views` | ON | Useful while validating tables and pivots. |
| `Show/Hide Columns option in table/query table/tabular views` | ON | Useful for checking underlying fields during demo prep. |
| `Show Contextual Options Menu, on Hover` | ON | Keeps chart controls accessible. |
| `Smart Align Charts` | ON | Keeps dashboard layout clean. |
| `Fit the Pivot/Summary view to card width` | ON | Important for the weekday heatmap and matrix/table visuals. |
| `Sync pan and zoom movements across maps` | Leave as default | Not relevant unless using map visuals. |
| `Allow Export in reports` | ON | Useful for demo validation and review. |
| `Enable Zia Insights for dashboard` | ON | Required for dashboard-level insight story. |
| `Enable Zia Insights for reports` | ON | Required for chart-level insight story. |

Click `Apply`.

### 8.2 Zia Insights Customize Panel

Open:

```text
Zia Insights -> Customize
```

Use these sections:

```text
Explain By Reports
Insight Categories
Key Driver Analysis (Diagnostics)
```

#### 8.2.1 Explain By Reports

Select only the final charts/tables for that dashboard. Do not worry if KPI widgets are missing from the list.

For Sales And Menu Intelligence, select exactly these reports:

```text
Daily Net Sales Trend
Category Revenue Mix
Top Items By Net Sales
Top Items By Quantity
Revenue Vs Quantity
Realized Price Vs Menu Rate
Category Trend
Days Of Week HeatMap
Top 5 Menu Winners
Menu Item Detail
```

#### 8.2.2 Insight Categories

Use this default setup for all four final dashboards:

| Insight category | Setting |
|---|---|
| `Contribution Analysis` | ON |
| `Total Contribution` | ON |
| `Extreme Value (Min and Max)` | ON |
| `Top Contribution` | ON |
| `Exceeding Threshold` | OFF unless a real business threshold is defined |
| `Value in Categories/Dimensions` | ON |
| `Skewness Analysis` | ON |
| `Time series insights` | ON for trend charts, optional for static tables |
| `Time series insights (Diagnosable)` | ON for daily trend charts |
| `Comparison between Dimensions` | ON |
| `Analysis of Measures` | ON |

Why `Exceeding Threshold` is OFF by default:

```text
Without a real threshold, Zia may say a value exceeded a threshold without business meaning.
Turn it ON only after defining threshold logic like low stock, high PO gap, or high purchase-to-sales pressure.
```

#### 8.2.3 Key Driver Analysis (Diagnostics)

Use this setup unless a dashboard-specific section below says otherwise:

| Zoho field | Value |
|---|---|
| `Show Key Drivers for the Diagnosable Insights` | ON |
| `Show Top` | `5` Drivers |
| `Model Used for Diagnosis` | `Auto` |

In `Factors for Analysis`, keep business dimensions and supporting measures. Remove technical IDs and row keys.

Do not use these as factors:

```text
row_id
uid
raw table columns
item_number unless no item_name exists
net_sale itself when net_sale is the selected measure
ordered_value itself when ordered_value is the selected measure
total_amt itself when total_amt is the selected measure
```

### 8.3 Executive Outlet Health

| Final visual | Dashboard source table | Insight focus, not a Zoho field | Explain by columns | Key driver target |
|---|---|---|---|---|
| Outlet Performance Summary | `FACT_Outlet_Daily_Health` | High | `outlet_name`, `net_sales`, `po_value`, `receipt_value`, `inventory_value`, `low_stock_item_count`, `health_note` | `net_sales` |
| Daily Sales Trend By Outlet | `FACT_Outlet_Daily_Health` | High | `activity_date`, `outlet_name`, `net_sales`, `event_count`, `low_stock_item_count`, `po_value` | `net_sales` |
| Sales Purchase Receipt Comparison | `FACT_Outlet_Daily_Health` | High | `outlet_name`, `net_sales`, `po_value`, `receipt_value` | `net_sales` |
| Outlet Sales Ranking | `FACT_Outlet_Daily_Health` | Medium | `outlet_name`, `net_sales`, `po_value`, `receipt_value`, `low_stock_item_count` | `net_sales` |

`Explain By Reports` selection:

```text
Outlet Performance Summary
Daily Sales Trend By Outlet
Sales Purchase Receipt Comparison
Outlet Sales Ranking
```

`Key Driver Analysis (Diagnostics)`:

| Zoho field | Value |
|---|---|
| `Select Measure` | `net_sales (Sum)` |
| `Show Top` | `5` Drivers |
| `Model Used for Diagnosis` | `Auto` |

`Factors for Analysis`:

```text
outlet_name (Actual): All
activity_date (Actual): All
po_value (Sum)
receipt_value (Sum)
inventory_value (Average)
low_stock_item_count (Sum)
event_count (Sum)
```

What Zia should explain:

```text
Which outlet leads revenue.
Whether purchase spend pressure is high relative to sales.
Whether receipt booked value is behind PO raised value.
Whether low-stock/watch item pressure is concentrated in one outlet.
```

### 8.4 Sales And Menu Intelligence

| Final visual | Dashboard source table | Insight focus, not a Zoho field | Explain by columns | Key driver target |
|---|---|---|---|---|
| Daily Net Sales Trend | `FACT_Sales` | High | `sales_date`, `outlet_name`, `category`, `super_category`, `net_sale`, `qty` | `net_sale` |
| Category Revenue Mix | `FACT_Sales` | High | `category`, `super_category`, `outlet_name`, `net_sale`, `qty` | `net_sale` |
| Top Items By Net Sales | `FACT_Sales` | Medium | `item_name`, `category`, `super_category`, `outlet_name`, `net_sale`, `qty` | `net_sale` |
| Top Items By Quantity | `FACT_Sales` | Medium | `item_name`, `category`, `super_category`, `outlet_name`, `qty`, `net_sale` | `qty` |
| Revenue Vs Quantity | `SUM_Menu_Item_Performance` | High | `item_name`, `category`, `total_net_sale`, `total_qty`, `avg_realized_unit_price` | `total_net_sale` |
| Realized Price Vs Menu Rate | `SUM_Menu_Item_Performance` | High | `item_name`, `category`, `menu_rate`, `avg_realized_unit_price`, `avg_price_index`, `price_position` | `avg_realized_unit_price` |
| Category Trend | `FACT_Sales` | High | `sales_date`, `category`, `super_category`, `outlet_name`, `net_sale` | `net_sale` |
| Days Of Week HeatMap | `FACT_Sales` plus `DIM_Date` lookup | High | `day_of_week_name`, `day_of_week_sort`, `category`, `outlet_name`, `net_sale` | `net_sale` |
| Top 5 Menu Winners | `SUM_Menu_Item_Performance` | Medium | `item_name`, `category`, `total_net_sale`, `total_qty`, `avg_realized_unit_price`, `performance_note` | `total_net_sale` |
| Menu Item Detail | `SUM_Menu_Item_Performance` | Medium | `item_number`, `item_name`, `category`, `super_category`, `total_net_sale`, `total_qty`, `avg_realized_unit_price`, `performance_note` | `total_net_sale` |

`Explain By Reports` selection:

```text
Daily Net Sales Trend
Category Revenue Mix
Top Items By Net Sales
Top Items By Quantity
Revenue Vs Quantity
Realized Price Vs Menu Rate
Category Trend
Days Of Week HeatMap
Top 5 Menu Winners
Menu Item Detail
```

`Key Driver Analysis (Diagnostics)` for the Sales/Menu dashboard:

| Zoho field | Value |
|---|---|
| `Select Measure` | `net_sale (Sum)` |
| `Show Top` | `5` Drivers |
| `Model Used for Diagnosis` | `Auto` |

`Factors for Analysis`:

```text
category (Actual): All
super_category (Actual): All
item_name (Actual): All
outlet_name (Actual): All
day_of_week_name (Actual): All
qty (Sum)
```

If `day_of_week_name` is not available in the factor list, use:

```text
sales_date (Actual): All
```

but `day_of_week_name` is better for the weekday heatmap story.

What Zia should explain:

```text
Which categories drive revenue.
Which items drive revenue versus quantity.
Which items have high units but weaker value.
Which items are priced above or below their menu rate.
Which weekdays are stronger inside the selected date range.
```

Days Of Week HeatMap rule:

```text
Rows should use day_of_week_name.
Sorting should use day_of_week_sort.
Ask Zia should answer by weekday names, not numbers 1 to 7.
When a 10-day date range is selected, it should aggregate only those 10 dates into their weekday buckets.
```

### 8.5 Vendor And Procurement Analytics

| Final visual | Dashboard source table | Insight focus, not a Zoho field | Explain by columns | Key driver target |
|---|---|---|---|---|
| Vendor PO Raised Share | `FACT_Vendor_Spend` | High | `vendor_name`, `outlet_name`, `ordered_value`, `item_name`, `category_name` | `ordered_value` |
| Vendor Receipt Booked Share | `FACT_Vendor_Spend` | High | `vendor_name`, `outlet_name`, `received_value`, `item_name`, `category_name` | `received_value` |
| Vendor Spend Trend | `FACT_Vendor_Spend` | High | `activity_date`, `vendor_name`, `outlet_name`, `ordered_value`, `received_value` | `ordered_value` |
| PO Status Value | `FACT_Vendor_Spend` or `FACT_Purchase_Order` | Medium | `po_status`, `vendor_name`, `outlet_name`, `ordered_value` | `ordered_value` |
| PO VS Receipt Gap By Vendor | `FACT_Vendor_Spend` | High | `vendor_name`, `outlet_name`, `ordered_value`, `received_value`, `AF_PO_vs_Receipt_Value_Gap` | `AF_PO_vs_Receipt_Value_Gap` |
| Pending Quantity By Material | `FACT_PO_Receipt_Comparison` | Medium | `item_name`, `vendor_name`, `outlet_name`, `remaining_qty`, `unmatched_order_qty`, `po_status` | `remaining_qty` |
| Vendor Material Concentration | `FACT_Vendor_Spend` | Medium | `vendor_name`, `item_name`, `category_name`, `ordered_value`, `received_value` | `ordered_value` |
| Pending Partial PO Detail | `FACT_PO_Receipt_Comparison` | Medium | `po_number`, `po_date`, `expected_delivery_date`, `vendor_name`, `item_name`, `remaining_qty`, `po_status` | `remaining_qty` |
| Receipt Booking Trend | `FACT_Vendor_Spend` | High | `activity_date`, `vendor_name`, `outlet_name`, `received_value`, `item_name` | `received_value` |

`Explain By Reports` selection:

```text
Vendor PO Raised Share
Vendor Receipt Booked Share
Vendor Spend Trend
PO Status Value
PO VS Receipt Gap By Vendor
Pending Quantity By Material
Vendor Material Concentration
Pending Partial PO Detail
Receipt Booking Trend
```

`Key Driver Analysis (Diagnostics)` for the dashboard:

| Zoho field | Value |
|---|---|
| `Select Measure` | `ordered_value (Sum)` |
| `Show Top` | `5` Drivers |
| `Model Used for Diagnosis` | `Auto` |

`Factors for Analysis`:

```text
vendor_name (Actual): All
outlet_name (Actual): All
item_name (Actual): All
category_name (Actual): All
po_status (Actual): All
received_value (Sum)
open_or_partial_po_count (Sum)
```

For `Receipt Booking Trend`, if Zoho lets you set report-specific diagnostics, use:

```text
Select Measure: received_value (Sum)
Factors: vendor_name, outlet_name, item_name, category_name
```

For `Pending Quantity By Material` and `Pending Partial PO Detail`, if Zoho lets you set report-specific diagnostics, use:

```text
Select Measure: remaining_qty (Sum)
Factors: vendor_name, outlet_name, item_name, po_status, expected_delivery_date
```

What Zia should explain:

```text
Which vendors dominate PO value.
Which vendors dominate receipt booking.
Where PO raised value and receipt booked value are different.
Which materials still have pending quantity.
Which vendor-material combinations are concentrated.
```

### 8.6 Inventory And Consumption Intelligence

| Final visual | Dashboard source table | Insight focus, not a Zoho field | Explain by columns | Key driver target |
|---|---|---|---|---|
| Top Inventory Value Items By Category | `SUM_Inventory_Risk` | High | `outlet_name`, `item_name`, `category_name`, `super_category_name`, `total_amt`, `total_qty` | `total_amt` |
| Current Stock Pressure Band Chart | `SUM_Inventory_Risk` | Medium | `inventory_pressure_band`, `outlet_name`, `item_name`, `total_qty`, `total_amt`, `low_stock_flag` | `low_stock_flag` |
| Inventory Trend | `FACT_Inventory_Closing` | High | `inventory_date`, `outlet_name`, `category_name`, `super_category_name`, `total_amt` | `total_amt` |
| Theoretical Demand Trend (Packaging) | `FACT_Theoretical_Consumption` | High | `sales_date`, `outlet_name`, `ingredient_name`, `demand_component_type`, `theoretical_ingredient_qty` | `theoretical_ingredient_qty` |
| Top Theoretical Ingredients (Recipe) | `FACT_Theoretical_Consumption` | High | `ingredient_name`, `menu_item_name`, `outlet_name`, `demand_component_type`, `theoretical_ingredient_qty` | `theoretical_ingredient_qty` |
| Top Theoretical Materials (Packaging) | `FACT_Theoretical_Consumption` | High | `ingredient_name`, `outlet_name`, `demand_component_type`, `theoretical_ingredient_qty` | `theoretical_ingredient_qty` |
| Theoretical Demand Trend (Recipe) | `FACT_Theoretical_Consumption` | High | `sales_date`, `outlet_name`, `ingredient_name`, `menu_item_name`, `demand_component_type`, `theoretical_ingredient_qty` | `theoretical_ingredient_qty` |

`Explain By Reports` selection:

```text
Top Inventory Value Items By Category
Current Stock Pressure Band Chart
Inventory Trend
Theoretical Demand Trend (Packaging)
Top Theoretical Ingredients (Recipe)
Top Theoretical Materials (Packaging)
Theoretical Demand Trend (Recipe)
```

`Key Driver Analysis (Diagnostics)` for the stock/current inventory reports:

| Zoho field | Value |
|---|---|
| `Select Measure` | `total_amt (Sum)` |
| `Show Top` | `5` Drivers |
| `Model Used for Diagnosis` | `Auto` |

`Factors for Analysis`:

```text
outlet_name (Actual): All
item_name (Actual): All
category_name (Actual): All
super_category_name (Actual): All
inventory_pressure_band (Actual): All
total_qty (Sum)
low_stock_flag (Sum)
```

For theoretical consumption reports, if Zoho lets you set report-specific diagnostics, use:

```text
Select Measure: theoretical_ingredient_qty (Sum)
Factors: demand_component_type, ingredient_name, menu_item_name, outlet_name, sales_date
```

Filters for theoretical charts:

| Chart | Required chart filter |
|---|---|
| Theoretical Demand Trend (Packaging) | `demand_component_type = Packaging Consumable` |
| Top Theoretical Materials (Packaging) | `demand_component_type = Packaging Consumable` |
| Theoretical Demand Trend (Recipe) | `demand_component_type = Recipe Ingredient` |
| Top Theoretical Ingredients (Recipe) | `demand_component_type = Recipe Ingredient` |

What Zia should explain:

```text
Current inventory value is a latest-stock snapshot.
Inventory trend is daily closing value over time.
Theoretical demand is not physical stock; it is recipe/packaging demand calculated from menu sales.
Current watch material count is based on the latest stock pressure band.
```

## 9. Baseline Question Bank For Ask Zia

After synonyms are configured:

1. Ask the question.
2. Check which table Zia used.
3. Check the value.
4. If the table is wrong, adjust table priority.
5. If the metric is wrong, adjust column synonyms/default function.
6. If the outlet/vendor/category is misunderstood, add data synonyms.

### 9.1 Executive Outlet Health Questions

| Ask Zia question | Expected source | What Zia should answer |
|---|---|---|
| Which outlet had the highest net sales in January 2026? | `ZIA_Executive_Outlet_Month` | Saket Premium, about `6.92L` in Month 1 baseline. |
| Show net sales by outlet for January 2026 | `ZIA_Executive_Outlet_Month` | Saket about `6.92L`, Hauz Khas about `6.27L`, Connaught about `6.26L`. |
| What is average daily revenue for all outlets in January 2026? | `ZIA_Executive_Outlet_Month` | About `62.75K`. |
| What is purchase to sales ratio for Hauz Khas? | `ZIA_Executive_Outlet_Month` | Hauz Khas should be highest in the Month 1 story. |
| Which outlet has the highest procurement pressure? | `ZIA_Executive_Outlet_Month` | The outlet with highest PO value relative to sales. |
| Show sales, PO raised value, and receipt booked value by outlet | `ZIA_Executive_Outlet_Month` | A comparison by outlet using `net_sales`, `po_raised_value`, and `receipt_booked_value`. |
| Which outlet has the most low stock pressure? | `ZIA_Executive_Outlet_Month` | Rank by `inventory_pressure_item_days`. |

### 9.2 Sales And Menu Intelligence Questions

| Ask Zia question | Expected source | What Zia should answer |
|---|---|---|
| Top 5 menu items by net sales for Connaught Place in January 2026 | `ZIA_Sales_Menu_Daily_Item` | Top items ranked by `SUM(net_sales)`, not quantity. |
| Top 5 menu items by quantity for Hauz Khas in January 2026 | `ZIA_Sales_Menu_Daily_Item` | Top items ranked by `SUM(menu_units_sold)`. |
| Which category has highest revenue for Saket Premium? | `ZIA_Sales_Menu_Daily_Category` | Category ranking by `SUM(net_sales)`. |
| Show category revenue mix for Connaught Place | `ZIA_Sales_Menu_Daily_Category` | Revenue by `category`, filtered to Connaught Place. |
| Which items have high quantity but lower revenue? | `ZIA_Sales_Menu_Item_Summary` | Items where `menu_units_sold` is high relative to `net_sales` or average realized price. |
| Show revenue vs quantity for menu items | `ZIA_Sales_Menu_Item_Summary` | Item-level scatter/table using `net_sales` and `menu_units_sold`. |
| Which items are selling below menu rate? | `ZIA_Sales_Menu_Item_Summary` | Items with weaker realized price versus menu rate. |
| Which weekday has the highest sales for Hauz Khas? | `ZIA_Sales_Weekday_Category` | Weekday ranked by `SUM(net_sales)` using `day_of_week_name`. |
| Show category trend for Coffee Classics by date | `ZIA_Sales_Menu_Daily_Category` | Daily trend filtered to category `Coffee Classics`. |
| Show menu item detail for Mocha Medium | `ZIA_Sales_Menu_Item_Summary` | Item detail row with revenue, units, realized price, and performance note. |

### 9.3 Vendor And Procurement Questions

| Ask Zia question | Expected source | What Zia should answer |
|---|---|---|
| Which vendor has the highest PO raised value for Hauz Khas? | `ZIA_Procurement_Monthly_Vendor` | Vendor ranked by `SUM(po_raised_value)`. |
| Which vendor has highest receipt booked value for Connaught Place? | `ZIA_Procurement_Monthly_Vendor` | Vendor ranked by `SUM(receipt_booked_value)`. |
| What is PO vs receipt gap by vendor? | `ZIA_Procurement_Monthly_Vendor` | `SUM(po_receipt_gap_value)` by vendor. |
| Show PO status value by outlet | `ZIA_Procurement_Daily_Vendor_Material` | PO value grouped by `po_status` and outlet. |
| Which materials have the highest pending quantity? | `ZIA_Pending_PO_Detail` | Material ranking by `remaining_qty` or `unmatched_order_qty`. |
| Show pending partial PO detail for PackPro Disposables | `ZIA_Pending_PO_Detail` | PO-level rows filtered to vendor and pending/partial status. |
| Which vendor-material combinations dominate spend? | `ZIA_Procurement_Daily_Vendor_Material` | Matrix/table using `vendor_name`, `material_name`, and `po_raised_value`. |
| Show receipt booking trend by vendor | `ZIA_Procurement_Daily_Vendor_Material` | Date trend of `receipt_booked_value` by vendor. |
| Why can PO raised value be higher than receipt booked value while open PO count is zero? | `ZIA_Procurement_Monthly_Vendor` / `ZIA_Pending_PO_Detail` | Because value gap and open/partial status count are different business measures. |

### 9.4 Inventory And Consumption Questions

| Ask Zia question | Expected source | What Zia should answer |
|---|---|---|
| What is current inventory value by outlet? | `ZIA_Current_Inventory_Snapshot` | Latest stock value by outlet. |
| Which outlet has the most current low stock items? | `ZIA_Current_Inventory_Snapshot` | Rank by `SUM(low_stock_flag)`. |
| What is current watch material count? | `ZIA_Current_Inventory_Snapshot` | Count materials using `SUM(watch_material_flag)`. |
| Which inventory category has the highest value? | `ZIA_Current_Inventory_Snapshot` | Category ranked by `SUM(current_inventory_value)`. |
| Show top inventory value items by category for Hauz Khas | `ZIA_Current_Inventory_Snapshot` | Item/category ranking filtered to Hauz Khas. |
| Show inventory trend for Dairy category | `ZIA_Inventory_Daily_Trend` | Daily trend of `SUM(inventory_value)` filtered to Dairy. |
| Which recipe ingredients have highest theoretical demand? | `ZIA_Theoretical_Demand_Summary` | Filter `demand_component_type = Recipe Ingredient`, rank by theoretical quantity. |
| Which packaging materials have highest theoretical demand? | `ZIA_Theoretical_Demand_Summary` | Filter `demand_component_type = Packaging Consumable`, rank by theoretical quantity. |
| Show theoretical recipe demand trend for Milk | `ZIA_Theoretical_Demand_Daily` | Daily demand trend filtered to Milk and recipe component type. |
| Show theoretical packaging demand trend for Napkin | `ZIA_Theoretical_Demand_Daily` | Daily demand trend filtered to Napkin and packaging component type. |

### 9.5 Optional Event/Competitor Questions

Use these only if optional Event/Competitor pages are retained and trained.

| Ask Zia question | Expected source | Required caveat |
|---|---|---|
| What was the sales lift from Coffee Subscription Launch? | `SUM_Event_Impact` | Event data shows association, not audited causality. |
| Which event had highest sales lift? | `SUM_Event_Impact` | Use lift and confidence together. |
| Which competitor category has the highest price index? | `SUM_Competitor_Positioning` | Competitor pricing is market context, not proof of sales cause. |

## 10. Extra Questions Ask Zia Can Answer Beyond Dashboards

These questions show why Ask Zia is useful even after dashboards are built.

### 10.1 Cross-Filtered Menu Ranking

Ask:

```text
Show top 10 menu items by net sales for Hauz Khas after 15 Jan 2026
```

Expected:

```text
ZIA_Sales_Menu_Daily_Item
Rows = menu_item_name
Measure = SUM(net_sales)
Filters = outlet_name = Hauz Khas, business_date after 15 Jan 2026
Sort = descending by SUM(net_sales)
```

Business value:

```text
The dashboard may show a fixed top-items chart, but Zia can generate any outlet/date-specific ranking.
```

### 10.2 Revenue Versus Quantity Interpretation

Ask:

```text
Which items sell many units but generate weaker revenue?
```

Expected:

```text
ZIA_Sales_Menu_Item_Summary
Compare menu_units_sold, net_sales, and average_realized_unit_price.
```

Business value:

```text
This helps separate volume drivers from value drivers.
```

### 10.3 PO And Receipt Gap Explanation

Ask:

```text
Which vendors have high PO receipt gap?
```

Expected:

```text
ZIA_Procurement_Monthly_Vendor
Use po_receipt_gap_value.
```

Business value:

```text
This shows where ordering commitment is ahead of goods receipt booking.
```

### 10.4 Pending PO Operational Follow-Up

Ask:

```text
Which pending POs need follow-up this week?
```

Expected:

```text
FACT_PO_Receipt_Comparison
Use pending_or_partial_flag, expected_delivery_date, vendor_name, item_name, remaining_qty.
```

Business value:

```text
This turns a chart into an operational follow-up list.
```

### 10.5 Demand-To-Stock Thinking

Ask:

```text
Which high theoretical demand ingredients are currently low stock?
```

Expected:

```text
ZIA_Theoretical_Demand_Summary + ZIA_Current_Inventory_Snapshot
```

If Zia cannot join it cleanly, build a dedicated combined query table later. The correct answer needs both demand pressure and latest stock pressure.

### 10.6 Weekday Business Pattern

Ask:

```text
Which weekday has the highest sales for Coffee Classics in Saket Premium?
```

Expected:

```text
ZIA_Sales_Weekday_Category
Rows = day_of_week_name
Measure = SUM(net_sales)
Filters = category = Coffee Classics, outlet_name = Saket Premium
Sort = descending by SUM(net_sales)
```

Business value:

```text
This gives demand pattern by weekday without manually rebuilding the heatmap.
```

## 11. Demo Script For Ask Zia

Use this exact order in the demo.

### 11.1 Executive

Ask:

```text
Which outlet had highest net sales in January 2026?
```

Expected business answer:

```text
Saket Premium is the revenue leader in the Month 1 baseline.
```

Then ask:

```text
Which outlet has the highest purchase to sales ratio?
```

Expected business answer:

```text
The answer should rank outlets by PO value relative to net sales. This shows procurement pressure, not profit.
```

### 11.2 Sales And Menu

Ask:

```text
Top 5 menu items by net sales for Connaught Place in January 2026
```

Expected business answer:

```text
The answer should rank menu items by revenue, not by quantity.
```

Then ask:

```text
Which weekday has highest sales for Connaught Place?
```

Expected business answer:

```text
The answer should use weekday names and aggregate net sales across the selected date range.
```

Then ask:

```text
Which items sell high quantity but lower revenue?
```

Expected business answer:

```text
Zia should compare units, revenue, and realized price to separate volume winners from value winners.
```

### 11.3 Vendor And Procurement

Ask:

```text
Which vendor has highest PO raised value for Hauz Khas?
```

Expected business answer:

```text
Vendor ranked by PO raised value.
```

Then ask:

```text
Which materials have the highest pending quantity?
```

Expected business answer:

```text
Material-level operational list from the PO receipt comparison table.
```

Then ask:

```text
Why can PO raised be higher than receipt booked while open PO count is zero?
```

Expected business answer:

```text
PO raised value, receipt booked value, and open/partial PO count measure different things. Value gap is financial/timing; open count is status/count.
```

### 11.4 Inventory And Consumption

Ask:

```text
What is current inventory value by outlet?
```

Expected business answer:

```text
Use ZIA_Current_Inventory_Snapshot as the latest snapshot, not daily inventory summed across dates.
```

Then ask:

```text
Which packaging materials have highest theoretical demand?
```

Expected business answer:

```text
Use ZIA_Theoretical_Demand_Summary filtered to Packaging Consumable.
```

Then ask:

```text
Which recipe ingredients have highest theoretical demand?
```

Expected business answer:

```text
Use ZIA_Theoretical_Demand_Summary filtered to Recipe Ingredient.
```

## 12. Common Failures And Fixes

| Failure | Cause | Fix |
|---|---|---|
| Zia uses a RAW table | RAW tables not excluded or too high priority | Exclude RAW or set Low |
| Zia gives global answer when user asked for an outlet | Outlet synonym/value synonym missing | Add outlet data synonyms and raise `outlet_name` priority |
| Zia sums a ratio | Ratio is a normal formula or default function is Sum | Use aggregate formula and avoid Sum default for ratio output |
| Zia uses event sales for normal sales | Event tables are still high priority | Exclude/Low event tables and keep `ZIA_Executive_Outlet_Month` High |
| Zia uses quantity for top item | Quantity is interpreted as performance | Train "top performing item" toward `net_sales`; use quantity only for "most sold" |
| Date filter ignored | Zia used a summary table without date grain | Use daily ZIA tables for date-range questions |
| Vendor filter does not affect receipt | Wrong table or disconnected chart | Use `ZIA_Procurement_Daily_Vendor_Material` for vendor/date receipt booked questions |
| Inventory value inflated | Daily inventory fact is summed across dates | Use `ZIA_Current_Inventory_Snapshot` for current inventory snapshot |
| Weekday heatmap shows numbers | Chart uses `day_of_week_sort` as label | Use `day_of_week_name` as row/column label and sort by `day_of_week_sort` |
| Packaging and recipe demand mix together | No demand type filter | Filter `demand_component_type` to Packaging Consumable or Recipe Ingredient |
| Ask Zia invents profit/margin | Synonyms imply profit when raw data has no COGS | Remove profit/margin synonyms unless a true COGS table is added |

## 13. Acceptance Criteria

Ask Zia is demo-ready when these pass:

| Test | Pass condition |
|---|---|
| `CP`, `HK`, `Saket` | Map to correct outlets |
| `revenue` | Maps to `net_sales`, not quantity, event sales, or baseline sales |
| `top performing item` | Ranks by `SUM(net_sales)` |
| `most sold item` | Ranks by `SUM(menu_units_sold)` |
| `average realized price` | Uses ZIA realized-price fields or `SUM(net_sales) / SUM(menu_units_sold)` |
| `purchase pressure` | Uses `purchase_to_sales_pct` in `ZIA_Executive_Outlet_Month` |
| `PO receipt gap` | Uses `po_receipt_gap_value` |
| `open PO` | Uses PO status or pending flag, not receipt gap |
| `current inventory` | Uses `ZIA_Current_Inventory_Snapshot` |
| `inventory trend` | Uses `ZIA_Inventory_Daily_Trend` |
| `recipe demand` | Uses `ZIA_Theoretical_Demand_Summary` or `ZIA_Theoretical_Demand_Daily` filtered to Recipe Ingredient |
| `packaging demand` | Uses `ZIA_Theoretical_Demand_Summary` or `ZIA_Theoretical_Demand_Daily` filtered to Packaging Consumable |
| `weekday sales` | Uses `day_of_week_name`, sorted by `day_of_week_sort` |

If any test fails, fix Zia training before adding more questions.
