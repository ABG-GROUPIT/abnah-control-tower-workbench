# Model Validation Checklist

Use this after importing RAW tables and after each Month 2/Month 3 refresh.

## RAW Import Checks

- `RAW_Sales_Report_OUT001`, `RAW_Sales_Report_OUT002`, and `RAW_Sales_Report_OUT003` exist.
- `RAW_Purchase_Report_OUT001`, `RAW_Purchase_Report_OUT002`, and `RAW_Purchase_Report_OUT003` exist.
- `RAW_Entry_Report_OUT001`, `RAW_Entry_Report_OUT002`, and `RAW_Entry_Report_OUT003` exist.
- `RAW_Inventory_Closing_Report_OUT001`, `RAW_Inventory_Closing_Report_OUT002`, and `RAW_Inventory_Closing_Report_OUT003` exist.
- `RAW_Menu_Master` exists.
- `RAW_Vendor_Report` exists.
- `RAW_Brand_Recipe_Consumption` exists.
- `RAW_Indian_Calendar_Holidays` exists.
- `RAW_Manual_Calendar_Events` exists.
- `RAW_Competitor_Pricing` exists.
- All RAW tables include `row_id`.
- `RAW_Sales_Report_OUT###.date` is usable as a date.
- `RAW_Purchase_Report_OUT###.po_date` and `expected_delivery` are usable as dates.
- `RAW_Entry_Report_OUT###.date` and `invoice_date` are usable as dates.
- `RAW_Inventory_Closing_Report_OUT###.date` is usable as a date.
- The combined `/zoho/sales_report.csv`, `/zoho/purchase_report.csv`, `/zoho/entry_report.csv`, and `/zoho/inventory_closing_report.csv` feeds are not used as the operational Zoho model source.

## Duplicate Checks

Run for each RAW table, starting with sales:

```sql
SELECT "row_id", COUNT(*) AS row_count
FROM "RAW_Sales_Report_OUT001"
GROUP BY "row_id"
HAVING COUNT(*) > 1
```

Expected result: no rows.

Repeat for `RAW_Sales_Report_OUT002` and `RAW_Sales_Report_OUT003`.

If duplicates appear after refresh, Zoho is likely appending the full feed. Change refresh behavior to replace/re-fetch or update/add by `row_id`.

## Standardization Checks

- `STD_Sales_Report` row count equals the combined count of `RAW_Sales_Report_OUT001`, `RAW_Sales_Report_OUT002`, and `RAW_Sales_Report_OUT003`.
- `STD_Purchase_Report` row count equals the combined count of `RAW_Purchase_Report_OUT001`, `RAW_Purchase_Report_OUT002`, and `RAW_Purchase_Report_OUT003`.
- `STD_Entry_Report` row count equals the combined count of `RAW_Entry_Report_OUT001`, `RAW_Entry_Report_OUT002`, and `RAW_Entry_Report_OUT003`.
- `STD_Inventory_Closing_Report` row count equals the combined count of `RAW_Inventory_Closing_Report_OUT001`, `RAW_Inventory_Closing_Report_OUT002`, and `RAW_Inventory_Closing_Report_OUT003`.
- `STD_Sales_Report` includes `outlet_code`, `outlet_name`, and `market_area`.
- `STD_Purchase_Report` includes `outlet_code`, `outlet_name`, and `market_area`.
- `STD_Entry_Report` includes `outlet_code`, `outlet_name`, and `market_area`.
- `STD_Inventory_Closing_Report` includes `outlet_code`, `outlet_name`, and `market_area`.
- `STD_Competitor_Pricing` includes `outlet_code`, `outlet_name`, and `market_area` where market area maps to a demo outlet.
- `STD_Sales_Report` maps `ABNAH Cafe Connaught Place` to `OUT001` and `Connaught Place`.
- `STD_Sales_Report` maps `ABNAH Cafe Hauz Khas` to `OUT002` and `Hauz Khas`.
- `STD_Sales_Report` maps `ABNAH Cafe Saket Premium` to `OUT003` and `Saket`.
- `STD_Menu_Master` has one row per `item_number`.
- `STD_Vendor_Report` has one row per `vendor_code` where available.
- `STD_Recipe_BOM.recipe_name_filled` is not blank for continuation rows.
- `STD_Recipe_BOM.ingredient_name` is not blank.

## Dimension Checks

- `DIM_Date` includes all sales dates.
- `DIM_Outlet` includes all three synthetic outlets with `outlet_code`, `outlet_name`, and `market_area`.
- `DIM_Menu_Item` includes all sold items.
- `DIM_Vendor` includes all purchase and entry vendors.
- `DIM_Ingredient` includes inventory, purchase, entry, and BOM ingredient names.
- `DIM_Event` includes all manual events.
- `DIM_Holiday` includes configured Jan-Mar 2026 holiday rows.
- `DIM_Competitor` includes competitor names and market areas.

## Fact Checks

- `FACT_Sales` total net sale equals `STD_Sales_Report` total net sale.
- `FACT_Sales` grain is outlet + date + item and includes `outlet_code` or `outlet_name`.
- `FACT_Purchase_Order` total item cost equals `STD_Purchase_Report` total item cost.
- `FACT_Purchase_Order` grain is outlet + PO line + item + vendor and includes `outlet_code` or `outlet_name`.
- `FACT_Entry_Receipt` grand total equals `STD_Entry_Report` grand total.
- `FACT_Entry_Receipt` grain is outlet + receipt line + item + vendor and includes `outlet_code` or `outlet_name`.
- `FACT_Inventory_Closing` latest inventory date matches RAW after refresh.
- `FACT_Inventory_Closing` grain is outlet + date + inventory item and includes `outlet_code` or `outlet_name`.
- `FACT_Theoretical_Consumption` returns rows for high-volume items like coffee and dairy recipes.
- `FACT_Theoretical_Consumption` grain is outlet + date + sold menu item + ingredient and includes `outlet_code` or `outlet_name`.
- `FACT_PO_Receipt_Comparison` returns pending/partial rows for partially received POs.
- `FACT_Event_Sales_Impact` returns event-day rows for manual calendar events.
- `FACT_Event_Sales_Impact` grain is outlet + event + date + category/item where possible and includes `outlet_code` or `outlet_name`.
- `FACT_Competitor_Price_Position` returns mapped competitor rows for ABNAH menu items.
- `FACT_Competitor_Price_Position` includes outlet or market-area context.
- `FACT_Outlet_Daily_Health` has one row per outlet/date where activity exists.
- `FACT_Vendor_Spend` includes ordered and received value by outlet + vendor + date/month.

## Summary Outlet Checks

- `SUM_Executive_KPIs` can contain all-outlet totals.
- `SUM_Outlet_Health` compares outlets and includes `outlet_code`, `outlet_name`, and `market_area`.
- `SUM_Sales_Category_Mix` includes `outlet_code`, `outlet_name`, and `market_area`.
- `SUM_Menu_Item_Performance` includes `outlet_code`, `outlet_name`, and `market_area`.
- `SUM_Vendor_Share` includes `outlet_code`, `outlet_name`, and `market_area`.
- `SUM_Inventory_Risk` includes `outlet_code`, `outlet_name`, and `market_area`.
- `SUM_Event_Impact` includes `outlet_code`, `outlet_name`, and `market_area`.
- `SUM_Competitor_Positioning` includes outlet fields or market-area fields.
- `SUM_Event_Markers` includes `outlet_code`, `outlet_name`, and `market_area`.
- Non-executive summaries do not combine Connaught Place, Hauz Khas, and Saket unless grouped by outlet.

## Dashboard Checks

- Executive KPIs are not blank.
- Outlet sales ranking answers "which outlet had highest sales last month."
- Executive / Outlet Comparison is the only cross-outlet dashboard.
- Sales and Menu Intelligence dashboard has a mandatory outlet filter.
- Vendor and Procurement Analytics dashboard has a mandatory outlet filter.
- Inventory and Consumption Intelligence dashboard has a mandatory outlet filter.
- Calendar, Event, and Competitor Intelligence dashboard has a mandatory outlet or market-area filter.
- Non-executive dashboards do not accidentally combine Connaught Place, Hauz Khas, and Saket values without grouping by outlet.
- Menu item ranking answers "which menu items sold the most" for the selected outlet.
- Category mix answers "which categories contribute most revenue" for the selected outlet.
- Vendor share answers "which vendor has highest procurement value" for the selected outlet.
- PO comparison shows pending/partial POs.
- Inventory risk shows low stock pressure as heuristic, not prediction.
- Event impact dashboard shows event day sales, baseline sales, lift percentage, and confidence level.
- Competitor dashboard shows higher/lower/parity price context and does not claim causation.

## Month Refresh Checks

After Month 2 load:

- FastAPI outlet sales feed row counts increase.
- `RAW_Sales_Report_OUT001`, `RAW_Sales_Report_OUT002`, and `RAW_Sales_Report_OUT003` row counts increase after Zoho refresh.
- `STD_Sales_Report` and `FACT_Sales` reflect the new count.
- Dashboards include Month 2 dates.

After Month 3 load:

- FastAPI outlet sales feed row counts increase again.
- Zoho RAW tables refresh without duplicates.
- Event/holiday/competitor dashboards show Month 3 story rows.

## Caveat Checks

- No dashboard title or text claims full forecasting.
- No dashboard title or text claims true stockout prediction.
- No dashboard title or text claims full actual-vs-theoretical variance.
- Competitor pricing is presented as context and review signal, not proof of causation.
