-- Query Table: FACT_Purchase_Order
-- Purpose: Purchase order line fact with vendor and ingredient context.
-- Sources: STD_Purchase_Report, DIM_Vendor, DIM_Ingredient
-- Join keys: vendor_name, item_code/item_name.

SELECT
    p."purchase_row_id" AS "purchase_row_id",
    p."po_number" AS "po_number",
    p."po_date" AS "po_date",
    p."expected_delivery_date" AS "expected_delivery_date",
    p."outlet_code" AS "outlet_code",
    p."outlet_name" AS "outlet_name",
    p."market_area" AS "market_area",
    p."store_name" AS "store_name",
    p."vendor_name" AS "vendor_name",
    v."vendor_code" AS "vendor_code",
    p."po_status" AS "po_status",
    p."item_code" AS "item_code",
    p."item_name" AS "item_name",
    p."category_name" AS "category_name",
    p."super_category_name" AS "super_category_name",
    p."ordered_qty" AS "ordered_qty",
    p."processed_qty" AS "processed_qty",
    p."remaining_qty" AS "remaining_qty",
    p."unit" AS "unit",
    p."unit_price" AS "unit_price",
    p."subtotal" AS "subtotal",
    p."tax" AS "tax",
    p."total_item_cost" AS "total_item_cost",
    CASE
        WHEN p."ordered_qty" <> 0 THEN p."total_item_cost" * p."processed_qty" / p."ordered_qty"
        ELSE NULL
    END AS "processed_value_est",
    CASE
        WHEN p."ordered_qty" <> 0 THEN p."total_item_cost" * p."remaining_qty" / p."ordered_qty"
        ELSE NULL
    END AS "remaining_value_est",
    p."is_open_or_partial" AS "is_open_or_partial"
FROM "STD_Purchase_Report" p
LEFT JOIN "DIM_Vendor" v
    ON v."vendor_name" = p."vendor_name"
LEFT JOIN "DIM_Ingredient" i
    ON i."ingredient_code" = p."item_code";
