-- Query Table: SUM_Menu_Item_Performance
-- Purpose: Menu item performance and competitor-context summary.
-- Sources: FACT_Sales, STD_Competitor_Pricing
-- Supplemental file: requested dashboard layer includes SUM_Menu_Item_Performance, but the requested numbered file list omitted it.

SELECT
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    s."market_area" AS "market_area",
    s."item_number" AS "item_number",
    s."item_name" AS "item_name",
    s."super_category" AS "super_category",
    s."category" AS "category",
    SUM(s."qty") AS "total_qty",
    SUM(s."net_sale") AS "total_net_sale",
    AVG(s."net_sale_per_qty") AS "avg_realized_unit_price",
    c."avg_price_index" AS "avg_price_index",
    c."price_position" AS "price_position",
    CASE
        WHEN c."avg_price_index" > 1.05 AND SUM(s."net_sale") > 0 THEN 'Premium item with sales'
        WHEN c."avg_price_index" > 1.05 THEN 'Premium item to review'
        WHEN c."avg_price_index" < 0.95 THEN 'Lower than mapped competitor'
        ELSE 'No issue flagged'
    END AS "performance_note"
FROM "FACT_Sales" s
LEFT JOIN (
    SELECT
        cp."abnah_item_number" AS "abnah_item_number",
        AVG(cp."price_index") AS "avg_price_index",
        MAX(cp."price_position") AS "price_position"
    FROM "STD_Competitor_Pricing" cp
    GROUP BY cp."abnah_item_number"
) c
    ON c."abnah_item_number" = s."item_number"
GROUP BY
    s."outlet_code",
    s."outlet_name",
    s."market_area",
    s."item_number",
    s."item_name",
    s."super_category",
    s."category",
    c."avg_price_index",
    c."price_position";
