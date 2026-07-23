-- Query Table: 32_sum_ct_menu_profitability.sql
-- Logical model name: SUM_CT_Menu_Profitability
-- Layer: summary
-- Purpose: Expose menu profitability with BCG quadrant classification.
-- Sources: 25_fact_ct_menu_profitability.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    m.*,
    CASE
        WHEN m."sold_qty" >= 150 AND m."gross_margin_percent" >= 60 THEN 'Stars'
        WHEN m."sold_qty" < 150 AND m."gross_margin_percent" >= 60 THEN 'Niche gems'
        WHEN m."sold_qty" >= 150 AND m."gross_margin_percent" < 60 THEN 'Volume drags'
        ELSE 'Review / rationalize'
    END AS "bcg_quadrant"
FROM "25_fact_ct_menu_profitability.sql" m;
