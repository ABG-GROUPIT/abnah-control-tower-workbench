# Zoho Dashboard Click-By-Click Build Manual

Use this file while your Zoho Analytics screen is open.

This is not a concept note. It is the exact build checklist.

Follow it in order:

1. Build Dashboard 1 first.
2. Build every filter before building widgets.
3. Build every KPI as a `KPI Widget` / `Label Widget`.
4. Build every chart as a saved `Chart View`.
5. Add saved views to the dashboard after they are created.
6. Do not use RAW tables for dashboard visuals.
7. Do not use `SUM_Executive_KPIs` for the executive dashboard KPIs.

If Zoho uses slightly different wording:

| This manual says | Zoho may call it |
|---|---|
| KPI Widget | Label Widget / Single Label / Number Widget |
| Chart View | New Chart / Report / View |
| Table View | Tabular View / Summary View |
| X-axis | X Axis / Columns / Dimension |
| Y-axis | Y Axis / Rows / Measure |
| Color | Legend / Series / Break By |
| Filter | Criteria / User Filter |

## 0. Interconnected Dashboard Filters

Use this rule on every dashboard before adding charts:

1. Build dropdown filters from the same primary fact table used by most charts on that dashboard.
2. Put broad filters first and narrow filters later.
3. For each dropdown filter, open filter settings and choose:

```text
List only relevant values
```

4. Save filters in this order:
   - Dashboard 1: `Outlet -> Date Range -> Event Type`
   - Dashboard 2: `Outlet -> Date Range -> Super Category -> Category -> Menu Item`
   - Dashboard 3: `Outlet -> Procurement Date Range -> Vendor -> Material -> PO Status`
   - Dashboard 4: `Outlet -> Inventory Date Range -> Category -> Inventory Item`
   - Dashboard 5: `Outlet/Market Area -> Event Type -> Competitor Category -> Item`

If a dropdown still shows irrelevant values, rebuild that dropdown from the dashboard's primary fact table instead of a dimension or summary table.

## 1. Before Building Any Dashboard

Confirm these objects already exist:

1. All 18 RAW tables.
2. All 37 Query Tables.
3. Lookup relationships already created.
4. At minimum, these tables are present:
   - `FACT_Outlet_Daily_Health`
   - `FACT_Sales`
   - `FACT_Purchase_Order`
   - `FACT_Entry_Receipt`
   - `FACT_Vendor_Spend`
   - `FACT_Inventory_Closing`
   - `FACT_Theoretical_Consumption`
   - `FACT_Competitor_Price_Position`
   - `SUM_Event_Impact`
   - `SUM_Event_Markers`
   - `SUM_Sales_Category_Mix`
   - `SUM_Menu_Item_Performance`
   - `SUM_Vendor_Share`
   - `SUM_Inventory_Risk`
   - `SUM_Competitor_Positioning`

## 2. Dashboard 1: Executive Outlet Health

Dashboard name:

```text
01_Executive_Outlet_Health
```

Build this dashboard first.

### 2.1 Create Dashboard 1

1. In Zoho Analytics, click `+ New`.
2. Choose `Dashboard`.
3. Dashboard name:

```text
01_Executive_Outlet_Health
```

4. Add a text widget at the top.
5. Text to type:

```text
Executive Outlet Health
Cross-outlet view of revenue, purchase spend, inventory pressure, and event exposure.
```

### 2.2 Create Dashboard 1 Filters

Create only these filters first.

#### Filter 1: Date Range

1. Open dashboard `01_Executive_Outlet_Health`.
2. Click `Edit Design`.
3. Click `Add User Filter`.
4. Source table: `FACT_Outlet_Daily_Health`.
5. Column: `activity_date`.
6. Filter type: `Date Range`.
7. Filter label:

```text
Date Range
```

8. Default: full available date range.
9. Save the filter.

Use this filter on:

- all KPI widgets from `FACT_Outlet_Daily_Health`,
- all executive charts from `FACT_Outlet_Daily_Health`,
- table `TB01_Outlet_Health_Detail`.

#### Filter 2: Outlet

1. Click `Add User Filter`.
2. Source table: `FACT_Outlet_Daily_Health`.
3. Column: `outlet_name`.
4. Filter type: dropdown.
5. Selection: multi-select or single-select.
6. Filter label:

```text
Outlet
```

7. Default: `All`.
8. Save the filter.

Use this filter on every executive object that has `outlet_name`.

#### Filter 3: Event Type

1. Click `Add User Filter`.
2. Source table: `SUM_Event_Impact`.
3. Column: `event_type`.
4. Filter type: dropdown.
5. Filter label:

```text
Event Type
```

6. Default: `All`.
7. Save the filter.

Use this filter only on:

- KPI `Event-Linked Sales Lift %`,
- event charts,
- event tables.

### 2.3 Create Required Aggregate Formulas

Open table:

```text
FACT_Outlet_Daily_Health
```

Create these aggregate formulas.

#### Formula 1: Average Daily Revenue

1. Open `FACT_Outlet_Daily_Health`.
2. Click `Add Formula` / `New Formula`.
3. Choose `Aggregate Formula`.
4. Formula name:

```text
AF_Average_Daily_Revenue
```

5. Formula:

```text
SUM("net_sales") / DISTINCTCOUNT("activity_date")
```

6. Format: Currency / INR.
7. Save.

If `DISTINCTCOUNT` fails, use Zoho's formula helper and select `Distinct Count` for `activity_date`.

#### Formula 2: Purchase-To-Sales Ratio

1. Open `FACT_Outlet_Daily_Health`.
2. Click `Add Formula` / `New Formula`.
3. Choose `Aggregate Formula`.
4. Formula name:

```text
AF_Purchase_To_Sales_Ratio
```

5. Formula:

```text
SUM("po_value") / SUM("net_sales") * 100
```

6. Format: Percentage.
7. Save.

#### Formula 3: Revenue Per Inventory Rupee

1. Open `FACT_Outlet_Daily_Health`.
2. Click `Add Formula` / `New Formula`.
3. Choose `Aggregate Formula`.
4. Formula name:

```text
AF_Revenue_Per_Inventory_Rupee
```

5. Formula:

```text
SUM("net_sales") / AVG("inventory_value")
```

6. Format: Decimal number.
7. Save.

### 2.4 Build KPI 1: Net Sales Revenue

1. Open dashboard `01_Executive_Outlet_Health`.
2. Click `Edit Design`.
3. Click `Widget`.
4. Choose `KPI Widget`.
5. Choose `Label Widget` / `Single Label`.
6. Source table: `FACT_Outlet_Daily_Health`.
7. Data column: `net_sales`.
8. Calculation: `SUM`.
9. Group By: leave blank.
10. Apply filters:
    - `Date Range` -> `activity_date`
    - `Outlet` -> `outlet_name`
11. Label text:

```text
Net Sales Revenue
```

12. Format: Currency / INR.
13. Save.
14. Place in KPI row 1.

### 2.5 Build KPI 2: Average Daily Revenue

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Value: `AF_Average_Daily_Revenue`.
5. Group By: leave blank.
6. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Label text:

```text
Average Daily Revenue
```

8. Format: Currency / INR.
9. Save.
10. Place in KPI row 1.

### 2.6 Build KPI 3: Procurement Spend

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Data column: `po_value`.
5. Calculation: `SUM`.
6. Group By: leave blank.
7. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
8. Label text:

```text
Procurement Spend
```

9. Format: Currency / INR.
10. Save.
11. Place in KPI row 1.

### 2.7 Build KPI 4: Purchase-To-Sales Ratio

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Value: `AF_Purchase_To_Sales_Ratio`.
5. Group By: leave blank.
6. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Label text:

```text
Purchase-To-Sales Ratio
```

8. Format: Percentage.
9. Save.
10. Place in KPI row 1.

### 2.8 Build KPI 5: Revenue Per Inventory Rupee

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Value: `AF_Revenue_Per_Inventory_Rupee`.
5. Group By: leave blank.
6. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Label text:

```text
Revenue Per Inventory Rupee
```

8. Format: Decimal number.
9. Save.
10. Place in KPI row 2.

### 2.9 Build KPI 6: Inventory Pressure Item-Days

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Data column: `low_stock_item_count`.
5. Calculation: `SUM`.
6. Group By: leave blank.
7. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
8. Label text:

```text
Inventory Pressure Item-Days
```

9. Format: Number.
10. Save.
11. Place in KPI row 2.

### 2.10 Build KPI 7: Event-Linked Sales Lift %

1. Add `KPI Widget`.
2. Choose `Label Widget` / `Single Label`.
3. Source table: `SUM_Event_Impact`.
4. Data column: `sales_lift_pct`.
5. Calculation: `AVG`.
6. Group By: leave blank.
7. Apply filters:
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
8. Optional date filter:
   - If Zoho asks for a date field, use `start_date`.
   - If this gives trouble, skip the date filter for this KPI first.
9. Label text:

```text
Event-Linked Sales Lift %
```

10. Format: Percentage.
11. Save.
12. Place in KPI row 2.

### 2.11 Build Card 8: Best Performing Outlet

This is a small table, not a KPI widget.

1. Click `+ New`.
2. Choose `Table View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Add column: `outlet_name`.
5. Add measure: `net_sales`.
6. Aggregation for `net_sales`: `SUM`.
7. Sort: `SUM(net_sales)` descending.
8. If Zoho supports row limit, set `Top 1`.
9. Save as:

```text
CARD_Best_Performing_Outlet
```

10. Add this view to dashboard row 2.
11. Apply filters:
    - `Date Range` -> `activity_date`
    - `Outlet` -> `outlet_name`

### 2.12 Build Chart CH01: Outlet Sales Ranking

1. Click `+ New`.
2. Choose `Chart View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Chart type: horizontal bar.
5. X-axis: `outlet_name`.
6. Y-axis: `net_sales`.
7. Aggregation: `SUM`.
8. Sort: `SUM(net_sales)` descending.
9. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
10. Save as:

```text
CH01_Outlet_Sales_Ranking
```

11. Add this chart to dashboard row 3.

### 2.13 Build Chart CH02: Daily Sales Trend By Outlet

1. Click `+ New`.
2. Choose `Chart View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Chart type: line chart.
5. X-axis: `activity_date`.
6. Y-axis: `net_sales`.
7. Aggregation: `SUM`.
8. Color/series: `outlet_name`.
9. Sort: `activity_date` ascending.
10. Apply filters:
    - `Date Range` -> `activity_date`
    - `Outlet` -> `outlet_name`
11. Save as:

```text
CH02_Daily_Sales_Trend_By_Outlet
```

12. Add this chart to dashboard row 3.

### 2.14 Build Chart CH03: Sales Purchase Receipt Comparison

1. Click `+ New`.
2. Choose `Chart View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Chart type: clustered bar.
5. X-axis: `outlet_name`.
6. Y-axis measure 1: `net_sales`, aggregation `SUM`.
7. Y-axis measure 2: `po_value`, aggregation `SUM`.
8. Y-axis measure 3: `receipt_value`, aggregation `SUM`.
9. Series/color: measure name, if Zoho asks.
10. Apply filters:
    - `Date Range` -> `activity_date`
    - `Outlet` -> `outlet_name`
11. Save as:

```text
CH03_Sales_Purchase_Receipt_Comparison
```

12. Add this chart to dashboard row 4.

### 2.15 Build Chart CH04: Inventory Pressure By Outlet

1. Click `+ New`.
2. Choose `Chart View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Chart type: bar.
5. X-axis: `outlet_name`.
6. Y-axis: `low_stock_item_count`.
7. Aggregation: `SUM`.
8. Color/series: `health_note`.
9. Sort: `SUM(low_stock_item_count)` descending.
10. Apply filters:
    - `Date Range` -> `activity_date`
    - `Outlet` -> `outlet_name`
11. Save as:

```text
CH04_Inventory_Pressure_By_Outlet
```

12. Add this chart to dashboard row 4.

### 2.16 Build Chart CH05: Event Exposure By Outlet

1. Click `+ New`.
2. Choose `Chart View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Chart type: bar.
5. X-axis: `outlet_name`.
6. Y-axis: `event_count`.
7. Aggregation: `SUM`.
8. Sort: `SUM(event_count)` descending.
9. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
10. Save as:

```text
CH05_Event_Exposure_By_Outlet
```

11. Add this chart to dashboard row 4.

### 2.17 Build Chart CH06: Outlet Health Note Mix

1. Click `+ New`.
2. Choose `Chart View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Chart type: stacked bar or donut.
5. X-axis/category: `health_note`.
6. Y-axis: `activity_date`.
7. Aggregation: `COUNT`.
8. Color/series: `outlet_name`, if using stacked bar.
9. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
10. Save as:

```text
CH06_Outlet_Health_Note_Mix
```

11. Add this chart to dashboard row 5.

### 2.18 Build Table TB01: Outlet Health Detail

1. Click `+ New`.
2. Choose `Table View`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Add detail columns:
   - `activity_date`
   - `outlet_name`
   - `market_area`
   - `health_note`
5. Add measure columns:
   - `net_sales`
   - `sold_qty`
   - `po_value`
   - `receipt_value`
   - `inventory_value`
   - `low_stock_item_count`
   - `event_count`
6. Apply filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Sort:
   - `activity_date` ascending
   - `outlet_name` ascending
8. Save as:

```text
TB01_Outlet_Health_Detail
```

9. Add this table full width near the bottom.

### 2.19 Build Table TB02: Spike Explanation Panel

1. Click `+ New`.
2. Choose `Table View`.
3. Source table: `SUM_Event_Markers`.
4. Add detail columns:
   - `event_date`
   - `outlet_name`
   - `event_name`
   - `event_type`
   - `affected_category`
   - `affected_items`
   - `confidence_level`
5. Add measure columns:
   - `event_day_sales`
   - `baseline_sales`
   - `sales_lift_percentage`
6. Apply filters:
   - `Date Range` -> `event_date`
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
7. Sort: `event_date` ascending.
8. Save as:

```text
TB02_Spike_Explanation_Panel
```

9. Add this table full width at the bottom.

### 2.20 Dashboard 1 Layout

Arrange the finished dashboard like this:

1. Row 1: title text and filters.
2. Row 2: `Net Sales Revenue`, `Average Daily Revenue`, `Procurement Spend`, `Purchase-To-Sales Ratio`.
3. Row 3: `Revenue Per Inventory Rupee`, `Inventory Pressure Item-Days`, `Event-Linked Sales Lift %`, `CARD_Best_Performing_Outlet`.
4. Row 4: `CH01_Outlet_Sales_Ranking` and `CH02_Daily_Sales_Trend_By_Outlet`.
5. Row 5: `CH03_Sales_Purchase_Receipt_Comparison`, `CH04_Inventory_Pressure_By_Outlet`, `CH05_Event_Exposure_By_Outlet`.
6. Row 6: `CH06_Outlet_Health_Note_Mix`.
7. Row 7: `TB01_Outlet_Health_Detail`.
8. Row 8: `TB02_Spike_Explanation_Panel`.

## 3. Dashboard 2: Sales And Menu Intelligence

Dashboard name:

```text
02_Sales_Menu_Intelligence
```

### 3.1 Create Dashboard 2 Filters

Create these filters:

1. `Outlet`
   - Source table: `FACT_Sales`
   - Field: `outlet_name`
   - Type: dropdown
   - Default for first build: `ABNAH Cafe Connaught Place`

2. `Date Range`
   - Source table: `FACT_Sales`
   - Field: `sales_date`
   - Type: date range

3. `Category`
   - Source table: `FACT_Sales`
   - Field: `category`
   - Type: dropdown

4. `Super Category`
   - Source table: `FACT_Sales`
   - Field: `super_category`
   - Type: dropdown

5. `Menu Item`
   - Source table: `FACT_Sales`
   - Field: `item_name`
   - Type: dropdown/search

### 3.2 Build Dashboard 2 KPIs

#### KPI: Net Sales

1. Add KPI Widget.
2. Source table: `FACT_Sales`.
3. Data column: `net_sale`.
4. Calculation: `SUM`.
5. Group By: blank.
6. Filters:
   - `Outlet` -> `outlet_name`
   - `Date Range` -> `sales_date`
   - `Category` -> `category`
7. Label:

```text
Net Sales
```

#### KPI: Menu Units Sold

1. Add KPI Widget.
2. Source table: `FACT_Sales`.
3. Data column: `qty`.
4. Calculation: `SUM`.
5. Group By: blank.
6. Filters:
   - `Outlet` -> `outlet_name`
   - `Date Range` -> `sales_date`
   - `Category` -> `category`
7. Label:

```text
Menu Units Sold
```

Meaning: number of customer-facing menu items sold, not ingredients.

#### KPI: Average Realized Unit Price

1. Add KPI Widget.
2. Source table: `FACT_Sales`.
3. Data column: `net_sale_per_qty`.
4. Calculation: `AVG`.
5. Group By: blank.
6. Filters:
   - `Outlet` -> `outlet_name`
   - `Date Range` -> `sales_date`
   - `Category` -> `category`
7. Label:

```text
Average Realized Unit Price
```

#### KPI: Active Menu Items

1. Add KPI Widget.
2. Source table: `FACT_Sales`.
3. Data column: `item_number`.
4. Calculation: `COUNT DISTINCT`.
5. Group By: blank.
6. Filters:
   - `Outlet` -> `outlet_name`
   - `Date Range` -> `sales_date`
7. Label:

```text
Active Menu Items
```

### 3.3 Build Dashboard 2 Charts

Build chart `CH07_Daily_Net_Sales_Trend`:

1. Chart View.
2. Source table: `FACT_Sales`.
3. Chart type: line.
4. X-axis: `sales_date`.
5. Y-axis: `net_sale`.
6. Aggregation: `SUM`.
7. Color/series: optional `category`.
8. Filters:
   - `Outlet` -> `outlet_name`
   - `Date Range` -> `sales_date`
   - `Category` -> `category`
9. Save as `CH07_Daily_Net_Sales_Trend`.

Build chart `CH08_Category_Revenue_Mix`:

1. Chart View.
2. Source table: `FACT_Sales`.
3. Chart type: horizontal bar.
4. X-axis: `category`.
5. Y-axis: `net_sale`.
6. Aggregation: `SUM`.
7. Color/series: `super_category`.
8. Filters:
   - `Outlet` -> `outlet_name`
   - `Date Range` -> `sales_date`
   - `Category` -> `category`
   - `Super Category` -> `super_category`
9. Sort: `SUM(net_sale)` descending.
10. Save as `CH08_Category_Revenue_Mix`.

Important:

Do not build this chart from `SUM_Sales_Category_Mix` if the dashboard has a `Date Range` filter. `SUM_Sales_Category_Mix` has no `sales_date`, so a date filter cannot change it. Use `FACT_Sales` for this visual.

Build chart `CH10_Top_Items_By_Net_Sales`:

1. Chart View.
2. Source table: `SUM_Menu_Item_Performance`.
3. Chart type: horizontal bar.
4. X-axis: `item_name`.
5. Y-axis: `total_net_sale`.
6. Aggregation: `SUM`.
7. Color/series: `category`.
8. Filters:
   - `Outlet` -> `outlet_name`
   - `Category` -> `category`
9. Sort: `SUM(total_net_sale)` descending.
10. Limit: Top 10 or Top 15.
11. Save as `CH10_Top_Items_By_Net_Sales`.

Build chart `CH11_Top_Items_By_Quantity`:

1. Chart View.
2. Source table: `SUM_Menu_Item_Performance`.
3. Chart type: horizontal bar.
4. X-axis: `item_name`.
5. Y-axis: `total_qty`.
6. Aggregation: `SUM`.
7. Color/series: `category`.
8. Filters:
   - `Outlet` -> `outlet_name`
   - `Category` -> `category`
9. Sort: `SUM(total_qty)` descending.
10. Limit: Top 10 or Top 15.
11. Save as `CH11_Top_Items_By_Quantity`.

Build table `TB03_Menu_Item_Detail`:

1. Table View.
2. Source table: `SUM_Menu_Item_Performance`.
3. Detail columns:
   - `item_number`
   - `item_name`
   - `super_category`
   - `category`
   - `performance_note`
4. Measure columns:
   - `total_qty`
   - `total_net_sale`
   - `avg_realized_unit_price`
   - `avg_price_index`
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Category` -> `category`
6. Sort: `total_net_sale` descending.
7. Save as `TB03_Menu_Item_Detail`.

## 4. Dashboard 3: Vendor And Procurement Analytics

Dashboard name:

```text
03_Vendor_Procurement_Analytics
```

### 4.1 Create Dashboard 3 Filters

Before creating these filters, update/recreate Zoho query table `FACT_Vendor_Spend` using:

```text
docs/zoho_query_table_sql/32_fact_vendor_spend.sql
```

The updated version includes `item_code`, `item_name`, `category_name`, `super_category_name`, `po_status`, and `open_or_partial_po_count`, which are needed for cascading material/category/status filters and unified KPI filtering.

Create these filters:

1. `Outlet`
   - Source table: `FACT_Vendor_Spend`
   - Field: `outlet_name`
   - Filter values: `List only relevant values`

2. `Procurement Date Range`
   - Source table: `FACT_Vendor_Spend`
   - Field: `activity_date`

3. `Vendor`
   - Source table: `FACT_Vendor_Spend`
   - Field: `vendor_name`
   - Filter values: `List only relevant values`

4. `Material`
   - Source table: `FACT_Vendor_Spend`
   - Field: `item_name`
   - Filter values: `List only relevant values`

5. `PO Status`
   - Source table: `FACT_Vendor_Spend`
   - Field: `po_status`
   - Use only on PO-status/open-PO reports, not on receipt value cards.

The filter order should be:

```text
Outlet -> Procurement Date Range -> Vendor -> Material -> PO Status
```

In each dropdown filter's settings, turn on `List only relevant values`. This is what makes the `Vendor` dropdown show only vendors active for the selected outlet.

If any of these KPI cards stay static after choosing date/vendor/material, the dashboard is still using old filters or old KPI sources from `FACT_Purchase_Order`:

- `PO Raised Value`
- `Receipt Booked Value`
- `PO vs Receipt Value Gap`
- `Open / Partial PO Status Count`

Fix it like this:

1. Open dashboard `03_Vendor_Procurement_Analytics`.
2. Click `Edit Design`.
3. Delete these existing filters from the top filter strip if they were created from `FACT_Purchase_Order`:
   - `po_date`
   - `vendor_name`
   - `item_name`
   - `po_status`
4. Recreate these filters from `FACT_Vendor_Spend` so the KPI cards all share the same filter source.
5. Add a new user filter for procurement date.
6. Source table:

```text
FACT_Vendor_Spend
```

7. Field:

```text
activity_date
```

8. Display name:

```text
Procurement Date Range
```

9. Save the filter.
10. Add a new user filter for vendor.
11. Source table:

```text
FACT_Vendor_Spend
```

12. Field:

```text
vendor_name
```

13. Display name:

```text
Vendor
```

14. Turn on:

```text
List only relevant values
```

15. Save the filter.
16. Add a new user filter for material.
17. Source table:

```text
FACT_Vendor_Spend
```

18. Field:

```text
item_name
```

19. Display name:

```text
Material
```

20. Turn on:

```text
List only relevant values
```

21. Save the filter.
22. Add a new user filter for PO status.
23. Source table:

```text
FACT_Vendor_Spend
```

24. Field:

```text
po_status
```

25. Display name:

```text
PO Status
```

26. Turn on:

```text
List only relevant values
```

27. Save the filter.
28. Open the `PO Raised Value` KPI editor.
29. In the KPI/card options, keep `Apply Dashboard Filters` enabled.
30. If Zoho gives `Customize`, map:
    - `Outlet` -> `FACT_Vendor_Spend.outlet_name`
    - `Procurement Date Range` -> `FACT_Vendor_Spend.activity_date`
    - `Vendor` -> `FACT_Vendor_Spend.vendor_name`
    - `Material` -> `FACT_Vendor_Spend.item_name`
31. Repeat the same mapping for `Receipt Booked Value`.
32. Do not map `PO Status` to `Receipt Booked Value`.
33. Open the `Open / Partial PO Count` KPI editor.
34. Change source table to:

```text
FACT_Vendor_Spend
```

35. Change data column to:

```text
open_or_partial_po_count
```

36. Show value as:

```text
SUM
```

37. Map:
    - `Outlet` -> `FACT_Vendor_Spend.outlet_name`
    - `Procurement Date Range` -> `FACT_Vendor_Spend.activity_date`
    - `Vendor` -> `FACT_Vendor_Spend.vendor_name`
    - `Material` -> `FACT_Vendor_Spend.item_name`
    - `PO Status` -> `FACT_Vendor_Spend.po_status`
38. Save the dashboard.

Expected test:

1. Select one outlet.
2. Select a procurement date range.
3. `PO Raised Value` and `Receipt Booked Value` must change.
4. Select one vendor.
5. `PO Raised Value` must change again.
6. `Receipt Booked Value` must change or become blank/zero if that vendor has no receipts in the selected period.
7. Select one material.
8. Both value cards must change again.
9. `PO vs Receipt Value Gap` must change with outlet/date/vendor/material.
10. `Open / Partial PO Status Count` must change with outlet/date/vendor/material.
11. `PO Status` should control `Open / Partial PO Status Count`.
12. `PO Status` should not control `Receipt Booked Value`, because receipt rows do not have PO status.

### 4.2 Build Dashboard 3 KPIs

Build KPI `PO Raised Value`:

1. KPI Widget.
2. Source table: `FACT_Vendor_Spend`.
3. Data column: `ordered_value`.
4. Calculation: `SUM`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Vendor` -> `vendor_name`
   - `Material` -> `item_name`
6. Label: `PO Raised Value`.

Build KPI `Receipt Booked Value`:

1. KPI Widget.
2. Source table: `FACT_Vendor_Spend`.
3. Data column: `received_value`.
4. Calculation: `SUM`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Vendor` -> `vendor_name`
   - `Material` -> `item_name`
6. Label: `Receipt Booked Value`.

Why this label matters:

`Receipt Booked Value` can be higher than `PO Raised Value` in a selected date range because receipts can be booked for purchase orders raised earlier, and receipt/entry rows are operational receiving records, not the same thing as PO creation rows.

Build KPI `PO vs Receipt Value Gap`:

1. Open table `FACT_Vendor_Spend`.
2. Click `Add Formula` / `New Formula`.
3. Choose `Aggregate Formula`.
4. Formula name:

```text
AF_PO_vs_Receipt_Value_Gap
```

5. Formula:

```text
SUM("ordered_value") - SUM("received_value")
```

6. Format: Currency / INR.
7. Save.
8. Add KPI Widget.
9. Source table: `FACT_Vendor_Spend`.
10. Value: `AF_PO_vs_Receipt_Value_Gap`.
11. Group By: blank.
12. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Vendor` -> `vendor_name`
   - `Material` -> `item_name`
13. Do not map `PO Status` to this card.
14. Label: `PO vs Receipt Value Gap`.

Build KPI `Open / Partial PO Status Count`:

1. KPI Widget.
2. Source table: `FACT_Vendor_Spend`.
3. Data column: `open_or_partial_po_count`.
4. Calculation: `SUM`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Vendor` -> `vendor_name`
   - `Material` -> `item_name`
   - `PO Status` -> `po_status`
6. Label: `Open / Partial PO Status Count`.

Meaning: this card counts PO lines that are Pending, Partially Received, or have positive remaining quantity. It is not a value-gap card.

Build KPI `Active Vendors In Selected Outlet`:

1. KPI Widget.
2. Source table: `FACT_Vendor_Spend`.
3. Data column: `vendor_name`.
4. Calculation: `COUNT DISTINCT`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Material` -> `item_name`
6. Do not apply the `Vendor` filter to this KPI if you want it to show the available vendor base for the selected outlet.
7. Label: `Active Vendors In Selected Outlet`.

### 4.3 Build Dashboard 3 Charts

Build chart `CH14_Vendor_PO_Raised_Share`:

1. Chart View.
2. Source table: `FACT_Vendor_Spend`.
3. Chart type: horizontal bar.
4. X-axis: `vendor_name`.
5. Y-axis: `ordered_value`.
6. Aggregation: `SUM`.
7. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Vendor` -> `vendor_name`
   - `Material` -> `item_name`
8. Sort: `SUM(ordered_value)` descending.
9. Save as `CH14_Vendor_PO_Raised_Share`.

Build chart `CH15_Vendor_Receipt_Booked_Share`:

1. Chart View.
2. Source table: `FACT_Vendor_Spend`.
3. Chart type: horizontal bar or donut.
4. X-axis: `vendor_name`.
5. Y-axis: `received_value`.
6. Aggregation: `SUM`.
7. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Vendor` -> `vendor_name`
   - `Material` -> `item_name`
8. Sort: `SUM(received_value)` descending.
9. Save as `CH15_Vendor_Receipt_Booked_Share`.

Build chart `CH17_Vendor_Spend_Trend`:

1. Chart View.
2. Source table: `FACT_Vendor_Spend`.
3. Chart type: combo or multi-line.
4. X-axis: `activity_date`.
5. Y-axis measure 1: `ordered_value`, aggregation `SUM`.
6. Y-axis measure 2: `received_value`, aggregation `SUM`.
7. Filters:
   - `Outlet` -> `outlet_name`
   - `Procurement Date Range` -> `activity_date`
   - `Vendor` -> `vendor_name`
   - `Material` -> `item_name`
8. Save as `CH17_Vendor_Spend_Trend`.

Build table `TB05_Pending_Partial_PO_Detail`:

1. Table View.
2. Source table: `FACT_PO_Receipt_Comparison`.
3. Detail columns:
   - `po_number`
   - `vendor_name`
   - `item_name`
   - `po_status`
   - `po_date`
   - `expected_delivery_date`
4. Measure columns:
   - `ordered_qty`
   - `processed_qty`
   - `matched_received_qty`
   - `unmatched_order_qty`
   - `remaining_qty`
   - `total_item_cost`
5. Criteria:

```text
pending_or_partial_flag = 1
```

6. Filters:
   - `Outlet` -> `outlet_name`
   - `Vendor` -> `vendor_name`
7. Save as `TB05_Pending_Partial_PO_Detail`.

## 5. Dashboard 4: Inventory And Consumption Intelligence

Dashboard name:

```text
04_Inventory_Consumption_Intelligence
```

### 5.1 Create Dashboard 4 Filters

Create these filters:

1. `Outlet`
   - Source table: `SUM_Inventory_Risk`
   - Field: `outlet_name`

2. `Inventory Pressure Band`
   - Source table: `SUM_Inventory_Risk`
   - Field: `inventory_pressure_band`

3. `Inventory Item`
   - Source table: `SUM_Inventory_Risk`
   - Field: `item_name`

4. `Ingredient`
   - Source table: `FACT_Theoretical_Consumption`
   - Field: `ingredient_name`

### 5.2 Build Dashboard 4 KPIs

Build KPI `Inventory Value`:

1. KPI Widget.
2. Source table: `SUM_Inventory_Risk`.
3. Data column: `total_amt`.
4. Calculation: `SUM`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Inventory Pressure Band` -> `inventory_pressure_band`
6. Label: `Inventory Value`.

Build KPI `Low Stock Item Count`:

1. KPI Widget.
2. Source table: `SUM_Inventory_Risk`.
3. Data column: `low_stock_flag`.
4. Calculation: `SUM`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Inventory Pressure Band` -> `inventory_pressure_band`
6. Label: `Low Stock Item Count`.

Build KPI `Theoretical Ingredient Demand`:

1. KPI Widget.
2. Source table: `FACT_Theoretical_Consumption`.
3. Data column: `theoretical_ingredient_qty`.
4. Calculation: `SUM`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Ingredient` -> `ingredient_name`
6. Label: `Theoretical Ingredient Demand`.

### 5.3 Build Dashboard 4 Charts

Build chart `CH21_Inventory_Value_By_Category`:

1. Chart View.
2. Source table: `SUM_Inventory_Risk`.
3. Chart type: bar.
4. X-axis: `category_name`.
5. Y-axis: `total_amt`.
6. Aggregation: `SUM`.
7. Color/series: `super_category_name`.
8. Filters:
   - `Outlet` -> `outlet_name`
   - `Inventory Category` -> `category_name`
   - `Pressure Band` -> `inventory_pressure_band`
9. Do not map the dashboard date range to this chart. `SUM_Inventory_Risk` is already the latest inventory snapshot.
10. Sort: `SUM(total_amt)` descending.
11. Save as `CH21_Inventory_Value_By_Category`.

Validation:

```text
All outlets latest inventory value should be about 18.92L.
Connaught Place latest inventory value should be about 6.13L.
Hauz Khas latest inventory value should be about 6.77L.
Saket Premium latest inventory value should be about 6.02L.
```

Do not build this chart from `FACT_Inventory_Closing` with `SUM(total_amt)` unless the X-axis is `inventory_date`.
That table has one inventory snapshot per day, so summing it by category across Month 1 adds 31 daily snapshots and inflates the value.

Build chart `CH24_Low_Stock_Items`:

1. Chart View.
2. Source table: `SUM_Inventory_Risk`.
3. Chart type: horizontal bar.
4. X-axis: `item_name`.
5. Y-axis: `low_stock_flag`.
6. Aggregation: `SUM`.
7. Criteria:

```text
low_stock_flag = 1
```

8. Filters:
   - `Outlet` -> `outlet_name`
   - `Inventory Pressure Band` -> `inventory_pressure_band`
9. Save as `CH24_Low_Stock_Items`.

Build chart `CH26_Top_Theoretical_Ingredients`:

1. Chart View.
2. Source table: `FACT_Theoretical_Consumption`.
3. Chart type: horizontal bar.
4. X-axis: `ingredient_name`.
5. Y-axis: `theoretical_ingredient_qty`.
6. Aggregation: `SUM`.
7. Filters:
   - `Outlet` -> `outlet_name`
   - `Ingredient` -> `ingredient_name`
8. Sort: `SUM(theoretical_ingredient_qty)` descending.
9. Save as `CH26_Top_Theoretical_Ingredients`.

Build table `TB07_Low_Stock_Detail`:

1. Table View.
2. Source table: `SUM_Inventory_Risk`.
3. Detail columns:
   - `item_code`
   - `item_name`
   - `category_name`
   - `inventory_pressure_band`
   - `risk_note`
4. Measure columns:
   - `total_qty`
   - `total_amt`
   - `total_theoretical_qty`
   - `low_stock_flag`
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Inventory Pressure Band` -> `inventory_pressure_band`
6. Save as `TB07_Low_Stock_Detail`.

## 6. Dashboard 5: Calendar Event Competitor Intelligence

Dashboard name:

```text
05_Calendar_Event_Competitor_Intelligence
```

### 6.1 Create Dashboard 5 Filters

Create these filters:

1. `Outlet`
   - Source table: `SUM_Event_Impact`
   - Field: `outlet_name`

2. `Event Type`
   - Source table: `SUM_Event_Impact`
   - Field: `event_type`

3. `Competitor`
   - Source table: `SUM_Competitor_Positioning`
   - Field: `competitor_name`

4. `Market Area`
   - Source table: `SUM_Competitor_Positioning`
   - Field: `market_area`

5. `Price Position`
   - Source table: `SUM_Competitor_Positioning`
   - Field: `price_position_band`

### 6.2 Build Dashboard 5 KPIs

Build KPI `Event Day Sales`:

1. KPI Widget.
2. Source table: `SUM_Event_Impact`.
3. Data column: `event_day_sales`.
4. Calculation: `SUM`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
6. Label: `Event Day Sales`.

Build KPI `Average Event Lift %`:

1. KPI Widget.
2. Source table: `SUM_Event_Impact`.
3. Data column: `sales_lift_pct`.
4. Calculation: `AVG`.
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
6. Label: `Average Event Lift %`.

Build KPI `Premium Context Sales`:

1. KPI Widget.
2. Source table: `SUM_Competitor_Positioning`.
3. Data column: `premium_context_sales_lines`.
4. Calculation: `SUM`.
5. Filters:
   - `Competitor` -> `competitor_name`
   - `Market Area` -> `market_area`
   - `Price Position` -> `price_position_band`
6. Label: `Premium Context Sales`.

### 6.3 Build Dashboard 5 Charts

Build chart `CH27_Event_Sales_By_Event`:

1. Chart View.
2. Source table: `SUM_Event_Impact`.
3. Chart type: bar.
4. X-axis: `event_name`.
5. Y-axis: `event_day_sales`.
6. Aggregation: `SUM`.
7. Color/series: `event_type`.
8. Filters:
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
9. Save as `CH27_Event_Sales_By_Event`.

Build chart `CH28_Event_Lift_By_Event`:

1. Chart View.
2. Source table: `SUM_Event_Impact`.
3. Chart type: bar.
4. X-axis: `event_name`.
5. Y-axis: `sales_lift_pct`.
6. Aggregation: `AVG`.
7. Color/series: `confidence_level`.
8. Filters:
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
9. Save as `CH28_Event_Lift_By_Event`.

Build chart `CH31_Competitor_Price_Index`:

1. Chart View.
2. Source table: `SUM_Competitor_Positioning`.
3. Chart type: bar.
4. X-axis: `competitor_name`.
5. Y-axis: `avg_price_index`.
6. Aggregation: `AVG`.
7. Color/series: `competitor_category`.
8. Filters:
   - `Competitor` -> `competitor_name`
   - `Market Area` -> `market_area`
   - `Price Position` -> `price_position_band`
9. Save as `CH31_Competitor_Price_Index`.

Build table `TB09_Spike_Explanation_Panel`:

1. Table View.
2. Source table: `SUM_Event_Markers`.
3. Detail columns:
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
5. Filters:
   - `Outlet` -> `outlet_name`
   - `Event Type` -> `event_type`
6. Save as `TB09_Spike_Explanation_Panel`.

## 7. If A Filter Does Not Apply

Use this rule:

1. Open the KPI/chart.
2. Check its source table.
3. Use a filter field from that exact source table.
4. Do not rely on lookup filters until the direct source-table filter works.

Examples:

```text
FACT_Sales chart -> filter with FACT_Sales.sales_date and FACT_Sales.outlet_name
FACT_Purchase_Order chart -> filter with FACT_Purchase_Order.po_date and FACT_Purchase_Order.outlet_name
SUM_Inventory_Risk chart -> filter with SUM_Inventory_Risk.outlet_name
SUM_Event_Impact chart -> filter with SUM_Event_Impact.outlet_name and SUM_Event_Impact.event_type
```

## 8. Build Order To Follow In Zoho

1. Build Dashboard 1 fully.
2. Confirm filters change Dashboard 1 numbers.
3. Build Dashboard 2.
4. Confirm outlet filter changes Dashboard 2.
5. Build Dashboard 3.
6. Confirm vendor and PO filters work.
7. Build Dashboard 4.
8. Confirm pressure-band filter works.
9. Build Dashboard 5.
10. Confirm event and competitor filters work.

## 9. If Filtered KPI Values Look Wrong

Use this section when an outlet filter changes some cards but ratio cards look strange.

From the current dashboard screenshots:

- `Net Sales Revenue` is changing correctly.
- `Procurement Spend` is changing correctly.
- `Purchase-To-Sales Ratio` is probably wrong because it stays `83.66%` for all outlet selections.
- `Revenue Per Inventory Rupee` is probably wrong because selected outlet values appear to add together instead of recalculating as a ratio.

### 9.1 Quick Check: Purchase-To-Sales Ratio

The correct logic is:

```text
Purchase-To-Sales Ratio = SUM(po_value) / SUM(net_sales) * 100
```

It must recalculate after the outlet filter changes.

Using the visible screenshot numbers:

```text
All outlets:
16.27L procurement / 19.45L sales * 100 = about 83.65%

Outlet with 6.27L sales and 6.05L procurement:
6.05L / 6.27L * 100 = about 96.49%

Outlet with 6.26L sales and 5.21L procurement:
5.21L / 6.26L * 100 = about 83.23%

Two selected outlets with 12.53L sales and 11.25L procurement:
11.25L / 12.53L * 100 = about 89.78%
```

So if the card always shows `83.66%`, the card is not filter-aware or is using a global formula.

### 9.2 Fix Purchase-To-Sales Ratio

First verify the formula:

1. Open table `FACT_Outlet_Daily_Health`.
2. Click `Edit Design`.
3. Open formula `AF_Purchase_To_Sales_Ratio`.
4. Confirm it is an aggregate formula, not a normal row formula.
5. Formula must be:

```text
SUM("po_value") / SUM("net_sales") * 100
```

6. Save.

Then fix the KPI widget:

1. Open dashboard `01_Executive_Outlet_Health`.
2. Click `Edit Design`.
3. Click KPI card `Purchase-To-Sales Ratio`.
4. Click edit / pencil.
5. Source table must be:

```text
FACT_Outlet_Daily_Health
```

6. Value must be:

```text
AF_Purchase_To_Sales_Ratio
```

7. Group By must be blank.
8. Do not use `SUM(AF_Purchase_To_Sales_Ratio)`.
9. Do not use `AVG(AF_Purchase_To_Sales_Ratio)`.
10. Do not click the small connected-boxes icon beside `Reset`.
    - That icon opens `Paths Used`.
    - `Paths Used` is only for choosing join paths between related tables.
    - If it says `No paths used in this report`, that is not an error for this KPI.
11. Save / Apply the KPI editor.
12. Close the KPI editor.
13. Hover over the KPI card on the dashboard canvas.
14. Click the card's three-dot menu.
15. Click `Options`.
16. Keep `Apply Dashboard Filters` checked.
17. Click `Customize` beside `Apply Dashboard Filters`.
18. In the customize dialog, map only these filters for this card:
    - `Date Range` -> `FACT_Outlet_Daily_Health.activity_date`
    - `Outlet` -> `FACT_Outlet_Daily_Health.outlet_name`
19. Leave `Event Type` unmapped for this card.
20. Click `Apply`.
21. Save the dashboard.

If the KPI card menu does not show `Options`, fix the dashboard filters themselves:

1. Stay in dashboard `Edit Design`.
2. In the top `Filters` row, click the edit icon for `Outlet`.
3. Make sure the `Outlet` filter column is from:

```text
FACT_Outlet_Daily_Health.outlet_name
```

4. If it is coming only from `DIM_Outlet`, delete that dashboard filter for now.
5. Click `Add User Filter`.
6. Choose table `FACT_Outlet_Daily_Health`.
7. Choose column `outlet_name`.
8. Display name:

```text
Outlet
```

9. Save.
10. Repeat for `Date Range` using `FACT_Outlet_Daily_Health.activity_date`.

If Zoho does not let you choose the aggregate formula directly:

1. Delete the KPI card.
2. Add a new `KPI Widget`.
3. Source table: `FACT_Outlet_Daily_Health`.
4. Choose formula `AF_Purchase_To_Sales_Ratio` as the value.
5. Group By: blank.
6. Add filters:
   - `Date Range` -> `activity_date`
   - `Outlet` -> `outlet_name`
7. Label:

```text
Purchase-To-Sales Ratio
```

8. Save.

### 9.3 Quick Check: Revenue Per Inventory Rupee

The correct logic is:

```text
Revenue Per Avg Inventory Rupee =
SUM(net_sales) / average combined inventory value for the selected outlets and dates
```

This is a ratio. It must not be summed across outlets.

If one outlet shows `1.16`, another shows `1.27`, and two selected outlets show `2.43`, that means Zoho is probably doing:

```text
1.16 + 1.27 = 2.43
```

That is wrong for a ratio KPI.

### 9.4 Fix Revenue Per Inventory Rupee

Do not use the old formula if Zoho keeps adding it across outlets.

Create a fresh aggregate formula:

1. Open table `FACT_Outlet_Daily_Health`.
2. Click `Add`.
3. Choose `Aggregate Formula`.
4. Do not choose normal `Formula Column`.
5. Formula name:

```text
AF_Inventory_Turnover_Rupee
```

6. Formula:

```text
SUM("net_sales") * DISTINCTCOUNT("activity_date") / SUM("inventory_value")
```

7. Save.

This calculates:

```text
total selected net sales / average combined daily inventory value
```

So if two outlets are selected, it combines the two outlets first and then calculates the ratio. It does not add outlet-level ratios together.

Then fix the KPI widget:

1. Open dashboard `01_Executive_Outlet_Health`.
2. Click `Edit Design`.
3. Click KPI card `Revenue Per Inventory Rupee`.
4. Click edit / pencil.
5. Source table must be:

```text
FACT_Outlet_Daily_Health
```

6. Value must be:

```text
AF_Inventory_Turnover_Rupee
```

7. Group By must be blank.
8. Do not use `SUM(AF_Inventory_Turnover_Rupee)`.
9. Do not click the small connected-boxes icon beside `Reset`.
   - That icon opens `Paths Used`.
   - It is not the dashboard filter mapping dialog.
10. Save / Apply the KPI editor.
11. Close the KPI editor.
12. Hover over the KPI card on the dashboard canvas.
13. Click the card's three-dot menu.
14. Click `Options`.
15. Keep `Apply Dashboard Filters` checked.
16. Click `Customize` beside `Apply Dashboard Filters`.
17. Map only these filters:
   - `Date Range` -> `FACT_Outlet_Daily_Health.activity_date`
   - `Outlet` -> `FACT_Outlet_Daily_Health.outlet_name`
18. Leave `Event Type` unmapped for this card.
19. Click `Apply`.
20. Rename the KPI label:

```text
Revenue Per Avg Inventory Rupee
```

21. Save the dashboard.

### 9.5 Fix The Low Stock Label

The current card label in the screenshot says:

```text
Low Stock Item Count
```

That label is only correct if the card source is:

```text
SUM_Inventory_Risk.low_stock_flag
```

with calculation:

```text
SUM
```

If the card source is:

```text
FACT_Outlet_Daily_Health.low_stock_item_count
```

with calculation:

```text
SUM
```

then rename the label to:

```text
Inventory Pressure Item-Days
```

Reason:

`FACT_Outlet_Daily_Health.low_stock_item_count` is daily outlet-level pressure. Summing it across dates creates item-days, not a simple current item count.

### 9.6 What Looks Correct In The Screenshot

These values look logically consistent:

```text
6.26L + 6.27L + third outlet sales = 19.45L all-outlet sales
5.21L + 6.05L + third outlet spend = 16.27L all-outlet procurement spend
```

So the basic outlet filter is working for simple SUM cards.

The problem is specifically with calculated ratio cards.

### 9.7 Rule For Ratio KPIs

For any KPI that contains `/`, such as ratios:

1. Use an aggregate formula.
2. Do not create it as a normal row formula.
3. Do not sum the formula result.
4. Make sure the same dashboard filters apply to the formula's source table.

Good:

```text
SUM(po_value) / SUM(net_sales)
```

Bad:

```text
SUM(po_value / net_sales)
```

Bad:

```text
SUM(AF_Purchase_To_Sales_Ratio)
```

### 9.8 If A Tabular View Repeats Outlets Or Filters Weirdly

The screenshot with `Untitled-1` is not broken. It is the wrong report type for the question.

`FACT_Outlet_Daily_Health` is a daily fact table. Its grain is:

```text
one row per outlet per activity_date
```

So if you drag only `outlet_name` into a tabular report, Zoho will repeat the same outlet once for each matching date. That is expected.

The `net_sales` filter in that screenshot is also not filtering total outlet revenue. It is filtering each daily row where `net_sales` is `29000 and above`. That means it removes low-sales days and then shows duplicate outlet names.

Do not use this tabular view for executive outlet performance.

Use this instead for a dashboard-ready outlet summary table:

1. Click `+ Create`.
2. Choose `New Chart View` or `New Pivot View`.
3. Choose source table:

```text
FACT_Outlet_Daily_Health
```

4. If Zoho asks for chart type, choose `Pivot Table` or `Summary View`.
5. Rows:

```text
outlet_name
```

6. Values:

```text
net_sales                SUM
po_value                 SUM
inventory_value          SUM or AVG, depending on the table purpose
low_stock_item_count     SUM
event_count              SUM
```

7. Sort by:

```text
SUM(net_sales) descending
```

8. Do not add a filter on raw `net_sales` ranges.
9. If you want only top outlets, use report `Sort` and `Top N`, not a raw row-level `net_sales` range.
10. Save the report as:

```text
Outlet Performance Summary
```

11. Add this saved report to the dashboard.
12. Apply dashboard filters:
    - `Date Range` -> `FACT_Outlet_Daily_Health.activity_date`
    - `Outlet` -> `FACT_Outlet_Daily_Health.outlet_name`

Use a normal `Tabular View` only when you want row-level detail. If using a tabular view, include the grain columns so the repeated rows make sense:

```text
activity_date
outlet_name
net_sales
po_value
inventory_value
low_stock_item_count
health_note
```

Save that row-level report as:

```text
Daily Outlet Detail
```
