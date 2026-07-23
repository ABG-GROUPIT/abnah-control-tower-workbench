# Zoho Actual Data Model Build README

Use this after the small/main-data refresh test has proven that Zoho can refresh `RAW_Sales_Report_OUT001`, `RAW_Sales_Report_OUT002`, and `RAW_Sales_Report_OUT003` from FastAPI/ngrok feeds without duplicate `row_id` values.

This guide explains:

- how to keep Zoho imports attached to the correct RAW tables,
- which Query Table to create first,
- the exact build sequence,
- where each layer fits,
- how to validate before moving to the next layer,
- how to test Month 2, Month 3, and reset behavior after the model exists.

For the finished dashboard build, including lookup relationships, chart x-axis/y-axis fields, and module-wise page layout, use:

- `docs/zoho_dashboard_build_readme.md`

## 1. Start Only After RAW Refresh Is Proven

Before building the full model, complete:

- `docs/ngrok_fastapi_zoho_main_data_test_runbook.md`

Minimum proof required:

| Backend state | `RAW_Sales_Report_OUT001` | `RAW_Sales_Report_OUT002` | `RAW_Sales_Report_OUT003` | `STD_Sales_Report` after union | Duplicate `row_id` check |
|---|---:|---:|---:|---:|---|
| Month 1 | 1,529 | 1,595 | 1,731 | 4,855 | no rows |
| Month 1 + Month 2 | 3,003 | 3,088 | 3,325 | 9,416 | no rows |
| Month 1 + Month 2 + Month 3 | 4,623 | 4,747 | 5,206 | 14,576 | no rows |
| Reset back to Month 1 | 1,529 | 1,595 | 1,731 | 4,855 | no rows |

Do not build `STD_*`, `DIM_*`, `FACT_*`, or `SUM_*` tables if Zoho refresh is blindly appending the full CSV. That will duplicate rows in every downstream query table.

## 2. Reset To The Build Starting Point

For the actual month-update demo, build the Zoho model at Month 1, then test Month 2 and Month 3 refreshes.

Run:

```powershell
python manage_demo.py reset-to-month 1
python manage_demo.py status
```

Expected Month 1 operational rows:

| Neon table | Expected rows |
|---|---:|
| `raw.sales_report` | 4,855 |
| `raw.purchase_report` | 224 |
| `raw.entry_report` | 180 |
| `raw.inventory_closing_report` | 3,348 |

Keep FastAPI and the public tunnel running:

```powershell
scripts/run_api.bat
ngrok http 8000
```

Use the HTTPS ngrok URL in Zoho.

## 3. How To Force Imports Into The Correct RAW Tables

In Zoho, the important rule is: create each RAW table once, then refresh/re-fetch that same table. Operational tables are outlet-specific. Do not create new Month 2 or Month 3 tables.

### First Import

For each feed:

1. Choose Web URL/feed import.
2. Paste the FastAPI feed URL.
3. Choose create new table.
4. Name the table exactly as listed below.
5. Set first row as column headers.
6. Keep `row_id` as text.
7. Set dates as date columns where Zoho allows.
8. Save the import/data source settings.

### Future Refreshes

For Month 2, Month 3, and reset tests:

1. Do not create a new import.
2. Open the existing RAW table in Zoho.
3. Use the table's import/data-source settings.
4. Choose refresh, re-fetch, sync now, or update existing table.
5. If Zoho offers update/add by key, use `row_id`.
6. Prefer replace/re-fetch mode if available.
7. Avoid blind append.

If the ngrok URL changes, edit the existing table's source URL if Zoho allows it. Creating a new table with a new name will break the model. If Zoho does not allow editing the URL and you are still early in testing, delete the RAW table and recreate it with the same exact name before building query tables.

For a leadership demo, use hosted FastAPI or a stable tunnel URL so source URLs do not change.

## 4. RAW Tables To Import

Import these exact RAW table names.

| Build order | Zoho RAW table | FastAPI endpoint |
|---:|---|---|
| 1 | `RAW_Sales_Report_OUT001` | `/zoho/sales_report_OUT001.csv` |
| 2 | `RAW_Sales_Report_OUT002` | `/zoho/sales_report_OUT002.csv` |
| 3 | `RAW_Sales_Report_OUT003` | `/zoho/sales_report_OUT003.csv` |
| 4 | `RAW_Purchase_Report_OUT001` | `/zoho/purchase_report_OUT001.csv` |
| 5 | `RAW_Purchase_Report_OUT002` | `/zoho/purchase_report_OUT002.csv` |
| 6 | `RAW_Purchase_Report_OUT003` | `/zoho/purchase_report_OUT003.csv` |
| 7 | `RAW_Entry_Report_OUT001` | `/zoho/entry_report_OUT001.csv` |
| 8 | `RAW_Entry_Report_OUT002` | `/zoho/entry_report_OUT002.csv` |
| 9 | `RAW_Entry_Report_OUT003` | `/zoho/entry_report_OUT003.csv` |
| 10 | `RAW_Inventory_Closing_Report_OUT001` | `/zoho/inventory_closing_report_OUT001.csv` |
| 11 | `RAW_Inventory_Closing_Report_OUT002` | `/zoho/inventory_closing_report_OUT002.csv` |
| 12 | `RAW_Inventory_Closing_Report_OUT003` | `/zoho/inventory_closing_report_OUT003.csv` |
| 13 | `RAW_Menu_Master` | `/zoho/menu_master.csv` |
| 14 | `RAW_Vendor_Report` | `/zoho/vendor_report.csv` |
| 15 | `RAW_Brand_Recipe_Consumption` | `/zoho/brand_recipe_consumption.csv` |
| 16 | `RAW_Indian_Calendar_Holidays` | `/zoho/indian_calendar_holidays.csv` |
| 17 | `RAW_Manual_Calendar_Events` | `/zoho/manual_calendar_events.csv` |
| 18 | `RAW_Competitor_Pricing` | `/zoho/competitor_pricing.csv` |

With a token:

```text
https://<ngrok-url>/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
```

Without a token:

```text
https://<ngrok-url>/zoho/sales_report_OUT001.csv
```

## 5. Validate RAW Before Query Tables

Before creating any Query Table:

1. Confirm all 18 RAW tables exist.
2. Confirm Month 1 sales row counts are `1,529`, `1,595`, and `1,731` for `OUT001`, `OUT002`, and `OUT003`.
3. Confirm no duplicate sales `row_id`:

```sql
SELECT "row_id", COUNT(*) AS row_count
FROM "RAW_Sales_Report_OUT001"
GROUP BY "row_id"
HAVING COUNT(*) > 1
```

Repeat the duplicate query for `RAW_Sales_Report_OUT002` and `RAW_Sales_Report_OUT003`.

4. Confirm the key columns exist:

| RAW table | Must-have columns |
|---|---|
| `RAW_Sales_Report_OUT###` | `row_id`, `outlet_name`, `date`, `item_number`, `item_name`, `qty`, `net_sale` |
| `RAW_Purchase_Report_OUT###` | `row_id`, `deployment`, `vendor_name`, `po_number`, `po_date`, `item_code`, `total_item_cost` |
| `RAW_Entry_Report_OUT###` | `row_id`, `deployment_name`, `vendor_name`, `date`, `transaction_number`, `item_code`, `grand_total` |
| `RAW_Inventory_Closing_Report_OUT###` | `row_id`, `deployment`, `date`, `item_code`, `item_name`, `total_qty`, `total_amt` |
| `RAW_Menu_Master` | `row_id`, `item_number`, `item_name`, `rate`, `category_name` |
| `RAW_Vendor_Report` | `row_id`, `vendor_name`, `vendor_code` |
| `RAW_Brand_Recipe_Consumption` | `row_id`, `recipe_name`, `item_name`, `item_qty`, `item_unit` |
| `RAW_Indian_Calendar_Holidays` | `row_id`, `calendar_date`, `holiday_name` |
| `RAW_Manual_Calendar_Events` | `row_id`, `event_id`, `event_name`, `start_date`, `end_date` |
| `RAW_Competitor_Pricing` | `row_id`, `market_area`, `competitor_name`, `abnah_item_number`, `price_index` |

## 6. Where To Put Query Tables In Zoho

Create these as Zoho Query Tables in the same workspace as the RAW imports.

Use the exact table names:

- `STD_*` for standardization.
- `DIM_*` for reusable dimensions.
- `FACT_*` for analysis facts.
- `SUM_*` for dashboard summaries.

If Zoho lets you organize objects into folders, use:

- `01_RAW`
- `02_STD`
- `03_DIM`
- `04_FACT`
- `05_SUM`
- `06_DASHBOARDS`

If Zoho does not provide folders in your workspace view, the prefixes still keep the model understandable.

## 7. Build Layer 1 First: Standardized Tables

Create `STD_*` tables first. These clean the RAW imports and add outlet fields where needed.

Use SQL files from:

- `docs/zoho_query_table_sql/`

Build in this order:

| Order | Query Table | SQL file | Validate before next step |
|---:|---|---|---|
| 1 | `STD_Sales_Report` | `01_std_sales_report.sql` | Row count equals all three `RAW_Sales_Report_OUT###` tables combined; includes `outlet_code`, `outlet_name`, `market_area`. |
| 2 | `STD_Purchase_Report` | `02_std_purchase_report.sql` | Row count equals all three `RAW_Purchase_Report_OUT###` tables combined; includes outlet fields. |
| 3 | `STD_Entry_Report` | `03_std_entry_report.sql` | Row count equals all three `RAW_Entry_Report_OUT###` tables combined; includes outlet fields. |
| 4 | `STD_Inventory_Closing_Report` | `04_std_inventory_closing_report.sql` | Row count equals all three `RAW_Inventory_Closing_Report_OUT###` tables combined; includes outlet fields. |
| 5 | `STD_Menu_Master` | `05_std_menu_master.sql` | One row per menu item. |
| 6 | `STD_Vendor_Report` | `06_std_vendor_report.sql` | Vendor fields are available. |
| 7 | `STD_Recipe_BOM` | `07_std_recipe_bom.sql` | `recipe_name_filled` is populated on continuation rows. |
| 8 | `STD_Holiday_Calendar` | `08_std_holiday_calendar.sql` | Holiday dates are usable as dates. |
| 9 | `STD_Manual_Events` | `09_std_manual_events.sql` | Event date ranges are usable. |
| 10 | `STD_Competitor_Pricing` | `10_std_competitor_pricing.sql` | Includes `outlet_code`, `outlet_name`, `market_area`. |

First Query Table to make: `STD_Sales_Report`.

If `STD_Recipe_BOM` fails because Zoho does not support the fill-down SQL, stop before `FACT_Theoretical_Consumption`. Use the fallback documented in `docs/zoho_data_model_plan.md`.

## 8. Build Layer 2: Dimensions

Create dimensions after all `STD_*` tables exist.

| Order | Query Table | SQL file | Validate |
|---:|---|---|---|
| 1 | `DIM_Date` | `11_dim_date.sql` | Contains all sales dates. |
| 2 | `DIM_Outlet` | `12_dim_outlet.sql` | Contains `OUT001`, `OUT002`, `OUT003`. |
| 3 | `DIM_Menu_Item` | `13_dim_menu_item.sql` | Contains sold menu items. |
| 4 | `DIM_Vendor` | `14_dim_vendor.sql` | Contains purchase and entry vendors. |
| 5 | `DIM_Ingredient` | `15_dim_ingredient.sql` | Contains inventory/procurement/BOM materials. |
| 6 | `DIM_Event` | `16_dim_event.sql` | Contains manual events. |
| 7 | `DIM_Holiday` | `30_dim_holiday.sql` | Contains calendar markers. |
| 8 | `DIM_Competitor` | `31_dim_competitor.sql` | Contains competitor and market area fields. |

If `DIM_Date` fails due to date functions like `YEAR`, `MONTH`, or `LPAD`, create a simpler Query Table with only `date_value`, then add year/month formula columns in Zoho.

## 9. Build Layer 3: Facts

Create facts after dimensions.

| Order | Query Table | SQL file | Grain |
|---:|---|---|---|
| 1 | `FACT_Sales` | `17_fact_sales.sql` | Outlet + date + item |
| 2 | `FACT_Purchase_Order` | `18_fact_purchase_order.sql` | Outlet + PO line + item + vendor |
| 3 | `FACT_Entry_Receipt` | `19_fact_entry_receipt.sql` | Outlet + receipt line + item + vendor |
| 4 | `FACT_Inventory_Closing` | `20_fact_inventory_closing.sql` | Outlet + date + inventory item |
| 5 | `FACT_Theoretical_Consumption` | `21_fact_theoretical_consumption.sql` | Outlet + date + sold menu item + ingredient |
| 6 | `FACT_PO_Receipt_Comparison` | `22_fact_po_receipt_comparison.sql` | Outlet + PO line + item + vendor |
| 7 | `FACT_Event_Sales_Impact` | `23_fact_event_sales_impact.sql` | Outlet + event + date + category/item |
| 8 | `FACT_Competitor_Price_Position` | `24_fact_competitor_price_position.sql` | Outlet/market area + competitor + ABNAH item |
| 9 | `FACT_Outlet_Daily_Health` | `25_fact_outlet_daily_health.sql` | Outlet + date |
| 10 | `FACT_Vendor_Spend` | `32_fact_vendor_spend.sql` | Outlet + vendor + date/month |

Validation after key facts:

- `FACT_Sales` total `net_sale` should match `STD_Sales_Report`.
- `FACT_Purchase_Order` total `total_item_cost` should match `STD_Purchase_Report`.
- `FACT_Entry_Receipt` total `grand_total` should match `STD_Entry_Report`.
- `FACT_Inventory_Closing` should show latest stock by outlet and inventory item.
- `FACT_Theoretical_Consumption` should return rows for ingredients like Milk and Coffee Beans.
- `FACT_Event_Sales_Impact` should return rows for manual event dates.
- Every operational fact should include `outlet_code` or `outlet_name`.

If `FACT_Event_Sales_Impact` fails due to `DATEADD`, `CONCAT`, or correlated baseline logic, first create a simpler event-day-only table without baseline columns. Then calculate baseline/lift later using Zoho formulas or a second Query Table.

## 10. Build Layer 4: Summaries

Create summaries after facts.

| Order | Query Table | SQL file | Dashboard use |
|---:|---|---|---|
| 1 | `SUM_Executive_KPIs` | `33_sum_executive_kpis.sql` | Executive KPI tiles. |
| 2 | `SUM_Outlet_Health` | `34_sum_outlet_health.sql` | Cross-outlet comparison. |
| 3 | `SUM_Sales_Category_Mix` | `35_sum_sales_category_mix.sql` | Outlet-specific sales/menu. |
| 4 | `SUM_Menu_Item_Performance` | `36_sum_menu_item_performance.sql` | Outlet-specific menu ranking. |
| 5 | `SUM_Vendor_Share` | `26_sum_vendor_share.sql` | Outlet-specific procurement. |
| 6 | `SUM_Inventory_Risk` | `27_sum_inventory_risk.sql` | Outlet-specific inventory. |
| 7 | `SUM_Event_Impact` | `28_sum_event_impact.sql` | Outlet-specific event impact. |
| 8 | `SUM_Competitor_Positioning` | `29_sum_competitor_positioning.sql` | Outlet/market-area competitor context. |
| 9 | `SUM_Event_Markers` | `37_sum_event_markers.sql` | Spike explanation panel. |

Validation:

- `SUM_Executive_KPIs` may contain all-outlet totals.
- `SUM_Outlet_Health` should compare outlets.
- Every other `SUM_*` table should include `outlet_code`, `outlet_name`, or market-area fields.
- Non-executive summaries should not blend Connaught Place, Hauz Khas, and Saket without grouping by outlet.

## 11. Build Dashboards Last

Build dashboards only after RAW, STD, DIM, FACT, and SUM layers are validated.

Dashboard structure:

| Dashboard | Scope | Required behavior |
|---|---|---|
| Executive / Outlet Comparison / Outlet Health | Cross-outlet | Compares Connaught Place, Hauz Khas, and Saket. |
| Sales and Menu Intelligence | Outlet-specific | Mandatory outlet filter. |
| Vendor and Procurement Analytics | Outlet-specific | Mandatory outlet filter. |
| Inventory and Consumption Intelligence | Outlet-specific | Mandatory outlet filter. |
| Calendar, Event, and Competitor Intelligence | Outlet or market-area specific | Mandatory outlet or market-area filter. |

Preferred outlet-specific page pattern:

- `Sales_Menu_OUT001`
- `Sales_Menu_OUT002`
- `Sales_Menu_OUT003`

Repeat the same idea for procurement, inventory, and calendar/competitor dashboards.

Do not create separate SQL models per outlet unless Zoho cannot lock dashboard filters.

## 12. Create Lookup Relationships In Zoho

The Query Tables are already written with the fields needed for joins. After creating the tables, add lookup relationships in Zoho where the product allows them. This improves filtering, drilldown, Ask Zia behavior, and dashboard cross-filtering.

If Zoho does not allow a lookup on a Query Table in your workspace/version, do not block the build. The Query Tables already contain the key columns and many denormalized labels. Continue with dashboard filters using the fields directly, and document which lookup could not be created.

### Relationship Rules

- Create lookups after the relevant `DIM_*` and `FACT_*` tables exist.
- Use `DIM_*` tables as lookup targets.
- Use `FACT_*` tables and `SUM_*` tables as lookup sources.
- Do not create lookup relationships directly on RAW tables unless you need a RAW audit view.
- Prefer code keys where available, for example `outlet_code`, `item_number`, `item_code`.
- Use name keys only where the raw export does not provide a stable code, for example `vendor_name`.

### Required Lookup Relationships

| Source table | Source column | Lookup target table | Target column | Purpose |
|---|---|---|---|---|
| `FACT_Sales` | `sales_date` | `DIM_Date` | `date_value` | Date/month filters for sales. |
| `FACT_Sales` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet filters and outlet drilldown. |
| `FACT_Sales` | `item_number` | `DIM_Menu_Item` | `item_number` | Menu item/category drilldown. |
| `FACT_Purchase_Order` | `po_date` | `DIM_Date` | `date_value` | PO date filtering. |
| `FACT_Purchase_Order` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific procurement. |
| `FACT_Purchase_Order` | `vendor_name` | `DIM_Vendor` | `vendor_name` | Vendor filtering and details. |
| `FACT_Purchase_Order` | `item_code` | `DIM_Ingredient` | `ingredient_code` | Material/ingredient filtering. |
| `FACT_Entry_Receipt` | `receipt_date` | `DIM_Date` | `date_value` | Receipt date filtering. |
| `FACT_Entry_Receipt` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific receipts. |
| `FACT_Entry_Receipt` | `vendor_name` | `DIM_Vendor` | `vendor_name` | Receipt vendor filtering. |
| `FACT_Entry_Receipt` | `item_code` | `DIM_Ingredient` | `ingredient_code` | Receipt material filtering. |
| `FACT_Inventory_Closing` | `inventory_date` | `DIM_Date` | `date_value` | Inventory date filtering. |
| `FACT_Inventory_Closing` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific inventory. |
| `FACT_Inventory_Closing` | `item_code` | `DIM_Ingredient` | `ingredient_code` | Inventory material filtering. |
| `FACT_Theoretical_Consumption` | `sales_date` | `DIM_Date` | `date_value` | Consumption date filtering. |
| `FACT_Theoretical_Consumption` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific theoretical consumption. |
| `FACT_Theoretical_Consumption` | `item_number` | `DIM_Menu_Item` | `item_number` | Sold menu item drilldown. |
| `FACT_Theoretical_Consumption` | `ingredient_name` | `DIM_Ingredient` | `ingredient_name` | BOM material drilldown when item code is unavailable. |
| `FACT_Event_Sales_Impact` | `event_id` | `DIM_Event` | `event_id` | Event drilldown. |
| `FACT_Event_Sales_Impact` | `sales_date` | `DIM_Date` | `date_value` | Event date filtering. |
| `FACT_Event_Sales_Impact` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific event analysis. |
| `FACT_Event_Sales_Impact` | `item_number` | `DIM_Menu_Item` | `item_number` | Event item/category drilldown. |
| `FACT_Competitor_Price_Position` | `competitor_id` | `DIM_Competitor` | `competitor_id` | Competitor drilldown. |
| `FACT_Competitor_Price_Position` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet/market competitor filtering. |
| `FACT_Competitor_Price_Position` | `abnah_item_number` | `DIM_Menu_Item` | `item_number` | ABNAH item drilldown. |
| `FACT_Outlet_Daily_Health` | `activity_date` | `DIM_Date` | `date_value` | Daily health date filtering. |
| `FACT_Outlet_Daily_Health` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet comparison and drilldown. |
| `FACT_Vendor_Spend` | `activity_date` | `DIM_Date` | `date_value` | Vendor spend date filtering. |
| `FACT_Vendor_Spend` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific vendor spend. |
| `FACT_Vendor_Spend` | `vendor_name` | `DIM_Vendor` | `vendor_name` | Vendor spend drilldown. |

### Optional Lookup Relationships

| Source table | Source column | Lookup target table | Target column | When to use |
|---|---|---|---|---|
| `SUM_Outlet_Health` | `outlet_code` | `DIM_Outlet` | `outlet_code` | If Zoho dashboards need dimension-driven outlet filters on summary tables. |
| `SUM_Sales_Category_Mix` | `outlet_code` | `DIM_Outlet` | `outlet_code` | For outlet-specific category dashboards. |
| `SUM_Menu_Item_Performance` | `item_number` | `DIM_Menu_Item` | `item_number` | For menu item drilldown from summary charts. |
| `SUM_Menu_Item_Performance` | `outlet_code` | `DIM_Outlet` | `outlet_code` | For outlet-specific menu dashboards. |
| `SUM_Vendor_Share` | `vendor_name` | `DIM_Vendor` | `vendor_name` | For vendor detail drilldown. |
| `SUM_Vendor_Share` | `outlet_code` | `DIM_Outlet` | `outlet_code` | For outlet-specific procurement dashboards. |
| `SUM_Inventory_Risk` | `item_code` | `DIM_Ingredient` | `ingredient_code` | For inventory material drilldown. |
| `SUM_Inventory_Risk` | `outlet_code` | `DIM_Outlet` | `outlet_code` | For outlet-specific inventory dashboards. |
| `SUM_Event_Impact` | `event_id` | `DIM_Event` | `event_id` | For event detail drilldown. |
| `SUM_Event_Markers` | `event_id` | `DIM_Event` | `event_id` | For spike explanation panel filters. |
| `SUM_Competitor_Positioning` | `outlet_code` | `DIM_Outlet` | `outlet_code` | For outlet/market competitor filters. |

### How To Create A Lookup In Zoho

The exact Zoho labels can vary, but the flow is usually:

1. Open the source table, for example `FACT_Sales`.
2. Open table design/edit design.
3. Select the source column, for example `outlet_code`.
4. Change type or relationship to Lookup Column.
5. Select the target table, for example `DIM_Outlet`.
6. Select the target column, for example `outlet_code`.
7. Save.
8. Test by opening a chart or pivot and confirming dimension fields are available.

Build lookups in this order:

1. `FACT_Sales` lookups.
2. `FACT_Purchase_Order`, `FACT_Entry_Receipt`, `FACT_Inventory_Closing`.
3. `FACT_Theoretical_Consumption`.
4. `FACT_Event_Sales_Impact`.
5. `FACT_Competitor_Price_Position`.
6. `FACT_Outlet_Daily_Health`, `FACT_Vendor_Spend`.
7. Optional `SUM_*` lookups.

## 13. Dashboard Build Specification

Build dashboards only after the lookup relationships are created or after you have confirmed the workspace does not support the needed Query Table lookups.

### Global Dashboard Settings

Use these conventions:

- Date filter: `DIM_Date.month_key` or the fact date field if lookup is unavailable.
- Outlet filter: `DIM_Outlet.outlet_code` / `DIM_Outlet.outlet_name`.
- Category filter: category fields from the source table.
- Vendor filter: `DIM_Vendor.vendor_name` or source `vendor_name`.
- Ingredient filter: `DIM_Ingredient.ingredient_name` or source `item_name`.
- Event filter: `DIM_Event.event_type` / `event_name`.
- Competitor filter: `DIM_Competitor.competitor_name` / `market_area`.

Dashboard 1 can allow all outlets. Dashboards 2 through 5 should be locked to one outlet or require an outlet filter.

### Dashboard 1: Executive / Outlet Comparison / Outlet Health

Scope: cross-outlet. This is the only dashboard intended to compare all outlets together.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Total Net Sales | KPI tile | `SUM_Executive_KPIs` or `FACT_Sales` | none | `SUM(net_sale)` or metric `Total Net Sales` | Date/month | All-outlet sales headline. |
| Total Quantity Sold | KPI tile | `SUM_Executive_KPIs` or `FACT_Sales` | none | `SUM(qty)` or metric `Total Quantity Sold` | Date/month | All-outlet volume headline. |
| Active Outlets | KPI tile | `DIM_Outlet` | none | `COUNT(outlet_code)` | none | Confirms three outlets. |
| Outlet Sales Ranking | Bar chart | `SUM_Outlet_Health` | `outlet_name` | `total_net_sales` | Date/month | Answers highest-sales outlet. |
| Outlet Sales Trend | Line chart | `FACT_Outlet_Daily_Health` | `activity_date` | `SUM(net_sales)` | Series/color: `outlet_name`; date/month | Shows cross-outlet trend. |
| Outlet Health Table | Table/pivot | `SUM_Outlet_Health` | `outlet_name`, `market_area` | `total_net_sales`, `avg_daily_net_sales`, `total_po_value`, `avg_inventory_value`, `low_stock_item_days`, `event_day_markers` | Date/month | Outlet health comparison. |
| Inventory Pressure By Outlet | Bar chart | `SUM_Outlet_Health` | `outlet_name` | `low_stock_item_days` | Date/month | Compares inventory pressure. |
| Event Exposure By Outlet | Bar chart | `SUM_Outlet_Health` | `outlet_name` | `event_day_markers` | Date/month, event type if available | Compares event exposure. |
| Spike Explanation Panel | Table | `SUM_Event_Markers` | `event_date`, `outlet_name`, `event_name`, `event_type` | `event_day_sales`, `baseline_sales`, `sales_lift_percentage` | Date/month | Explains event spikes. |

### Dashboard 2: Sales and Menu Intelligence

Scope: outlet-specific. Add a mandatory dashboard filter for `outlet_code` or duplicate pages such as `Sales_Menu_OUT001`, `Sales_Menu_OUT002`, `Sales_Menu_OUT003`.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Selected Outlet Net Sales | KPI tile | `FACT_Sales` | none | `SUM(net_sale)` | Mandatory outlet, date/month | Sales headline for one outlet. |
| Selected Outlet Quantity Sold | KPI tile | `FACT_Sales` | none | `SUM(qty)` | Mandatory outlet, date/month | Volume headline for one outlet. |
| Sales Trend | Line chart | `FACT_Sales` | `sales_date` | `SUM(net_sale)` | Mandatory outlet, date/month | Shows daily sales movement. |
| Category Mix | Bar chart | `SUM_Sales_Category_Mix` | `category` | `total_net_sale` | Mandatory outlet, date/month | Shows revenue by category. |
| Super Category Mix | Stacked bar or donut | `SUM_Sales_Category_Mix` | `super_category` | `total_net_sale` | Mandatory outlet, date/month | Shows beverage/food contribution. |
| Top Menu Items | Horizontal bar | `SUM_Menu_Item_Performance` | `item_name` | `total_net_sale` | Mandatory outlet, date/month, category | Identifies best-selling items. |
| Menu Quantity Ranking | Horizontal bar | `SUM_Menu_Item_Performance` | `item_name` | `total_qty` | Mandatory outlet, date/month, category | Identifies highest-volume items. |
| Realized Unit Price | Bar/scatter | `SUM_Menu_Item_Performance` | `item_name` | `avg_realized_unit_price` | Mandatory outlet, category | Reviews item price realization. |
| Event Item Lift | Table | `SUM_Event_Impact` | `event_name`, `item_name`, `category` | `event_day_sales`, `baseline_sales`, `sales_lift_pct` | Mandatory outlet, event type, date/month | Shows event-sensitive items. |

### Dashboard 3: Vendor and Procurement Analytics

Scope: outlet-specific. Mandatory outlet filter.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Ordered Value | KPI tile | `FACT_Purchase_Order` | none | `SUM(total_item_cost)` | Mandatory outlet, date/month | PO value headline. |
| Received Value | KPI tile | `FACT_Entry_Receipt` | none | `SUM(grand_total)` | Mandatory outlet, date/month | Receipt value headline. |
| Vendor Share | Bar chart | `SUM_Vendor_Share` | `vendor_name` | `total_ordered_value` | Mandatory outlet, date/month | Answers vendor share by ordered value. |
| Vendor Received Share | Bar chart | `SUM_Vendor_Share` | `vendor_name` | `total_received_value` | Mandatory outlet, date/month | Compares receipt value by vendor. |
| Vendor Spend Trend | Line chart | `FACT_Vendor_Spend` | `activity_date` | `SUM(ordered_value)`, `SUM(received_value)` | Mandatory outlet, vendor, date/month | Shows procurement trend. |
| PO Status | Stacked bar | `FACT_Purchase_Order` | `po_status` | `COUNT(po_number)` or `SUM(total_item_cost)` | Mandatory outlet, date/month | Shows closed/pending/partial status. |
| Pending PO Table | Table | `FACT_PO_Receipt_Comparison` | `po_number`, `vendor_name`, `item_name`, `po_status` | `ordered_qty`, `matched_received_qty`, `unmatched_order_qty`, `remaining_qty` | Mandatory outlet, vendor, PO status | Finds pending/partial POs. |
| Vendor Material Matrix | Pivot table | `FACT_Purchase_Order` | Rows: `vendor_name`; columns: `item_name` or `category_name` | `SUM(total_item_cost)` | Mandatory outlet, date/month | Shows which vendors supply which materials. |

### Dashboard 4: Inventory and Consumption Intelligence

Scope: outlet-specific. Mandatory outlet filter.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Latest Inventory Value | KPI tile | `SUM_Inventory_Risk` | none | `SUM(total_amt)` | Mandatory outlet, latest date/month | Inventory value headline. |
| Low Stock Item Count | KPI tile | `SUM_Inventory_Risk` | none | `SUM(low_stock_flag)` | Mandatory outlet, latest date/month | Inventory pressure headline. |
| Inventory Value By Category | Bar chart | `SUM_Inventory_Risk` | `category_name` | `SUM(total_amt)` | Mandatory outlet; latest snapshot only | Shows current stock value mix. |
| Low Stock Table | Table | `SUM_Inventory_Risk` | `item_name`, `category_name`, `inventory_pressure_band` | `total_qty`, `total_amt`, `total_theoretical_qty` | Mandatory outlet, latest date/month | Identifies low stock items. |
| Theoretical Consumption Trend | Line chart | `FACT_Theoretical_Consumption` | `sales_date` | `SUM(theoretical_ingredient_qty)` | Mandatory outlet, ingredient/material, date/month | Shows ingredient demand from sales. |
| Recipe To Material Demand | Pivot/table | `FACT_Theoretical_Consumption` | Rows: `menu_item_name`; columns: `ingredient_name` | `SUM(theoretical_ingredient_qty)` | Mandatory outlet, category, date/month | Shows which materials are used by recipes sold. |
| Event Day Inventory Pressure | Table | `FACT_Outlet_Daily_Health` + `SUM_Event_Markers` if combined manually | `activity_date`, `outlet_name`, `health_note` | `low_stock_item_count`, `event_count`, `net_sales` | Mandatory outlet, event type/date | Connects events and inventory pressure. |

### Dashboard 5: Calendar, Event, and Competitor Intelligence

Scope: outlet-specific or market-area-specific. Mandatory outlet or market-area filter.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Event Day Sales | Bar chart | `SUM_Event_Impact` | `event_name` | `event_day_sales` | Mandatory outlet, event type, date/month | Shows event sales by event. |
| Event Lift % | Bar chart | `SUM_Event_Impact` | `event_name` | `sales_lift_pct` | Mandatory outlet, event type | Shows directional lift. |
| Spike Explanation Panel | Table | `SUM_Event_Markers` | `event_date`, `event_name`, `event_type`, `affected_items` | `event_day_sales`, `baseline_sales`, `sales_lift_percentage`, `confidence_level` | Mandatory outlet, date/month | Replaces chart annotations if needed. |
| Holiday/Event Sales Trend | Line chart | `FACT_Sales` with holiday/event filter panel | `sales_date` | `SUM(net_sale)` | Mandatory outlet, date/month, event/holiday | Shows sales around calendar markers. |
| Competitor Price Index | Bar chart | `SUM_Competitor_Positioning` | `competitor_name` or `competitor_category` | `avg_price_index` | Mandatory market area/outlet, category | Shows higher/lower pricing context. |
| ABNAH Vs Competitor Difference | Bar chart | `SUM_Competitor_Positioning` | `competitor_category` | `avg_price_difference` | Mandatory market area/outlet | Shows price disadvantage/advantage areas. |
| Premium Overperformance Table | Table | `FACT_Competitor_Price_Position` | `abnah_item_name`, `competitor_name`, `price_position` | `price_index`, `price_difference`, `SUM(net_sale)`, `SUM(qty)` | Mandatory outlet/market area, category | Reviews premium items still selling. |

## 14. Dashboard Testing Checklist

After building each dashboard:

1. Confirm the source table is a `FACT_*` or `SUM_*` table, not RAW, unless it is an audit table.
2. Confirm Dashboard 1 can compare all outlets.
3. Confirm Dashboards 2 through 5 have a mandatory outlet or market-area filter.
4. Set the filter to `OUT001`, then verify values change when switched to `OUT002` and `OUT003`.
5. Confirm no outlet-specific dashboard combines all three outlets without `outlet_code` or `outlet_name`.
6. Confirm chart titles mention selected outlet where useful.
7. Confirm competitor charts are described as context, not causation.
8. Confirm inventory charts say inventory pressure or low stock, not prediction.

## 15. Test The Completed Model With Month 2

After the model is built at Month 1:

1. Load Month 2:
   ```powershell
   python manage_demo.py load-month 2
   ```
2. Refresh/re-fetch all RAW Zoho tables.
3. Confirm sales RAW rows are `3,003`, `3,088`, and `3,325` by outlet, and `STD_Sales_Report` has `9,416` rows after union.
4. Confirm no duplicate sales `row_id`.
5. Refresh/recompute Query Tables if Zoho does not do it automatically.
6. Validate:
   - `STD_Sales_Report` row count updated.
   - `FACT_Sales` total net sale updated.
   - `SUM_Outlet_Health` changed.
   - outlet-specific dashboards still show only the selected outlet.

If Query Tables do not automatically update, refresh them in this order:

```text
RAW -> STD -> DIM -> FACT -> SUM -> Dashboards
```

## 16. Test The Completed Model With Month 3

1. Load Month 3:
   ```powershell
   python manage_demo.py load-month 3
   ```
2. Refresh/re-fetch all RAW Zoho tables.
3. Confirm sales RAW rows are `4,623`, `4,747`, and `5,206` by outlet, and `STD_Sales_Report` has `14,576` rows after union.
4. Confirm no duplicate sales `row_id`.
5. Refresh/recompute Query Tables if needed.
6. Validate:
   - event/holiday rows appear in event summaries,
   - competitor positioning still maps by outlet/market area,
   - inventory pressure summaries include outlet fields,
   - dashboards 2 through 5 remain outlet-scoped.

## 17. Reset And Retest

Run:

```powershell
python manage_demo.py reset-to-month 1
```

Then in Zoho:

1. Refresh/re-fetch all RAW tables.
2. Confirm sales RAW rows return to `1,529`, `1,595`, and `1,731` by outlet, and `STD_Sales_Report` returns to `4,855`.
3. Confirm duplicate `row_id` check still returns no rows.
4. Refresh/recompute Query Tables if needed.
5. Confirm dashboards return to Month 1 baseline.

If Zoho still shows Month 2/3 rows after backend reset, the source is not replacing/re-fetching correctly. Fix RAW import mode before continuing.

## 18. Quick Build Checklist

Use this as the short operating checklist:

1. Complete sales refresh test.
2. Reset backend to Month 1.
3. Import all 10 RAW tables with exact names.
4. Validate RAW row counts and duplicate `row_id`.
5. Build `STD_Sales_Report` first.
6. Build remaining `STD_*` tables.
7. Build `DIM_*` tables.
8. Create required lookup relationships.
9. Build `FACT_*` tables.
10. Build `SUM_*` tables.
11. Create optional summary lookups if useful.
12. Build Dashboard 1 as cross-outlet.
13. Build Dashboards 2 through 5 as outlet-specific templates.
14. Load Month 2, refresh Zoho, validate.
15. Load Month 3, refresh Zoho, validate.
16. Reset to Month 1, refresh Zoho, validate.

## 19. Most Common Mistakes

- Creating `RAW_Sales_Report_OUT001_Month_2` instead of refreshing `RAW_Sales_Report_OUT001`.
- Importing the combined `/zoho/sales_report.csv` endpoint as the operational Zoho model source instead of the outlet-specific feed endpoints.
- Importing a new RAW table when the ngrok URL changes instead of editing the existing source URL.
- Building Query Tables before proving refresh behavior.
- Forgetting `row_id` duplicate checks.
- Skipping lookup relationships and then wondering why dashboard filters do not cascade cleanly.
- Building outlet-specific dashboards without a mandatory outlet filter.
- Comparing vendor share across all outlets in the outlet-specific procurement dashboard.
- Treating theoretical consumption as actual-vs-theoretical variance.
- Treating competitor pricing as proof of causation.
