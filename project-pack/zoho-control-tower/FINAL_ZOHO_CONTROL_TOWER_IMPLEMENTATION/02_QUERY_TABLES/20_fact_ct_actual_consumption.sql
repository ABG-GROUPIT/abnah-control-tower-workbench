-- Query Table: 20_fact_ct_actual_consumption.sql
-- Logical model name: FACT_CT_Actual_Consumption
-- Layer: fact
-- Purpose: Calculate the approved inventory movement bridge for actual consumption.
-- Sources: 04_std_ct_inventory_period.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    p.*,
    -1 * p."transfer_out_qty" AS "bridge_transfer_out_qty",
    -1 * p."return_qty" AS "bridge_return_qty",
    -1 * p."closing_qty" AS "bridge_closing_qty",
    p."opening_qty"
      + p."purchase_qty"
      + p."transfer_in_qty"
      - p."transfer_out_qty"
      - p."return_qty"
      - p."closing_qty" AS "calculated_actual_consumption_qty",
    (
      p."opening_qty"
      + p."purchase_qty"
      + p."transfer_in_qty"
      - p."transfer_out_qty"
      - p."return_qty"
      - p."closing_qty"
    ) * p."average_unit_cost" AS "calculated_actual_consumption_value"
FROM "04_std_ct_inventory_period.sql" p;
