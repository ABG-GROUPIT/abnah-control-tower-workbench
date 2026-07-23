# Stock Administration Screenshot Sample Observations

Sample folder reviewed:

```text
C:\Users\ARNAV\Downloads\Stock Administration
```

Review date: 2026-07-13

This was a manual visual review only. The screenshots were not run through the OCR scraper.

## Conclusion

The separate POSist Stock Administration area appears to contain the BOH/raw-report families that were missing from the earlier FOH/reporting screenshots. This is enough to treat the earlier gap as a navigation/module-access issue until proven otherwise.

It is conclusive for capture planning, but not final schema proof. Field-level screenshots, exports, or API sample responses are still required before changing SQL models.

## Top-Level Stock Administration Areas

Observed top-level menu items:

- Stock Reports
- Catering
- Summary
- Bill Passing

The Summary screen showed Deployment Summary rows including warehouse/testing deployments.

## Stock Reports Tree

Observed report families:

| Family | Reports visible in sample |
|---|---|
| Enterprise Reports | Enterprise Entry, ERP Vendor Price, Enterprise Stock Return, Enterprise Consumption, Enterprise Stock Re-Order, Enterprise Purchase Order, Enterprise Consolidated Indent, Enterprise Variance, Enterprise categorywise cogs, Enterprise Bill Passing, Enterprise Credit Note Report, Enterprise Wastage Report, Enterprise Purchase Summary Report, Enterprise Internal Indent Report, Enterprise Food Cost Report |
| Transactional Reports | Entry Report, Entry Sync Report, Payment Report, Stock Return, Purchase Detail, Purchase Detail Consolidated, Purchase Requisition Report, Cut Code Report, Bill Passing Report, Stock In Stock Out Report |
| PO/SO Reports | Purchase Order, Standing Purchase Order, Sales Order, OpenReturn Sales Order Report, ERP Vendor Invoice, Consolidated salesorder Report receiverWise |
| Indent Reports | Indent Report, Consolidated Indent, Consolidated Indent Items, Issue Report, Consolidated Indent Report Outlet Wise, Suspense Report, Bulk Return Report |
| Aggregation Reports | Item Wise Inflation Report, Consumption Report, Variance Report, Intermediate (Semi), Movement Report, Finished Food, Recipe Consumption Report |
| Analytical Reports | Booking Journal, Food Cost Report, Re-Order Level, Closing Stock Report, Cost margin Report, Pricing Ledger, Purchase Summary, Stock Recipe Report |
| Other Reports | Advance Ordering Report, NC Head Consumption Cost, Expiry Report, Default Cost Report, Kitchen Wise Item Report, Vendor Pricing Report, Late Delivery Report, RR Reports, Pending Requests, Manual Month End Report, HSN Wise Summary, Sales Payout Report, Vendor Last 5 Purchase Price, Yield Report, Production Plan Report, Gate Pass Report, Bin Packaging Report |

## Item Master Detail Signal

One screenshot showed a raw-material/item detail page with fields including:

- item name
- type
- item code
- HSN/SAC code
- category
- assigned units
- preferred unit
- status
- expiry flag
- non-stockable/perishable flag
- yield
- tax type/default rate/applicable value

This should be captured as a master-data target because it can improve `DIM_Ingredient`, UOM normalization, tax attributes, expiry/perishability logic, and procurement/inventory joins.

## Capture Priority

First capture priority for ABNAH phase 1:

1. Enterprise Consumption, Wastage, Re-order, Purchase Order, Vendor Price, Bill Passing, Internal Indent, Food Cost.
2. Transactional Entry, Purchase Detail, Purchase Requisition, Bill Passing, Stock In Stock Out.
3. Indent Reports and Aggregation Reports, especially Consumption, Variance, Movement, Recipe Consumption.
4. Analytical Closing Stock, Re-order Level, Purchase Summary, Stock Recipe.
5. Other Reports that support vendor and spoilage intelligence: Expiry, Vendor Pricing, Late Delivery, Vendor Last 5 Purchase Price, Yield, Production Plan.

Use the `p4_stock_admin` scaffold in the screenshot dump for future captures.
