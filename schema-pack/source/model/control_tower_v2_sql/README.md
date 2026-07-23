# ABNAH Control Tower v2 Query Tables

Build the SQL files in numeric order. The pack contains 38 Query Tables:

- 11 standardized tables
- 7 dimensions
- 14 facts
- 6 summaries

Every Query Table is dependency level 1, 2, or 3. This is a hard build constraint in Zoho Analytics.

This build targets the 14 Zoho import tables whose names end in `-Copy`.

Save every Query Table with the exact SQL filename, including the numeric prefix and `.sql` suffix. All downstream SQL already references that exact Zoho table name.

In `QUERY_TABLE_MANIFEST.csv`, `query_table_name` is the physical Zoho name and `logical_model_name` is the semantic label used in dashboard documentation.

The following conceptual views are implemented as reports or aggregate formulas instead of additional Query Tables:

- `FACT_CT_Vendor_Performance`: Use FACT_CT_PO_Receipt_Line directly for vendor detail reports.
- `FACT_CT_Action_Queue`: Action, owner and due-band fields are embedded in FACT_CT_Inventory_Risk.
- `SUM_CT_Risk_Action`: Build Page 1 widgets from FACT_CT_Inventory_Risk and FACT_CT_Menu_Impact aggregate formulas.
- `SUM_CT_Consumption_Variance`: Build Page 3 and Page 4 variance views directly from FACT_CT_Consumption_Variance.

The following legacy or unavailable-source Query Tables remain gated:

- `STD_CT_Expiry_Estimate`: The old expiry standardization step is retired. Query 38 exposes the new explicitly synthetic scenario directly, while production expiry remains gated until batch evidence exists.
- `STD_CT_Vendor_Return`: Enterprise Stock Return is header-only in the audited UAT export. Create this table only after a populated extract passes the same audit.

The original 37-table model remains a legacy reference. This v2 package uses the validated Restroworks landing contracts and should be used for the four-page control tower.

Do not create a Query Table until every source listed in its file header exists. Run the validation queries documented in `../zoho_control_tower_v2_validation.md` after each layer.
