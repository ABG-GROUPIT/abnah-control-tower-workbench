# Ask Zia Semantic Query Tables

This folder contains a separate Ask Zia semantic layer.

Do not replace the dashboard query tables with these. The dashboard tables still drive the actual charts. These `ZIA_*` tables exist because Ask Zia was choosing technically valid but business-wrong columns such as event sales, baseline sales, or inventory snapshot dates for normal sales questions.

The new rule is:

```text
Dashboards use existing FACT/SUM tables.
Ask Zia uses these ZIA_* query tables.
RAW, STD, event, competitor, and most old FACT/SUM tables should be excluded or low priority for Ask Zia.
```

## Build Order In Zoho

Create these as Zoho Query Tables in this order:

| Order | Query table | File | Grain |
|---:|---|---|---|
| 1 | `ZIA_Executive_Outlet_Daily` | `01_zia_executive_outlet_daily.sql` | outlet + day |
| 2 | `ZIA_Executive_Outlet_Month` | `02_zia_executive_outlet_month.sql` | outlet + month |
| 3 | `ZIA_Sales_Menu_Daily_Item` | `03_zia_sales_menu_daily_item.sql` | outlet + day + menu item |
| 4 | `ZIA_Sales_Menu_Daily_Category` | `04_zia_sales_menu_daily_category.sql` | outlet + day + category |
| 5 | `ZIA_Sales_Menu_Item_Summary` | `05_zia_sales_menu_item_summary.sql` | outlet + menu item |
| 6 | `ZIA_Sales_Weekday_Category` | `06_zia_sales_weekday_category.sql` | outlet + month + weekday + category |
| 7 | `ZIA_Procurement_Daily_Vendor_Material` | `07_zia_procurement_daily_vendor_material.sql` | outlet + day + vendor + material + PO status |
| 8 | `ZIA_Procurement_Monthly_Vendor` | `08_zia_procurement_monthly_vendor.sql` | outlet + month + vendor |
| 9 | `ZIA_Pending_PO_Detail` | `09_zia_pending_po_detail.sql` | pending/partial PO material line |
| 10 | `ZIA_Current_Inventory_Snapshot` | `10_zia_current_inventory_snapshot.sql` | outlet + latest material snapshot |
| 11 | `ZIA_Inventory_Daily_Trend` | `11_zia_inventory_daily_trend.sql` | outlet + day + material category |
| 12 | `ZIA_Theoretical_Demand_Daily` | `12_zia_theoretical_demand_daily.sql` | outlet + day + menu item + ingredient/material |
| 13 | `ZIA_Theoretical_Demand_Summary` | `13_zia_theoretical_demand_summary.sql` | outlet + demand type + material |

## Why These Tables Work

The existing query tables work because each has a clear grain:

| Existing table | Why it works | How Zia table uses it |
|---|---|---|
| `FACT_Outlet_Daily_Health` | One row per outlet per day; clean executive daily metrics | Daily and monthly executive Zia tables |
| `FACT_Sales` | One row per outlet/date/menu item; date-safe sales grain | Item, category, and weekday sales Zia tables |
| `SUM_Menu_Item_Performance` | One row per outlet/menu item for the loaded period | Menu item detail and value-vs-volume Zia table |
| `FACT_Vendor_Spend` | One row per date/outlet/vendor/material/status with PO and receipt movement | Procurement daily and monthly vendor Zia tables |
| `FACT_PO_Receipt_Comparison` | PO line plus matched receipt approximation | Pending PO detail Zia table |
| Raw inventory closing feeds | One imported table per outlet with daily stock snapshots | Current inventory Zia table, to avoid Zoho's 5-level query-over-query limit |
| `FACT_Inventory_Closing` | Daily inventory snapshot | Inventory trend Zia table |
| `FACT_Theoretical_Consumption` | Sales multiplied by recipe BOM | Theoretical demand Zia tables |

`ZIA_Current_Inventory_Snapshot` intentionally does not use `SUM_Inventory_Risk`. The dashboard can still use `SUM_Inventory_Risk`, but Ask Zia query 10 must stay shallow enough for Zoho to save it.

## Ask Zia Priority Setup

In `Ask Zia -> Manage Synonyms`, set priority like this:

| Table group | Priority |
|---|---|
| `ZIA_*` tables in this folder | High |
| `RAW_*` | Exclude, or Low if exclude is unavailable |
| `STD_*` | Exclude, or Low if exclude is unavailable |
| `FACT_Event_Sales_Impact`, `SUM_Event_Impact`, `SUM_Event_Markers` | Exclude/Low unless event demo is active |
| `SUM_Competitor_Positioning`, `FACT_Competitor_Price_Position` | Exclude/Low unless competitor demo is active |
| Old `FACT_*` and `SUM_*` dashboard tables | Low after `ZIA_*` tables are ready |
| `DIM_*` | Low |

This is important. If the old event tables stay High, Ask Zia can keep answering normal net sales questions with `event_day_sales`, `baseline_sales`, or `sales_lift_value`.

## Table Synonyms To Paste

| ZIA table | Table synonyms |
|---|---|
| `ZIA_Executive_Outlet_Daily` | daily outlet health, daily executive scorecard, outlet daily sales, daily cafe performance |
| `ZIA_Executive_Outlet_Month` | monthly outlet health, monthly executive scorecard, outlet monthly sales, net sales by outlet, purchase to sales by outlet |
| `ZIA_Sales_Menu_Daily_Item` | menu item sales, item sales, daily item revenue, top menu items, item quantity |
| `ZIA_Sales_Menu_Daily_Category` | category sales, category revenue, menu category mix, category trend |
| `ZIA_Sales_Menu_Item_Summary` | menu winners, menu item performance, revenue versus quantity, realized price, menu rate |
| `ZIA_Sales_Weekday_Category` | weekday sales, day of week sales, weekday heatmap, category by weekday |
| `ZIA_Procurement_Daily_Vendor_Material` | procurement daily, vendor spend daily, material purchase, PO and receipt movement |
| `ZIA_Procurement_Monthly_Vendor` | vendor monthly scorecard, top vendors, PO receipt gap, receipt coverage |
| `ZIA_Pending_PO_Detail` | pending PO detail, partial PO detail, PO follow up, pending quantity |
| `ZIA_Current_Inventory_Snapshot` | current inventory, latest stock, current stock pressure, low stock, watch materials |
| `ZIA_Inventory_Daily_Trend` | inventory trend, daily inventory value, stock value trend |
| `ZIA_Theoretical_Demand_Daily` | daily theoretical demand, recipe demand daily, packaging demand daily, ingredient demand trend |
| `ZIA_Theoretical_Demand_Summary` | top ingredients, top packaging materials, theoretical demand summary, recipe demand summary |

## Core Column Synonyms

Use these column synonym patterns across all `ZIA_*` tables where the column exists.

| Column | Synonyms | Default function |
|---|---|---|
| `business_date` | date, day, business date, sales date, procurement date, inventory date | Actual / Date |
| `month_key` | month, month key, year month, reporting month | Actual |
| `outlet_name` | outlet, cafe, store, branch, location | Actual / Group by |
| `market_area` | market, area, locality | Actual / Group by |
| `net_sales` | net sales, sales, revenue, sales revenue, outlet sales, menu sales | Sum |
| `menu_units_sold` | units sold, menu units, quantity sold, item quantity | Sum |
| `po_raised_value` | PO raised value, ordered value, purchase order value, procurement spend | Sum |
| `receipt_booked_value` | receipt booked value, received value, GRN value, goods received value | Sum |
| `po_receipt_gap_value` | PO receipt gap, order receipt gap, pending value gap | Sum |
| `purchase_to_sales_pct` | purchase to sales ratio, PO to sales ratio, procurement pressure | Average |
| `menu_item_name` | menu item, item, dish, drink, product | Actual / Group by |
| `category` | category, menu category, product category | Actual / Group by |
| `super_category` | super category, broad category | Actual / Group by |
| `day_of_week_name` | weekday, day of week, sales weekday | Actual / Group by |
| `vendor_name` | vendor, supplier, procurement partner | Actual / Group by |
| `material_name` | material, ingredient, inventory item, supply item | Actual / Group by |
| `material_category` | material category, inventory category, ingredient category | Actual / Group by |
| `current_inventory_value` | current inventory value, latest stock value, inventory value | Sum |
| `current_stock_qty` | current stock quantity, stock on hand, inventory quantity | Sum |
| `low_stock_flag` | low stock count, low stock items | Sum |
| `watch_material_flag` | watch material count, stock pressure count, current watch material count | Sum |
| `theoretical_demand_qty` | theoretical demand, recipe demand, packaging demand, ingredient demand | Sum |
| `demand_component_type` | recipe or packaging, demand type, component type | Actual / Group by |

Do not use generic `sales` synonyms on event/baseline/lift columns in optional event tables.

## Question Bank And Expected Month 1 Answers

Use these after building the `ZIA_*` tables.

| Question to ask | Expected ZIA table | Expected answer / check |
|---|---|---|
| Show net sales by outlet for January 2026 | `ZIA_Executive_Outlet_Month` | Saket `6.92L`, Hauz Khas `6.27L`, Connaught `6.26L`; total about `19.45L` |
| Which outlet had the highest net sales in January 2026? | `ZIA_Executive_Outlet_Month` | `ABNAH Cafe Saket Premium` |
| Show purchase to sales ratio by outlet for January 2026 | `ZIA_Executive_Outlet_Month` | Hauz Khas highest at about `96.5%` |
| Show PO raised and receipt booked by outlet for January 2026 | `ZIA_Executive_Outlet_Month` | Saket `5.02L/3.89L`, Hauz `6.05L/4.41L`, Connaught `5.21L/3.88L` |
| Top 5 menu items by net sales for Connaught Place | `ZIA_Sales_Menu_Daily_Item` or `ZIA_Sales_Menu_Item_Summary` | Top item `Cappuccino - Medium`, about `17.85K` |
| Top 5 menu items by quantity for Hauz Khas | `ZIA_Sales_Menu_Daily_Item` or `ZIA_Sales_Menu_Item_Summary` | Top volume item `Americano - Medium`, `69` units |
| Which category has highest revenue for Connaught Place? | `ZIA_Sales_Menu_Daily_Category` | `Coffee Classics`, about `2.07L` |
| Which weekday has highest sales by category? | `ZIA_Sales_Weekday_Category` | Should return weekday names, not numbers |
| Which vendor has highest PO raised value for Saket? | `ZIA_Procurement_Monthly_Vendor` | `FreshDairy Foods NCR`, about `1.59L` |
| Which vendor has highest PO receipt gap for Hauz Khas? | `ZIA_Procurement_Monthly_Vendor` | `FreshDairy Foods NCR`, gap about `85.74K` |
| Which materials have highest pending quantity? | `ZIA_Pending_PO_Detail` | Material ranking by `remaining_qty` or `unmatched_order_qty` |
| Show current inventory value by outlet | `ZIA_Current_Inventory_Snapshot` | Connaught about `6.13L`, Hauz about `6.77L`, Saket about `6.02L` |
| Which outlet has most current low stock items? | `ZIA_Current_Inventory_Snapshot` | Hauz and Saket have `2` low items; Connaught has `1` |
| Which inventory category has highest current value for Hauz Khas? | `ZIA_Current_Inventory_Snapshot` | `Syrups & Sauces`, about `1.06L` |
| Which recipe ingredients have highest theoretical demand for Saket? | `ZIA_Theoretical_Demand_Summary` | Filter demand type to Recipe Ingredient |
| Which packaging materials have highest theoretical demand? | `ZIA_Theoretical_Demand_Summary` | Filter demand type to Packaging Consumable; packaging examples include Napkin, Lid, Cup |

## Test Prompts To Force Correct Table Choice

If Ask Zia still chooses a wrong table, ask one of these explicit prompts while tuning synonyms:

```text
Using monthly outlet health, show net sales by outlet for January 2026
Using menu item sales, show top 5 menu items by net sales for Connaught Place
Using weekday sales, show net sales by weekday and category for January 2026
Using vendor monthly scorecard, show PO raised value by vendor for Hauz Khas
Using current inventory, show inventory value by outlet
Using theoretical demand summary, show top packaging materials by demand
```

Once those work, shorten the prompts naturally.

## Acceptance Rule

Ask Zia is acceptable only when a plain question like:

```text
Show net sales by outlet for January 2026
```

uses `ZIA_Executive_Outlet_Month` or `ZIA_Executive_Outlet_Daily`, not event, baseline, competitor, inventory, or raw tables.
