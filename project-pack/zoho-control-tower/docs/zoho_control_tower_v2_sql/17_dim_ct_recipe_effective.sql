-- Query Table: 17_dim_ct_recipe_effective.sql
-- Logical model name: DIM_CT_Recipe_Effective
-- Layer: dimension
-- Purpose: Resolve recipe ingredients to canonical item UOM and unit cost.
-- Sources: RAWN_CT_item_recipe_report-Copy, RAWN_CT_closing_stock-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    r."menu_item_number" AS "menu_item_code",
    r."menu_item_name" AS "menu_item_name",
    r."ingredient_code" AS "ingredient_code",
    r."ingredient_name" AS "ingredient_name",
    CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6)) AS "recipe_qty_per_menu_unit",
    r."recipe_unit" AS "recipe_uom",
    i."canonical_uom" AS "canonical_uom",
    CASE
        WHEN LOWER(r."recipe_unit") = LOWER(i."canonical_uom") THEN 1
        ELSE NULL
    END AS "uom_conversion_factor",
    CASE
        WHEN LOWER(r."recipe_unit") = LOWER(i."canonical_uom")
        THEN CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6))
        ELSE NULL
    END AS "canonical_recipe_qty",
    CAST(i."average_price" AS DECIMAL(18,4)) AS "ingredient_unit_cost",
    CASE
        WHEN LOWER(r."recipe_unit") = LOWER(i."canonical_uom")
        THEN CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6))
          * CAST(i."average_price" AS DECIMAL(18,4))
        ELSE NULL
    END AS "ingredient_cost_per_menu_unit"
FROM "RAWN_CT_item_recipe_report-Copy" r
LEFT JOIN (
    SELECT
        "item_code" AS "item_code",
        MAX("unit_name") AS "canonical_uom",
        AVG(
            CASE
                WHEN CAST("average_price" AS DECIMAL(18,4)) > 0
                THEN CAST("average_price" AS DECIMAL(18,4))
                ELSE NULL
            END
        ) AS "average_price"
    FROM "RAWN_CT_closing_stock-Copy"
    GROUP BY "item_code"
) i
  ON r."ingredient_code" = i."item_code"
WHERE r."menu_item_number" IS NOT NULL
  AND r."ingredient_code" IS NOT NULL;
