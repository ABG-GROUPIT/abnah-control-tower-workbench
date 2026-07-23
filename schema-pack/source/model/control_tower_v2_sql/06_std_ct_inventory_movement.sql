-- Query Table: 06_std_ct_inventory_movement.sql
-- Logical model name: STD_CT_Inventory_Movement
-- Layer: standardized
-- Purpose: Unify internal transfers and wastage into signed inventory movements.
-- Sources: RAWN_CT_enterprise_transfer_from-Copy, RAWN_CT_enterprise_transfer_to-Copy, RAWN_CT_enterprise_wastage_normal-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    f."source_period_code" AS "source_period_code",
    f."source_outlet_code" AS "outlet_code",
    f."deployment_name" AS "outlet_name",
    CAST(f."transfer_date" AS DATE) AS "movement_date",
    f."transaction_number" AS "transaction_number",
    f."item_code" AS "item_code",
    f."item_name" AS "item_name",
    f."category_name" AS "category_name",
    f."super_category_name" AS "super_category_name",
    f."unit" AS "canonical_uom",
    'TRANSFER_OUT' AS "movement_type",
    -1 * CAST(f."transfer_qty" AS DECIMAL(18,6)) AS "signed_qty",
    -1 * CAST(f."transfer_amt" AS DECIMAL(18,2)) AS "signed_value"
FROM "RAWN_CT_enterprise_transfer_from-Copy" f
UNION ALL
SELECT
    t."source_period_code" AS "source_period_code",
    t."source_outlet_code" AS "outlet_code",
    t."deployment_name" AS "outlet_name",
    CAST(t."transfer_date" AS DATE) AS "movement_date",
    t."transaction_number" AS "transaction_number",
    t."item_code" AS "item_code",
    t."item_name" AS "item_name",
    t."category_name" AS "category_name",
    t."super_category_name" AS "super_category_name",
    t."unit" AS "canonical_uom",
    'TRANSFER_IN' AS "movement_type",
    CAST(t."transfer_qty" AS DECIMAL(18,6)) AS "signed_qty",
    CAST(t."transfer_amt" AS DECIMAL(18,2)) AS "signed_value"
FROM "RAWN_CT_enterprise_transfer_to-Copy" t
UNION ALL
SELECT
    w."source_period_code" AS "source_period_code",
    w."source_outlet_code" AS "outlet_code",
    w."deployment_name" AS "outlet_name",
    CAST(w."wastage_date" AS DATE) AS "movement_date",
    w."transaction_number" AS "transaction_number",
    w."item_code" AS "item_code",
    w."item_name" AS "item_name",
    w."category_name" AS "category_name",
    w."super_category_name" AS "super_category_name",
    w."unit" AS "canonical_uom",
    'WASTAGE' AS "movement_type",
    -1 * CAST(w."wastage_qty" AS DECIMAL(18,6)) AS "signed_qty",
    -1 * CAST(w."wastage_amt" AS DECIMAL(18,2)) AS "signed_value"
FROM "RAWN_CT_enterprise_wastage_normal-Copy" w;
