-- Query Table: 16_dim_ct_vendor.sql
-- Logical model name: DIM_CT_Vendor
-- Layer: dimension
-- Purpose: Create the vendor identity dimension from Vendor Report with transaction-only fallbacks.
-- Sources: 10_std_ct_vendor_report.sql, RAWN_CT_enterprise_purchase_order-Copy, RAWN_CT_enterprise_entry-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    MAX(v."vendor_code") AS "vendor_code",
    v."vendor_name" AS "vendor_name",
    MAX(v."description") AS "description",
    MAX(v."state") AS "state",
    MIN(v."valid_from_date") AS "valid_from_date",
    MAX(v."valid_to_date") AS "valid_to_date",
    MAX(v."msme") AS "msme",
    MAX(v."gstin_number") AS "gstin_number",
    MAX(v."fssai_number") AS "fssai_number",
    MAX(v."pan_number") AS "pan_number",
    NULL AS "active_status",
    NULL AS "default_lead_time_days",
    NULL AS "approved_category_mapping",
    'vendor_report' AS "source_evidence"
FROM "10_std_ct_vendor_report.sql" v
GROUP BY v."vendor_name"
UNION ALL
SELECT
    NULL AS "vendor_code",
    t."vendor_name" AS "vendor_name",
    NULL AS "description",
    NULL AS "state",
    NULL AS "valid_from_date",
    NULL AS "valid_to_date",
    NULL AS "msme",
    NULL AS "gstin_number",
    NULL AS "fssai_number",
    NULL AS "pan_number",
    NULL AS "active_status",
    NULL AS "default_lead_time_days",
    NULL AS "approved_category_mapping",
    'observed_in_po_or_entry_only' AS "source_evidence"
FROM (
    SELECT "vendor_name" AS "vendor_name"
    FROM "RAWN_CT_enterprise_purchase_order-Copy"
    WHERE "vendor_name" IS NOT NULL
    UNION
    SELECT "vendor_name" AS "vendor_name"
    FROM "RAWN_CT_enterprise_entry-Copy"
    WHERE "vendor_name" IS NOT NULL
) t
LEFT JOIN (
    SELECT DISTINCT "vendor_name" AS "vendor_name"
    FROM "10_std_ct_vendor_report.sql"
) v
  ON t."vendor_name" = v."vendor_name"
WHERE v."vendor_name" IS NULL;
