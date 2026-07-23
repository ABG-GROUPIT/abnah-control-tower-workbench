-- Query Table: 37_dim_ct_outlet_enriched.sql
-- Logical model name: DIM_CT_Outlet_Enriched
-- Layer: dimension
-- Purpose: Enrich source-derived outlet identity with synthetic demonstrator geography.
-- Sources: 13_dim_ct_outlet.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    d."outlet_code" AS "outlet_code",
    d."outlet_name" AS "outlet_name",
    'North' AS "region",
    'Delhi' AS "city",
    CASE
        WHEN d."outlet_code" = 'OUT001' THEN 'Connaught Place'
        WHEN d."outlet_code" = 'OUT002' THEN 'Hauz Khas'
        WHEN d."outlet_code" = 'OUT003' THEN 'Saket'
        ELSE 'Unmapped'
    END AS "market_area",
    CASE
        WHEN d."outlet_code" = 'OUT001' THEN 28.6315
        WHEN d."outlet_code" = 'OUT002' THEN 28.5494
        WHEN d."outlet_code" = 'OUT003' THEN 28.5245
        ELSE 0
    END AS "latitude",
    CASE
        WHEN d."outlet_code" = 'OUT001' THEN 77.2167
        WHEN d."outlet_code" = 'OUT002' THEN 77.2001
        WHEN d."outlet_code" = 'OUT003' THEN 77.2066
        ELSE 0
    END AS "longitude",
    CASE
        WHEN d."outlet_code" = 'OUT003' THEN 'New'
        ELSE 'Matured'
    END AS "new_matured_flag",
    'Active' AS "active_status",
    'synthetic_demo_geography_on_source_derived_outlet'
      AS "source_evidence",
    1 AS "is_synthetic",
    'replace_with_approved_abnah_outlet_reference'
      AS "production_use_status"
FROM "13_dim_ct_outlet.sql" d
WHERE d."outlet_code" IN ('OUT001', 'OUT002', 'OUT003');
