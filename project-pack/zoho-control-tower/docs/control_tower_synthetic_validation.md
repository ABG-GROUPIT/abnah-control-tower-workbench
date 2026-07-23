# ABNAH Control Tower Synthetic Validation

This pack extends the original three-outlet story into Restroworks-shaped control-tower reports.

## Outlet Narrative

- OUT001 Connaught Place: corporate and weekday-led coffee/lunch demand.
- OUT002 Hauz Khas: youth, social-event, cold-beverage and wrap demand with higher consumption pressure.
- OUT003 Saket Premium: mall, premium beverage, dessert and weekend demand with higher chilled/dessert exposure.

## Contract Coverage

- Validated CSV contracts generated: 21
- Exact source export files generated: 180
- Total synthetic source rows: 48,713
- Reconciliation checks: 35
- Failed checks: 0

The `RAW_CT_` source files preserve Restroworks header spelling and order, including repeated headers and trailing blank columns where observed. Fields proven fully blank or zero-only in the audited POSIST exports remain in those raw contracts but carry no synthetic signal. `AUX_` files are explicitly labelled and are never presented as Restroworks exports. Forecast and theoretical consumption are model outputs; outlet geography and expiry exposure are demo-only reference scenarios that must be replaced before production.

## Source Fidelity Boundary

- Audited fields mirrored as fully blank: 38
- Audited decimal fields mirrored as zero-only: 31
- Header-only report contracts mirrored with zero rows: 2
- Blank and zero-only fields are excluded from active Query Table projections and dashboard measures until a later populated POSIST extract proves usable signal.
- `RAWN_CT_` files are intentionally normalized landing tables with canonical source-period and outlet metadata; they are not byte-for-byte POSIST exports.
- Synthetic rows preserve the observed report grain and column behavior, but they do not claim to reproduce actual POSIST row counts, transaction identifiers, or operational value distributions.

## Controlled Demo Exceptions

- One negative month-end stock row is intentionally retained for Page 4 data-quality validation.
- Two zero-stock-with-demand rows are intentionally retained for Page 1 and Page 4 validation.
- Three March open/partial PO lines have blank expected-delivery dates to validate the PO completeness control.
- Formula and identity fields otherwise reconcile through the common synthetic ledger.

## Report Rows

| Report | Contract | Rows | Files |
|---|---|---:|---:|
| AUX Expiry Estimate | synthetic_demo_batch_scenario | 206 | 1 |
| AUX Menu Demand Forecast | approved_model_output | 6,923 | 1 |
| AUX Outlet Master | synthetic_demo_reference | 3 | 1 |
| AUX Theoretical Consumption | approved_model_output | 378 | 1 |
| Bill Item Detail Report | validated_uat_csv_contract | 14,576 | 9 |
| Bulk Return Report | validated_uat_csv_contract | 19 | 9 |
| Closing Stock Report | validated_uat_csv_contract | 387 | 9 |
| ERP Vendor Price | schema_capture_only_pending_uat_csv_validation | 303 | 1 |
| Enterprise Consolidated Indent | schema_capture_only_pending_uat_csv_validation | 25 | 1 |
| Enterprise Consumption Report - detail | validated_uat_csv_contract | 387 | 9 |
| Enterprise Entry Report - Stock Entry | validated_uat_csv_contract | 585 | 9 |
| Enterprise Opening Report - Opening Stock | validated_uat_csv_contract | 387 | 9 |
| Enterprise Physical Report - Physical Stock | validated_uat_csv_contract | 387 | 9 |
| Enterprise Purchase Order Report - item detail | validated_uat_csv_contract | 638 | 9 |
| Enterprise Purchase Summary | schema_capture_only_pending_uat_csv_validation | 100 | 1 |
| Enterprise Stock Re-Order | validated_uat_csv_contract | 0 | 9 |
| Enterprise Stock Return | validated_uat_csv_contract | 0 | 9 |
| Enterprise Transfer Report - Transfer From | validated_uat_csv_contract | 18 | 9 |
| Enterprise Transfer Report - Transfer To | validated_uat_csv_contract | 18 | 9 |
| Enterprise Variance Report - master | validated_uat_csv_contract | 387 | 9 |
| Enterprise Variance Report - normal detailed CSV | validated_uat_csv_contract | 387 | 9 |
| Enterprise Wastage Report - transaction detail | validated_uat_csv_contract | 108 | 9 |
| Gross/Net Margin Report - bill item detail | validated_uat_csv_contract | 14,576 | 9 |
| Item Recipe Report | validated_uat_csv_contract | 723 | 1 |
| Purchase Detail - PO details enabled | validated_uat_csv_contract | 585 | 9 |
| Recipe Consumption Report | validated_uat_csv_contract | 6,501 | 9 |
| Stock In Stock Out Report - movement detail | validated_uat_csv_contract | 36 | 9 |
| Vendor Report | validated_historical_abnah_contract | 70 | 1 |

## Reconciliation Results

| Check | Status | Observed | Expected |
|---|---|---|---|
| sales_line_count | PASS | 14576 | 14576 |
| sales_qty_reconciliation | PASS | 23319.0 | 23319.0 |
| bill_item_net_bridge | PASS | 0 | 0 |
| po_quantity_bridge | PASS | 0 | 0 |
| transfer_quantity_balance | PASS | 690.12 | 690.12 |
| closing_value_bridge | PASS | 0 | 0 |
| actual_consumption_bridge | PASS | 0 | 0 |
| variance_bridge | PASS | 0 | 0 |
| controlled_data_quality_exceptions | PASS | negative=1; zero=2 | negative=1; zero>=2 |
| aux_outlet_master_unique | PASS | rows=3; unique_outlets=3 | rows=3; unique_outlets=3 |
| aux_expiry_estimate_traceable | PASS | rows=206; risky_rows=206; value_gap_rows=0; tranche_gap_rows=0; duplicate_batch_keys=0 | rows>0; risky_rows>0; value_gap_rows=0; tranche_gap_rows=0; duplicate_batch_keys=0 |
| report_non_empty:vendor_report | PASS | 70 | >0 |
| report_non_empty:bill_item_detail | PASS | 14576 | >0 |
| report_non_empty:bulk_return | PASS | 19 | >0 |
| report_non_empty:enterprise_consumption_detail | PASS | 387 | >0 |
| report_non_empty:enterprise_entry | PASS | 585 | >0 |
| report_non_empty:enterprise_purchase_order | PASS | 638 | >0 |
| report_header_only:enterprise_reorder | PASS | 0 | 0 |
| report_header_only:enterprise_stock_return | PASS | 0 | 0 |
| report_non_empty:enterprise_transfer_from | PASS | 18 | >0 |
| report_non_empty:enterprise_transfer_to | PASS | 18 | >0 |
| report_non_empty:enterprise_variance_master | PASS | 387 | >0 |
| report_non_empty:enterprise_variance_normal | PASS | 387 | >0 |
| report_non_empty:enterprise_wastage_normal | PASS | 108 | >0 |
| report_non_empty:gross_net_margin | PASS | 14576 | >0 |
| report_non_empty:item_recipe_report | PASS | 723 | >0 |
| report_non_empty:purchase_detail | PASS | 585 | >0 |
| report_non_empty:recipe_consumption | PASS | 6501 | >0 |
| report_non_empty:stock_in_stock_out | PASS | 36 | >0 |
| report_non_empty:enterprise_opening | PASS | 387 | >0 |
| report_non_empty:enterprise_physical | PASS | 387 | >0 |
| report_non_empty:closing_stock | PASS | 387 | >0 |
| schema_capture_non_empty:ERP_Vendor_Price | PASS | 303 | >0 |
| schema_capture_non_empty:Enterprise_Purchase_Summary | PASS | 100 | >0 |
| schema_capture_non_empty:Enterprise_Consolidated_Indent | PASS | 25 | >0 |

## Remaining Source Gaps

- Approved item/UOM reference for shelf life, reorder quantity, order quantity and criticality
- Vendor lead time, service SLA and approved vendor-item relationships; Vendor Report supports identity, validity dates, compliance context, state and address only
- Expiry Report or batch-expiry evidence; the ABNAH module is not enabled, so the packaged expiry table remains a visibly labelled demo estimate
- Standing Purchase Order export schema and release linkage
- Food Cost Report missing child columns

There is no verified report named `Raw Material Item Detail`. Item identity, category, UOM and observed cost are derived from Closing Stock, Entry, Purchase Order and Item Recipe. Vendor identity comes from the exact historical `Vendor Report` schema after structural cleaning. Exact expiry and Standing PO remain unavailable; the demonstrator's AUX expiry output is an explicit scenario estimate, not a POSIST fact.