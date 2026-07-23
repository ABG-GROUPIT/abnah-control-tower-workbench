-- Query Table: ZIA_Sales_Menu_Item_Summary
-- Purpose: Ask Zia-safe menu item performance summary.
-- Source: SUM_Menu_Item_Performance.
-- Grain: one row per outlet and menu item for the loaded period.
-- Use for: item winners, revenue vs quantity, realized price vs menu rate.

SELECT
    m."outlet_code" AS "outlet_code",
    m."outlet_name" AS "outlet_name",
    m."market_area" AS "market_area",
    m."item_number" AS "menu_item_code",
    m."item_name" AS "menu_item_name",
    m."super_category" AS "super_category",
    m."category" AS "category",
    m."total_qty" AS "menu_units_sold",
    m."total_net_sale" AS "net_sales",
    m."avg_realized_unit_price" AS "average_realized_unit_price",
    m."avg_price_index" AS "competitor_price_index",
    m."price_position" AS "price_position",
    m."performance_note" AS "menu_performance_note"
FROM "SUM_Menu_Item_Performance" m;
