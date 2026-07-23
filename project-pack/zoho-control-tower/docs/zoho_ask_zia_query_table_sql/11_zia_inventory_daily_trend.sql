-- Query Table: ZIA_Inventory_Daily_Trend
-- Purpose: Ask Zia-safe inventory trend table.
-- Source: FACT_Inventory_Closing.
-- Grain: one row per outlet, inventory date, material category.
-- Use for: inventory value trend by outlet/category.

SELECT
    i."inventory_date" AS "business_date",
    YEAR(i."inventory_date") AS "year_number",
    MONTH(i."inventory_date") AS "month_number",
    CONCAT(YEAR(i."inventory_date"), '-', LPAD(MONTH(i."inventory_date"), 2, '0')) AS "month_key",
    i."outlet_code" AS "outlet_code",
    i."outlet_name" AS "outlet_name",
    i."market_area" AS "market_area",
    i."category_name" AS "material_category",
    i."super_category_name" AS "material_super_category",
    COUNT(DISTINCT i."item_code") AS "inventory_material_count",
    SUM(i."total_qty") AS "inventory_qty",
    SUM(i."total_amt") AS "inventory_value",
    SUM(i."low_stock_flag") AS "low_stock_item_count",
    SUM(
        CASE
            WHEN i."inventory_pressure_band" IN ('Low', 'Watch') THEN 1
            ELSE 0
        END
    ) AS "watch_material_count"
FROM "FACT_Inventory_Closing" i
GROUP BY
    i."inventory_date",
    YEAR(i."inventory_date"),
    MONTH(i."inventory_date"),
    CONCAT(YEAR(i."inventory_date"), '-', LPAD(MONTH(i."inventory_date"), 2, '0')),
    i."outlet_code",
    i."outlet_name",
    i."market_area",
    i."category_name",
    i."super_category_name";
