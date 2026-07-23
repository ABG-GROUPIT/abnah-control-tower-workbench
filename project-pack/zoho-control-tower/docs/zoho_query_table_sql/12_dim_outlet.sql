-- Query Table: DIM_Outlet
-- Purpose: Reusable outlet dimension for dashboard filters and fact joins.
-- Source: Fixed ABNAH outlet mapping used by all synthetic operational feeds.
-- Grain: one row per outlet.

SELECT
    'OUT001' AS "outlet_key",
    'OUT001' AS "outlet_code",
    'ABNAH Cafe Connaught Place' AS "outlet_name",
    'Connaught Place' AS "market_area"
UNION ALL
SELECT
    'OUT002' AS "outlet_key",
    'OUT002' AS "outlet_code",
    'ABNAH Cafe Hauz Khas' AS "outlet_name",
    'Hauz Khas' AS "market_area"
UNION ALL
SELECT
    'OUT003' AS "outlet_key",
    'OUT003' AS "outlet_code",
    'ABNAH Cafe Saket Premium' AS "outlet_name",
    'Saket' AS "market_area";
