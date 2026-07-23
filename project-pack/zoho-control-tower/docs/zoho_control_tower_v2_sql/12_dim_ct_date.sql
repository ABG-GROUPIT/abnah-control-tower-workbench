-- Query Table: 12_dim_ct_date.sql
-- Logical model name: DIM_CT_Date
-- Layer: dimension
-- Purpose: Create the sales-date calendar used by the three-month baseline.
-- Sources: 01_std_ct_sales_item.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT DISTINCT
    s."sales_date" AS "calendar_date",
    YEAR(s."sales_date") AS "calendar_year",
    MONTH(s."sales_date") AS "calendar_month_number",
    DAY(s."sales_date") AS "calendar_day",
    DAYOFWEEK(s."sales_date") AS "day_of_week_number",
    CASE
        WHEN DAYOFWEEK(s."sales_date") IN (1, 7) THEN 1
        ELSE 0
    END AS "is_weekend"
FROM "01_std_ct_sales_item.sql" s;
