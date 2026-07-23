-- Query Table: FACT_Inventory_Closing
-- Purpose: Daily closing inventory fact with simple pressure flags.
-- Sources: STD_Inventory_Closing_Report, DIM_Ingredient
-- Caveat: low_stock_flag is heuristic and should not be described as stockout prediction.

SELECT
    inv."inventory_row_id" AS "inventory_row_id",
    inv."inventory_date" AS "inventory_date",
    inv."outlet_code" AS "outlet_code",
    inv."outlet_name" AS "outlet_name",
    inv."market_area" AS "market_area",
    inv."generation_date" AS "generation_date",
    inv."generation_time" AS "generation_time",
    inv."item_code" AS "item_code",
    inv."item_name" AS "item_name",
    inv."super_category_code" AS "super_category_code",
    inv."super_category_name" AS "super_category_name",
    inv."category_code" AS "category_code",
    inv."category_name" AS "category_name",
    inv."unit_name" AS "unit_name",
    inv."average_price" AS "average_price",
    inv."store_stock_qty" AS "store_stock_qty",
    inv."total_qty" AS "total_qty",
    inv."total_amt" AS "total_amt",
    CASE
        WHEN inv."total_qty" <= 10 THEN 1
        ELSE 0
    END AS "low_stock_flag",
    CASE
        WHEN inv."total_qty" <= 10 THEN 'Low'
        WHEN inv."total_qty" <= 25 THEN 'Watch'
        ELSE 'OK'
    END AS "inventory_pressure_band"
FROM "STD_Inventory_Closing_Report" inv
LEFT JOIN "DIM_Ingredient" i
    ON i."ingredient_code" = inv."item_code";
