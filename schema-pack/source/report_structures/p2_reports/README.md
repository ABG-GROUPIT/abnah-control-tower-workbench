# P2 Report Structure Ledger

This folder stores the portable, screenshot-free structural model for P2 reports. It contains only derived labels, layout relationships, semantic points, and evidence-boundary notes.

## Batch-One State

Reviewed on 2026-07-15:

| Section | Catalogue | Captured | Partial | Pending | Reviewed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Analytics | 10 | 9 | 1 | 0 | 10 |
| Attendance | 2 | 0 | 0 | 2 | 0 |
| Audit | 50 | 23 | 2 | 25 | 25 |
| Remaining P2 sections | 93 | 0 | 0 | 93 | 0 |
| **P2 total** | **155** | **32** | **3** | **120** | **35** |

`pending` means that the report remains in the known catalogue but usable result-schema evidence has not yet been transcribed. It does not mean the report is unavailable in Restroworks.

## Analytics Ledger

| Report | Schema | Shape | Evidence transcription |
| --- | --- | --- | --- |
| Hourly Sales Report | Captured | Mixed | Export headers plus business-date and total-row context |
| half_hourly_sales_report | Captured | Flat | Export headers |
| Hourly Sales By Category | Captured | Mixed | Export headers plus selected-category context |
| Growth Report | Captured | Mixed | Pivot structure |
| Average Bill | Captured | Flat | Export headers |
| Income Analysis Report | Captured | Grouped columns | Export headers with budget, actual, and variance groups |
| Forecast Comparison Report | Captured | Mixed | Manually reconstructed repeating month and session structure |
| Food Cost Report | Partial | Grouped columns | Manually reconstructed visible hierarchy and formula context |
| KDS Report | Captured | Flat | Export headers |
| Location Wise Sales | Captured | Flat | Export headers |

Food Cost Report remains partial because the supplied header view ends after `Sale` and one child label under `Actual Cost` is not visible. Its inclusion rules and formulas are preserved in `structure_notes`; no missing label has been invented.

## Audit Ledger

| Report | Schema | Shape |
| --- | --- | --- |
| KOT Detail Report | Captured | Flat |
| KOT Delete History Report | Captured | Grouped rows |
| Complimentary Report | Partial | Grouped rows |
| Complimentary Detail Report Headwise | Captured | Grouped rows |
| Discount Report | Captured | Flat |
| discount_and_voucher_report | Captured | Flat |
| Offers Report | Captured | Flat |
| KOT Tracking Report | Captured | Mixed |
| Report By Time | Partial | Mixed |
| Revenue Report | Captured | Flat |
| Negative Orders Report | Captured | Mixed |
| Delivery Audit Report | Captured | Mixed |
| Non Taxable Item Report | Captured | Flat |
| Food Bills Void Tax Report | Captured | Flat |
| Online Orders Time Log | Captured | Flat |
| Item Based Offer Report | Captured | Grouped columns |
| BI Logs Report | Captured | Flat |
| Offline Log Report | Captured | Flat |
| Aggregator Status Report | Captured | Flat |
| Custom Group Report | Captured | Flat |
| audit_report | Captured | Flat |
| billwise_distribution | Captured | Flat |
| Billwise_sale_GST | Captured | Flat |
| day_part_daily_sales | Captured | Mixed |
| BTS Itemwise Report | Captured | Grouped rows |

Complimentary Report remains partial because the visible table ends inside `Item Name`. Report By Time remains partial because only its leading tables and the start of the print-to-settlement section were supplied.

`day_part_daily_sales` is intentionally represented as five independently editable structural regions: headline measures, section quantity/amount, complimentary and void quantity/amount, hourly quantity/amount, and payment-mode financials. Dynamic day parts repeat by sales channel without storing any displayed outlet, date, or result values.

## Transfer Workflow

1. Add one JSON blueprint per newly transcribed report under its catalogue section.
2. Keep the stable `report_id` from `schema-pack/generated/report_catalog.csv`.
3. Use `captured` only when the full result structure is known; otherwise use `partial` and state the exact missing boundary.
4. Never copy screenshots, evidence paths, filenames, sample rows, users, outlets, or dates into this folder.
5. Run `refresh_atlas.bat` and inspect every new complex table in the editable workspace.
6. Update the P2 baseline in `scripts/validate_workspace_data.py` only after the new schema has been reviewed.

The generated runtime contract is `schema-pack/generated/workspace.json`; do not edit it manually.
