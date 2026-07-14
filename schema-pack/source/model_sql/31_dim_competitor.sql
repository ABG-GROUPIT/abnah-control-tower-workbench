-- Query Table: DIM_Competitor
-- Purpose: Reusable competitor dimension from competitor pricing rows.
-- Source: STD_Competitor_Pricing
-- Supplemental file: requested layer list includes DIM_Competitor, but the requested numbered file list omitted it.

SELECT DISTINCT
    c."competitor_id" AS "competitor_key",
    c."competitor_id" AS "competitor_id",
    c."competitor_name" AS "competitor_name",
    c."market_area" AS "market_area",
    c."outlet_code" AS "outlet_code",
    c."outlet_name" AS "outlet_name",
    c."competitor_category" AS "competitor_category"
FROM "STD_Competitor_Pricing" c;
