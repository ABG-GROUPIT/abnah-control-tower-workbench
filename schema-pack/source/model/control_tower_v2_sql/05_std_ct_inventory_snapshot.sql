-- Query Table: 05_std_ct_inventory_snapshot.sql
-- Logical model name: STD_CT_Inventory_Snapshot
-- Layer: standardized
-- Purpose: Standardize closing stock quantity and value checkpoints.
-- Sources: RAWN_CT_closing_stock-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    c."source_period_code" AS "source_period_code",
    c."source_outlet_code" AS "outlet_code",
    c."deployment_name" AS "outlet_name",
    CAST(c."stock_date" AS DATE) AS "snapshot_date",
    c."item_code" AS "item_code",
    c."item_name" AS "item_name",
    c."category_code" AS "category_code",
    c."category_name" AS "category_name",
    c."super_category_code" AS "super_category_code",
    c."super_category_name" AS "super_category_name",
    c."unit_name" AS "canonical_uom",
    CAST(c."average_price" AS DECIMAL(18,4)) AS "average_unit_cost",
    CAST(c."total_qty" AS DECIMAL(18,6)) AS "closing_qty",
    CAST(c."total_amt" AS DECIMAL(18,2)) AS "closing_value"
FROM "RAWN_CT_closing_stock-Copy" c;
