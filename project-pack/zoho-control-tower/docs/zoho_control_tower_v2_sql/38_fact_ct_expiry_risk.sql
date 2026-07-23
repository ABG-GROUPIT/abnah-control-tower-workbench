-- Query Table: 38_fact_ct_expiry_risk.sql
-- Logical model name: FACT_CT_Expiry_Risk
-- Layer: fact
-- Purpose: Expose traceable batch-linked demo expiry exposure without claiming POSIST batch truth.
-- Sources: AUX_Expiry_Estimate-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    e."source_period_code" AS "source_period_code",
    e."as_of_date" AS "as_of_date",
    e."outlet_code" AS "outlet_code",
    e."outlet_name" AS "outlet_name",
    e."region" AS "region",
    e."city" AS "city",
    e."market_area" AS "market_area",
    e."latitude" AS "latitude",
    e."longitude" AS "longitude",
    e."store_name" AS "store_name",
    e."batch_allocation_id" AS "batch_allocation_id",
    e."batch_number" AS "batch_number",
    e."receipt_date" AS "receipt_date",
    e."grn_number" AS "grn_number",
    e."po_number" AS "po_number",
    e."vendor_name" AS "vendor_name",
    e."receipt_source_status" AS "receipt_source_status",
    e."item_code" AS "item_code",
    e."item_name" AS "item_name",
    e."category_name" AS "category_name",
    e."unit" AS "canonical_uom",
    e."available_qty" AS "available_qty",
    e."received_qty" AS "received_qty",
    e."batch_remaining_qty" AS "batch_remaining_qty",
    e."item_closing_qty" AS "item_closing_qty",
    e."qty_at_risk" AS "expiry_qty_at_risk",
    e."average_unit_cost" AS "average_unit_cost",
    e."shelf_life_days_assumption" AS "shelf_life_days_assumption",
    e."estimated_fifo_tranche_qty" AS "estimated_fifo_tranche_qty",
    e."daily_theoretical_demand" AS "daily_theoretical_demand",
    e."expected_consumption_before_expiry"
      AS "expected_consumption_before_expiry",
    e."estimated_expiry_date" AS "estimated_expiry_date",
    e."days_to_expiry" AS "days_to_expiry",
    e."expiry_risk_value" AS "expiry_risk_value",
    e."risk_status" AS "expiry_batch_risk_status",
    'EXPIRY' AS "risk_type",
    CASE
        WHEN e."risk_status" IN ('EXPIRED', 'EXPIRES_TODAY')
        THEN 'PURPLE'
        WHEN e."risk_status" = 'CRITICAL' THEN 'RED'
        ELSE 'AMBER'
    END AS "risk_severity",
    CASE
        WHEN e."risk_status" IN ('EXPIRED', 'EXPIRES_TODAY') THEN 4
        WHEN e."risk_status" = 'CRITICAL' THEN 3
        ELSE 2
    END AS "risk_severity_rank",
    e."batch_allocation_id" AS "action_id",
    CASE
        WHEN e."risk_status" = 'EXPIRED'
        THEN 'Quarantine expired batch and investigate'
        WHEN e."risk_status" IN ('EXPIRES_TODAY', 'CRITICAL')
        THEN 'Transfer, promote, or consume near-expiry stock'
        ELSE 'Review FIFO rotation and demand plan'
    END AS "recommended_action",
    'Operations' AS "action_owner",
    CASE
        WHEN e."risk_status" IN (
            'EXPIRED', 'EXPIRES_TODAY', 'CRITICAL'
        )
        THEN 'Due today'
        ELSE 'Due in 3 days'
    END AS "due_band",
    e."is_estimated" AS "is_estimated",
    e."estimation_method" AS "estimation_method",
    e."source_evidence" AS "source_evidence",
    e."production_use_status" AS "production_use_status"
FROM "AUX_Expiry_Estimate-Copy" e;
