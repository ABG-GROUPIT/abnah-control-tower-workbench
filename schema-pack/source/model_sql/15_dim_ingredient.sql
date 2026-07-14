-- Query Table: DIM_Ingredient
-- Purpose: Reusable material/ingredient dimension across inventory, procurement, receipts, and recipe BOM.
-- Sources: STD_Inventory_Closing_Report, STD_Purchase_Report, STD_Entry_Report, STD_Recipe_BOM
-- Join keys: ingredient_code where available, ingredient_name where code is missing.

SELECT
    COALESCE(i."ingredient_code", i."ingredient_name") AS "ingredient_key",
    i."ingredient_code" AS "ingredient_code",
    i."ingredient_name" AS "ingredient_name",
    MAX(i."category_name") AS "category_name",
    MAX(i."super_category_name") AS "super_category_name",
    MAX(i."unit_name") AS "default_unit",
    MAX(i."source_type") AS "source_type"
FROM (
    SELECT
        inv."item_code" AS "ingredient_code",
        inv."item_name" AS "ingredient_name",
        inv."category_name" AS "category_name",
        inv."super_category_name" AS "super_category_name",
        inv."unit_name" AS "unit_name",
        'Inventory' AS "source_type"
    FROM "STD_Inventory_Closing_Report" inv

    UNION ALL

    SELECT
        p."item_code" AS "ingredient_code",
        p."item_name" AS "ingredient_name",
        p."category_name" AS "category_name",
        p."super_category_name" AS "super_category_name",
        p."unit" AS "unit_name",
        'Purchase' AS "source_type"
    FROM "STD_Purchase_Report" p

    UNION ALL

    SELECT
        e."item_code" AS "ingredient_code",
        e."item_name" AS "ingredient_name",
        e."category_name" AS "category_name",
        e."super_category_name" AS "super_category_name",
        e."unit" AS "unit_name",
        'Entry' AS "source_type"
    FROM "STD_Entry_Report" e

    UNION ALL

    SELECT
        NULL AS "ingredient_code",
        b."ingredient_name" AS "ingredient_name",
        NULL AS "category_name",
        NULL AS "super_category_name",
        b."ingredient_unit" AS "unit_name",
        'Recipe BOM' AS "source_type"
    FROM "STD_Recipe_BOM" b
) i
WHERE i."ingredient_name" IS NOT NULL
  AND TRIM(i."ingredient_name") <> ''
GROUP BY
    COALESCE(i."ingredient_code", i."ingredient_name"),
    i."ingredient_code",
    i."ingredient_name";
