-- Query Table: 15_dim_ct_menu_item.sql
-- Logical model name: DIM_CT_Menu_Item
-- Layer: dimension
-- Purpose: Create the canonical menu-item dimension from validated sales.
-- Sources: 01_std_ct_sales_item.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    s."item_code" AS "menu_item_code",
    s."item_name" AS "menu_item_name",
    MAX(s."super_category_name") AS "super_category_name",
    MAX(s."category_name") AS "category_name",
    AVG(s."item_rate") AS "average_menu_rate"
FROM "01_std_ct_sales_item.sql" s
GROUP BY s."item_code", s."item_name";
