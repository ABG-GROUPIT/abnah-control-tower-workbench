-- Query Table: FACT_Competitor_Price_Position
-- Purpose: Map competitor price context to ABNAH item sales.
-- Sources: STD_Competitor_Pricing, FACT_Sales
-- Join key: abnah_item_number = item_number.
-- Caveat: This table supports price context and review signals, not causation.

SELECT
    c."competitor_id" AS "competitor_id",
    c."competitor_name" AS "competitor_name",
    c."market_area" AS "market_area",
    c."competitor_category" AS "competitor_category",
    c."competitor_item_name" AS "competitor_item_name",
    c."competitor_price" AS "competitor_price",
    c."abnah_item_number" AS "abnah_item_number",
    c."abnah_item_name" AS "abnah_item_name",
    c."abnah_price" AS "abnah_price",
    c."price_difference" AS "price_difference",
    c."price_index" AS "price_index",
    c."price_position" AS "price_position",
    c."price_position_band" AS "price_position_band",
    c."expected_sales_impact" AS "expected_sales_impact",
    s."sales_date" AS "sales_date",
    COALESCE(s."outlet_code", c."outlet_code") AS "outlet_code",
    COALESCE(s."outlet_name", c."outlet_name") AS "outlet_name",
    COALESCE(s."market_area", c."market_area") AS "outlet_market_area",
    s."item_number" AS "item_number",
    s."item_name" AS "item_name",
    s."category" AS "category",
    s."super_category" AS "super_category",
    s."qty" AS "qty",
    s."net_sale" AS "net_sale",
    s."net_sale_per_qty" AS "net_sale_per_qty",
    CASE
        WHEN c."price_index" > 1.05 AND s."net_sale" > 0 THEN 1
        ELSE 0
    END AS "premium_context_sale_flag"
FROM "STD_Competitor_Pricing" c
LEFT JOIN "FACT_Sales" s
    ON s."item_number" = c."abnah_item_number"
   AND s."market_area" = c."market_area";
