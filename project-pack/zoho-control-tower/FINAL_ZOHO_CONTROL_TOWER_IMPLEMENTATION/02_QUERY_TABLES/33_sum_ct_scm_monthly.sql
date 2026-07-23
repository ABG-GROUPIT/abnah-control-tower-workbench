-- Query Table: 33_sum_ct_scm_monthly.sql
-- Logical model name: SUM_CT_SCM_Monthly
-- Layer: summary
-- Purpose: Join monthly sales, closing stock, open PO and actual consumption for Page 4.
-- Sources: 18_fact_ct_sales.sql, 05_std_ct_inventory_snapshot.sql, 22_fact_ct_purchase_order.sql, 20_fact_ct_actual_consumption.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    k."source_period_code" AS "source_period_code",
    k."outlet_code" AS "outlet_code",
    k."outlet_name" AS "outlet_name",
    COALESCE(s."net_sales", 0) AS "net_sales",
    COALESCE(i."closing_stock_value", 0) AS "closing_stock_value",
    COALESCE(p."open_po_value", 0) AS "open_po_value",
    COALESCE(a."actual_consumption_value", 0) AS "actual_consumption_value"
FROM (
    SELECT DISTINCT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name"
    FROM "05_std_ct_inventory_snapshot.sql"
) k
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("net_sales") AS "net_sales"
    FROM "18_fact_ct_sales.sql"
    GROUP BY "source_period_code", "outlet_code"
) s
  ON k."source_period_code" = s."source_period_code"
 AND k."outlet_code" = s."outlet_code"
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("closing_value") AS "closing_stock_value"
    FROM "05_std_ct_inventory_snapshot.sql"
    GROUP BY "source_period_code", "outlet_code"
) i
  ON k."source_period_code" = i."source_period_code"
 AND k."outlet_code" = i."outlet_code"
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("open_po_value") AS "open_po_value"
    FROM "22_fact_ct_purchase_order.sql"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code"
) p
  ON k."source_period_code" = p."source_period_code"
 AND k."outlet_code" = p."outlet_code"
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("calculated_actual_consumption_value") AS "actual_consumption_value"
    FROM "20_fact_ct_actual_consumption.sql"
    GROUP BY "source_period_code", "outlet_code"
) a
  ON k."source_period_code" = a."source_period_code"
 AND k."outlet_code" = a."outlet_code";
