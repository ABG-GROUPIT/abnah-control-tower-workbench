-- Query Table: 14_dim_ct_item.sql
-- Logical model name: DIM_CT_Item
-- Layer: dimension
-- Purpose: Create the item identity, category, UOM and cost reference from Closing Stock.
-- Sources: RAWN_CT_closing_stock-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    c."item_code" AS "item_code",
    MAX(c."item_name") AS "item_name",
    MAX(c."category_name") AS "category_name",
    MAX(c."super_category_name") AS "super_category_name",
    MAX(c."unit_name") AS "canonical_uom",
    CASE
        WHEN COUNT(DISTINCT c."unit_name") = 1 THEN 1
        ELSE NULL
    END AS "uom_conversion_factor",
    AVG(
        CASE
            WHEN CAST(c."average_price" AS DECIMAL(18,4)) > 0
            THEN CAST(c."average_price" AS DECIMAL(18,4))
            ELSE NULL
        END
    ) AS "baseline_average_price",
    NULL AS "reorder_level_qty",
    NULL AS "standard_order_qty",
    NULL AS "primary_vendor",
    NULL AS "alternate_vendor",
    NULL AS "shelf_life_days",
    NULL AS "storage_type",
    NULL AS "food_beverage_non_food_flag",
    NULL AS "criticality",
    'derived_from_closing_stock' AS "source_evidence"
FROM "RAWN_CT_closing_stock-Copy" c
WHERE c."item_code" IS NOT NULL
GROUP BY c."item_code";
