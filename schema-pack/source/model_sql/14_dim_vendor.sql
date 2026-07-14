-- Query Table: DIM_Vendor
-- Purpose: Reusable vendor dimension from vendor master plus purchase/entry vendor names.
-- Sources: STD_Vendor_Report, STD_Purchase_Report, STD_Entry_Report
-- Join key: vendor_name; vendor_code is available only from the vendor master.

SELECT
    v."vendor_name" AS "vendor_key",
    v."vendor_name" AS "vendor_name",
    v."vendor_code" AS "vendor_code",
    v."description" AS "description",
    v."contact_person" AS "contact_person",
    v."contact_number" AS "contact_number",
    v."email" AS "email",
    v."gstin_number" AS "gstin_number",
    v."msme" AS "msme",
    v."fssai_number" AS "fssai_number",
    v."pan_number" AS "pan_number",
    v."state" AS "state",
    'Vendor Master' AS "source_type"
FROM "STD_Vendor_Report" v

UNION

SELECT
    p."vendor_name" AS "vendor_key",
    p."vendor_name" AS "vendor_name",
    NULL AS "vendor_code",
    NULL AS "description",
    NULL AS "contact_person",
    NULL AS "contact_number",
    NULL AS "email",
    NULL AS "gstin_number",
    NULL AS "msme",
    NULL AS "fssai_number",
    NULL AS "pan_number",
    NULL AS "state",
    'Purchase Only' AS "source_type"
FROM "STD_Purchase_Report" p
LEFT JOIN "STD_Vendor_Report" vm
    ON vm."vendor_name" = p."vendor_name"
WHERE p."vendor_name" IS NOT NULL
  AND vm."vendor_name" IS NULL

UNION

SELECT
    e."vendor_name" AS "vendor_key",
    e."vendor_name" AS "vendor_name",
    NULL AS "vendor_code",
    NULL AS "description",
    NULL AS "contact_person",
    NULL AS "contact_number",
    NULL AS "email",
    NULL AS "gstin_number",
    NULL AS "msme",
    NULL AS "fssai_number",
    NULL AS "pan_number",
    NULL AS "state",
    'Entry Only' AS "source_type"
FROM "STD_Entry_Report" e
LEFT JOIN "STD_Vendor_Report" vm
    ON vm."vendor_name" = e."vendor_name"
WHERE e."vendor_name" IS NOT NULL
  AND vm."vendor_name" IS NULL;
