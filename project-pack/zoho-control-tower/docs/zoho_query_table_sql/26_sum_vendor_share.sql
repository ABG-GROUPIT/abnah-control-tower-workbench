-- Query Table: SUM_Vendor_Share
-- Purpose: Vendor share of ordered and received value.
-- Source: FACT_Vendor_Spend
-- Dashboard usage: Vendor and procurement analytics.

SELECT
    v."outlet_code" AS "outlet_code",
    v."outlet_name" AS "outlet_name",
    v."market_area" AS "market_area",
    v."vendor_name" AS "vendor_name",
    SUM(v."ordered_value") AS "total_ordered_value",
    SUM(v."received_value") AS "total_received_value",
    SUM(v."po_line_count") AS "po_line_count",
    SUM(v."receipt_line_count") AS "receipt_line_count",
    CASE
        WHEN t."outlet_ordered_value" <> 0
        THEN SUM(v."ordered_value") / t."outlet_ordered_value" * 100
        ELSE NULL
    END AS "ordered_value_share_pct",
    CASE
        WHEN t."outlet_received_value" <> 0
        THEN SUM(v."received_value") / t."outlet_received_value" * 100
        ELSE NULL
    END AS "received_value_share_pct"
FROM "FACT_Vendor_Spend" v
LEFT JOIN (
        SELECT
            fvs."outlet_code" AS "outlet_code",
            SUM(fvs."ordered_value") AS "outlet_ordered_value",
            SUM(fvs."received_value") AS "outlet_received_value"
        FROM "FACT_Vendor_Spend" fvs
        GROUP BY fvs."outlet_code"
     ) t
    ON t."outlet_code" = v."outlet_code"
GROUP BY
    v."outlet_code",
    v."outlet_name",
    v."market_area",
    v."vendor_name",
    t."outlet_ordered_value",
    t."outlet_received_value";
