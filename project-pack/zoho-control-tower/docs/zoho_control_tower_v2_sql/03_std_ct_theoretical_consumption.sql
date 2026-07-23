-- Query Table: 03_std_ct_theoretical_consumption.sql
-- Logical model name: STD_CT_Theoretical_Consumption
-- Layer: standardized
-- Purpose: Standardize the synthetic theoretical ingredient baseline at outlet-item-month grain.
-- Sources: AUX_Theoretical_Consumption-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    t."source_period_code" AS "source_period_code",
    t."outlet_code" AS "outlet_code",
    t."outlet_name" AS "outlet_name",
    t."item_code" AS "item_code",
    t."item_name" AS "item_name",
    t."category_name" AS "category_name",
    t."super_category_name" AS "super_category_name",
    t."unit" AS "canonical_uom",
    CAST(t."average_price" AS DECIMAL(18,4)) AS "average_unit_cost",
    CAST(t."theoretical_qty" AS DECIMAL(18,6)) AS "theoretical_consumption_qty"
FROM "AUX_Theoretical_Consumption-Copy" t;
