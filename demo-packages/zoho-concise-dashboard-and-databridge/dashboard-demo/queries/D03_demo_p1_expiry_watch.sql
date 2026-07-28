-- Query Table: D03_demo_p1_expiry_watch.sql
-- Purpose: Concise Page 1 estimated expiry watch for the time-boxed visual demo.
-- Source: AUX_Expiry_Estimate-Copy
-- Dependency level: 1
-- Governance: Values remain synthetic estimates, not POSIST batch/expiry truth.
SELECT
    e."source_period_code" AS "source_period_code",
    e."as_of_date" AS "filter_date",
    e."outlet_name" AS "filter_outlet",
    e."category_name" AS "filter_category",
    CASE
        WHEN e."risk_status" IN ('EXPIRED', 'EXPIRES_TODAY')
        THEN 'PURPLE'
        WHEN e."risk_status" = 'CRITICAL' THEN 'RED'
        ELSE 'AMBER'
    END AS "filter_severity",
    e."outlet_code" AS "outlet_code",
    e."item_code" AS "item_code",
    e."item_name" AS "item_name",
    e."vendor_name" AS "vendor_name",
    e."batch_number" AS "batch_number",
    e."unit" AS "canonical_uom",
    e."qty_at_risk" AS "expiry_qty_at_risk",
    e."estimated_expiry_date" AS "estimated_expiry_date",
    e."days_to_expiry" AS "days_to_expiry",
    e."expiry_risk_value" AS "expiry_risk_value",
    e."risk_status" AS "expiry_status",
    CASE
        WHEN e."risk_status" = 'EXPIRED'
        THEN 'Quarantine and investigate'
        WHEN e."risk_status" IN ('EXPIRES_TODAY', 'CRITICAL')
        THEN 'Transfer, promote, or consume'
        ELSE 'Review FIFO rotation'
    END AS "recommended_action",
    e."is_estimated" AS "is_estimated",
    e."production_use_status" AS "production_use_status"
FROM "AUX_Expiry_Estimate-Copy" e;
