-- Query Table: 01_std_ct_sales_item.sql
-- Logical model name: STD_CT_Sales_Item
-- Layer: standardized
-- Purpose: Standardize bill-item sales, realized revenue and source-reported margin fields.
-- Sources: RAWN_CT_gross_net_margin-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    s."source_period_code" AS "source_period_code",
    s."source_outlet_code" AS "outlet_code",
    s."source_outlet_name" AS "outlet_name",
    CAST(s."sale_date" AS DATE) AS "sales_date",
    s."bill_number" AS "bill_number",
    s."tab_type" AS "tab_type",
    s."source" AS "order_source",
    s."super_category_name" AS "super_category_name",
    s."category_name" AS "category_name",
    s."item_code" AS "item_code",
    s."item_name" AS "item_name",
    CAST(s."item_rate" AS DECIMAL(18,2)) AS "item_rate",
    CAST(s."item_qty" AS DECIMAL(18,4)) AS "sold_qty",
    CAST(s."item_subtotal" AS DECIMAL(18,2)) AS "item_subtotal",
    CAST(s."total_discount_amt" AS DECIMAL(18,2)) AS "discount_amount",
    CAST(s."net_sale_value" AS DECIMAL(18,2)) AS "net_sales",
    CAST(s."tax_amt" AS DECIMAL(18,2)) AS "tax_amount",
    CAST(s."gross_sale_value" AS DECIMAL(18,2)) AS "gross_sales",
    CAST(s."purchase_rate" AS DECIMAL(18,4)) AS "source_purchase_rate",
    CAST(s."purchase_value" AS DECIMAL(18,2)) AS "source_purchase_value"
FROM "RAWN_CT_gross_net_margin-Copy" s
WHERE CAST(s."item_qty" AS DECIMAL(18,4)) <> 0;
