-- Query Table: 13_dim_ct_outlet.sql
-- Logical model name: DIM_CT_Outlet
-- Layer: dimension
-- Purpose: Create the outlet identity dimension from the captured stock source.
-- Sources: RAWN_CT_closing_stock-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    c."source_outlet_code" AS "outlet_code",
    MAX(c."source_outlet_name") AS "outlet_name",
    NULL AS "region",
    NULL AS "city",
    NULL AS "market_area",
    NULL AS "latitude",
    NULL AS "longitude",
    NULL AS "new_matured_flag",
    NULL AS "active_status",
    'derived_from_closing_stock' AS "source_evidence"
FROM "RAWN_CT_closing_stock-Copy" c
WHERE c."source_outlet_code" IS NOT NULL
GROUP BY c."source_outlet_code";
