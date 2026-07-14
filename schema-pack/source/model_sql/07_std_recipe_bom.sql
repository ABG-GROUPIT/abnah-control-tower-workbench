-- Query Table: STD_Recipe_BOM
-- Purpose: Normalize the ABNAH-style recipe block export into one fully identified row per ingredient.
-- Source: RAW_Brand_Recipe_Consumption
-- Special handling: recipe_name, recipe_qty, and recipe_unit are blank on continuation rows.
-- Logic: each ingredient row is attached to the most recent recipe header row at or before its row_id.

SELECT DISTINCT
    b."row_id" AS "bom_row_id",
    h."recipe_name" AS "recipe_name_filled",
    h."recipe_qty" AS "recipe_qty_filled",
    h."recipe_unit" AS "recipe_unit_filled",
    b."item_name" AS "ingredient_name",
    CAST(b."item_qty" AS DECIMAL(14,4)) AS "ingredient_qty",
    b."item_unit" AS "ingredient_unit",
    b."item_tab_type" AS "item_tab_type"
FROM "RAW_Brand_Recipe_Consumption" b
JOIN "RAW_Brand_Recipe_Consumption" h
    ON h."row_id" <= b."row_id"
   AND h."recipe_name" IS NOT NULL
   AND TRIM(h."recipe_name") <> ''
LEFT JOIN "RAW_Brand_Recipe_Consumption" hn
    ON hn."row_id" <= b."row_id"
   AND hn."row_id" > h."row_id"
   AND hn."recipe_name" IS NOT NULL
   AND TRIM(hn."recipe_name") <> ''
WHERE hn."row_id" IS NULL;
