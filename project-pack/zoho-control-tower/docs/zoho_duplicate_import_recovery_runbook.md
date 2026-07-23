# Zoho Duplicate Import Recovery Runbook

## What Happened

The hosted Neon and FastAPI feed are still clean. The bad dashboard values are caused by Zoho RAW receiving tables containing appended duplicate Month 1 rows after a refetch/import.

Evidence from the live Render API on 2026-07-06:

| Layer | Result |
|---|---|
| Render admin status | Only `month_01` is loaded |
| Sales source rows | `4855` total rows |
| Purchase source rows | `224` total rows |
| Entry source rows | `180` total rows |
| Inventory source rows | `3348` total rows |
| Static source rows | Vendor `70`, Menu `110`, BOM `723`, Holidays `9`, Events `11`, Competitors `126` |

The inflated dashboard values match duplicate Zoho rows:

| Metric | Correct Month 1 value | Bad value pattern seen in Zoho | Meaning |
|---|---:|---:|---|
| Connaught latest inventory value | `6.13L` | `12.26L` | Exactly 2x |
| Hauz Khas latest inventory value | `6.77L` | `13.54L` | Exactly 2x |
| All-outlet latest inventory value | `18.92L` | `37.84L` | Exactly 2x |
| Connaught PO raised value | `5.21L` | About `10L` | About 2x |
| Connaught receipt booked value | About `3.88L` | About `7.76L` | About 2x |

This means the source database did not get Month 2 by mistake. The Zoho workspace has extra rows inside the RAW receiving tables from a previous import/refetch. Those extra rows can be exact duplicate Month 1 rows, old Month 2/Month 3 rows left from connector testing, or both.

## Files Added Or Changed

Update these STD query tables in Zoho with the latest SQL from the repo. They now use `SELECT DISTINCT` so exact duplicate RAW rows do not double downstream facts.

1. `01_std_sales_report.sql`
2. `02_std_purchase_report.sql`
3. `03_std_entry_report.sql`
4. `04_std_inventory_closing_report.sql`
5. `05_std_menu_master.sql`
6. `06_std_vendor_report.sql`
7. `07_std_recipe_bom.sql`
8. `08_std_holiday_calendar.sql`
9. `09_std_manual_events.sql`
10. `10_std_competitor_pricing.sql`

Also create this diagnostic query table:

`00_check_raw_duplicate_state.sql`

## Step 1: Confirm RAW Duplicate State In Zoho

Create a new Query Table in Zoho:

| Field | Value |
|---|---|
| Query table name | `CHECK_Raw_Duplicate_State` |
| SQL source | `docs/zoho_query_table_sql/00_check_raw_duplicate_state.sql` |

After saving it, read these columns:

| Column | Meaning |
|---|---|
| `expected_clean_rows` | What the table should contain for clean Month 1 |
| `zoho_row_count` | What Zoho currently has in the RAW table |
| `distinct_row_id_count` | Number of unique source rows by `row_id` |
| `duplicate_row_count` | Extra appended rows inside Zoho |

Interpret the result carefully:

| Pattern | Meaning | Can `SELECT DISTINCT` fully fix it? |
|---|---|---|
| `zoho_row_count = expected_clean_rows` and `duplicate_row_count = 0` | RAW table is clean | No fix needed |
| `zoho_row_count = 2 * expected_clean_rows` and `distinct_row_id_count = expected_clean_rows` | Exact Month 1 duplicate append | Yes, the updated STD SQL removes exact duplicates |
| `zoho_row_count > expected_clean_rows` and `distinct_row_id_count > expected_clean_rows` | Zoho still has old distinct rows, usually Month 2/Month 3 test rows | No, RAW table must be replaced/recreated |
| `zoho_row_count > expected_clean_rows` and `duplicate_row_count > 0` | Mixed state: duplicates plus possible old rows | Replace/recreate RAW is safest |

## Step 2: Fix The STD Layer

For each STD table, open the existing Query Table and replace the full SQL with the matching file from `docs/zoho_query_table_sql`.

Update these in order:

1. `STD_Sales_Report`
2. `STD_Purchase_Report`
3. `STD_Entry_Report`
4. `STD_Inventory_Closing_Report`
5. `STD_Menu_Master`
6. `STD_Vendor_Report`
7. `STD_Recipe_BOM`
8. `STD_Holiday_Calendar`
9. `STD_Manual_Events`
10. `STD_Competitor_Pricing`

Save each table after replacing the SQL.

## Step 3: Refresh Dependent Query Tables

After the STD layer is fixed, refresh downstream tables in this order. Do not start from dashboards first.

### Dimensions

1. `DIM_Date`
2. `DIM_Outlet`
3. `DIM_Menu_Item`
4. `DIM_Vendor`
5. `DIM_Ingredient`
6. `DIM_Event`
7. `DIM_Holiday`
8. `DIM_Competitor`

### Facts

1. `FACT_Sales`
2. `FACT_Purchase_Order`
3. `FACT_Entry_Receipt`
4. `FACT_Inventory_Closing`
5. `FACT_Theoretical_Consumption`
6. `FACT_PO_Receipt_Comparison`
7. `FACT_Event_Sales_Impact`
8. `FACT_Competitor_Price_Position`
9. `FACT_Outlet_Daily_Health`
10. `FACT_Vendor_Spend`

### Summaries

1. `SUM_Vendor_Share`
2. `SUM_Inventory_Risk`
3. `SUM_Event_Impact`
4. `SUM_Competitor_Positioning`
5. `SUM_Executive_KPIs`
6. `SUM_Outlet_Health`
7. `SUM_Sales_Category_Mix`
8. `SUM_Menu_Item_Performance`
9. `SUM_Event_Markers`

## Step 4: Validate Expected Dashboard Values

Before trusting charts, validate these Month 1 totals:

| Dashboard / metric | Expected after fix |
|---|---:|
| Sales and Menu Intelligence, all outlets net sale | `19.45L` |
| Sales and Menu Intelligence, Connaught net sale | `6.26L` |
| Sales and Menu Intelligence, Hauz Khas net sale | `6.27L` |
| Sales and Menu Intelligence, Saket net sale | `6.92L` |
| Vendor dashboard, Connaught PO raised value | `5.21L` |
| Vendor dashboard, Connaught receipt booked value | About `3.88L` |
| Inventory dashboard, all outlets latest inventory value | `18.92L` |
| Inventory dashboard, Connaught latest inventory value | `6.13L` |
| Inventory dashboard, Hauz Khas latest inventory value | `6.77L` |
| Inventory dashboard, Saket latest inventory value | `6.02L` |

If values are still high after updating STD tables, check `CHECK_Raw_Duplicate_State`:

1. If RAW contains only exact duplicates, the dashboard widgets are probably pointing directly to RAW tables or stale duplicate query tables instead of refreshed STD/FACT/SUM tables.
2. If RAW contains old distinct rows, the updated STD tables cannot remove them because those rows are not duplicates. Replace/recreate the RAW receiving tables and import Month 1 cleanly.

## Step 5: Clean RAW Tables Later

The `SELECT DISTINCT` fix protects the model from exact duplicate RAW appends. Still, the clean long-term solution is to make Zoho RAW imports replace data instead of append data.

When re-importing a RAW URL feed in Zoho:

1. Prefer replace/delete existing data before import.
2. Do not append the same Month 1 URL into an existing RAW table.
3. If Zoho does not give a reliable replace option, delete and recreate the RAW receiving table before re-importing.
4. After RAW is clean, rerun the same refresh order from STD to dashboard.

Do not refetch every RAW table again until `CHECK_Raw_Duplicate_State` proves what is duplicated.
