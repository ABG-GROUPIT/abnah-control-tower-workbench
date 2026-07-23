-- Query Table: 18_fact_ct_sales.sql
-- Logical model name: FACT_CT_Sales
-- Layer: fact
-- Purpose: Expose validated bill-item sales at its native grain.
-- Sources: 01_std_ct_sales_item.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    s.*,
    CASE
        WHEN s."sold_qty" <> 0 THEN s."net_sales" / s."sold_qty"
        ELSE NULL
    END AS "realized_unit_price"
FROM "01_std_ct_sales_item.sql" s;
