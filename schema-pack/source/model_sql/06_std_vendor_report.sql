-- Query Table: STD_Vendor_Report
-- Purpose: Standardize vendor master data.
-- Source: RAW_Vendor_Report
-- Join keys downstream: vendor_name, vendor_code.

SELECT DISTINCT
    v."row_id" AS "vendor_row_id",
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
    CAST(v."from_date" AS DATE) AS "from_date",
    CAST(v."to_date" AS DATE) AS "to_date",
    v."state" AS "state",
    v."address" AS "address"
FROM "RAW_Vendor_Report" v;
