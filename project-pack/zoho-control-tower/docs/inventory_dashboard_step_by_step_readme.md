# Inventory And Consumption Dashboard Step-By-Step Build README

This README is only for the Inventory and Consumption dashboard. It is written to prevent the filter issues that came up in Zoho.

The main rule:

```text
Current inventory visuals use SUM_Inventory_Risk.
Historical inventory trend visuals use FACT_Inventory_Closing.
Theoretical ingredient demand visuals use FACT_Theoretical_Consumption.
```

Do not use one chart source for all three ideas. They answer different questions.

## 1. Business Meaning Of The Three Metric Families

### 1.1 Current Inventory Value

Meaning:

```text
How much money is currently sitting in stock?
```

Zoho source:

```text
SUM_Inventory_Risk
```

Metric:

```text
SUM(total_amt)
```

Data logic:

```text
total_amt = latest total_qty * average_price
```

This is a latest-snapshot metric. It should not be summed across all inventory dates.

### 1.2 Current Low-Stock Material Count

Meaning:

```text
How many current inventory materials are in low-stock condition?
```

Zoho source:

```text
SUM_Inventory_Risk
```

Metric:

```text
SUM(low_stock_flag)
```

Flag logic:

```text
total_qty <= 10 -> low_stock_flag = 1
total_qty > 10  -> low_stock_flag = 0
```

This is a count of risky material rows, not a stock quantity.

### 1.3 Current Stock Pressure Band

Meaning:

```text
Which materials are Low, Watch, or OK based on current stock quantity?
```

Zoho source:

```text
SUM_Inventory_Risk
```

Band logic:

```text
total_qty <= 10             -> Low
total_qty > 10 and <= 25    -> Watch
total_qty > 25              -> OK
```

Important caveat:

```text
This is a demo pressure heuristic, not a production stockout forecast.
```

Production stockout forecasting would need reorder level, vendor lead time, opening stock, transfers, wastage, expiry, and actual consumption posting.

### 1.4 Theoretical Ingredient Demand From Menu Sales

Meaning:

```text
Based on menu items sold, how much ingredient should have been consumed according to the recipe BOM?
```

Zoho source:

```text
FACT_Theoretical_Consumption
```

Metric:

```text
SUM(theoretical_ingredient_qty)
```

Data logic:

```text
sold menu qty * recipe ingredient qty / recipe output qty
```

Example:

```text
100 Cappuccino - Medium sold
recipe uses 0.018 kg coffee beans per item
theoretical ingredient demand = 1.8 kg coffee beans
```

This is not current inventory value. It is sales-driven material demand.

## 2. Dashboard User Filters To Create

Create only these user filters for this dashboard.

Do not create a generic filter unless it is mapped to every table listed here.

### 2.1 Filter List

| Filter label in dashboard | Primary table / column | Purpose | Should affect current-stock KPIs? | Should affect theoretical-demand visuals? |
|---|---|---|---|---|
| `Outlet` | `DIM_Outlet.outlet_name` or direct source mappings below | Select cafe/outlet | Yes | Yes |
| `Inventory Category` | `SUM_Inventory_Risk.category_name` | Filter current stock by inventory category | Yes | No |
| `Inventory Item` | `SUM_Inventory_Risk.item_name` | Filter current stock by inventory item/material | Yes | No |
| `Stock Pressure Band` | `SUM_Inventory_Risk.inventory_pressure_band` | Filter current stock by Low/Watch/OK | Yes | No |
| `Sales Date Range` | `FACT_Theoretical_Consumption.sales_date` | Filter recipe demand by sales date | No | Yes |
| `Demand Component Type` | `FACT_Theoretical_Consumption.demand_component_type` | Split true recipe ingredients from packaging consumables | No | Yes |
| `Demand Ingredient` | `FACT_Theoretical_Consumption.ingredient_name` | Filter theoretical ingredient demand | No | Yes |
| `Menu Category` | `FACT_Theoretical_Consumption.category` | Filter theoretical demand by sold menu category | No | Yes |
| `Menu Item` | `FACT_Theoretical_Consumption.menu_item_name` | Filter theoretical demand by sold menu item | No | Yes |

### 2.2 Why There Are Separate Item Filters

`Inventory Item` and `Demand Ingredient` look similar, but they are not the same dashboard filter.

`Inventory Item` filters current stock:

```text
SUM_Inventory_Risk.item_name
```

`Demand Ingredient` filters recipe demand:

```text
FACT_Theoretical_Consumption.ingredient_name
```

If you select a `Demand Ingredient`, the current inventory value KPI may not change unless Zoho maps that same filter to `SUM_Inventory_Risk.item_name`. That mismatch caused confusion earlier.

Use separate filters first. After the dashboard works, you can attempt an advanced combined material filter.

## 3. Exact User Filter Mapping

In dashboard edit mode:

1. Click `Add User Filter`.
2. Create the filter.
3. Open the filter settings.
4. Find `Apply To` / `Associated Reports` / `Affected Reports`.
5. Map only to the views listed below.
6. Do not force a filter onto a chart whose source table does not contain the mapped column.

### 3.1 `Outlet` Filter Mapping

Map `Outlet` to every report on this dashboard.

| Dashboard object | Source table | Map `Outlet` to |
|---|---|---|
| `KPI_Current_Inventory_Value` | `SUM_Inventory_Risk` | `outlet_name` |
| `KPI_Current_Low_Stock_Material_Count` | `SUM_Inventory_Risk` | `outlet_name` |
| `KPI_Current_Watch_Material_Count` | `SUM_Inventory_Risk` | `outlet_name` |
| `KPI_Theoretical_Ingredient_Demand` | `FACT_Theoretical_Consumption` | `outlet_name` |
| `CH21_Inventory_Value_By_Category` | `SUM_Inventory_Risk` | `outlet_name` |
| `CH22_Current_Stock_Pressure_Band` | `SUM_Inventory_Risk` | `outlet_name` |
| `CH23_Top_Inventory_Value_Items` | `SUM_Inventory_Risk` | `outlet_name` |
| `CH24_Low_Stock_Items` | `SUM_Inventory_Risk` | `outlet_name` |
| `CH25_Inventory_Value_Trend` | `FACT_Inventory_Closing` | `outlet_name` |
| `CH26_Top_Theoretical_Ingredients` | `FACT_Theoretical_Consumption` | `outlet_name` |
| `CH27_Theoretical_Demand_Trend` | `FACT_Theoretical_Consumption` | `outlet_name` |
| `TB07_Low_Stock_Detail` | `SUM_Inventory_Risk` | `outlet_name` |
| `TB08_Menu_To_Material_Demand` | `FACT_Theoretical_Consumption` | `outlet_name` |
| `TB09_Stock_Vs_Theoretical_Demand` | `SUM_Inventory_Risk` | `outlet_name` |

### 3.2 `Inventory Category` Filter Mapping

Map this only to current-stock visuals.

| Dashboard object | Source table | Map `Inventory Category` to |
|---|---|---|
| `KPI_Current_Inventory_Value` | `SUM_Inventory_Risk` | `category_name` |
| `KPI_Current_Low_Stock_Material_Count` | `SUM_Inventory_Risk` | `category_name` |
| `KPI_Current_Watch_Material_Count` | `SUM_Inventory_Risk` | `category_name` |
| `CH21_Inventory_Value_By_Category` | `SUM_Inventory_Risk` | `category_name` |
| `CH22_Current_Stock_Pressure_Band` | `SUM_Inventory_Risk` | `category_name` |
| `CH23_Top_Inventory_Value_Items` | `SUM_Inventory_Risk` | `category_name` |
| `CH24_Low_Stock_Items` | `SUM_Inventory_Risk` | `category_name` |
| `TB07_Low_Stock_Detail` | `SUM_Inventory_Risk` | `category_name` |
| `TB09_Stock_Vs_Theoretical_Demand` | `SUM_Inventory_Risk` | `category_name` |

Do not map this to `FACT_Theoretical_Consumption.category`. That column is menu category, not inventory category.

### 3.3 `Inventory Item` Filter Mapping

Map this only to current-stock visuals.

| Dashboard object | Source table | Map `Inventory Item` to |
|---|---|---|
| `KPI_Current_Inventory_Value` | `SUM_Inventory_Risk` | `item_name` |
| `KPI_Current_Low_Stock_Material_Count` | `SUM_Inventory_Risk` | `item_name` |
| `KPI_Current_Watch_Material_Count` | `SUM_Inventory_Risk` | `item_name` |
| `CH21_Inventory_Value_By_Category` | `SUM_Inventory_Risk` | `item_name` |
| `CH22_Current_Stock_Pressure_Band` | `SUM_Inventory_Risk` | `item_name` |
| `CH23_Top_Inventory_Value_Items` | `SUM_Inventory_Risk` | `item_name` |
| `CH24_Low_Stock_Items` | `SUM_Inventory_Risk` | `item_name` |
| `TB07_Low_Stock_Detail` | `SUM_Inventory_Risk` | `item_name` |
| `TB09_Stock_Vs_Theoretical_Demand` | `SUM_Inventory_Risk` | `item_name` |

### 3.4 `Stock Pressure Band` Filter Mapping

Map this only to current-stock visuals.

| Dashboard object | Source table | Map `Stock Pressure Band` to |
|---|---|---|
| `KPI_Current_Inventory_Value` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `KPI_Current_Low_Stock_Material_Count` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `KPI_Current_Watch_Material_Count` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `CH21_Inventory_Value_By_Category` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `CH22_Current_Stock_Pressure_Band` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `CH23_Top_Inventory_Value_Items` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `CH24_Low_Stock_Items` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `TB07_Low_Stock_Detail` | `SUM_Inventory_Risk` | `inventory_pressure_band` |
| `TB09_Stock_Vs_Theoretical_Demand` | `SUM_Inventory_Risk` | `inventory_pressure_band` |

### 3.5 `Sales Date Range` Filter Mapping

Map this only to demand and historical-date visuals.

| Dashboard object | Source table | Map `Sales Date Range` to |
|---|---|---|
| `KPI_Theoretical_Ingredient_Demand` | `FACT_Theoretical_Consumption` | `sales_date` |
| `CH26_Top_Theoretical_Ingredients` | `FACT_Theoretical_Consumption` | `sales_date` |
| `CH27_Theoretical_Demand_Trend` | `FACT_Theoretical_Consumption` | `sales_date` |
| `TB08_Menu_To_Material_Demand` | `FACT_Theoretical_Consumption` | `sales_date` |

Do not map `Sales Date Range` to `SUM_Inventory_Risk`. That table is latest inventory only.

If you build `CH25_Inventory_Value_Trend`, create a separate filter label:

```text
Inventory Date Range
```

Map it to:

```text
FACT_Inventory_Closing.inventory_date
```

### 3.6 `Demand Ingredient` Filter Mapping

Map this only to theoretical-demand visuals.

| Dashboard object | Source table | Map `Demand Ingredient` to |
|---|---|---|
| `KPI_Theoretical_Ingredient_Demand` | `FACT_Theoretical_Consumption` | `ingredient_name` |
| `CH26_Top_Theoretical_Ingredients` | `FACT_Theoretical_Consumption` | `ingredient_name` |
| `CH27_Theoretical_Demand_Trend` | `FACT_Theoretical_Consumption` | `ingredient_name` |
| `TB08_Menu_To_Material_Demand` | `FACT_Theoretical_Consumption` | `ingredient_name` |

### 3.7 `Demand Component Type` Filter Mapping

Map this only to theoretical-demand visuals.

| Dashboard object | Source table | Map `Demand Component Type` to |
|---|---|---|
| `KPI_Theoretical_Ingredient_Demand` | `FACT_Theoretical_Consumption` | `demand_component_type` |
| `CH26_Top_Theoretical_Ingredients` | `FACT_Theoretical_Consumption` | `demand_component_type` |
| `CH27_Theoretical_Demand_Trend` | `FACT_Theoretical_Consumption` | `demand_component_type` |
| `TB08_Menu_To_Material_Demand` | `FACT_Theoretical_Consumption` | `demand_component_type` |

Use these values:

```text
Recipe Ingredient
Packaging Consumable
```

Default dashboard selection for `CH26_Top_Theoretical_Ingredients` should be:

```text
Demand Component Type = Recipe Ingredient
```

This prevents Napkin, Lid, Straw, Cups, and Boxes from dominating an ingredient chart.

### 3.8 `Menu Category` Filter Mapping

Map this only to theoretical-demand visuals.

| Dashboard object | Source table | Map `Menu Category` to |
|---|---|---|
| `KPI_Theoretical_Ingredient_Demand` | `FACT_Theoretical_Consumption` | `category` |
| `CH26_Top_Theoretical_Ingredients` | `FACT_Theoretical_Consumption` | `category` |
| `CH27_Theoretical_Demand_Trend` | `FACT_Theoretical_Consumption` | `category` |
| `TB08_Menu_To_Material_Demand` | `FACT_Theoretical_Consumption` | `category` |

### 3.9 `Menu Item` Filter Mapping

Map this only to theoretical-demand visuals.

| Dashboard object | Source table | Map `Menu Item` to |
|---|---|---|
| `KPI_Theoretical_Ingredient_Demand` | `FACT_Theoretical_Consumption` | `menu_item_name` |
| `CH26_Top_Theoretical_Ingredients` | `FACT_Theoretical_Consumption` | `menu_item_name` |
| `CH27_Theoretical_Demand_Trend` | `FACT_Theoretical_Consumption` | `menu_item_name` |
| `TB08_Menu_To_Material_Demand` | `FACT_Theoretical_Consumption` | `menu_item_name` |

## 4. KPI Build Steps

Build these KPI widgets in this order.

### 4.1 KPI: Current Inventory Value

1. Create `KPI Widget`.
2. Source table:

```text
SUM_Inventory_Risk
```

3. Data column:

```text
total_amt
```

4. Show value as:

```text
Sum
```

5. Label:

```text
Current Inventory Value
```

6. Format:

```text
Currency / INR
```

7. Connect filters:

```text
Outlet
Inventory Category
Inventory Item
Stock Pressure Band
```

Do not connect `Sales Date Range`.

### 4.2 KPI: Current Low-Stock Material Count

1. Create `KPI Widget`.
2. Source table:

```text
SUM_Inventory_Risk
```

3. Data column:

```text
low_stock_flag
```

4. Show value as:

```text
Sum
```

5. Label:

```text
Current Low-Stock Material Count
```

6. Format:

```text
Number, 0 decimals
```

7. Connect filters:

```text
Outlet
Inventory Category
Inventory Item
Stock Pressure Band
```

### 4.3 KPI: Current Watch Material Count

Zoho KPI widgets may not support conditional count easily. If available, create an aggregate formula on `SUM_Inventory_Risk`.

Formula name:

```text
AF_Watch_Material_Count
```

Formula logic:

```text
COUNT_IF("inventory_pressure_band" = 'Watch')
```

If Zoho does not support `COUNT_IF`, skip this KPI and use the pressure band chart instead.

Label:

```text
Current Watch Material Count
```

Source:

```text
SUM_Inventory_Risk
```

Connect filters:

```text
Outlet
Inventory Category
Inventory Item
Stock Pressure Band
```

### 4.4 KPI: Theoretical Ingredient Demand From Menu Sales

1. Create `KPI Widget`.
2. Source table:

```text
FACT_Theoretical_Consumption
```

3. Data column:

```text
theoretical_ingredient_qty
```

4. Show value as:

```text
Sum
```

5. Label:

```text
Theoretical Ingredient Demand From Menu Sales
```

6. Format:

```text
Number, 1 decimal
```

7. Connect filters:

```text
Outlet
Sales Date Range
Demand Component Type
Demand Ingredient
Menu Category
Menu Item
```

Do not connect:

```text
Inventory Category
Inventory Item
Stock Pressure Band
```

## 5. Chart Build Steps

### 5.1 Chart: Inventory Value By Category

Purpose:

```text
Where is current stock value concentrated?
```

Build:

```text
View type: Chart View
Source table: SUM_Inventory_Risk
Chart type: Horizontal bar
X-axis: category_name
Y-axis: total_amt
Y-axis aggregation: Sum
Color: super_category_name
Sort: SUM(total_amt) descending
Save as: CH21_Inventory_Value_By_Category
```

Connect filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

Do not connect `Sales Date Range`.

Expected Month 1 validation:

```text
All outlets current inventory value should be about 18.92L.
Connaught Place should be about 6.13L.
Hauz Khas should be about 6.77L.
Saket Premium should be about 6.02L.
```

### 5.2 Chart: Current Stock Pressure Band

Purpose:

```text
How many current materials are Low, Watch, and OK?
```

Build:

```text
View type: Chart View
Source table: SUM_Inventory_Risk
Chart type: Donut or stacked bar
X-axis / dimension: inventory_pressure_band
Y-axis / measure: item_code
Aggregation: Count Distinct
Color: inventory_pressure_band
Save as: CH22_Current_Stock_Pressure_Band
```

Connect filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

### 5.3 Chart: Top Inventory Value Items

Purpose:

```text
Which current materials hold the most inventory value?
```

Build:

```text
View type: Chart View
Source table: SUM_Inventory_Risk
Chart type: Horizontal bar
X-axis: item_name
Y-axis: total_amt
Y-axis aggregation: Sum
Color: category_name
Sort: SUM(total_amt) descending
Top N: 10
Save as: CH23_Top_Inventory_Value_Items
```

Connect filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

### 5.4 Chart: Low Stock Items

Purpose:

```text
Which materials are currently low-stock?
```

Build:

```text
View type: Chart View
Source table: SUM_Inventory_Risk
Chart type: Horizontal bar
X-axis: item_name
Y-axis: total_qty
Y-axis aggregation: Sum
Color: inventory_pressure_band
Criteria: low_stock_flag = 1
Sort: SUM(total_qty) ascending
Save as: CH24_Low_Stock_Items
```

Connect filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

### 5.5 Chart: Inventory Value Trend

Purpose:

```text
How did inventory value move over time?
```

Build this only if you want a date-aware inventory trend.

```text
View type: Chart View
Source table: FACT_Inventory_Closing
Chart type: Line
X-axis: inventory_date
Y-axis: total_amt
Y-axis aggregation: Sum
Color: outlet_name or category_name
Save as: CH25_Inventory_Value_Trend
```

Connect filters:

```text
Outlet -> FACT_Inventory_Closing.outlet_name
Inventory Date Range -> FACT_Inventory_Closing.inventory_date
```

Optional filters:

```text
Inventory Category -> FACT_Inventory_Closing.category_name
Inventory Item -> FACT_Inventory_Closing.item_name
```

Do not use this chart as the current inventory value KPI.

### 5.6 Chart: Top Theoretical Ingredients

Purpose:

```text
Which ingredients were demanded most by menu sales?
```

Build:

```text
View type: Chart View
Source table: FACT_Theoretical_Consumption
Chart type: Horizontal bar
X-axis: ingredient_name
Y-axis: theoretical_ingredient_qty
Y-axis aggregation: Sum
Color: ingredient_unit
Sort: SUM(theoretical_ingredient_qty) descending
Top N: 10
Save as: CH26_Top_Theoretical_Ingredients
```

Criteria:

```text
demand_component_type = 'Recipe Ingredient'
```

Connect filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Demand Component Type -> demand_component_type
Demand Ingredient -> ingredient_name
Menu Category -> category
Menu Item -> menu_item_name
```

If Zoho has not yet refreshed the updated `FACT_Theoretical_Consumption` table and `demand_component_type` is not visible, use this temporary chart criteria instead:

```text
ingredient_name NOT IN ('Napkin', 'Lid', 'Straw', 'Cold Cup', 'Hot Cup', 'Dessert Box', 'Sandwich Box', 'Wrap Packaging')
```

Expected top non-packaging items for Month 1 all outlets should include:

```text
Milk
Bread
Cake Base
Croissant Base
Ice
Coffee Beans
Sugar Syrup
```

### 5.7 Chart: Theoretical Demand Trend

Purpose:

```text
How did ingredient demand move over the selected sales dates?
```

Build:

```text
View type: Chart View
Source table: FACT_Theoretical_Consumption
Chart type: Line
X-axis: sales_date
Y-axis: theoretical_ingredient_qty
Y-axis aggregation: Sum
Color: ingredient_name
Save as: CH27_Theoretical_Demand_Trend
```

Connect filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Demand Component Type -> demand_component_type
Demand Ingredient -> ingredient_name
Menu Category -> category
Menu Item -> menu_item_name
```

Use this only for selected ingredients or Top N ingredients. If all ingredients are shown at once, the line chart will be noisy.

## 6. Table Build Steps

### 6.1 Table: Low Stock Detail

Purpose:

```text
Operational list of materials to review.
```

Build:

```text
View type: Table or Summary View
Source table: SUM_Inventory_Risk
Columns:
  item_code
  item_name
  category_name
  unit_name
  total_qty
  total_amt
  inventory_pressure_band
  total_theoretical_qty
  risk_note
Criteria:
  low_stock_flag = 1
Sort:
  inventory_pressure_band ascending
  total_qty ascending
Save as:
  TB07_Low_Stock_Detail
```

Connect filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

### 6.2 Table: Menu To Material Demand

Purpose:

```text
Shows which menu items create demand for which ingredients.
```

Build:

```text
View type: Pivot or Summary View
Source table: FACT_Theoretical_Consumption
Rows:
  menu_item_name
  ingredient_name
Values:
  SUM(sold_qty)
  SUM(theoretical_ingredient_qty)
Optional columns:
  category
  ingredient_unit
  demand_component_type
Sort:
  SUM(theoretical_ingredient_qty) descending
Save as:
  TB08_Menu_To_Material_Demand
```

Connect filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Demand Component Type -> demand_component_type
Demand Ingredient -> ingredient_name
Menu Category -> category
Menu Item -> menu_item_name
```

### 6.3 Table: Stock Vs Theoretical Demand

Purpose:

```text
Current stock context plus sales-derived demand context in one list.
```

Build:

```text
View type: Table or Summary View
Source table: SUM_Inventory_Risk
Columns:
  item_name
  category_name
  unit_name
  total_qty
  total_amt
  total_theoretical_qty
  inventory_pressure_band
  risk_note
Sort:
  risk_note
  total_theoretical_qty descending
Save as:
  TB09_Stock_Vs_Theoretical_Demand
```

Connect filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

Caveat:

```text
total_theoretical_qty in SUM_Inventory_Risk is not date-filtered. Use FACT_Theoretical_Consumption for date-specific demand.
```

## 7. Recommended Dashboard Layout

Use this layout.

### Row 1: Filters

Left to right:

```text
Outlet
Inventory Category
Inventory Item
Stock Pressure Band
Sales Date Range
Demand Component Type
Demand Ingredient
Menu Category
Menu Item
Reset
```

If the row becomes too wide, put current-stock filters on row 1 and theoretical-demand filters on row 2.

### Row 2: KPI Cards

Left to right:

```text
Current Inventory Value
Current Low-Stock Material Count
Current Watch Material Count
Theoretical Ingredient Demand From Menu Sales
```

### Row 3: Current Stock Visuals

Left:

```text
CH21_Inventory_Value_By_Category
```

Right:

```text
CH22_Current_Stock_Pressure_Band
```

### Row 4: Current Stock Drilldown

Left:

```text
CH23_Top_Inventory_Value_Items
```

Right:

```text
CH24_Low_Stock_Items
```

### Row 5: Demand Visuals

Left:

```text
CH26_Top_Theoretical_Ingredients
```

Right:

```text
CH27_Theoretical_Demand_Trend
```

### Row 6: Detail Tables

Left:

```text
TB07_Low_Stock_Detail
```

Right:

```text
TB08_Menu_To_Material_Demand
```

Optional full-width bottom:

```text
TB09_Stock_Vs_Theoretical_Demand
```

## 8. Validation Tests

Run these after building.

### 8.1 All-Outlets Current Inventory Test

Set:

```text
Outlet = All
Inventory Category = All
Inventory Item = All
Stock Pressure Band = All
```

Expected:

```text
Current Inventory Value about 18.92L
```

If it shows crores or a very large value, the KPI/chart is using `FACT_Inventory_Closing` and summing dates. Rebuild from `SUM_Inventory_Risk`.

### 8.2 Outlet Test

Set:

```text
Outlet = ABNAH Cafe Connaught Place
```

Expected:

```text
Current Inventory Value about 6.13L
```

Set:

```text
Outlet = ABNAH Cafe Hauz Khas
```

Expected:

```text
Current Inventory Value about 6.77L
```

Set:

```text
Outlet = ABNAH Cafe Saket Premium
```

Expected:

```text
Current Inventory Value about 6.02L
```

### 8.3 Inventory Item Test

Set:

```text
Inventory Item = Chicken
```

Expected:

```text
Current Inventory Value should change.
Current Low-Stock Material Count should change.
Current stock charts should change.
Theoretical demand charts should not change unless Demand Ingredient is also set to Chicken.
```

### 8.4 Demand Ingredient Test

Set:

```text
Demand Ingredient = Coffee Beans
```

Expected:

```text
Theoretical Ingredient Demand From Menu Sales should change.
Top Theoretical Ingredients should narrow or change.
Current Inventory Value should not change unless Inventory Item is also set to Coffee Beans.
```

### 8.5 Demand Component Type Test

Set:

```text
Demand Component Type = Recipe Ingredient
```

Expected:

```text
Top Theoretical Ingredients should stop showing Napkin, Lid, Straw, Cold Cup, Hot Cup, Dessert Box, Sandwich Box, and Wrap Packaging.
```

Set:

```text
Demand Component Type = Packaging Consumable
```

Expected:

```text
Top Theoretical Ingredients should intentionally show packaging/serving items such as Napkin, Lid, Straw, Cups, and Boxes.
```

### 8.6 Sales Date Range Test

Set:

```text
Sales Date Range = 2026-01-01 to 2026-01-07
```

Expected:

```text
Theoretical demand visuals should change.
Current inventory KPIs should not change.
```

This is correct because current stock is latest snapshot, while theoretical demand is sales-date driven.

## 9. Common Mistakes And Fixes

| Problem | Cause | Fix |
|---|---|---|
| Inventory value shows crores | Built from `FACT_Inventory_Closing` with `SUM(total_amt)` by category | Rebuild from `SUM_Inventory_Risk` |
| Inventory value does not change by item | `Inventory Item` filter not mapped to `SUM_Inventory_Risk.item_name` | Edit dashboard filter mapping |
| Theoretical demand does not change by date | `Sales Date Range` not mapped to `FACT_Theoretical_Consumption.sales_date` | Edit dashboard filter mapping |
| Top Theoretical Ingredients shows only packaging | Packaging consumables dominate count-based BOM quantities | Add criteria `demand_component_type = 'Recipe Ingredient'`, or temporarily exclude Napkin/Lid/Straw/Cups/Boxes by ingredient name |
| Theoretical demand changes but stock value does not | You selected `Demand Ingredient`, not `Inventory Item` | This is expected unless both filters are set |
| Pressure band is misunderstood as forecast | Band is quantity-threshold logic only | Use label `Current Stock Pressure Band`, not `Stockout Prediction` |
| Low-stock KPI shows quantity | KPI uses `total_qty` instead of `low_stock_flag` | Use `SUM(low_stock_flag)` |
| Current inventory chart changes with sales date | Date filter incorrectly mapped to latest-stock table | Remove date filter from `SUM_Inventory_Risk` visuals |

## 10. Optional Advanced Combined Material Filter

Only attempt this after the basic dashboard works.

Goal:

```text
One filter named Material / Ingredient changes both current stock and theoretical demand visuals.
```

Possible mapping:

```text
Material / Ingredient -> SUM_Inventory_Risk.item_name
Material / Ingredient -> FACT_Theoretical_Consumption.ingredient_name
Material / Ingredient -> FACT_Inventory_Closing.item_name
```

If Zoho does not allow this mapping cleanly, do not force it. Keep `Inventory Item` and `Demand Ingredient` separate.
