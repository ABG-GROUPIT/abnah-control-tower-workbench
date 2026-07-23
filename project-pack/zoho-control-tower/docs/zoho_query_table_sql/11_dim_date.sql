-- Query Table: DIM_Date
-- Purpose: Reusable date dimension built from all date-bearing standardized tables.
-- Sources: STD_Sales_Report, STD_Purchase_Report, STD_Entry_Report, STD_Inventory_Closing_Report,
--          STD_Holiday_Calendar, STD_Manual_Events
-- Needs Zoho syntax validation: YEAR, MONTH, QUARTER, DAYOFWEEK, CONCAT, and LPAD may differ by Zoho workspace.
-- Fallback: keep only date_value here and create year/month/quarter formula columns in Zoho.

SELECT DISTINCT
    d."date_value" AS "date_value",
    YEAR(d."date_value") AS "year_number",
    MONTH(d."date_value") AS "month_number",
    CONCAT(YEAR(d."date_value"), '-', LPAD(MONTH(d."date_value"), 2, '0')) AS "month_key",
    QUARTER(d."date_value") AS "quarter_number",
    DAYOFWEEK(d."date_value") AS "day_of_week_number",
    CASE DAYOFWEEK(d."date_value")
        WHEN 2 THEN 1
        WHEN 3 THEN 2
        WHEN 4 THEN 3
        WHEN 5 THEN 4
        WHEN 6 THEN 5
        WHEN 7 THEN 6
        WHEN 1 THEN 7
    END AS "day_of_week_sort",
    CASE DAYOFWEEK(d."date_value")
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END AS "day_of_week_name"
FROM (
    SELECT s."sales_date" AS "date_value" FROM "STD_Sales_Report" s
    UNION
    SELECT p."po_date" AS "date_value" FROM "STD_Purchase_Report" p
    UNION
    SELECT p2."expected_delivery_date" AS "date_value" FROM "STD_Purchase_Report" p2
    UNION
    SELECT e."receipt_date" AS "date_value" FROM "STD_Entry_Report" e
    UNION
    SELECT inv."inventory_date" AS "date_value" FROM "STD_Inventory_Closing_Report" inv
    UNION
    SELECT h."calendar_date" AS "date_value" FROM "STD_Holiday_Calendar" h
    UNION
    SELECT ev."start_date" AS "date_value" FROM "STD_Manual_Events" ev
    UNION
    SELECT ev2."end_date" AS "date_value" FROM "STD_Manual_Events" ev2
) d
WHERE d."date_value" IS NOT NULL;
