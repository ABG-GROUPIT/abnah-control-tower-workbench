-- Query Table: 09_std_ct_wastage.sql
-- Logical model name: STD_CT_Wastage
-- Layer: standardized
-- Purpose: Standardize inventory wastage transactions.
-- Sources: RAWN_CT_enterprise_wastage_normal-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    w."source_period_code" AS "source_period_code",
    w."source_outlet_code" AS "outlet_code",
    w."deployment_name" AS "outlet_name",
    w."store_kitchen_name" AS "store_kitchen_name",
    CAST(w."wastage_date" AS DATE) AS "wastage_date",
    w."transaction_number" AS "transaction_number",
    w."item_code" AS "item_code",
    w."item_name" AS "item_name",
    w."category_name" AS "category_name",
    w."super_category_name" AS "super_category_name",
    w."comment" AS "wastage_reason",
    CAST(w."wastage_qty" AS DECIMAL(18,6)) AS "wastage_qty",
    w."unit" AS "canonical_uom",
    CAST(w."unit_price" AS DECIMAL(18,4)) AS "unit_price",
    CAST(w."wastage_amt" AS DECIMAL(18,2)) AS "wastage_value"
FROM "RAWN_CT_enterprise_wastage_normal-Copy" w;
