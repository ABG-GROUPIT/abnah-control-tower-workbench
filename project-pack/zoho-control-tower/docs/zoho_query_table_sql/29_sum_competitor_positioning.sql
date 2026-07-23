-- Query Table: SUM_Competitor_Positioning
-- Purpose: Competitor price context summary with mapped ABNAH sales.
-- Source: FACT_Competitor_Price_Position
-- Caveat: Context only; do not claim causation.

SELECT
    cp."outlet_code" AS "outlet_code",
    cp."outlet_name" AS "outlet_name",
    cp."outlet_market_area" AS "outlet_market_area",
    cp."market_area" AS "market_area",
    cp."competitor_name" AS "competitor_name",
    cp."competitor_category" AS "competitor_category",
    cp."price_position" AS "price_position",
    cp."price_position_band" AS "price_position_band",
    COUNT(DISTINCT cp."abnah_item_number") AS "mapped_abnah_item_count",
    AVG(cp."price_index") AS "avg_price_index",
    AVG(cp."price_difference") AS "avg_price_difference",
    SUM(cp."qty") AS "mapped_sales_qty",
    SUM(cp."net_sale") AS "mapped_net_sale",
    SUM(cp."premium_context_sale_flag") AS "premium_context_sales_lines",
    CASE
        WHEN AVG(cp."price_index") > 1.05 AND SUM(cp."net_sale") > 0 THEN 'Premium area with sales'
        WHEN AVG(cp."price_index") > 1.05 THEN 'Premium area to review'
        WHEN AVG(cp."price_index") < 0.95 THEN 'Lower price than competitor'
        ELSE 'Near parity'
    END AS "positioning_note"
FROM "FACT_Competitor_Price_Position" cp
GROUP BY
    cp."outlet_code",
    cp."outlet_name",
    cp."outlet_market_area",
    cp."market_area",
    cp."competitor_name",
    cp."competitor_category",
    cp."price_position",
    cp."price_position_band";
