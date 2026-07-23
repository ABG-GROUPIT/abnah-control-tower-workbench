# Zoho FastAPI Feed Test Guide

This document tests the intended demo path:

```text
Neon raw tables -> FastAPI CSV endpoints -> Zoho Analytics Web URL/feed import
```

Do not use direct Zoho-to-Neon import for the final demo except as a fallback/testing path.

## 1. Prepare Backend State

Reset to Month 1:

```powershell
python manage_demo.py reset-month-1
```

Check status:

```powershell
python manage_demo.py status
```

Expected Month 1 operational rows:

- `raw.sales_report`: 4,855
- `raw.purchase_report`: 224
- `raw.entry_report`: 180
- `raw.inventory_closing_report`: 3,348

## 2. Run FastAPI Locally

```powershell
.\scripts\run_api.bat
```

or:

```powershell
uvicorn app.main:app --reload --port 8000
```

Test locally:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/zoho/sales_report_OUT001.csv
```

If `FEED_TOKEN` is set, use:

```text
http://127.0.0.1:8000/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
```

## 3. Make FastAPI Public For Zoho

Zoho cloud cannot access `localhost` or `127.0.0.1`.

Use ngrok/cloudflared or deploy FastAPI to a public HTTPS host.

ngrok is not part of this repo. Manual test:

```powershell
ngrok http 8000
```

Then test:

```text
https://<ngrok-url>/health
https://<ngrok-url>/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
```

Free ngrok URLs are temporary. For a stable leadership demo, host FastAPI on Render, Railway, Koyeb, or another approved platform.

## 4. Import Into Zoho

In Zoho Analytics:

1. Create or open a workspace.
2. Choose data import.
3. Choose Web URL/feed import.
4. Paste the public FastAPI CSV URL.
5. Ensure the first row is treated as headers.
6. Create a new table.
7. Name the table after the report.
8. Repeat for all endpoints.

Endpoint mapping:

| Zoho table | Endpoint |
|---|---|
| `vendor_report` | `/zoho/vendor_report.csv` |
| `menu_master` | `/zoho/menu_master.csv` |
| `brand_recipe_consumption` | `/zoho/brand_recipe_consumption.csv` |
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
| `indian_calendar_holidays` | `/zoho/indian_calendar_holidays.csv` |
| `manual_calendar_events` | `/zoho/manual_calendar_events.csv` |
| `competitor_pricing` | `/zoho/competitor_pricing.csv` |

## 5. Test Month Refresh

Month 1:

1. Import `RAW_Sales_Report_OUT001`.
2. Confirm Zoho row count matches FastAPI/Neon Month 1 count.

Month 2:

```powershell
python manage_demo.py load-month 2
```

Expected `RAW_Sales_Report_OUT001`: 3,003 rows.

Refresh/re-fetch the same Zoho table. Confirm rows increase and dashboards update.

Month 3:

```powershell
python manage_demo.py load-month 3
```

Expected `RAW_Sales_Report_OUT001`: 4,623 rows.

Refresh/re-fetch Zoho again. Confirm rows increase and Month 3 stories appear.

## 6. Retest Reset/Delete

Delete Month 3:

```powershell
python manage_demo.py delete-month 3
```

Reset to Month 1:

```powershell
python manage_demo.py reset-to-month 1
```

After any delete/reset, Zoho will not change until the feed is manually refreshed/re-fetched.

## 7. Watch For Duplicate Behavior

FastAPI returns the full current table every request.

If Zoho appends each refresh instead of replacing/updating by `row_id`, duplicates may appear in Zoho. Use `row_id` as an update key if Zoho offers that mode, or configure refresh/re-import behavior carefully.
