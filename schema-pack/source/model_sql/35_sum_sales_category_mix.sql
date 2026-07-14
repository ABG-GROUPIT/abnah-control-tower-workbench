-- Query Table: SUM_Sales_Category_Mix
-- Purpose: Sales contribution by super-category and category.
-- Source: FACT_Sales
-- Supplemental file: requested dashboard layer includes SUM_Sales_Category_Mix, but the requested numbered file list omitted it.

SELECT
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    s."market_area" AS "market_area",
    s."super_category" AS "super_category",
    s."category" AS "category",
    SUM(s."qty") AS "total_qty",
    SUM(s."net_sale") AS "total_net_sale",
    CASE
        WHEN t."outlet_net_sale" <> 0 THEN SUM(s."net_sale") / t."outlet_net_sale" * 100
        ELSE NULL
    END AS "net_sale_share_pct"
FROM "FACT_Sales" s
LEFT JOIN
     (
        SELECT
            fs."outlet_code" AS "outlet_code",
            SUM(fs."net_sale") AS "outlet_net_sale"
        FROM "FACT_Sales" fs
        GROUP BY fs."outlet_code"
     ) t
    ON t."outlet_code" = s."outlet_code"
GROUP BY
    s."outlet_code",
    s."outlet_name",
    s."market_area",
    s."super_category",
    s."category",
    t."outlet_net_sale";
