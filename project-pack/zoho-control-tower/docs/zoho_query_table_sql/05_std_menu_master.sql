-- Query Table: STD_Menu_Master
-- Purpose: Standardize the menu item master for joins and dashboard filters.
-- Source: RAW_Menu_Master
-- Join keys downstream: item_number, item_name.

SELECT DISTINCT
    m."row_id" AS "menu_row_id",
    m."item_number" AS "item_number",
    m."item_name" AS "item_name",
    m."uid" AS "uid",
    m."item_description" AS "item_description",
    CAST(m."rate" AS DECIMAL(14,2)) AS "menu_rate",
    m."category_name" AS "category_name",
    m."super_category_name" AS "super_category_name",
    CAST(m."non_veg" AS DECIMAL(10,0)) AS "non_veg",
    m."hsn_code" AS "hsn_code",
    m."aggregator_alias_name" AS "aggregator_alias_name",
    m."aggregator_alias_description" AS "aggregator_alias_description",
    m."not_in_sweetshop" AS "not_in_sweetshop",
    CAST(m."has_variant" AS DECIMAL(10,0)) AS "has_variant",
    m."is_inclusive_item" AS "is_inclusive_item",
    m."is_scannable_item" AS "is_scannable_item",
    m."do_not_print_sticker" AS "do_not_print_sticker"
FROM "RAW_Menu_Master" m;
