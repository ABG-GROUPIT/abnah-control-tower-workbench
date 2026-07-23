-- Query Table: STD_Competitor_Pricing
-- Purpose: Standardize competitor price context mapped to ABNAH menu items.
-- Source: RAW_Competitor_Pricing
-- Caveat: Competitor pricing is context, not proof of causation.

SELECT DISTINCT
    c."row_id" AS "competitor_row_id",
    c."competitor_id" AS "competitor_id",
    c."competitor_name" AS "competitor_name",
    c."market_area" AS "market_area",
    CASE
        WHEN c."market_area" = 'Connaught Place' THEN 'OUT001'
        WHEN c."market_area" = 'Hauz Khas' THEN 'OUT002'
        WHEN c."market_area" = 'Saket' THEN 'OUT003'
        ELSE NULL
    END AS "outlet_code",
    CASE
        WHEN c."market_area" = 'Connaught Place' THEN 'ABNAH Cafe Connaught Place'
        WHEN c."market_area" = 'Hauz Khas' THEN 'ABNAH Cafe Hauz Khas'
        WHEN c."market_area" = 'Saket' THEN 'ABNAH Cafe Saket Premium'
        ELSE NULL
    END AS "outlet_name",
    c."competitor_category" AS "competitor_category",
    c."competitor_item_name" AS "competitor_item_name",
    CAST(c."competitor_price" AS DECIMAL(14,2)) AS "competitor_price",
    c."abnah_item_number" AS "abnah_item_number",
    c."abnah_item_name" AS "abnah_item_name",
    CAST(c."abnah_price" AS DECIMAL(14,2)) AS "abnah_price",
    CAST(c."price_difference" AS DECIMAL(14,2)) AS "price_difference",
    CAST(c."price_index" AS DECIMAL(10,3)) AS "price_index",
    c."price_position" AS "price_position",
    c."expected_sales_impact" AS "expected_sales_impact",
    c."notes" AS "notes",
    CASE
        WHEN CAST(c."price_index" AS DECIMAL(10,3)) > 1.05 THEN 'Meaningfully Higher'
        WHEN CAST(c."price_index" AS DECIMAL(10,3)) < 0.95 THEN 'Meaningfully Lower'
        ELSE 'Near Parity'
    END AS "price_position_band"
FROM "RAW_Competitor_Pricing" c;
