-- Query Table: DIM_Menu_Item
-- Purpose: Reusable menu item dimension from menu master plus any sold items not found in the master.
-- Sources: STD_Menu_Master, STD_Sales_Report
-- Join keys: item_number, item_name.

SELECT
    m."item_number" AS "menu_item_key",
    m."item_number" AS "item_number",
    m."item_name" AS "item_name",
    m."menu_rate" AS "menu_rate",
    m."category_name" AS "category_name",
    m."super_category_name" AS "super_category_name",
    m."non_veg" AS "non_veg",
    m."has_variant" AS "has_variant",
    'Menu Master' AS "source_type"
FROM "STD_Menu_Master" m

UNION

SELECT
    s."item_number" AS "menu_item_key",
    s."item_number" AS "item_number",
    s."item_name" AS "item_name",
    NULL AS "menu_rate",
    MAX(s."category") AS "category_name",
    MAX(s."super_category") AS "super_category_name",
    NULL AS "non_veg",
    NULL AS "has_variant",
    'Sales Only' AS "source_type"
FROM "STD_Sales_Report" s
LEFT JOIN "STD_Menu_Master" mm
    ON mm."item_number" = s."item_number"
WHERE mm."item_number" IS NULL
GROUP BY
    s."item_number",
    s."item_name";
