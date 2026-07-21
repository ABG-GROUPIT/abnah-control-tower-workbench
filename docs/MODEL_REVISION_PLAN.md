# Model Revision Plan

## Decision

Revise the existing 37-query Zoho model. Do not restart from zero and do not keep the current model unchanged.

The layered `RAW -> STD -> DIM/FACT -> SUM` convention, core facts, and dependency order are useful. The current implementation also contains synthetic assumptions that cannot support the requested control tower in production.

## What Stays

- standard sales, purchase, receipt, closing inventory, recipe, vendor, item, outlet, and date concepts;
- existing layer naming and query dependency order where semantics remain valid;
- detailed facts as calculation authorities and aggregate reports as reconciliation surfaces;
- one shared model for P1, P2, and P4 rather than a separate Stock Administration model.

## What Must Change

| Current behavior | Required change |
| --- | --- |
| Three outlet-specific RAW unions and hardcoded outlet `CASE` logic | Ingest a source-driven outlet key and join a verified outlet master. |
| `DIM_Outlet` contains three synthetic outlets | Build from ABNAH outlet master, including region, city, coordinates, active state, and new/matured flag when available. |
| Recipe and ingredient joins use names | Use canonical menu, recipe, and ingredient identifiers with an unresolved-mapping exception table. |
| PO receipts are matched approximately by outlet, vendor, item, and date | Require PO line or PO number linkage before OTIF, lead-time, or in-full metrics are published. |
| Low stock is hardcoded as quantity `<= 10` | Replace with forecast demand, safety quantity, valid inbound timing, shortage, and days-cover logic. |
| Only theoretical consumption exists | Add inventory movements, stock checkpoints, actual consumption, variance, leakage, wastage, and data completeness. |
| Unit labels pass through without conversion | Add canonical UOM and item-specific conversion rules before quantity, price, or COGS calculations. |
| Event and competitor tables are part of the current model | Keep available but outside the first control-tower release. |

## Target Additions

### Dimensions

- `DIM_Outlet` rebuilt from source
- `DIM_Item_Identity`
- `DIM_UOM_Conversion`
- `DIM_Recipe_Effective`
- vendor-item approval/mapping where available

### Facts

- `FACT_Bill_Item_Line` or revised `FACT_Sales`
- revised `FACT_Purchase_Order`
- revised `FACT_Entry_Receipt`
- `FACT_Physical_Stock_Count`
- `FACT_Inventory_Movement`
- `FACT_Actual_Consumption`
- `FACT_Consumption_Variance`
- `FACT_Inventory_Wastage`
- `FACT_Vendor_Return`
- `FACT_Menu_Demand_Forecast`
- `FACT_Inventory_Risk`
- `FACT_Action_Recommendation`

### Summaries

- `SUM_Vendor_Performance`
- `SUM_Procurement_Funnel`
- `SUM_Inventory_Risk`
- `SUM_Menu_Profitability`
- `SUM_Data_Quality_Exceptions`

The exact query count is not a design target. Use the fewest query tables that preserve correct grain, reusable calculations, clear ownership, and reconciliation.

## API and CSV Boundary

The current public Restroworks packet indicates useful candidates for bill/KOT lines, menu metadata, inventory transaction modes, physical stock, PO candidates, wastage, vendor returns, and indents. None are ABNAH UAT verified.

The public packet does not yet prove complete recipe BOM, outlet geo master, expiry/batch, standing PO releases, vendor master, complete transfers, or guaranteed PO-line-to-GRN linkage. A hybrid design is therefore required unless UAT reveals additional enabled endpoints.

- POC: controlled CSV exports into stable Zoho tables, followed by schema/type/reconciliation checks.
- Production: validated Restroworks APIs where complete; persistent scheduled file feed or small middleware for gaps.
- Do not design automation around repeated local-drive uploads. Zoho states that local-drive and pasted imports cannot be scheduled; persistent sources such as web/FTP, cloud storage, databases, Databridge, or the Analytics API are the automation options.

References:

- [Restroworks API reference](https://api.restroworks.com/)
- [Zoho Analytics import methods](https://www.zoho.com/analytics/help/import-data/)
- [Zoho Analytics file and scheduled import behavior](https://www.zoho.com/analytics/help/import-data/files-feeds.html)
- [Zoho Analytics bulk import API](https://www.zoho.com/analytics/api/v2/bulk-api/import-data.html)
- [Zoho Analytics embedded and white-label setup](https://www.zoho.com/analytics/help/whitelabel-setup.html)

## Zoho Versus Custom UI

Use Zoho Analytics first for governed data, query tables, KPI calculations, standard charts, filters, drilldowns, exports, permissions, and refresh monitoring.

Test the four-page experience natively before committing to a custom application. Add an embedded or white-label custom shell only if the action queue, cross-page RAG state, India risk map, owner workflow, or presentation fidelity cannot be achieved cleanly in native Zoho. This avoids building a second analytics engine while preserving a path to the supplied visual direction.

## Build Sequence

1. Complete the prioritized schemas in `REPORT_CAPTURE_PRIORITY.md`.
2. Export a small controlled CSV set and record import defects.
3. Define source contracts, canonical identifiers, UOM rules, and stock period rules.
4. Create synthetic data with exact source schemas and controlled edge cases.
5. Refactor the retained model layers and add missing movement/variance/risk facts.
6. Reconcile each layer before adding KPI query tables.
7. Prototype all four pages in Zoho.
8. Run UAT API comparisons against the CSV model.
9. Select the production ingestion path source by source.
10. Decide native portal versus embedded shell from a documented capability test.
