-- Query Table: D05_demo_p2_vendor_control.sql
-- Purpose: Concise Page 2 vendor performance table for the visual demo.
-- Source: 24_fact_ct_po_receipt_line.sql
-- Dependency level: 3
-- Isolation rule: Do not replace or edit Query 30.
SELECT
    v."source_period_code" AS "source_period_code",
    v."po_date" AS "filter_date",
    v."outlet_name" AS "filter_outlet",
    v."vendor_name" AS "filter_vendor",
    v."category_name" AS "filter_category",
    v."outlet_code" AS "outlet_code",
    v."vendor_name" AS "vendor_name",
    v."category_name" AS "category_name",
    COUNT(DISTINCT v."po_number") AS "po_count",
    SUM(v."gross_order_value") AS "purchase_value",
    SUM(v."open_po_value") AS "open_po_value",
    CASE
        WHEN SUM(v."eligible_closed_line_flag") <> 0
        THEN SUM(v."otif_success_flag")
          / SUM(v."eligible_closed_line_flag") * 100
        ELSE NULL
    END AS "otif_percent",
    CASE
        WHEN SUM(v."ordered_qty") <> 0
        THEN SUM(v."received_qty") / SUM(v."ordered_qty") * 100
        ELSE NULL
    END AS "fill_rate_percent",
    AVG(
        CASE
            WHEN v."eligible_closed_line_flag" = 1
            THEN v."lead_time_deviation_days"
            ELSE NULL
        END
    ) AS "average_lead_time_deviation_days",
    SUM(v."delayed_po_flag") AS "delayed_po_line_count",
    CASE
        WHEN SUM(v."delayed_po_flag") > 0 THEN 'RED'
        WHEN SUM(v."eligible_closed_line_flag") > 0
         AND (
            SUM(v."otif_success_flag")
              / SUM(v."eligible_closed_line_flag") * 100 < 80
            OR (
                SUM(v."ordered_qty") <> 0
                AND SUM(v."received_qty")
                  / SUM(v."ordered_qty") * 100 < 80
            )
         )
        THEN 'AMBER'
        ELSE 'GREEN'
    END AS "vendor_control_status"
FROM "24_fact_ct_po_receipt_line.sql" v
GROUP BY
    v."source_period_code",
    v."po_date",
    v."outlet_code",
    v."outlet_name",
    v."vendor_name",
    v."category_name";
