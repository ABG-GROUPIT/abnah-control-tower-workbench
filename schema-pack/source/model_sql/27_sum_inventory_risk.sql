-- Query Table: SUM_Inventory_Risk
-- Purpose: Latest inventory pressure table with theoretical consumption context.
-- Sources: FACT_Inventory_Closing, FACT_Theoretical_Consumption
-- Caveat: This is inventory pressure, not stockout prediction.

SELECT
    inv."outlet_code" AS "outlet_code",
    inv."outlet_name" AS "outlet_name",
    inv."market_area" AS "market_area",
    inv."inventory_date" AS "latest_inventory_date",
    inv."item_code" AS "item_code",
    inv."item_name" AS "item_name",
    inv."category_name" AS "category_name",
    inv."super_category_name" AS "super_category_name",
    inv."unit_name" AS "unit_name",
    inv."total_qty" AS "total_qty",
    inv."total_amt" AS "total_amt",
    inv."low_stock_flag" AS "low_stock_flag",
    inv."inventory_pressure_band" AS "inventory_pressure_band",
    COALESCE(tc."total_theoretical_qty", 0) AS "total_theoretical_qty",
    CASE
        WHEN inv."low_stock_flag" = 1 AND COALESCE(tc."total_theoretical_qty", 0) > 0 THEN 'Review after demand'
        WHEN inv."low_stock_flag" = 1 THEN 'Review stock'
        ELSE 'OK'
    END AS "risk_note"
FROM "FACT_Inventory_Closing" inv
INNER JOIN (
    SELECT
        fi."outlet_name" AS "outlet_name",
        fi."outlet_code" AS "outlet_code",
        fi."market_area" AS "market_area",
        fi."item_code" AS "item_code",
        MAX(fi."inventory_date") AS "latest_inventory_date"
    FROM "FACT_Inventory_Closing" fi
    GROUP BY
        fi."outlet_name",
        fi."outlet_code",
        fi."market_area",
        fi."item_code"
) latest
    ON latest."outlet_name" = inv."outlet_name"
   AND latest."outlet_code" = inv."outlet_code"
   AND latest."market_area" = inv."market_area"
   AND latest."item_code" = inv."item_code"
   AND latest."latest_inventory_date" = inv."inventory_date"
LEFT JOIN (
    SELECT
        ft."outlet_name" AS "outlet_name",
        ft."market_area" AS "market_area",
        ft."ingredient_name" AS "ingredient_name",
        SUM(ft."theoretical_ingredient_qty") AS "total_theoretical_qty"
    FROM "FACT_Theoretical_Consumption" ft
    GROUP BY
        ft."outlet_name",
        ft."market_area",
        ft."ingredient_name"
) tc
    ON tc."outlet_name" = inv."outlet_name"
   AND tc."market_area" = inv."market_area"
   AND tc."ingredient_name" = inv."item_name";
