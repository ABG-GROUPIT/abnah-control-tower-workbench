-- Query Table: 29_sum_ct_procurement_funnel.sql
-- Logical model name: SUM_CT_Procurement_Funnel
-- Layer: summary
-- Purpose: Summarize ordered, received, pending and delayed PO value for Page 2.
-- Sources: 22_fact_ct_purchase_order.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    p."source_period_code" AS "source_period_code",
    p."as_of_date" AS "as_of_date",
    p."outlet_code" AS "outlet_code",
    p."outlet_name" AS "outlet_name",
    p."vendor_name" AS "vendor_name",
    SUM(p."gross_order_value") AS "ordered_value",
    SUM(p."processed_po_value") AS "processed_value",
    SUM(p."open_po_value") AS "pending_value",
    SUM(CASE WHEN p."delayed_po_flag" = 1 THEN p."open_po_value" ELSE 0 END) AS "delayed_value",
    COUNT(DISTINCT p."po_number") AS "po_count",
    COUNT(DISTINCT CASE WHEN p."is_open_po" = 1 THEN p."po_number" ELSE NULL END) AS "open_po_count"
FROM "22_fact_ct_purchase_order.sql" p
GROUP BY
    p."source_period_code",
    p."as_of_date",
    p."outlet_code",
    p."outlet_name",
    p."vendor_name";
