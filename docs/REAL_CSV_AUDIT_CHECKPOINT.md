# Real CSV Audit Checkpoint

## Scope

This checkpoint records the first local, value-aware Restroworks export audit without
moving raw rows into the Workbench repository. The final sanitized packet covers 26 CSV
files across 20 report contracts. One legacy Purchase Detail `.xls` export was not part
of the CSV run because an equivalent Purchase Detail CSV was audited.

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
| Enterprise Entry | Invoice-number type parsing needs review, with 2 base-amount and 7 tax-bridge mismatches. |
| Purchase Detail | Invoice-number type parsing needs review; most PO fields are absent in the populated rows despite the PO-enabled export shape. |
| Bill Item Detail | Open/close timestamps need a source-format parser, and the provisional net bridge does not reconcile for many item rows. |
| Gross/Net Margin | Negative margin percentages exist; the conventional margin hypotheses do not reproduce many source rows and must not be treated as confirmed Restroworks formulas. |

## Local Semantic Review

The semantic pass used `qwen2.5:7b-instruct` through localhost Ollama with a separate
analyst and verifier pass. Deterministic category normalization and grounding reject
unsupported schema changes and impossible value claims. Model interpretation remains
secondary to deterministic counts and requires business confirmation.

## Workbench Effect

- 20 audit mappings update 15 stable source blueprints.
- Enterprise Entry now exposes five explicit CSV mode tables.
- Normal detailed Variance and transaction-detail Wastage are added without deleting the
  previously captured visual modes.
- Bulk Return and Closing Stock move from pending to captured.
- Every audit-touched blueprint is `needs_review` until its blank rendering is checked.
- The repository contains no CSV rows, normalized extracts, screenshots, local paths, or
  exact business values from the audit.

## Next Review

1. Review all changed blank tables in Discovery, especially Enterprise Entry variants,
   detailed Variance, and Consumption grouped columns.
2. Confirm Restroworks timestamp formats before treating Bill Item parse failures as data
   defects.
3. Confirm source price bases and formulas for the deterministic mismatch queue.
4. Obtain populated Enterprise ReOrder and Stock Entry Return exports.
5. Record accepted formula semantics in model mappings only after the source reports and
   business owners agree.
