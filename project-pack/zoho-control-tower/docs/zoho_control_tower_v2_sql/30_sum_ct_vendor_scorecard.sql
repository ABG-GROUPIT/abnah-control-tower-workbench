-- Query Table: 30_sum_ct_vendor_scorecard.sql
-- Logical model name: SUM_CT_Vendor_Scorecard
-- Layer: summary
-- Purpose: Summarize fill rate, OTIF and open PO exposure by vendor.
-- Sources: 24_fact_ct_po_receipt_line.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    v."source_period_code" AS "source_period_code",
    v."as_of_date" AS "as_of_date",
    v."po_date" AS "po_date",
    v."outlet_code" AS "outlet_code",
    v."outlet_name" AS "outlet_name",
    v."vendor_name" AS "vendor_name",
    v."po_status" AS "po_status",
    v."item_code" AS "item_code",
    v."item_name" AS "item_name",
    v."category_name" AS "category_name",
    v."canonical_uom" AS "canonical_uom",
    SUM(v."gross_order_value") AS "monthly_purchase_value",
    SUM(v."open_po_value") AS "open_po_value",
    SUM(v."otif_success_flag") AS "otif_success_line_count",
    SUM(v."eligible_closed_line_flag") AS "eligible_closed_line_count",
    SUM(v."received_qty") AS "received_qty",
    SUM(v."ordered_qty") AS "ordered_qty",
    SUM(
        CASE
            WHEN v."eligible_closed_line_flag" = 1
             AND v."lead_time_deviation_days" IS NOT NULL
            THEN v."lead_time_deviation_days"
            ELSE 0
        END
    ) AS "eligible_lead_time_deviation_days_total",
    SUM(
        CASE
            WHEN v."eligible_closed_line_flag" = 1
             AND v."lead_time_deviation_days" IS NOT NULL
            THEN 1
            ELSE 0
        END
    ) AS "eligible_lead_time_line_count",
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
    SUM(v."delayed_po_flag") AS "delayed_po_line_count"
FROM "24_fact_ct_po_receipt_line.sql" v
GROUP BY
    v."source_period_code",
    v."as_of_date",
    v."po_date",
    v."outlet_code",
    v."outlet_name",
    v."vendor_name",
    v."po_status",
    v."item_code",
    v."item_name",
    v."category_name",
    v."canonical_uom";
