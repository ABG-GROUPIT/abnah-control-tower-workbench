# Zoho Import Notes

For the final demo, Zoho Analytics should import from FastAPI CSV feed URLs, not directly from Neon/PostgreSQL.

Direct Neon PostgreSQL import can remain a fallback/test path, but the intended architecture is:

```text
Neon raw tables -> FastAPI CSV feeds -> Zoho Web URL import
```

Import these FastAPI endpoints as separate Zoho tables:

- `/zoho/vendor_report.csv`
- `/zoho/menu_master.csv`
- `/zoho/brand_recipe_consumption.csv`
- `/zoho/sales_report_OUT001.csv`
- `/zoho/sales_report_OUT002.csv`
- `/zoho/sales_report_OUT003.csv`
- `/zoho/purchase_report_OUT001.csv`
- `/zoho/purchase_report_OUT002.csv`
- `/zoho/purchase_report_OUT003.csv`
- `/zoho/entry_report_OUT001.csv`
- `/zoho/entry_report_OUT002.csv`
- `/zoho/entry_report_OUT003.csv`
- `/zoho/inventory_closing_report_OUT001.csv`
- `/zoho/inventory_closing_report_OUT002.csv`
- `/zoho/inventory_closing_report_OUT003.csv`
- `/zoho/indian_calendar_holidays.csv`
- `/zoho/manual_calendar_events.csv`
- `/zoho/competitor_pricing.csv`

The combined operational endpoints, such as `/zoho/sales_report.csv`, are still useful for quick backend checks but should not be the RAW source for the outlet-specific Zoho model.

If `FEED_TOKEN` is set in `.env`, append it as a query parameter:

```text
https://your-public-api.example.com/zoho/sales_report_OUT001.csv?token=YOUR_TOKEN
```

Zoho modeling should happen inside Zoho through lookup columns, formulas, aggregate formulas, and query tables.
