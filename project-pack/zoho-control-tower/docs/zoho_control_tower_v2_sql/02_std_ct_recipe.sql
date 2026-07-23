-- Query Table: 02_std_ct_recipe.sql
-- Logical model name: STD_CT_Recipe
-- Layer: standardized
-- Purpose: Standardize menu-item-to-ingredient recipe quantities.
-- Sources: RAWN_CT_item_recipe_report-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    r."menu_item_type" AS "menu_item_type",
    r."menu_item_number" AS "menu_item_code",
    r."menu_item_name" AS "menu_item_name",
    r."recipe_item_type" AS "recipe_item_type",
    r."ingredient_code" AS "ingredient_code",
    r."ingredient_name" AS "ingredient_name",
    CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6)) AS "recipe_qty_per_menu_unit",
    r."recipe_unit" AS "recipe_uom"
FROM "RAWN_CT_item_recipe_report-Copy" r
WHERE r."menu_item_number" IS NOT NULL
  AND r."ingredient_code" IS NOT NULL;
