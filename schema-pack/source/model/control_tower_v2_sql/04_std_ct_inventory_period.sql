-- Query Table: 04_std_ct_inventory_period.sql
-- Logical model name: STD_CT_Inventory_Period
-- Layer: standardized
-- Purpose: Standardize month-end inventory, actual consumption and source variance measures.
-- Sources: RAWN_CT_enterprise_variance_normal-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    v."source_period_code" AS "source_period_code",
    v."source_outlet_code" AS "outlet_code",
    v."deployment_name" AS "outlet_name",
    v."store_kitchen_name" AS "store_kitchen_name",
    v."item_code" AS "item_code",
    v."item_name" AS "item_name",
    v."category_name" AS "category_name",
    v."super_category_name" AS "super_category_name",
    v."unit" AS "canonical_uom",
    CAST(v."average_price" AS DECIMAL(18,4)) AS "average_unit_cost",
    CAST(v."opening_date" AS DATE) AS "opening_date",
    CAST(v."closing_date" AS DATE) AS "closing_date",
    CAST(v."opening_qty" AS DECIMAL(18,6)) AS "opening_qty",
    CAST(v."purchase_qty" AS DECIMAL(18,6)) AS "purchase_qty",
    CAST(v."stock_in_qty" AS DECIMAL(18,6)) AS "transfer_in_qty",
    CAST(v."stock_out_qty" AS DECIMAL(18,6)) AS "transfer_out_qty",
    CAST(v."return_qty" AS DECIMAL(18,6)) AS "return_qty",
    CAST(v."wastage_qty" AS DECIMAL(18,6)) AS "wastage_qty",
    CAST(v."closing_qty" AS DECIMAL(18,6)) AS "closing_qty",
    CAST(v."physical_qty" AS DECIMAL(18,6)) AS "physical_qty",
    CAST(v."actual_consumption_qty" AS DECIMAL(18,6)) AS "actual_consumption_qty",
    CAST(v."variance_qty" AS DECIMAL(18,6)) AS "source_variance_qty",
    CAST(v."variance_percent" AS DECIMAL(18,4)) AS "source_variance_percent"
FROM "RAWN_CT_enterprise_variance_normal-Copy" v;
