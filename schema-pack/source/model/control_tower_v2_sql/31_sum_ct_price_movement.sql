-- Query Table: 31_sum_ct_price_movement.sql
-- Logical model name: SUM_CT_Price_Movement
-- Layer: summary
-- Purpose: Compare weighted receipt prices with the immediately prior synthetic month.
-- Sources: 23_fact_ct_purchase_receipt.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    c."source_period_code" AS "source_period_code",
    c."price_as_of_date" AS "price_as_of_date",
    c."outlet_code" AS "outlet_code",
    c."outlet_name" AS "outlet_name",
    c."vendor_name" AS "vendor_name",
    c."item_code" AS "item_code",
    c."item_name" AS "item_name",
    c."category_name" AS "category_name",
    c."canonical_uom" AS "canonical_uom",
    c."current_purchase_qty" AS "current_purchase_qty",
    c."current_purchase_value" AS "current_purchase_value",
    c."current_unit_price" AS "current_unit_price",
    p."current_unit_price" AS "previous_unit_price",
    c."current_unit_price" - p."current_unit_price" AS "price_change_amount",
    c."current_unit_price" - p."current_unit_price" AS "unit_price_change",
    CASE
        WHEN p."current_unit_price" IS NULL THEN 'NO_BASELINE'
        WHEN c."current_unit_price" > p."current_unit_price" THEN 'INCREASE'
        WHEN c."current_unit_price" < p."current_unit_price" THEN 'DECREASE'
        ELSE 'NO_CHANGE'
    END AS "price_movement_direction",
    CASE
        WHEN p."current_unit_price" <> 0
        THEN (c."current_unit_price" - p."current_unit_price") / p."current_unit_price" * 100
        ELSE NULL
    END AS "price_change_percent",
    CASE
        WHEN p."current_unit_price" <> 0
        THEN (c."current_unit_price" - p."current_unit_price") / p."current_unit_price" * 100
        ELSE NULL
    END AS "unit_price_change_percent",
    CASE
        WHEN p."current_unit_price" <> 0
        THEN ABS(
            (c."current_unit_price" - p."current_unit_price")
            / p."current_unit_price" * 100
        )
        ELSE NULL
    END AS "absolute_price_change_percent",
    CASE
        WHEN p."current_unit_price" <> 0
        THEN ABS(
            (c."current_unit_price" - p."current_unit_price")
            / p."current_unit_price" * 100
        )
        ELSE NULL
    END AS "absolute_unit_price_change_percent",
    CASE
        WHEN p."current_unit_price" IS NOT NULL
        THEN (c."current_unit_price" - p."current_unit_price")
           * c."current_purchase_qty"
        ELSE NULL
    END AS "price_change_value_impact"
FROM (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "vendor_name" AS "vendor_name",
        "item_code" AS "item_code",
        "item_name" AS "item_name",
        "category_name" AS "category_name",
        "canonical_uom" AS "canonical_uom",
        MAX("receipt_date") AS "price_as_of_date",
        SUM("received_qty") AS "current_purchase_qty",
        SUM("receipt_subtotal") AS "current_purchase_value",
        SUM("receipt_subtotal") / NULLIF(SUM("received_qty"), 0) AS "current_unit_price"
    FROM "23_fact_ct_purchase_receipt.sql"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "vendor_name",
        "item_code",
        "item_name",
        "category_name",
        "canonical_uom"
) c
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "vendor_name" AS "vendor_name",
        "item_code" AS "item_code",
        "canonical_uom" AS "canonical_uom",
        SUM("receipt_subtotal") / NULLIF(SUM("received_qty"), 0) AS "current_unit_price"
    FROM "23_fact_ct_purchase_receipt.sql"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "vendor_name",
        "item_code",
        "canonical_uom"
) p
  ON c."outlet_code" = p."outlet_code"
 AND c."vendor_name" = p."vendor_name"
 AND c."item_code" = p."item_code"
 AND c."canonical_uom" = p."canonical_uom"
 AND (
      (c."source_period_code" = 'month_02' AND p."source_period_code" = 'month_01')
   OR (c."source_period_code" = 'month_03' AND p."source_period_code" = 'month_02')
 );
