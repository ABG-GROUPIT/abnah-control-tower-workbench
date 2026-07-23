# ngrok / FastAPI / Zoho Main Data Test Runbook

This runbook tests the real synthetic demo dataset, not dummy test data.

Full path tested:

```text
Neon raw tables
-> FastAPI CSV feed
-> ngrok public URL
-> Zoho Web URL/feed import
-> Month 2 load
-> Zoho refresh
-> duplicate check
-> reset/delete and retest
```

ngrok does not host the FastAPI app permanently. ngrok only creates a public HTTPS tunnel to the locally running FastAPI app. FastAPI must still be running locally using `uvicorn` or `scripts/run_api.bat`.

Zoho cannot access `localhost` or `127.0.0.1`. Zoho can only import the FastAPI feed if the URL is public, such as ngrok, cloudflared, or a hosted FastAPI deployment.

## 1. Prerequisites

Check that:

- `.env` exists.
- `DATABASE_URL` is set.
- `FEED_TOKEN` is known, if enabled.
- `ADMIN_TOKEN` is known, if admin endpoints are used.
- Python dependencies are installed:
  ```powershell
  pip install -r requirements.txt
  ```
- Neon database is reachable:
  ```powershell
  python manage_demo.py status
  ```

Use the project folder:

```powershell
cd "C:\Users\ARNAV\OneDrive\Desktop\ABNAH actual demo\abnah-zoho-synthetic-demo"
```

## 2. Reset Backend To Month 1

Use:

```powershell
python manage_demo.py reset-to-month 1
```

or, if a full rebuild is needed:

```powershell
python manage_demo.py reset-month-1
```

Then run:

```powershell
python manage_demo.py status
```

Expected Month 1 row counts:

| Table | Expected Month 1 rows |
|---|---:|
| `raw.sales_report` | 4,855 |
| `raw.purchase_report` | 224 |
| `raw.entry_report` | 180 |
| `raw.inventory_closing_report` | 3,348 |

## 3. Start FastAPI Locally

Use either:

```powershell
scripts/run_api.bat
```

or:

```powershell
uvicorn app.main:app --reload --port 8000
```

Then test locally:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/zoho/sales_report_OUT001.csv
```

If `FEED_TOKEN` is enabled, test:

```text
http://127.0.0.1:8000/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
```

## 4. Start ngrok

ngrok must be installed separately if it is not already installed. It is not part of this repo.

Command:

```powershell
ngrok http 8000
```

Copy the HTTPS forwarding URL.

Example:

```text
https://abc123.ngrok-free.app
```

Test:

```text
https://abc123.ngrok-free.app/health
https://abc123.ngrok-free.app/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
```

If `FEED_TOKEN` is blank, omit the `?token=<FEED_TOKEN>` query parameter.

## 5. Import One Outlet Sales Feed Into Zoho First

In Zoho Analytics:

1. Open or create workspace.
2. Choose Web URL/feed import.
3. Paste:
   ```text
   https://abc123.ngrok-free.app/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
   ```
4. Create table named:
   ```text
   RAW_Sales_Report_OUT001
   ```
5. Ensure first row is treated as column headers.
6. Ensure `row_id` is imported as text.
7. Ensure `date` is imported as date or can be converted later.
8. Record Zoho row count.

Expected Month 1 OUT001 sales rows: `1,529`.

## 6. Test Month 2 Refresh On Main Data

Run:

```powershell
python manage_demo.py load-month 2
```

Then check backend status:

```powershell
python manage_demo.py status
```

Open the same ngrok URL in a browser:

```text
https://abc123.ngrok-free.app/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
```

Expected OUT001 sales rows after Month 2: `3,003`.

In Zoho:

1. Refresh/re-fetch the same `RAW_Sales_Report_OUT001` source.
2. Do not create a new Month 2 table.
3. Confirm `RAW_Sales_Report_OUT001` row count becomes `3,003`.
4. Run duplicate `row_id` check if possible:

```sql
SELECT "row_id", COUNT(*) AS row_count
FROM "RAW_Sales_Report_OUT001"
GROUP BY "row_id"
HAVING COUNT(*) > 1
```

Expected: no rows.

## 7. Test Month 3 Refresh On Main Data

Run:

```powershell
python manage_demo.py load-month 3
```

Expected OUT001 sales rows after Month 3: `4,623`.

Refresh/re-fetch `RAW_Sales_Report_OUT001` in Zoho.

Confirm Zoho row count becomes `4,623`.

Confirm no duplicate `row_id` rows:

```sql
SELECT "row_id", COUNT(*) AS row_count
FROM "RAW_Sales_Report_OUT001"
GROUP BY "row_id"
HAVING COUNT(*) > 1
```

Expected: no rows.

## 8. Reset / Erase Test State

There are two reset levels.

### Backend Reset

Use:

```powershell
python manage_demo.py reset-to-month 1
```

This removes Month 2 and Month 3 operational rows from Neon while keeping Month 1 and static data.

FastAPI then returns Month 1 only again.

### Zoho Reset

After backend reset, Zoho will not change automatically.

Refresh/re-fetch `RAW_Sales_Report_OUT001`.

Expected Zoho row count returns to `1,529` if Zoho is replacing/re-fetching correctly.

If Zoho continues showing old rows or duplicates, then the Zoho import mode is not configured correctly. In that case, manually delete the `RAW_Sales_Report_OUT001` table from Zoho and re-import the feed.

### Full Clean Restart

If you want to erase all Zoho testing artifacts, delete the imported RAW tables and query tables from the Zoho workspace or create a fresh Zoho workspace for final build.

## 9. Import Remaining RAW Tables Only After Sales Refresh Works

After sales feed refresh is proven, import:

- `RAW_Sales_Report_OUT002`
- `RAW_Sales_Report_OUT003`
- `RAW_Purchase_Report_OUT001`
- `RAW_Purchase_Report_OUT002`
- `RAW_Purchase_Report_OUT003`
- `RAW_Entry_Report_OUT001`
- `RAW_Entry_Report_OUT002`
- `RAW_Entry_Report_OUT003`
- `RAW_Inventory_Closing_Report_OUT001`
- `RAW_Inventory_Closing_Report_OUT002`
- `RAW_Inventory_Closing_Report_OUT003`
- `RAW_Menu_Master`
- `RAW_Vendor_Report`
- `RAW_Brand_Recipe_Consumption`
- `RAW_Indian_Calendar_Holidays`
- `RAW_Manual_Calendar_Events`
- `RAW_Competitor_Pricing`

Endpoint mapping:

| Zoho RAW table | FastAPI endpoint |
|---|---|
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

## 10. Do Not Start Full Modeling Until Refresh Behavior Is Understood

Warning: if Zoho refresh appends the full CSV every time, duplicate rows will occur.

You must confirm whether Zoho is:

- replacing/re-fetching the full table, or
- update-adding by `row_id`, or
- blindly appending the full CSV.

Only after this is confirmed should you build `STD_*`, `DIM_*`, `FACT_*`, and `SUM_*` query tables.

## 11. Main-Data-Only Testing Sequence Summary

Exact command flow:

```powershell
python manage_demo.py reset-to-month 1
scripts/run_api.bat
ngrok http 8000
```

Then in Zoho:

```text
Import RAW_Sales_Report_OUT001 into Zoho
```

Continue:

```powershell
python manage_demo.py load-month 2
```

Then in Zoho:

```text
Refresh RAW_Sales_Report_OUT001 in Zoho
Validate row count and duplicates
```

Continue:

```powershell
python manage_demo.py load-month 3
```

Then in Zoho:

```text
Refresh RAW_Sales_Report_OUT001 in Zoho
Validate row count and duplicates
```

Reset:

```powershell
python manage_demo.py reset-to-month 1
```

Then in Zoho:

```text
Refresh RAW_Sales_Report_OUT001 in Zoho
Confirm row count returns to Month 1
```

## 12. Stability Note

ngrok free URLs are temporary.

If the ngrok URL changes, the Zoho source URL must be updated or the table must be re-imported.

For a leadership demo, hosted FastAPI is better than ngrok. For initial testing, ngrok is acceptable.

## 13. What This Runbook Does Not Prove

This runbook does not prove that Zoho is already connected. It is the manual test path to establish that connection.

This runbook does not prove that the full Zoho model is complete. The full model is complete only after RAW imports, query tables, formulas, dashboard filters, and refresh behavior are manually created and tested in Zoho.
