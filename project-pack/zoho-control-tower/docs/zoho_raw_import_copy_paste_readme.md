# Zoho RAW Import Copy-Paste README

Use this file while creating the Zoho receiving/RAW tables from Web URL feeds.

This is for the real full-project build, not the temporary connector test. Create these RAW tables first. After all RAW imports exist, create Query Tables from `docs/zoho_query_table_sql/` one by one.

## Common Values For Every Import

Use these values on Zoho's "Create table by importing data from Web URL" screen.

| Zoho field | Copy/paste value |
|---|---|
| File Type | `CSV,TSV & Other Text Format` |
| Authentication Type | `None` |
| First row as column headers | `Yes` |
| Delimiter | `Comma` |
| Encoding | `UTF-8` |
| Text qualifier | `Double quote` if Zoho asks |
| Refresh mode | Prefer `Replace`, `Re-fetch`, or `Update existing table` |
| Update key, if Zoho asks | `row_id` |

Token handling:

- Easiest option: paste the full URL with `?token=<FEED_TOKEN>` in the URL field.
- Cleaner option: put the URL without `?token=...`, open `Parameters`, add parameter name `token`, and set the parameter value to your feed token.
- Do not use append-only refresh. These feeds return the full current table each time.

Base URL:

```text
https://abnah-zoho-synthetic-demo-api.onrender.com
```

URL pattern:

```text
https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/<feed_name>.csv?token=<FEED_TOKEN>
```

## Import Order

Create the tables in this order.

| Order | Zoho Table Name | Feed URL Suffix | Month 1 expected rows |
|---:|---|---|---:|
| 1 | `RAW_Sales_Report_OUT001` | `/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>` | 1,529 |
| 2 | `RAW_Sales_Report_OUT002` | `/zoho/sales_report_OUT002.csv?token=<FEED_TOKEN>` | 1,595 |
| 3 | `RAW_Sales_Report_OUT003` | `/zoho/sales_report_OUT003.csv?token=<FEED_TOKEN>` | 1,731 |
| 4 | `RAW_Purchase_Report_OUT001` | `/zoho/purchase_report_OUT001.csv?token=<FEED_TOKEN>` | 78 |
| 5 | `RAW_Purchase_Report_OUT002` | `/zoho/purchase_report_OUT002.csv?token=<FEED_TOKEN>` | 72 |
| 6 | `RAW_Purchase_Report_OUT003` | `/zoho/purchase_report_OUT003.csv?token=<FEED_TOKEN>` | 74 |
| 7 | `RAW_Entry_Report_OUT001` | `/zoho/entry_report_OUT001.csv?token=<FEED_TOKEN>` | 62 |
| 8 | `RAW_Entry_Report_OUT002` | `/zoho/entry_report_OUT002.csv?token=<FEED_TOKEN>` | 57 |
| 9 | `RAW_Entry_Report_OUT003` | `/zoho/entry_report_OUT003.csv?token=<FEED_TOKEN>` | 61 |
| 10 | `RAW_Inventory_Closing_Report_OUT001` | `/zoho/inventory_closing_report_OUT001.csv?token=<FEED_TOKEN>` | 1,116 |
| 11 | `RAW_Inventory_Closing_Report_OUT002` | `/zoho/inventory_closing_report_OUT002.csv?token=<FEED_TOKEN>` | 1,116 |
| 12 | `RAW_Inventory_Closing_Report_OUT003` | `/zoho/inventory_closing_report_OUT003.csv?token=<FEED_TOKEN>` | 1,116 |
| 13 | `RAW_Menu_Master` | `/zoho/menu_master.csv?token=<FEED_TOKEN>` | 110 |
| 14 | `RAW_Vendor_Report` | `/zoho/vendor_report.csv?token=<FEED_TOKEN>` | 70 |
| 15 | `RAW_Brand_Recipe_Consumption` | `/zoho/brand_recipe_consumption.csv?token=<FEED_TOKEN>` | 723 |
| 16 | `RAW_Indian_Calendar_Holidays` | `/zoho/indian_calendar_holidays.csv?token=<FEED_TOKEN>` | 9 |
| 17 | `RAW_Manual_Calendar_Events` | `/zoho/manual_calendar_events.csv?token=<FEED_TOKEN>` | 11 |
| 18 | `RAW_Competitor_Pricing` | `/zoho/competitor_pricing.csv?token=<FEED_TOKEN>` | 126 |

## Screen-By-Screen Copy Paste

### 1. RAW_Sales_Report_OUT001

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Sales_Report_OUT001` |
| Description | `RAW receiving table - OUT001 sales report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>` |

### 2. RAW_Sales_Report_OUT002

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Sales_Report_OUT002` |
| Description | `RAW receiving table - OUT002 sales report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/sales_report_OUT002.csv?token=<FEED_TOKEN>` |

### 3. RAW_Sales_Report_OUT003

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Sales_Report_OUT003` |
| Description | `RAW receiving table - OUT003 sales report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/sales_report_OUT003.csv?token=<FEED_TOKEN>` |

### 4. RAW_Purchase_Report_OUT001

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Purchase_Report_OUT001` |
| Description | `RAW receiving table - OUT001 purchase report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/purchase_report_OUT001.csv?token=<FEED_TOKEN>` |

### 5. RAW_Purchase_Report_OUT002

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Purchase_Report_OUT002` |
| Description | `RAW receiving table - OUT002 purchase report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/purchase_report_OUT002.csv?token=<FEED_TOKEN>` |

### 6. RAW_Purchase_Report_OUT003

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Purchase_Report_OUT003` |
| Description | `RAW receiving table - OUT003 purchase report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/purchase_report_OUT003.csv?token=<FEED_TOKEN>` |

### 7. RAW_Entry_Report_OUT001

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Entry_Report_OUT001` |
| Description | `RAW receiving table - OUT001 entry receipt report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/entry_report_OUT001.csv?token=<FEED_TOKEN>` |

### 8. RAW_Entry_Report_OUT002

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Entry_Report_OUT002` |
| Description | `RAW receiving table - OUT002 entry receipt report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/entry_report_OUT002.csv?token=<FEED_TOKEN>` |

### 9. RAW_Entry_Report_OUT003

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Entry_Report_OUT003` |
| Description | `RAW receiving table - OUT003 entry receipt report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/entry_report_OUT003.csv?token=<FEED_TOKEN>` |

### 10. RAW_Inventory_Closing_Report_OUT001

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Inventory_Closing_Report_OUT001` |
| Description | `RAW receiving table - OUT001 inventory closing report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/inventory_closing_report_OUT001.csv?token=<FEED_TOKEN>` |

### 11. RAW_Inventory_Closing_Report_OUT002

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Inventory_Closing_Report_OUT002` |
| Description | `RAW receiving table - OUT002 inventory closing report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/inventory_closing_report_OUT002.csv?token=<FEED_TOKEN>` |

### 12. RAW_Inventory_Closing_Report_OUT003

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Inventory_Closing_Report_OUT003` |
| Description | `RAW receiving table - OUT003 inventory closing report from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/inventory_closing_report_OUT003.csv?token=<FEED_TOKEN>` |

### 13. RAW_Menu_Master

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Menu_Master` |
| Description | `RAW receiving table - shared menu master from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/menu_master.csv?token=<FEED_TOKEN>` |

### 14. RAW_Vendor_Report

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Vendor_Report` |
| Description | `RAW receiving table - shared vendor master from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/vendor_report.csv?token=<FEED_TOKEN>` |

### 15. RAW_Brand_Recipe_Consumption

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Brand_Recipe_Consumption` |
| Description | `RAW receiving table - shared recipe BOM export from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/brand_recipe_consumption.csv?token=<FEED_TOKEN>` |

### 16. RAW_Indian_Calendar_Holidays

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Indian_Calendar_Holidays` |
| Description | `RAW receiving table - shared holiday calendar from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/indian_calendar_holidays.csv?token=<FEED_TOKEN>` |

### 17. RAW_Manual_Calendar_Events

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Manual_Calendar_Events` |
| Description | `RAW receiving table - shared manual event calendar from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/manual_calendar_events.csv?token=<FEED_TOKEN>` |

### 18. RAW_Competitor_Pricing

| Zoho field | Copy/paste value |
|---|---|
| Table Name | `RAW_Competitor_Pricing` |
| Description | `RAW receiving table - shared competitor pricing context from Render FastAPI/Neon` |
| URL | `https://abnah-zoho-synthetic-demo-api.onrender.com/zoho/competitor_pricing.csv?token=<FEED_TOKEN>` |

## Column Type Settings

Keep every field name exactly as imported. Do not rename columns in RAW tables.

### Sales Report Columns

Applies to `RAW_Sales_Report_OUT001`, `RAW_Sales_Report_OUT002`, `RAW_Sales_Report_OUT003`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `outlet_name` | Plain Text |
| `date` | Date, `yyyy-MM-dd` |
| `super_category` | Plain Text |
| `category` | Plain Text |
| `item_number` | Plain Text |
| `item_name` | Plain Text |
| `qty` | Number / Decimal |
| `net_sale` | Currency / Decimal |

### Purchase Report Columns

Applies to `RAW_Purchase_Report_OUT001`, `RAW_Purchase_Report_OUT002`, `RAW_Purchase_Report_OUT003`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `deployment` | Plain Text |
| `store_name` | Plain Text |
| `vendor_name` | Plain Text |
| `po_number` | Plain Text |
| `po_date` | Date, `yyyy-MM-dd` |
| `expected_delivery` | Date, `yyyy-MM-dd` |
| `po_status` | Plain Text |
| `item_code` | Plain Text |
| `item_name` | Plain Text |
| `category_name` | Plain Text |
| `super_category_name` | Plain Text |
| `total_processed_qty` | Number / Decimal |
| `remaining_balance_qty` | Number / Decimal |
| `quantity` | Number / Decimal |
| `unit` | Plain Text |
| `unit_price` | Currency / Decimal |
| `subtotal` | Currency / Decimal |
| `tax` | Currency / Decimal |
| `total_item_cost` | Currency / Decimal |

### Entry Report Columns

Applies to `RAW_Entry_Report_OUT001`, `RAW_Entry_Report_OUT002`, `RAW_Entry_Report_OUT003`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `deployment_name` | Plain Text |
| `store_kitchen_name` | Plain Text |
| `user_name` | Plain Text |
| `vendor_name` | Plain Text |
| `date` | Date, `yyyy-MM-dd` |
| `transaction_number` | Plain Text |
| `invoice_number` | Plain Text |
| `invoice_date` | Date, `yyyy-MM-dd` |
| `item_code` | Plain Text |
| `item_name` | Plain Text |
| `category_name` | Plain Text |
| `super_category_name` | Plain Text |
| `quantity` | Number / Decimal |
| `unit` | Plain Text |
| `mrp` | Currency / Decimal |
| `unit_price` | Currency / Decimal |
| `amount` | Currency / Decimal |
| `discount` | Currency / Decimal |
| `gst_igst_rate` | Number / Decimal |
| `gst_igst_value` | Currency / Decimal |
| `total_tax` | Currency / Decimal |
| `item_charges_amount` | Currency / Decimal |
| `entry_total` | Currency / Decimal |
| `return_quantity` | Number / Decimal |
| `return_amount` | Currency / Decimal |
| `grand_total` | Currency / Decimal |

### Inventory Closing Report Columns

Applies to `RAW_Inventory_Closing_Report_OUT001`, `RAW_Inventory_Closing_Report_OUT002`, `RAW_Inventory_Closing_Report_OUT003`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `deployment` | Plain Text |
| `date` | Date, `yyyy-MM-dd` |
| `generation_date` | Date, `yyyy-MM-dd` |
| `generation_time` | Plain Text |
| `item_code` | Plain Text |
| `item_name` | Plain Text |
| `super_category_code` | Plain Text |
| `super_category_name` | Plain Text |
| `category_code` | Plain Text |
| `category_name` | Plain Text |
| `unit_name` | Plain Text |
| `average_price` | Currency / Decimal |
| `store_stock_qty` | Number / Decimal |
| `total_qty` | Number / Decimal |
| `total_amt` | Currency / Decimal |

### Menu Master Columns

Applies to `RAW_Menu_Master`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `item_number` | Plain Text |
| `item_name` | Plain Text |
| `uid` | Plain Text |
| `item_description` | Plain Text |
| `rate` | Currency / Decimal |
| `category_name` | Plain Text |
| `super_category_name` | Plain Text |
| `non_veg` | Plain Text |
| `hsn_code` | Plain Text |
| `aggregator_alias_name` | Plain Text |
| `aggregator_alias_description` | Plain Text |
| `not_in_sweetshop` | Plain Text |
| `has_variant` | Plain Text |
| `is_inclusive_item` | Plain Text |
| `is_scannable_item` | Plain Text |
| `do_not_print_sticker` | Plain Text |

### Vendor Report Columns

Applies to `RAW_Vendor_Report`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `vendor_name` | Plain Text |
| `vendor_code` | Plain Text |
| `description` | Plain Text |
| `contact_person` | Plain Text |
| `contact_number` | Plain Text |
| `email` | Plain Text |
| `tin_number` | Plain Text |
| `service_tax_number` | Plain Text |
| `gstin_number` | Plain Text |
| `msme` | Plain Text |
| `fssai_number` | Plain Text |
| `pan_number` | Plain Text |
| `from_date` | Date, `yyyy-MM-dd` |
| `to_date` | Date, `yyyy-MM-dd` |
| `state` | Plain Text |
| `address` | Plain Text |

### Brand Recipe Consumption Columns

Applies to `RAW_Brand_Recipe_Consumption`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `recipe_name` | Plain Text |
| `recipe_qty` | Number / Decimal |
| `recipe_unit` | Plain Text |
| `item_name` | Plain Text |
| `item_qty` | Number / Decimal |
| `item_unit` | Plain Text |
| `item_tab_type` | Plain Text |

### Indian Calendar Holidays Columns

Applies to `RAW_Indian_Calendar_Holidays`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `calendar_date` | Date, `yyyy-MM-dd` |
| `holiday_name` | Plain Text |
| `holiday_type` | Plain Text |
| `region` | Plain Text |
| `is_public_holiday` | Plain Text |
| `is_bank_holiday` | Plain Text |
| `expected_business_impact` | Plain Text |
| `impact_direction` | Plain Text |
| `notes` | Plain Text |

### Manual Calendar Events Columns

Applies to `RAW_Manual_Calendar_Events`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `event_id` | Plain Text |
| `event_name` | Plain Text |
| `event_type` | Plain Text |
| `start_date` | Date, `yyyy-MM-dd` |
| `end_date` | Date, `yyyy-MM-dd` |
| `outlet_scope` | Plain Text |
| `affected_outlets` | Plain Text |
| `affected_category` | Plain Text |
| `affected_items` | Plain Text |
| `expected_impact_pct` | Number / Decimal |
| `impact_direction` | Plain Text |
| `confidence_level` | Plain Text |
| `event_source` | Plain Text |
| `admin_status` | Plain Text |
| `notes` | Plain Text |

### Competitor Pricing Columns

Applies to `RAW_Competitor_Pricing`.

| Column | Zoho type |
|---|---|
| `row_id` | Plain Text |
| `competitor_id` | Plain Text |
| `competitor_name` | Plain Text |
| `market_area` | Plain Text |
| `competitor_category` | Plain Text |
| `competitor_item_name` | Plain Text |
| `competitor_price` | Currency / Decimal |
| `abnah_item_number` | Plain Text |
| `abnah_item_name` | Plain Text |
| `abnah_price` | Currency / Decimal |
| `price_difference` | Currency / Decimal |
| `price_index` | Number / Decimal |
| `price_position` | Plain Text |
| `expected_sales_impact` | Plain Text |
| `notes` | Plain Text |

## After Import Validation

After creating all RAW imports at Month 1, validate row counts:

| Group | Expected Month 1 total |
|---|---:|
| All three sales RAW tables | 4,855 |
| All three purchase RAW tables | 224 |
| All three entry RAW tables | 180 |
| All three inventory RAW tables | 3,348 |
| Static/master RAW tables | Counts shown in import order table |

Run this duplicate check for each RAW table, starting with sales:

```sql
SELECT "row_id", COUNT(*) AS "row_count"
FROM "RAW_Sales_Report_OUT001"
GROUP BY "row_id"
HAVING COUNT(*) > 1
```

Expected result: no rows.

After all RAW imports are created and counts match, create Query Table `STD_Sales_Report` from:

```text
docs/zoho_query_table_sql/01_std_sales_report.sql
```

Expected `STD_Sales_Report` row count at Month 1:

```text
4,855
```
