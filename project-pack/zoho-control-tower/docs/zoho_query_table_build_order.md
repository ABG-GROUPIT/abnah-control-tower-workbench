# Zoho Query Table Build Order

Build RAW imports first, then Query Tables in layers. Zoho Query Tables can only reference tables that already exist.

The model is outlet-aware. Operational RAW imports are outlet-specific because the source synthetic files are outlet-wise. Static/master RAW imports remain shared across all outlets. The first four operational `STD_*` Query Tables union the three outlet RAW imports back into one outlet-aware table.

Operational `STD_*`, all `FACT_*`, and non-executive `SUM_*` tables must preserve:

- `outlet_code`
- `outlet_name`
- `market_area`

Only `SUM_Executive_KPIs` may intentionally contain all-outlet totals. Dashboard 1 is cross-outlet; Dashboards 2 through 5 must be filtered to one outlet or grouped by outlet.

## 0. Import RAW Tables

Import these from FastAPI CSV feed URLs and name them exactly:

1. `RAW_Sales_Report_OUT001`
2. `RAW_Sales_Report_OUT002`
3. `RAW_Sales_Report_OUT003`
4. `RAW_Purchase_Report_OUT001`
5. `RAW_Purchase_Report_OUT002`
6. `RAW_Purchase_Report_OUT003`
7. `RAW_Entry_Report_OUT001`
8. `RAW_Entry_Report_OUT002`
9. `RAW_Entry_Report_OUT003`
10. `RAW_Inventory_Closing_Report_OUT001`
11. `RAW_Inventory_Closing_Report_OUT002`
12. `RAW_Inventory_Closing_Report_OUT003`
13. `RAW_Menu_Master`
14. `RAW_Vendor_Report`
15. `RAW_Brand_Recipe_Consumption`
16. `RAW_Indian_Calendar_Holidays`
17. `RAW_Manual_Calendar_Events`
18. `RAW_Competitor_Pricing`

Use `row_id` as the key if Zoho offers update/add by key. Prefer replace/re-fetch mode when available.

Do not create Month 1, Month 2, or Month 3 RAW tables. Future month changes should refresh/re-fetch these same outlet-specific operational tables.

## 1. Standardized Tables

Create these first:

1. `STD_Sales_Report` from `01_std_sales_report.sql`
2. `STD_Purchase_Report` from `02_std_purchase_report.sql`
3. `STD_Entry_Report` from `03_std_entry_report.sql`
4. `STD_Inventory_Closing_Report` from `04_std_inventory_closing_report.sql`
5. `STD_Menu_Master` from `05_std_menu_master.sql`
6. `STD_Vendor_Report` from `06_std_vendor_report.sql`
7. `STD_Recipe_BOM` from `07_std_recipe_bom.sql`
8. `STD_Holiday_Calendar` from `08_std_holiday_calendar.sql`
9. `STD_Manual_Events` from `09_std_manual_events.sql`
10. `STD_Competitor_Pricing` from `10_std_competitor_pricing.sql`

If `STD_Recipe_BOM` fails because Zoho does not accept the correlated fill-down logic, use the documented FastAPI normalized-feed fallback before building theoretical consumption tables.

After building the first four operational `STD_*` tables, confirm these fields exist:

- `outlet_code`
- `outlet_name`
- `market_area`

## 2. Dimensions

Create dimensions after all `STD_*` tables exist:

1. `DIM_Date` from `11_dim_date.sql`
2. `DIM_Outlet` from `12_dim_outlet.sql`
3. `DIM_Menu_Item` from `13_dim_menu_item.sql`
4. `DIM_Vendor` from `14_dim_vendor.sql`
5. `DIM_Ingredient` from `15_dim_ingredient.sql`
6. `DIM_Event` from `16_dim_event.sql`
7. `DIM_Holiday` from `30_dim_holiday.sql`
8. `DIM_Competitor` from `31_dim_competitor.sql`

`30_dim_holiday.sql` and `31_dim_competitor.sql` are supplemental files because the requested numbered file list omitted them, but the requested layer model includes them.

## 3. Facts

Create facts after dimensions:

1. `FACT_Sales` from `17_fact_sales.sql`
2. `FACT_Purchase_Order` from `18_fact_purchase_order.sql`
3. `FACT_Entry_Receipt` from `19_fact_entry_receipt.sql`
4. `FACT_Inventory_Closing` from `20_fact_inventory_closing.sql`
5. `FACT_Theoretical_Consumption` from `21_fact_theoretical_consumption.sql`
6. `FACT_PO_Receipt_Comparison` from `22_fact_po_receipt_comparison.sql`
7. `FACT_Event_Sales_Impact` from `23_fact_event_sales_impact.sql`
8. `FACT_Competitor_Price_Position` from `24_fact_competitor_price_position.sql`
9. `FACT_Outlet_Daily_Health` from `25_fact_outlet_daily_health.sql`
10. `FACT_Vendor_Spend` from `32_fact_vendor_spend.sql`

`FACT_PO_Receipt_Comparison` is an approximate reconciliation because the entry report does not include the PO number.

`FACT_Event_Sales_Impact` may require date-arithmetic and string-matching syntax changes in Zoho. If it fails, first create an event-day-only version without baseline, then calculate baseline/lift using Zoho formulas or a second query table.

Fact table grain requirements:

| Fact table | Required grain |
|---|---|
| `FACT_Sales` | Outlet + date + item |
| `FACT_Purchase_Order` | Outlet + PO line + item + vendor |
| `FACT_Entry_Receipt` | Outlet + receipt line + item + vendor |
| `FACT_Inventory_Closing` | Outlet + date + inventory item |
| `FACT_Theoretical_Consumption` | Outlet + date + sold menu item + ingredient |
| `FACT_PO_Receipt_Comparison` | Outlet + PO line + item + vendor |
| `FACT_Event_Sales_Impact` | Outlet + event + date + category/item where possible |
| `FACT_Competitor_Price_Position` | Outlet/market area + competitor + ABNAH item |
| `FACT_Outlet_Daily_Health` | Outlet + date |
| `FACT_Vendor_Spend` | Outlet + vendor + date/month |

## 4. Summaries

Create dashboard summaries after facts:

1. `SUM_Executive_KPIs` from `33_sum_executive_kpis.sql`
2. `SUM_Outlet_Health` from `34_sum_outlet_health.sql`
3. `SUM_Sales_Category_Mix` from `35_sum_sales_category_mix.sql`
4. `SUM_Menu_Item_Performance` from `36_sum_menu_item_performance.sql`
5. `SUM_Vendor_Share` from `26_sum_vendor_share.sql`
6. `SUM_Inventory_Risk` from `27_sum_inventory_risk.sql`
7. `SUM_Event_Impact` from `28_sum_event_impact.sql`
8. `SUM_Competitor_Positioning` from `29_sum_competitor_positioning.sql`
9. `SUM_Event_Markers` from `37_sum_event_markers.sql`

The supplemental `33` through `37` files fill gaps in the requested output list so all requested dashboards and business questions have a clear data source.

Summary table outlet requirements:

| Summary table | Outlet behavior |
|---|---|
| `SUM_Executive_KPIs` | May contain all-outlet totals. |
| `SUM_Outlet_Health` | Must compare outlets. |
| `SUM_Sales_Category_Mix` | Must include `outlet_code`, `outlet_name`, `market_area`. |
| `SUM_Menu_Item_Performance` | Must include `outlet_code`, `outlet_name`, `market_area`. |
| `SUM_Vendor_Share` | Must include `outlet_code`, `outlet_name`, `market_area`. |
| `SUM_Inventory_Risk` | Must include `outlet_code`, `outlet_name`, `market_area`. |
| `SUM_Event_Impact` | Must include `outlet_code`, `outlet_name`, `market_area`. |
| `SUM_Competitor_Positioning` | Must include outlet fields and/or market-area fields. |
| `SUM_Event_Markers` | Must include `outlet_code`, `outlet_name`, `market_area`. |

## Rebuild Rule After RAW Refresh

After Month 2 or Month 3 is loaded in Neon and FastAPI returns larger feeds:

1. Refresh/re-fetch RAW feed tables.
2. Confirm each outlet-specific sales RAW table row count changed, then confirm `STD_Sales_Report` equals the combined outlet total.
3. Refresh/recompute query tables if Zoho does not do this automatically.
4. Validate row counts and dashboard filters.
5. Validate that Dashboards 2 through 5 are filtered to one outlet.

Avoid blind append refresh mode because the feeds return full current tables.
