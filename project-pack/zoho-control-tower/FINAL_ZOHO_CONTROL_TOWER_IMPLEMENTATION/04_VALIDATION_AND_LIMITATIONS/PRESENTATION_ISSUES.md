# Control Tower Source Issues - Presentation Register

## Present These As Confirmed Risks

| Priority | Evidence | Business effect | Required treatment |
| --- | --- | --- | --- |
| Critical | Gross/Net Margin contains 2,879 non-zero net-sale rows with zero exported purchase value. The gap rises from 3.7% in May to 47.4% in June, then 0.2% in the captured July period. | Source margin cannot be treated as complete cost coverage, especially for June. | Use recipe-based theoretical COGS for the synthetic model; reconcile cost coverage before actual margin publication. |
| Critical | Enterprise Entry contains PO number on only 2 of 562 audited rows. Purchase Detail contains PO fields on only 2 of 288 rows. | Deterministic PO-to-GRN linkage, actual OTIF and lead-time deviation are not production-ready. | Keep linked-line service KPIs labelled synthetic/provisional until PO lineage is populated and approved. |
| High | Enterprise Stock Re-Order and Enterprise Stock Return are header-only. Expiry is not enabled and Entry batch number is unpopulated. | Source reorder rules, vendor-return rate and exact expiry-risk KPIs are unavailable. | Keep them out of production views until a populated source is validated. The demo expiry scenario must say that it is synthetic and has no POSIST batch/expiry source. |
| High | Two of four Recipe Consumption periods are header-only. Populated exports contain 205 exact repeated rows without a proven line key. | Consumption deduplication can change totals without an approved business key. | Use the approved theoretical-consumption model for the demo and preserve source repeats for review. |
| Medium | Enterprise Opening has only three populated rows and all have zero unit price and subtotal. | Opening quantity can be inspected, but opening valuation is unsupported. | Do not use this report as the valuation source. |
| Medium | The historical Vendor Report can contain phone overflow, address continuation rows, extra cells and malformed compliance identifiers. | Vendor identity rows may shift structurally before import. | Run the local structural cleaner and review rejected/ambiguous rows before Zoho import. |
| Medium | Negative closing, consumption, variance and margin values occur in actual exports. | A negative value may be a correction, reversal, oversold state or loss, not necessarily corrupt data. | Preserve the sign and agree each business convention before classifying it as an error. |

## Do Not Present These As Confirmed POSIST Errors

The local semantic reassessment removed these false positives:

- GST taxable-base columns are not additional tax values. The corrected GST
  bridge reconciles all populated Bill Item Detail rows.
- Quantity multiplied by displayed price can differ slightly from amount
  because the export uses hidden precision. Differences inside the full
  displayed-precision envelope are not defects.
- Enterprise Consumption reconciles when Purchase and Stock Out are included
  in the inventory bridge.
- Source margin reconciles where purchase cost exists after allowing less than
  INR 0.10 hidden cost precision. The real concern is missing cost coverage,
  not a general margin-formula failure.
- Blank cells and numeric zeros displayed by the local reviewer match the
  source profiles. They are not a viewer rendering fault.

## Presentation Wording

Use:

> The audit identified source-coverage and lineage constraints that affect
> specific production KPIs. Arithmetic findings were semantically retested so
> that display precision, GST band structure, document-charge rows, blanks,
> zeros and signed corrections are not misreported as system errors.

Do not say that POSIST totals are generally wrong. Separate:

1. confirmed structural or coverage limitations;
2. operational exceptions that need business interpretation;
3. synthetic assumptions used only for the demonstrator; and
4. production KPI publication gates.
