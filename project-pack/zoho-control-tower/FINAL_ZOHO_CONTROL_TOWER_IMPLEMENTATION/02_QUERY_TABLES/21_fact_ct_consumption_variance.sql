-- Query Table: 21_fact_ct_consumption_variance.sql
-- Logical model name: FACT_CT_Consumption_Variance
-- Layer: fact
-- Purpose: Compare actual and theoretical ingredient consumption.
-- Sources: 20_fact_ct_actual_consumption.sql, 19_fact_ct_theoretical_consumption.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    a."source_period_code" AS "source_period_code",
    a."outlet_code" AS "outlet_code",
    a."outlet_name" AS "outlet_name",
    a."closing_date" AS "closing_date",
    a."item_code" AS "item_code",
    a."item_name" AS "item_name",
    a."category_name" AS "category_name",
    a."super_category_name" AS "super_category_name",
    a."canonical_uom" AS "canonical_uom",
    a."average_unit_cost" AS "average_unit_cost",
    a."calculated_actual_consumption_qty" AS "actual_consumption_qty",
    COALESCE(t."theoretical_consumption_qty", 0) AS "theoretical_consumption_qty",
    a."calculated_actual_consumption_qty" - COALESCE(t."theoretical_consumption_qty", 0) AS "variance_qty",
    CASE
        WHEN a."calculated_actual_consumption_qty" > COALESCE(t."theoretical_consumption_qty", 0)
        THEN (a."calculated_actual_consumption_qty" - COALESCE(t."theoretical_consumption_qty", 0)) * a."average_unit_cost"
        ELSE 0
    END AS "leakage_value",
    CASE
        WHEN a."calculated_actual_consumption_qty" < COALESCE(t."theoretical_consumption_qty", 0)
        THEN COALESCE(t."theoretical_consumption_qty", 0) - a."calculated_actual_consumption_qty"
        ELSE 0
    END AS "low_consumption_qty"
FROM "20_fact_ct_actual_consumption.sql" a
LEFT JOIN "19_fact_ct_theoretical_consumption.sql" t
  ON a."source_period_code" = t."source_period_code"
 AND a."outlet_code" = t."outlet_code"
 AND a."item_code" = t."item_code";
