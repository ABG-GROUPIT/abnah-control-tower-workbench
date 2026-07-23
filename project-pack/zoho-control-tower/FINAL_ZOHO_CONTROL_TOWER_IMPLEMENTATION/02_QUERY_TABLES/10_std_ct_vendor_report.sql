-- Query Table: 10_std_ct_vendor_report.sql
-- Logical model name: STD_CT_Vendor_Report
-- Layer: standardized
-- Purpose: Standardize the exact historical Vendor Report after local structural cleaning.
-- Sources: RAWN_CT_vendor_report-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    v."vendor_name" AS "vendor_name",
    v."vendor_code" AS "vendor_code",
    v."description" AS "description",
    v."contact_person" AS "contact_person",
    v."contact_number" AS "contact_number",
    v."email" AS "email",
    v."tin_number" AS "tin_number",
    v."service_tax_number" AS "service_tax_number",
    v."gstin_number" AS "gstin_number",
    v."msme" AS "msme",
    v."fssai_number" AS "fssai_number",
    v."pan_number" AS "pan_number",
    CAST(v."from_date" AS DATE) AS "valid_from_date",
    CAST(v."to_date" AS DATE) AS "valid_to_date",
    v."state" AS "state",
    v."address" AS "address"
FROM "RAWN_CT_vendor_report-Copy" v
WHERE v."vendor_name" IS NOT NULL;
