-- Query Table: 23_fact_ct_purchase_receipt.sql
-- Logical model name: FACT_CT_Purchase_Receipt
-- Layer: fact
-- Purpose: Expose PO-linked accepted receipt lines.
-- Sources: 08_std_ct_purchase_receipt.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT r.*
FROM "08_std_ct_purchase_receipt.sql" r;
