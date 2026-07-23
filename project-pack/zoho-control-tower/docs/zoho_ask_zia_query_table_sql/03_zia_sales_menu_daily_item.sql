-- Query Table: ZIA_Sales_Menu_Daily_Item
-- Purpose: Ask Zia-safe item-level sales table.
-- Source: FACT_Sales.
-- Grain: one row per outlet, business_date, menu item.
-- Use for: top menu items, item sales, quantity, realized price, item/category filters.

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
    s."item_number" AS "menu_item_code",
    s."item_name" AS "menu_item_name",
    s."super_category" AS "super_category",
    s."category" AS "category",
    s."menu_rate" AS "menu_rate",
    s."qty" AS "menu_units_sold",
    s."net_sale" AS "net_sales",
    s."net_sale_per_qty" AS "realized_unit_price",
    CASE
        WHEN s."menu_rate" <> 0 THEN s."net_sale_per_qty" * 100 / s."menu_rate"
        ELSE NULL
    END AS "realized_price_to_menu_rate_pct",
    s."holiday_name" AS "holiday_name",
    s."holiday_type" AS "holiday_type"
FROM "FACT_Sales" s;
