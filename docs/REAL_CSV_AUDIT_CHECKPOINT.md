# Real CSV Semantic Audit Checkpoint

## Scope

This checkpoint records the Codex-reviewed local Restroworks export audit
without moving raw datasets into the Workbench repository. It covers 26 CSV
files, 20 report contracts, and 35,128 source rows.

The local evidence includes P1 Item Recipe; P2 Bill Item Detail and Gross/Net
Margin; and P4 purchase, entry, PO, inventory, transfer, consumption, variance,
wastage, return, reorder, recipe-consumption, and reconciliation reports.
Opening, physical, and directional transfer exports are Enterprise Entry source
modes with separate contracts and grains.

## Structural Result

- All 26 files match a reviewed contract; none are unmatched.
- All exported headers and all 20 Workbench structural variants match exactly.
- No type, row-width, shifted-column, or malformed-row error remains.
- Repeated `Amt` labels remain positionally attached to their parent movement.
- Embedded preambles, bill summaries, repeated headers, grouped recipe rows,
  and auxiliary totals are handled explicitly.
- Enterprise ReOrder and Stock Return are header-only.
- The first two Recipe Consumption periods are header-only; the next two are
  populated.

## Semantic Corrections

The earlier audit queue contained parser and formula assumptions that were not
source defects. They have been removed:

| Earlier signal | Correct interpretation |
| --- | --- |
| Bill-item net bridge | `GST@x% Amount` is the taxable base and adjacent `GST@x%` is the tax value. All 8,138 populated rows reconcile after correcting this positional meaning. |
| Gross and net margin formulas | Zero exported cost uses a zero-margin source convention. Non-zero-cost rows reconcile after allowing less than INR 0.10 of hidden cost precision. |
| Consumption ideal closing | The verified bridge includes Purchase and Stock In separately and subtracts Stock Out and Consumption separately. All 812 rows reconcile within 0.001 quantity. |
| Quantity x price values | Every earlier mismatch is inside the complete uncertainty created by displayed quantity, price, and amount precision. |
| Entry tax components | Document-charge rows carry Total Tax but leave item tax components blank. Their charge tax resolves to 0%, 3%, 5%, or 18%; item rows reconcile. |

The corrected deterministic run has zero business-rule exception rows. Its only
four deterministic warnings are the header-only ReOrder, Stock Return, and two
Recipe Consumption exports.

## Remaining Business Risks

- Gross/Net Margin has 2,879 non-zero net-sale rows with zero exported purchase
  value. The gap rate changes from 3.7% in May to 47.4% in June and 0.2% in the
  captured July period. This is a cost-coverage discontinuity, not proof of
  free cost or a margin-formula defect.
- Enterprise Entry carries PO number on 2 of 562 rows and no batch number.
  Purchase Detail carries its PO fields on 2 of 288 rows. Deterministic
  PO-to-receipt and expiry lineage therefore remains weak.
- Enterprise Opening contains only three populated rows, with zero unit price
  and subtotal throughout. It supports quantity reconciliation, not valuation.
- The two populated Recipe Consumption exports contain 205 exact repeated rows.
  They remain a deduplication risk until the business grain and line key are
  approved.
- Negative stock, variance, consumption, and margin observations remain
  operational exceptions requiring signed-off treatment. They are not
  automatically classified as source errors.

## Blank And Zero Verification

The local viewer was checked against every non-sensitive source-profile state:

- 804,322 viewable cells compared;
- 104,335 semantic blank/null cells;
- 168,329 numeric zero cells;
- zero source-profile versus normalized-view mismatches.

The localhost reviewer now renders blanks and numeric zeros differently and
shows per-export counts plus a fidelity status. The hosted Workbench stores only
aggregate state evidence and tightly bounded non-sensitive exception excerpts.

## Workbench Effect

- The evidence contract contains 11 semantic findings: coverage blockers,
  cost-coverage gaps, duplicate-grain risks, and sign-treatment reviews.
- It contains zero deterministic formula-exception rows and four minimal
  non-sensitive sign-review excerpts.
- Bill Item Detail canonical fields now distinguish GST taxable bases from tax
  values.
- Synthetic data remains appropriate for the demonstrator because the actual
  exports cover one operating scope with uneven periods and critical coverage
  gaps. It is not justified by widespread arithmetic defects.

## Production Gates

1. Obtain populated ReOrder and Stock Return evidence or approve alternates.
2. Resolve the June purchase-cost discontinuity.
3. Approve PO/receipt linkage and batch/expiry source coverage.
4. Approve recipe duplicate grain and sign conventions.
5. Validate equivalent multi-outlet, aligned-period extracts before replacing
   the synthetic demonstrator with actual production facts.
