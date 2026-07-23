-- Query Table: 35_sum_ct_financial_leakage.sql
-- Logical model name: SUM_CT_Financial_Leakage
-- Layer: summary
-- Purpose: Summarize observed wastage separately from demo expiry and unavailable vendor returns.
-- Sources: 09_std_ct_wastage.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    "source_period_code" AS "source_period_code",
    "outlet_code" AS "outlet_code",
    "outlet_name" AS "outlet_name",
    'WASTAGE' AS "leakage_type",
    SUM("wastage_value") AS "leakage_value",
    'observed' AS "evidence_type"
FROM "09_std_ct_wastage.sql"
GROUP BY "source_period_code", "outlet_code", "outlet_name";
