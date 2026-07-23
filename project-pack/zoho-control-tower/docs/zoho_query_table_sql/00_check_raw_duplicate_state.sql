-- Diagnostic Query Table: CHECK_Raw_Duplicate_State
-- Purpose: Prove whether Zoho RAW receiving tables were appended/refetched twice.
-- If "zoho_row_count" is greater than "distinct_row_id_count", the RAW table has duplicate imported rows.
-- Expected values below are for the clean Month 1 demo state plus static master files.

SELECT
    'RAW_Sales_Report_OUT001' AS "table_name",
    1529 AS "expected_clean_rows",
    COUNT(r1."row_id") AS "zoho_row_count",
    COUNT(DISTINCT r1."row_id") AS "distinct_row_id_count",
    COUNT(r1."row_id") - COUNT(DISTINCT r1."row_id") AS "duplicate_row_count"
FROM "RAW_Sales_Report_OUT001" r1

UNION ALL

SELECT
    'RAW_Sales_Report_OUT002' AS "table_name",
    1595 AS "expected_clean_rows",
    COUNT(r2."row_id") AS "zoho_row_count",
    COUNT(DISTINCT r2."row_id") AS "distinct_row_id_count",
    COUNT(r2."row_id") - COUNT(DISTINCT r2."row_id") AS "duplicate_row_count"
FROM "RAW_Sales_Report_OUT002" r2

UNION ALL

SELECT
    'RAW_Sales_Report_OUT003' AS "table_name",
    1731 AS "expected_clean_rows",
    COUNT(r3."row_id") AS "zoho_row_count",
    COUNT(DISTINCT r3."row_id") AS "distinct_row_id_count",
    COUNT(r3."row_id") - COUNT(DISTINCT r3."row_id") AS "duplicate_row_count"
FROM "RAW_Sales_Report_OUT003" r3

UNION ALL

SELECT
    'RAW_Purchase_Report_OUT001' AS "table_name",
    78 AS "expected_clean_rows",
    COUNT(p1."row_id") AS "zoho_row_count",
    COUNT(DISTINCT p1."row_id") AS "distinct_row_id_count",
    COUNT(p1."row_id") - COUNT(DISTINCT p1."row_id") AS "duplicate_row_count"
FROM "RAW_Purchase_Report_OUT001" p1

UNION ALL

SELECT
    'RAW_Purchase_Report_OUT002' AS "table_name",
    72 AS "expected_clean_rows",
    COUNT(p2."row_id") AS "zoho_row_count",
    COUNT(DISTINCT p2."row_id") AS "distinct_row_id_count",
    COUNT(p2."row_id") - COUNT(DISTINCT p2."row_id") AS "duplicate_row_count"
FROM "RAW_Purchase_Report_OUT002" p2

UNION ALL

SELECT
    'RAW_Purchase_Report_OUT003' AS "table_name",
    74 AS "expected_clean_rows",
    COUNT(p3."row_id") AS "zoho_row_count",
    COUNT(DISTINCT p3."row_id") AS "distinct_row_id_count",
    COUNT(p3."row_id") - COUNT(DISTINCT p3."row_id") AS "duplicate_row_count"
FROM "RAW_Purchase_Report_OUT003" p3

UNION ALL

SELECT
    'RAW_Entry_Report_OUT001' AS "table_name",
    62 AS "expected_clean_rows",
    COUNT(e1."row_id") AS "zoho_row_count",
    COUNT(DISTINCT e1."row_id") AS "distinct_row_id_count",
    COUNT(e1."row_id") - COUNT(DISTINCT e1."row_id") AS "duplicate_row_count"
FROM "RAW_Entry_Report_OUT001" e1

UNION ALL

SELECT
    'RAW_Entry_Report_OUT002' AS "table_name",
    57 AS "expected_clean_rows",
    COUNT(e2."row_id") AS "zoho_row_count",
    COUNT(DISTINCT e2."row_id") AS "distinct_row_id_count",
    COUNT(e2."row_id") - COUNT(DISTINCT e2."row_id") AS "duplicate_row_count"
FROM "RAW_Entry_Report_OUT002" e2

UNION ALL

SELECT
    'RAW_Entry_Report_OUT003' AS "table_name",
    61 AS "expected_clean_rows",
    COUNT(e3."row_id") AS "zoho_row_count",
    COUNT(DISTINCT e3."row_id") AS "distinct_row_id_count",
    COUNT(e3."row_id") - COUNT(DISTINCT e3."row_id") AS "duplicate_row_count"
FROM "RAW_Entry_Report_OUT003" e3

UNION ALL

SELECT
    'RAW_Inventory_Closing_Report_OUT001' AS "table_name",
    1116 AS "expected_clean_rows",
    COUNT(i1."row_id") AS "zoho_row_count",
    COUNT(DISTINCT i1."row_id") AS "distinct_row_id_count",
    COUNT(i1."row_id") - COUNT(DISTINCT i1."row_id") AS "duplicate_row_count"
FROM "RAW_Inventory_Closing_Report_OUT001" i1

UNION ALL

SELECT
    'RAW_Inventory_Closing_Report_OUT002' AS "table_name",
    1116 AS "expected_clean_rows",
    COUNT(i2."row_id") AS "zoho_row_count",
    COUNT(DISTINCT i2."row_id") AS "distinct_row_id_count",
    COUNT(i2."row_id") - COUNT(DISTINCT i2."row_id") AS "duplicate_row_count"
FROM "RAW_Inventory_Closing_Report_OUT002" i2

UNION ALL

SELECT
    'RAW_Inventory_Closing_Report_OUT003' AS "table_name",
    1116 AS "expected_clean_rows",
    COUNT(i3."row_id") AS "zoho_row_count",
    COUNT(DISTINCT i3."row_id") AS "distinct_row_id_count",
    COUNT(i3."row_id") - COUNT(DISTINCT i3."row_id") AS "duplicate_row_count"
FROM "RAW_Inventory_Closing_Report_OUT003" i3

UNION ALL

SELECT
    'RAW_Menu_Master' AS "table_name",
    110 AS "expected_clean_rows",
    COUNT(m."row_id") AS "zoho_row_count",
    COUNT(DISTINCT m."row_id") AS "distinct_row_id_count",
    COUNT(m."row_id") - COUNT(DISTINCT m."row_id") AS "duplicate_row_count"
FROM "RAW_Menu_Master" m

UNION ALL

SELECT
    'RAW_Vendor_Report' AS "table_name",
    70 AS "expected_clean_rows",
    COUNT(v."row_id") AS "zoho_row_count",
    COUNT(DISTINCT v."row_id") AS "distinct_row_id_count",
    COUNT(v."row_id") - COUNT(DISTINCT v."row_id") AS "duplicate_row_count"
FROM "RAW_Vendor_Report" v

UNION ALL

SELECT
    'RAW_Brand_Recipe_Consumption' AS "table_name",
    723 AS "expected_clean_rows",
    COUNT(b."row_id") AS "zoho_row_count",
    COUNT(DISTINCT b."row_id") AS "distinct_row_id_count",
    COUNT(b."row_id") - COUNT(DISTINCT b."row_id") AS "duplicate_row_count"
FROM "RAW_Brand_Recipe_Consumption" b

UNION ALL

SELECT
    'RAW_Indian_Calendar_Holidays' AS "table_name",
    9 AS "expected_clean_rows",
    COUNT(h."row_id") AS "zoho_row_count",
    COUNT(DISTINCT h."row_id") AS "distinct_row_id_count",
    COUNT(h."row_id") - COUNT(DISTINCT h."row_id") AS "duplicate_row_count"
FROM "RAW_Indian_Calendar_Holidays" h

UNION ALL

SELECT
    'RAW_Manual_Calendar_Events' AS "table_name",
    11 AS "expected_clean_rows",
    COUNT(ev."row_id") AS "zoho_row_count",
    COUNT(DISTINCT ev."row_id") AS "distinct_row_id_count",
    COUNT(ev."row_id") - COUNT(DISTINCT ev."row_id") AS "duplicate_row_count"
FROM "RAW_Manual_Calendar_Events" ev

UNION ALL

SELECT
    'RAW_Competitor_Pricing' AS "table_name",
    126 AS "expected_clean_rows",
    COUNT(c."row_id") AS "zoho_row_count",
    COUNT(DISTINCT c."row_id") AS "distinct_row_id_count",
    COUNT(c."row_id") - COUNT(DISTINCT c."row_id") AS "duplicate_row_count"
FROM "RAW_Competitor_Pricing" c;
