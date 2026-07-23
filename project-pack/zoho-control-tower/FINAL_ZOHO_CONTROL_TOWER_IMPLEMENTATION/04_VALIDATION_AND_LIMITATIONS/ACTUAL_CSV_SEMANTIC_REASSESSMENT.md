# Actual CSV Semantic Reassessment

## Purpose

This checkpoint re-evaluates every deterministic finding from the 26-file
Restroworks audit before it is presented as a source-data problem. The review
uses the complete local exports, report grain, grouped-column position, exact
arithmetic, displayed precision, and cross-period behavior. Raw rows remain
local.

## Corrected Interpretations

| Previous signal | Reassessment | Final treatment |
| --- | --- | --- |
| 6,735 Bill Item Detail net-bridge findings | The first column in each GST band is the taxable base; the second is the tax value. The earlier rule added taxable bases as tax. With corrected semantics, all 8,138 populated rows reconcile. | Parser/contract error removed. Canonical GST fields now distinguish taxable base from tax value. |
| 2,885 net-margin and 2,886 gross-margin findings | Restroworks exports margin as zero when exported purchase cost is zero. Where cost is present, the conventional formula reconciles after allowing less than INR 0.10 of hidden cost precision. | No row-level formula defect. Zero-cost rows are assessed as cost-coverage states. |
| 158 Enterprise Consumption ideal-closing findings | The earlier formula omitted Purchase and Stock Out. The verified bridge is opening + purchase + stock in - stock out - consumption - wastage + reuse - return. | Corrected formula reconciles all 812 rows within 0.001 quantity. |
| Quantity x price amount findings across stock, transfer, physical, wastage, recipe, entry, and closing reports | Amounts use precision beyond the displayed quantity or price. Every prior finding falls inside the complete uncertainty implied by three quantity decimals and two price/amount decimals. | Display-precision envelope is part of the rule. No source error is asserted. |
| Seven Enterprise Entry tax-component findings | These are document-charge rows. They export charge amount and Total Tax but leave item tax-rate/component columns blank. Taxed charge rows resolve exactly to 3%, 5%, or 18%. | Item tax-component rule excludes charge rows. The missing charge tax breakdown remains a schema limitation, not a wrong total. |

## Defensible Risks That Remain

- Enterprise ReOrder and Enterprise Stock Return are header-only. Dependent
  production KPIs remain blocked until populated evidence or an approved
  alternate source is available.
- Two of four Recipe Consumption periods are header-only.
- The populated Recipe Consumption exports contain 205 exact repeated rows.
  This is a deduplication risk because the export lacks a proven line key; it is
  not permission to delete the rows.
- Gross/Net Margin has 2,879 non-zero net-sale rows with zero exported purchase
  value. The gap is period-specific: 3.7% in May, 47.4% in June, and 0.2% in the
  captured July period. Do not interpret zero purchase value as free cost.
- Enterprise Entry has PO number on only 2 of 562 rows and no populated batch
  number. Purchase Detail similarly carries PO fields on only 2 of 288 rows.
  This limits deterministic PO-to-receipt and expiry lineage.
- The three populated Enterprise Opening rows have zero unit price and zero
  subtotal. They can support quantity reconciliation, not opening valuation.
- Negative closing, variance, consumption, and margin values are preserved as
  operational exceptions. They may represent corrections, oversold inventory,
  reversals, or loss-making sales and require signed-off business treatment.

## Blank And Zero Fidelity

The local reviewer does not manufacture empty or zero values. A complete
comparison covered 804,322 non-sensitive viewable cells:

- 104,335 semantic blank/null cells;
- 168,329 numeric zero cells;
- zero source-profile versus normalized-view state mismatches.

The reviewer now renders a source blank as `blank` and a numeric zero as `0`,
with separate styling and per-export counts. Sparse movement columns in
Consumption and Variance, mutually exclusive GST bands, optional identifiers,
and unused comments therefore remain visible as actual export states.

## Production Rule

Only evidence outside a verified formula and its full displayed-precision
envelope is a row-level reconciliation exception. Header-only periods, sparse
critical keys, abrupt cross-period coverage changes, exact duplicates, and
business sign conventions remain separate quality gates. None should be
presented as a confirmed Restroworks defect without source-owner confirmation.
