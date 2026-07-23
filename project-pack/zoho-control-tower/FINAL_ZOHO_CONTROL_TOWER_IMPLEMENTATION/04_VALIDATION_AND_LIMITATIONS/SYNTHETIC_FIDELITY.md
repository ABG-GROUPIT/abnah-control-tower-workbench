# Control Tower Synthetic Schema Fidelity

Source schemas are exact; values and operational distributions remain synthetic.

Twenty current UAT POSIST CSV contracts and one historically supplied ABNAH Vendor Report contract were checked against the generated raw source files. Exact means header spelling, order, field count and captured grain. Current-UAT empty-state behavior is also mirrored. It does not mean that synthetic values, row counts, identifiers, preamble rows, or missingness frequencies reproduce ABNAH operations.

## Verified Summary

- Exact validated POSIST headers: 21 of 21
- Current UAT contracts audited: 20
- Historical schema contracts retained: 1
- Populated source contracts: 18
- Mirrored header-only contracts: 2
- Confirmed all-blank fields excluded downstream: 38
- Confirmed all-zero fields excluded downstream: 31
- Schema-capture-only reports: 3
- Explicitly synthetic AUX tables: 4

## Layer Boundary

| Layer | Fidelity | Meaning |
|---|---|---|
| RAW_CT source-shaped CSV | exact_contract | POSIST header spelling and order, confirmed empty-state behavior, and captured report grain. |
| RAWN_CT Zoho landing | intentional_translation | Canonical field names plus source period and outlet metadata; not a byte-for-byte POSIST export. |
| STD / DIM / FACT / SUM | projected_fields_only | Only KPI-relevant fields with usable source evidence are carried into active calculations. |

## Report Register

| Report | Header | Pattern | Actual rows | Synthetic rows | Downstream | Ignored fields |
|---|---|---|---:|---:|---|---:|
| Bill Item Detail Report | exact | modelled_at_captured_grain | 8,138 | 14,576 | audit_or_reconciliation_only | 6 |
| Bulk Return Report | exact | modelled_at_captured_grain | 6 | 19 | audit_or_reconciliation_only | 2 |
| Closing Stock Report | exact | modelled_at_captured_grain | 1,148 | 387 | active_projected_fields | 0 |
| Enterprise Consumption Report - detail | exact | modelled_at_captured_grain | 812 | 387 | audit_or_reconciliation_only | 10 |
| Enterprise Entry Report - Stock Entry | exact | modelled_at_captured_grain | 562 | 585 | active_projected_fields | 11 |
| Enterprise Opening Report - Opening Stock | exact | modelled_at_captured_grain | 3 | 387 | audit_or_reconciliation_only | 4 |
| Enterprise Physical Report - Physical Stock | exact | modelled_at_captured_grain | 6,251 | 387 | audit_or_reconciliation_only | 2 |
| Enterprise Purchase Order Report - item detail | exact | modelled_at_captured_grain | 113 | 638 | active_projected_fields | 6 |
| Enterprise Stock Re-Order | exact | mirrored_header_only | 0 | 0 | gated_source_unavailable | 8 |
| Enterprise Stock Return | exact | mirrored_header_only | 0 | 0 | gated_source_unavailable | 36 |
| Enterprise Transfer Report - Transfer From | exact | modelled_at_captured_grain | 211 | 18 | active_projected_fields | 4 |
| Enterprise Transfer Report - Transfer To | exact | modelled_at_captured_grain | 211 | 18 | active_projected_fields | 2 |
| Enterprise Variance Report - master | exact | modelled_at_captured_grain | 426 | 387 | audit_or_reconciliation_only | 10 |
| Enterprise Variance Report - normal detailed CSV | exact | modelled_at_captured_grain | 812 | 387 | active_projected_fields | 4 |
| Enterprise Wastage Report - transaction detail | exact | modelled_at_captured_grain | 581 | 108 | active_projected_fields | 1 |
| Gross/Net Margin Report - bill item detail | exact | modelled_at_captured_grain | 11,511 | 14,576 | active_projected_fields | 0 |
| Item Recipe Report | exact | modelled_at_captured_grain | 899 | 723 | active_projected_fields | 0 |
| Purchase Detail - PO details enabled | exact | modelled_at_captured_grain | 288 | 585 | audit_or_reconciliation_only | 4 |
| Recipe Consumption Report | exact | modelled_at_captured_grain | 1,927 | 6,501 | audit_or_reconciliation_only | 3 |
| Stock In Stock Out Report - movement detail | exact | modelled_at_captured_grain | 1,229 | 36 | audit_or_reconciliation_only | 0 |
| Vendor Report | exact | historical_schema_with_structural_quality_gate | historical | 70 | active_projected_fields | 0 |

## No-Signal Field Decisions

- **Bill Item Detail Report**: `Covers` (all_blank), `customerMobile` (all_blank), `customerName` (all_blank), `Order Id` (all_blank), `Source` (all_blank), `Waiter Name` (all_blank)
- **Bulk Return Report**: `Comment` (all_blank), `Source` (all_blank)
- **Enterprise Consumption Report - detail**: `Amt` (all_zero), `Indent Dispatch Qty` (all_zero), `Amt` (all_zero), `InternalIndent Dispatch Qty` (all_zero), `Amt` (all_zero), `InternalIndent Receive Qty` (all_zero), `Amt` (all_zero), `Reuse Qty` (all_zero), `Amt` (all_zero), `Yield Wastage` (all_zero)
- **Enterprise Entry Report - Stock Entry**: `Batch Number` (all_blank), `CESS Rate` (all_blank), `CESS Value` (all_blank), `Comment` (all_blank), `Item Brand` (all_blank), `Item Charges Amount` (all_zero), `MRP` (all_zero), `Other Taxes Rate` (all_blank), `Other Taxes Value` (all_blank), `PR Number` (all_blank), `Source` (all_blank)
- **Enterprise Opening Report - Opening Stock**: `Comment` (all_blank), `Sub Total` (all_zero), `Source` (all_blank), `Unit Price` (all_zero)
- **Enterprise Physical Report - Physical Stock**: `Item Brand` (all_blank), `Source` (all_blank)
- **Enterprise Purchase Order Report - item detail**: `Bill Wise Discount Amount` (all_zero), `Comment` (all_blank), `Item Brand` (all_blank), `Item Wise Discount Amount` (all_zero), `PR Deployment` (all_blank), `PR Number` (all_blank)
- **Enterprise Stock Re-Order**: `Deployment Name` (no_rows), `Store Name` (no_rows), `Item Code` (no_rows), `Item Name` (no_rows), `Re-Order Level` (no_rows), `Minimum-Order Level` (no_rows), `Available Qty` (no_rows), `Unit Name` (no_rows)
- **Enterprise Stock Return**: `Deployment Name` (no_rows), `Store Name` (no_rows), `Stock Entry Date` (no_rows), `Transaction Number` (no_rows), `Invoice Number` (no_rows), `Batch Number` (no_rows), `Vendor Code` (no_rows), `Vendor Name` (no_rows), `Super Category Code` (no_rows), `Super Category Name` (no_rows), `Category Code` (no_rows), `Category Name` (no_rows), `Item Code` (no_rows), `Item Name` (no_rows), `Comment` (no_rows), `Unit` (no_rows), `Entry Qty` (no_rows), `Unit Price` (no_rows), `Sub Total` (no_rows), `Discount` (no_rows), `CGST` (no_rows), `SGST` (no_rows), `IGST` (no_rows), `Non GST` (no_rows), `Entry Amt` (no_rows), `Return Date` (no_rows), `Return Unit` (no_rows), `Return Qty` (no_rows), `Return SubTotal` (no_rows), `Return Discount` (no_rows), `Return CGST` (no_rows), `Return SGST` (no_rows), `Return IGST` (no_rows), `Return Non GST` (no_rows), `Return Amount` (no_rows), `Transaction Status` (no_rows)
- **Enterprise Transfer Report - Transfer From**: `Comment` (all_blank), `Receiver Store/Kitchen Name` (all_blank), `Source` (all_blank), `Supplier Store/Kitchen Code` (all_blank)
- **Enterprise Transfer Report - Transfer To**: `Comment` (all_blank), `Source` (all_blank)
- **Enterprise Variance Report - master**: `Production Amt` (all_zero), `Production Qty` (all_zero), `Purchase Amt` (all_zero), `Purchase Qty` (all_zero), `Return Amt` (all_zero), `Return Qty` (all_zero), `Reuse Amt` (all_zero), `Resue Qty` (all_zero), `Stock Out Amt` (all_zero), `Stock Out Qty` (all_zero)
- **Enterprise Variance Report - normal detailed CSV**: `Amt` (all_zero), `Reuse Qty` (all_zero), `Amt` (all_zero), `Yield Wastage` (all_zero)
- **Enterprise Wastage Report - transaction detail**: `Source` (all_blank)
- **Purchase Detail - PO details enabled**: `Batch Number` (all_blank), `Company` (all_blank), `Other Taxes` (all_zero), `PO Comment` (all_blank)
- **Recipe Consumption Report**: `Parent Item Quantity` (all_blank), `Parent Subtotal` (all_blank), `Parent Price Per Unit` (all_blank)

## Policy

- Keep every captured POSIST column in RAW_CT source-shaped CSVs, even when unused.
- Mirror fields confirmed all blank or all zero in the audited UAT exports.
- Do not project confirmed no-signal fields into active standardized, fact, summary, or dashboard logic.
- Treat a header-only report as unavailable, never as a genuine zero result.
- Use RAWN_CT landing tables for Zoho; they intentionally add source period and outlet metadata and canonical field names.
- Keep AUX tables visibly labelled because they are model inputs, not POSIST reports.
