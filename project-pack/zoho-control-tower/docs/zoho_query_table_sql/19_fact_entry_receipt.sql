-- Query Table: FACT_Entry_Receipt
-- Purpose: Receipt/GRN line fact with vendor and ingredient context.
-- Sources: STD_Entry_Report, DIM_Vendor, DIM_Ingredient
-- Join keys: vendor_name, item_code/item_name.

SELECT
    e."entry_row_id" AS "entry_row_id",
    e."receipt_date" AS "receipt_date",
    e."invoice_date" AS "invoice_date",
    e."transaction_number" AS "transaction_number",
    e."invoice_number" AS "invoice_number",
    e."outlet_code" AS "outlet_code",
    e."outlet_name" AS "outlet_name",
    e."market_area" AS "market_area",
    e."store_kitchen_name" AS "store_kitchen_name",
    e."user_name" AS "user_name",
    e."vendor_name" AS "vendor_name",
    v."vendor_code" AS "vendor_code",
    e."item_code" AS "item_code",
    e."item_name" AS "item_name",
    e."category_name" AS "category_name",
    e."super_category_name" AS "super_category_name",
    e."received_qty" AS "received_qty",
    e."unit" AS "unit",
    e."unit_price" AS "unit_price",
    e."amount" AS "amount",
    e."discount" AS "discount",
    e."gst_igst_rate" AS "gst_igst_rate",
    e."gst_igst_value" AS "gst_igst_value",
    e."total_tax" AS "total_tax",
    e."item_charges_amount" AS "item_charges_amount",
    e."entry_total" AS "entry_total",
    e."return_qty" AS "return_qty",
    e."return_amount" AS "return_amount",
    e."grand_total" AS "grand_total",
    CASE
        WHEN e."received_qty" <> 0 THEN e."grand_total" / e."received_qty"
        ELSE NULL
    END AS "realized_receipt_unit_cost"
FROM "STD_Entry_Report" e
LEFT JOIN "DIM_Vendor" v
    ON v."vendor_name" = e."vendor_name"
LEFT JOIN "DIM_Ingredient" i
    ON i."ingredient_code" = e."item_code";
