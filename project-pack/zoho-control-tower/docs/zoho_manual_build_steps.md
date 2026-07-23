# Zoho Manual Build Steps

Use these steps inside Zoho Analytics after FastAPI is running through a public HTTPS URL.

For the complete main-data ngrok/FastAPI/Zoho test sequence, use `docs/ngrok_fastapi_zoho_main_data_test_runbook.md`.

After that refresh test passes, use `docs/zoho_actual_data_model_build_readme.md` for the practical full model build sequence.

## 1. Test One Feed First

1. Run the backend at Month 1:
   ```powershell
   python manage_demo.py reset-to-month 1
   ```
2. Start FastAPI.
3. Expose FastAPI through ngrok/cloudflared or a hosted URL.
4. In a browser, open:
   ```text
   https://<public-url>/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
   ```
5. Confirm the CSV downloads and contains a `row_id` header.

## 2. Import `RAW_Sales_Report_OUT001`

1. In Zoho Analytics, choose the Web URL/feed import option.
2. Paste the public `sales_report_OUT001.csv` URL.
3. Set first row as column headers.
4. Name the table `RAW_Sales_Report_OUT001`.
5. Confirm `row_id` imports as text.
6. Confirm `date` imports as a date or can be converted to a date.
7. If Zoho offers refresh behavior:
   - Prefer replace/re-fetch mode.
   - If using update/add, set `row_id` as the key.
   - Avoid blind append.

## 3. Validate Refresh Behavior

1. Record the row count of `RAW_Sales_Report_OUT001`.
2. Load Month 2:
   ```powershell
   python manage_demo.py load-month 2
   ```
3. Open the same FastAPI URL and confirm it returns more rows.
4. Refresh/re-fetch `RAW_Sales_Report_OUT001` in Zoho.
5. Confirm the Zoho row count increased without duplicates.
6. Check duplicate count by `row_id` if Zoho supports query tables:
   ```sql
   SELECT "row_id", COUNT(*) AS row_count
   FROM "RAW_Sales_Report_OUT001"
   GROUP BY "row_id"
   HAVING COUNT(*) > 1
   ```

Only import all remaining RAW tables after this test is understood.

Do not build `STD_*`, `DIM_*`, `FACT_*`, or `SUM_*` query tables until refresh behavior is understood. If Zoho blindly appends the full CSV feed on refresh, query tables and dashboards will inherit duplicate rows.

Once this test passes, continue with `docs/zoho_actual_data_model_build_readme.md`.

## 4. Import All RAW Tables

Use these names exactly:

| Zoho RAW table | FastAPI endpoint |
|---|---|
| `RAW_Sales_Report_OUT001` | `/zoho/sales_report_OUT001.csv` |
| `RAW_Sales_Report_OUT002` | `/zoho/sales_report_OUT002.csv` |
| `RAW_Sales_Report_OUT003` | `/zoho/sales_report_OUT003.csv` |
| `RAW_Purchase_Report_OUT001` | `/zoho/purchase_report_OUT001.csv` |
| `RAW_Purchase_Report_OUT002` | `/zoho/purchase_report_OUT002.csv` |
| `RAW_Purchase_Report_OUT003` | `/zoho/purchase_report_OUT003.csv` |
| `RAW_Entry_Report_OUT001` | `/zoho/entry_report_OUT001.csv` |
| `RAW_Entry_Report_OUT002` | `/zoho/entry_report_OUT002.csv` |
| `RAW_Entry_Report_OUT003` | `/zoho/entry_report_OUT003.csv` |
| `RAW_Inventory_Closing_Report_OUT001` | `/zoho/inventory_closing_report_OUT001.csv` |
| `RAW_Inventory_Closing_Report_OUT002` | `/zoho/inventory_closing_report_OUT002.csv` |
| `RAW_Inventory_Closing_Report_OUT003` | `/zoho/inventory_closing_report_OUT003.csv` |
| `RAW_Menu_Master` | `/zoho/menu_master.csv` |
| `RAW_Vendor_Report` | `/zoho/vendor_report.csv` |
| `RAW_Brand_Recipe_Consumption` | `/zoho/brand_recipe_consumption.csv` |
| `RAW_Indian_Calendar_Holidays` | `/zoho/indian_calendar_holidays.csv` |
| `RAW_Manual_Calendar_Events` | `/zoho/manual_calendar_events.csv` |
| `RAW_Competitor_Pricing` | `/zoho/competitor_pricing.csv` |

## 5. Build Query Tables

Follow `docs/zoho_query_table_build_order.md`.

For each file in `docs/zoho_query_table_sql`:

1. Create a new Query Table in Zoho.
2. Paste the SQL.
3. Remove or keep SQL comments depending on Zoho editor behavior.
4. If Zoho rejects a date/string function, use the fallback note in the file.
5. Save with the table name shown in the SQL file header.

After creating the operational `STD_*` and `FACT_*` tables, confirm `outlet_code`, `outlet_name`, and `market_area` are present where required. Non-executive summaries must include outlet fields unless they are explicitly used only with a mandatory outlet dashboard filter.

## 6. Recipe BOM Handling

Try `07_std_recipe_bom.sql` first. It uses `row_id` to fill down the latest nonblank recipe name, recipe qty, and recipe unit.

If Zoho SQL does not support the correlated fill-down query:

1. Keep `RAW_Brand_Recipe_Consumption` for audit/demo.
2. Add a FastAPI technical endpoint in the future:
   ```text
   /zoho/brand_recipe_consumption_normalized.csv
   ```
3. Have FastAPI return already-filled fields:
   - `recipe_name_filled`
   - `recipe_qty_filled`
   - `recipe_unit_filled`
   - `ingredient_name`
   - `ingredient_qty`
   - `ingredient_unit`
   - `item_tab_type`
4. Import that as `STD_Recipe_BOM` or a technical RAW table.

## 7. Build Dashboards

Use `docs/dashboard_module_plan.md`.

Recommended build order:

1. Executive / Outlet Comparison / Outlet Health
2. Sales and Menu Intelligence, built as an outlet-specific template
3. Vendor and Procurement Analytics, built as an outlet-specific template
4. Inventory and Consumption Intelligence, built as an outlet-specific template
5. Calendar, Event, and Competitor Intelligence, built as an outlet-specific template

Dashboard scope rules:

- Dashboard 1 is cross-outlet and should compare Connaught Place, Hauz Khas, and Saket.
- Dashboards 2 through 5 require a mandatory outlet filter.
- Preferred page pattern: `Sales_Menu_OUT001`, `Sales_Menu_OUT002`, `Sales_Menu_OUT003`, repeated for procurement, inventory, and calendar/competitor modules.
- Do not create separate SQL models per outlet unless locked dashboard filters are not viable. The RAW operational imports are already outlet-specific and the `STD_*` query tables union them.

## 8. Refresh During Demo

For the month-wise demo:

1. Start at Month 1 and show baseline dashboard.
2. Load Month 2 in backend.
3. Refresh/re-fetch RAW Zoho feed tables.
4. Wait for Query Tables to refresh/recompute if needed.
5. Show updated sales/procurement dashboards.
6. Load Month 3.
7. Refresh/re-fetch RAW Zoho feed tables.
8. Show event, holiday, competitor, and inventory-pressure story.

If a dashboard does not update, first validate the RAW table row count, then validate the dependent `STD_*`, `FACT_*`, and `SUM_*` tables.

If Dashboards 2 through 5 show suspiciously high totals, check whether the page accidentally combines all three outlets without grouping or filtering by `outlet_code`/`outlet_name`.
