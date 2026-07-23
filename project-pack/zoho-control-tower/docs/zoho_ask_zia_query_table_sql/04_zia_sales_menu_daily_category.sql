-- Query Table: ZIA_Sales_Menu_Daily_Category
-- Purpose: Ask Zia-safe category sales table.
-- Source: FACT_Sales.
-- Grain: one row per outlet, business_date, category.
-- Use for: category revenue mix, category trend, weekday/category questions.

SELECT
    s."sales_date" AS "business_date",
    YEAR(s."sales_date") AS "year_number",
    MONTH(s."sales_date") AS "month_number",
    CONCAT(YEAR(s."sales_date"), '-', LPAD(MONTH(s."sales_date"), 2, '0')) AS "month_key",
    s."day_of_week_number" AS "day_of_week_number",
    s."day_of_week_sort" AS "day_of_week_sort",
    s."day_of_week_name" AS "day_of_week_name",
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    s."market_area" AS "market_area",
    s."super_category" AS "super_category",
    s."category" AS "category",
    COUNT(DISTINCT s."item_number") AS "active_menu_item_count",
    SUM(s."qty") AS "menu_units_sold",
    SUM(s."net_sale") AS "net_sales",
    CASE
        WHEN SUM(s."qty") <> 0 THEN SUM(s."net_sale") / SUM(s."qty")
        ELSE NULL
    END AS "average_realized_unit_price"
FROM "FACT_Sales" s
GROUP BY
    s."sales_date",
    YEAR(s."sales_date"),
    MONTH(s."sales_date"),
    CONCAT(YEAR(s."sales_date"), '-', LPAD(MONTH(s."sales_date"), 2, '0')),
    s."day_of_week_number",
    s."day_of_week_sort",
    s."day_of_week_name",
    s."outlet_code",
    s."outlet_name",
    s."market_area",
    s."super_category",
    s."category";
