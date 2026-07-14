-- Query Table: FACT_Sales
-- Purpose: Sales fact enriched with menu metadata and holiday context.
-- Sources: STD_Sales_Report, DIM_Menu_Item, STD_Holiday_Calendar
-- Join keys: item_number, sales_date.
-- Caveat: Sales grain is daily outlet-item aggregate, not individual bills.

SELECT
    s."sales_row_id" AS "sales_row_id",
    s."sales_date" AS "sales_date",
    DAYOFWEEK(s."sales_date") AS "day_of_week_number",
    CASE DAYOFWEEK(s."sales_date")
        WHEN 2 THEN 1
        WHEN 3 THEN 2
        WHEN 4 THEN 3
        WHEN 5 THEN 4
        WHEN 6 THEN 5
        WHEN 7 THEN 6
        WHEN 1 THEN 7
    END AS "day_of_week_sort",
    CASE DAYOFWEEK(s."sales_date")
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END AS "day_of_week_name",
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    s."market_area" AS "market_area",
    s."item_number" AS "item_number",
    s."item_name" AS "item_name",
    COALESCE(m."super_category_name", s."super_category") AS "super_category",
    COALESCE(m."category_name", s."category") AS "category",
    m."menu_rate" AS "menu_rate",
    s."qty" AS "qty",
    s."net_sale" AS "net_sale",
    s."net_sale_per_qty" AS "net_sale_per_qty",
    h."holiday_name" AS "holiday_name",
    h."holiday_type" AS "holiday_type",
    h."impact_direction" AS "holiday_impact_direction"
FROM "STD_Sales_Report" s
LEFT JOIN "DIM_Menu_Item" m
    ON m."item_number" = s."item_number"
LEFT JOIN "STD_Holiday_Calendar" h
    ON h."calendar_date" = s."sales_date";
