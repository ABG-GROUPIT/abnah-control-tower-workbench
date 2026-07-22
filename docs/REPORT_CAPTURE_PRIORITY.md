# Report Capture Priority

## Current Checkpoint

Collection is user-reported complete through P2 Sales report 17, `Daily Sales Summary Report`. This is a progress checkpoint, not a schema-complete claim: its exact schema still needs to be ingested into the portable workspace.

The objective is the smallest set that preserves all required detail. Overlapping names remain in the queue when they may differ by enterprise scope, transaction grain, identifiers, or reconciliation value.

## P2: Finish These First

### P0

| Report | Why |
| --- | --- |
| Daily Sales Report Detailed | Compare with already collected Daily Sales and Bill Item Detail to select the cleanest item/outlet sales fact. |
| Gross Sale Wastage Report | Potential direct wastage context for Page 3 and financial leakage. Capture even if Enterprise Wastage later becomes primary. |

### P1: Headers First, Full Structure Only if Unique

| Report | Possible extra context |
| --- | --- |
| Day Wise Sales Report | Daily trend and reconciliation fallback. |
| Week Cost Report | Cost context before P4 food-cost sources are confirmed. |
| Gross/Net Margin Report | Captured item-level quantity, sales, purchase value, and gross/net margin; validate as the primary menu-profitability source. |
| DSH Item Wise Report | Unknown item-wise context; retain until headers show duplication. |
| Day Closing Report | Close-period sales reconciliation. |
| Day Check Close Report | Alternate close-control fields or totals. |

The remaining P2 settlement, tax, payment, booking, reload, and channel reports can wait unless one of the tables above exposes a missing control-tower requirement.

## P4: P0 Core

### PO and GRN Lifecycle

- Enterprise Purchase Order
- Purchase Order
- Enterprise Entry
- Entry Report
- Purchase Detail
- Late Delivery Report

Capture both enterprise and operational names initially. OTIF, fill rate, open liability, and delivery breach depend on finding the version with stable PO line, expected delivery, actual delivery/close, received quantity, and GRN linkage.

### Inventory, Consumption, and Variance

- Closing Stock Report
- Raw Material Item Detail
- Enterprise Consumption
- Consumption Report
- Enterprise Variance
- Variance Report
- Recipe Consumption Report
- Stock Recipe Report
- Stock In Stock Out Report
- Movement Report
- Enterprise Wastage Report
- Expiry Report

These establish the stock checkpoint, item master, recipe BOM, movement coverage, actual and theoretical consumption, wastage, and exact-versus-estimated expiry boundary.

## P4: P1 Comparison and Validation

### Vendor Price, Return, Re-order, Standing PO

- ERP Vendor Price
- Vendor Pricing Report
- Vendor Last 5 Purchase Price
- Item Wise Inflation Report
- Pricing Ledger
- Enterprise Stock Return
- Stock Return
- Enterprise Stock Re-Order
- Re-Order Level
- Standing Purchase Order

Capture exact headers for all five price reports before selecting a primary. Their names overlap, but they may differ in vendor/item grain, effective date, purchase history, pack UOM, or source costing basis.

### COGS and Purchase Reconciliation

- Enterprise categorywise cogs
- Enterprise Food Cost Report
- Food Cost Report
- Cost margin Report
- Enterprise Purchase Summary Report
- Purchase Summary

Detailed transaction facts remain the KPI authority. These aggregates are reconciliation and formula-context candidates unless they provide a uniquely required grain.

### Optional Replenishment Workflow

- Enterprise Consolidated Indent
- Indent Report
- Consolidated Indent Items
- Issue Report

Capture these only if ABNAH includes internal store-to-store replenishment in the first action workflow. The public Indent API remains a UAT candidate.

## Defer for Current Release

- settlement, payment, tax, HSN, and statutory detail;
- loyalty, vouchers, gift cards, and reloads;
- booking, banquet, catering, and sales payout;
- bill passing and finance workflow detail unrelated to PO liability;
- production planning, gate pass, and packaging unless scope expands;
- event and competitor enrichment until the four control-tower pages reconcile.

## Capture Method

1. Download CSV and paste exact column headers into the report template.
2. Add a screenshot only when headers do not explain merged groups, multiple blocks, row labels, totals, continuation, or report grain.
3. Record filters once when they are genuinely shared; note report-specific filters only.
4. Do not include row values in the repository.
5. After comparison, label each report primary, fallback, reconciliation, validation, or deferred. Never silently discard an overlapping report.
