# Real CSV Audit Checkpoint

## Scope

This checkpoint records the corrected local, value-aware Restroworks export
audit without moving raw datasets into the Workbench repository. The audit
covers 26 CSV files, 20 report contracts, and 35,128 source rows. One legacy
Purchase Detail `.xls` export was not part of the CSV run because an equivalent
Purchase Detail CSV was audited.

| Area | Contract or mode | CSV files |
| --- | --- | ---: |
| P1 | Item Recipe | 1 |
| P2 | Bill Item Detail | 2 |
| P2 | Gross/Net Margin | 3 |
| P4 | Bulk Return | 1 |
| P4 | Closing Stock | 1 |
| P4 | Enterprise Consumption detail | 1 |
| P4 | Enterprise Entry: Stock Entry | 1 |
| P4 | Enterprise Entry: Opening Stock | 1 |
| P4 | Enterprise Entry: Physical Stock | 1 |
| P4 | Enterprise Entry: Transfer From | 1 |
| P4 | Enterprise Entry: Transfer To | 1 |
| P4 | Enterprise Purchase Order | 1 |
| P4 | Enterprise ReOrder | 1 |
| P4 | Enterprise Stock Entry Return | 1 |
| P4 | Enterprise Variance: Master | 1 |
| P4 | Enterprise Variance: Normal detailed CSV | 1 |
| P4 | Enterprise Wastage transaction detail | 1 |
| P4 | Purchase Detail with PO fields | 1 |
| P4 | Recipe Consumption | 4 |
| P4 | Stock In Stock Out | 1 |

Opening, physical, and directional transfer exports are Enterprise Entry source modes,
not new navigation reports. They share the stable Enterprise Entry report identity while
retaining separate table contracts and grains.

## Structural Result

- 26 CSV files matched a reviewed contract; none were unmatched.
- No observed header insertion, removal, rename, reorder, or row-width contract error
  remained after report-aware parsing.
- Repeated positional labels such as `Amt` remain attached to canonical movement fields.
- Embedded preambles, repeated Bill Item headers, bill summary rows, grouped Item Recipe
  rows, and auxiliary report totals are handled explicitly.
- Enterprise ReOrder and Stock Entry Return were header-only. Their headers are known,
  but value quality and formula behavior are not assessed.
- The first two Recipe Consumption months were header-only; the next two supplied
  populated rows for value profiling.

## Deterministic Review Queue

These are evidence counts for investigation, not declarations that Restroworks is wrong.
Negative and zero values may be valid for adjustments, reversals, unavailable processes,
or the selected report period.

| Report | Deterministic signal requiring review |
| --- | --- |
| Enterprise Consumption | Ten all-zero and four mostly-zero fields, negative inventory measures, and 158 rows against the provisional ideal-closing hypothesis. |
| Enterprise Variance | Negative opening, closing, variance, physical-gain/loss, actual-consumption, and adjusted-closing measures require movement-sign confirmation. |
| Closing Stock | Negative quantity/value measures and 24 amount-from-quantity/price review mismatches. |
| Enterprise Physical | 98 quantity-price-amount review mismatches; source formula or price basis must be confirmed. |
| Enterprise Wastage | 57 quantity-price-amount review mismatches. |
| Enterprise Transfer | One amount review mismatch in each direction. |
| Stock In Stock Out | 130 stock-in and 3 stock-out subtotal review mismatches. |
| Recipe Consumption | 33 parent subtotal review mismatches and 205 duplicate-row flags across the two populated monthly exports. |
| Enterprise Entry | Two base-amount and 7 tax-bridge mismatches; PO and batch coverage must be checked for receipt and expiry use. |
| Enterprise Purchase Order | The 113-row export is now populated and matches all encoded row rules; receipt linkage, status semantics, and eligible closed-line logic remain the production gate. |
| Purchase Detail | Most PO fields are absent in the populated rows despite the PO-enabled export shape; only 2 of 288 rows carry the PO fields needed for fallback use. |
| Bill Item Detail | The provisional net bridge does not reconcile for many item rows; timestamps remain valid source text and are not classified as parse defects. |
| Gross/Net Margin | Negative margin percentages exist; the conventional margin hypotheses do not reproduce many source rows and must not be treated as confirmed Restroworks formulas. |

## Local Semantic Review

The semantic pass used `qwen2.5:7b-instruct` through localhost Ollama with a
separate analyst and verifier pass. The deterministic profiler was then
corrected so optional type inference on declared text cannot create false parse
errors for timestamps or identifiers. Deterministic category normalization and
grounding reject unsupported schema changes and impossible value claims. Model
interpretation remains secondary to deterministic counts and requires business
confirmation.

## Workbench Effect

- 20 audit mappings update 15 stable source blueprints.
- Enterprise Entry now exposes five explicit CSV mode tables.
- Normal detailed Variance and transaction-detail Wastage are added without deleting the
  previously captured visual modes.
- Bulk Return and Closing Stock move from pending to captured.
- Every audit-touched blueprint is `needs_review` until its blank rendering is checked.
- The repository contains no raw CSVs, normalized extracts, screenshots, local
  paths, filenames, hashes, or sensitive values.
- `control-tower-evidence.json` contains 18 minimal issue excerpts: one
  non-sensitive numeric/date excerpt per deterministic finding type, with source
  row number retained for local verification.

## Next Review

1. Review all changed blank tables in Discovery, especially Enterprise Entry variants,
   detailed Variance, and Consumption grouped columns.
2. Confirm source price bases and formulas for the deterministic mismatch queue.
3. Confirm Enterprise Purchase Order status semantics and exact PO-line/GRN linkage.
4. Obtain populated Enterprise ReOrder and Stock Entry Return exports.
5. Record accepted formula semantics in model mappings only after the source reports and
   business owners agree.
