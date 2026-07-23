-- Query Table: 19_fact_ct_theoretical_consumption.sql
-- Logical model name: FACT_CT_Theoretical_Consumption
-- Layer: fact
-- Purpose: Expose theoretical ingredient consumption at outlet-item-month grain.
-- Sources: 03_std_ct_theoretical_consumption.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    t.*,
    t."theoretical_consumption_qty" * t."average_unit_cost" AS "theoretical_consumption_value"
FROM "03_std_ct_theoretical_consumption.sql" t;
