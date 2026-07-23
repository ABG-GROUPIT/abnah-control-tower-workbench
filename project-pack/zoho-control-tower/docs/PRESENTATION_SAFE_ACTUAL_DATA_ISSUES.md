# Presentation-Safe Actual Data Findings

## What To Say First

The 26 captured CSV exports were structurally parseable: their headers matched the governed contracts, row widths were valid, and declared field types parsed. The reason for keeping the demo on synthetic data is not a parser failure. It is that several actual exports are not fit to publish the required current-state and valuation KPIs without freshness, cost-coverage, and valuation controls.

Present the three findings below. They are factual fit-for-use blockers. Do not say POSIST is definitively wrong; say the captured export cannot safely support the stated KPI without clarification or correction.

# 1. Critical - Closing Stock Snapshot Is Not Current

| Evidence | Verified value |
| --- | --- |
| Exact POSIST report | `Closing Stock Report` |
| Export context | Snapshot generated on 22 July 2026 |
| Exact source row | CSV row `2` (the same date pair appears across all 1,148 rows) |
| `Date` / stock date | `2026-06-16` |
| `Generation Date` | `2026-07-22` |
| Lag | `36 days` |

## Why This Claim Is Safe

The source explicitly dates the stock position 36 days before the generation date. The historical date may have been intentionally selected, so do not call the underlying quantity wrong. It is nevertheless guaranteed that this export cannot represent current stock as of 22 July.

## What Would Go Wrong In Zoho

- Current closing inventory would actually be a 16 June checkpoint.
- Days cover, projected stockout, shortage value, and working capital would inherit that stale quantity.
- A current action queue could recommend the wrong items or miss genuine shortages.

## Presentation Line

> The Closing Stock export generated on 22 July carried a 16 June stock date across all 1,148 rows. We therefore blocked it from current-state KPIs rather than presenting a 36-day-old checkpoint as live stock.

## Likely Question And Answer

**Could the older date have been selected intentionally?** Yes. That would make it a valid historical extract, but it still cannot be used as the current snapshot required by the Control Tower.

# 2. Critical - June Source Margin Has A Material Cost-Coverage Gap

| Evidence | Verified value |
| --- | --- |
| Exact POSIST report | `Gross/Net Margin Report` |
| Report range | `1 June 2026 to 30 June 2026` |
| Exact source row | CSV row `15` |
| `SKU Code / Item No` | `IGC0052` |
| `Net Sale Value` | `235.00` |
| `Purchase Rate` | `0.00` |
| `Purchase Value` | `0.00` |
| `Net Margin%` / `Gross Margin%` | `0` / `0` |
| Period-wide result | `2,843 of 5,995` non-zero-sales rows, or `47.4%`, have zero purchase value |

## Why This Claim Is Safe

The claim is not that every zero-cost line is erroneous. A genuine no-cost item is possible. The guaranteed issue is that a non-zero sale with no approved cost or explicit no-cost classification cannot support a source margin KPI. The concentration in June makes period-to-period margin comparison especially unsafe.

## What Would Go Wrong In Zoho

- Treating zero as actual cost would overstate margin.
- Treating the source margin percentage as valid would mix cost-covered and uncovered sales.
- June margin would not be comparable with May or July.

## Presentation Line

> In the June Gross/Net Margin export, 47.4% of non-zero sales lines had zero purchase value. We did not interpret zero as free inventory; source margin publication remains blocked until cost coverage or an approved no-cost classification is available.

## Likely Question And Answer

**Could some items genuinely have zero purchase cost?** Yes. That is why the control asks for an explicit no-cost classification. Without it, zero is ambiguous and cannot be used as a production cost fact.

# 3. Major - Opening Quantity Exists Without Opening Valuation

| Evidence | Verified value |
| --- | --- |
| Exact POSIST report | `Enterprise Opening Report - Opening Stock` |
| Report range | `22 April 2026 to 22 July 2026` |
| Exact source row | CSV row `2` |
| `Item Code` | `7742` |
| `Opening Qty` | `1` |
| `Unit Price` | `0` |
| Opening subtotal | `0` |
| Report-wide result | All `3` captured rows have zero unit price and subtotal |

## Why This Claim Is Safe

The quantity may be valid and the zero valuation may reflect configuration or missing historical cost. The guaranteed limitation is monetary: these rows can support a quantity bridge but cannot support opening stock value without an approved valuation basis.

## What Would Go Wrong In Zoho

- Opening inventory value would be understated.
- The value-based consumption bridge could be distorted.
- Working-capital and leakage values could inherit an artificial zero-cost opening balance.

## Presentation Line

> The Opening Stock report supplied quantities but zero unit price and subtotal for every captured row. We retained the quantity signal but excluded those rows from monetary KPIs until an approved opening valuation method is defined.

# Engineering Controls - Useful To Show, But Do Not Call Them Source Errors

## PO Identifier Standardization

- `Enterprise Entry Report - Stock Entry`, row `2`: PO number `PO-11`.
- `Enterprise Purchase Order Report`, row `69`: PO number `11`.
- Both can refer to the same business PO, but an exact text join fails.
- The standardization layer preserves the raw values and creates a canonical identifier before PO-to-receipt logic.

## Recipe UOM Conversion

- `Item Recipe Report`, row `3`: recipe unit `GRAM` for ingredient code `7900`.
- `Closing Stock Report`, row `151`: inventory unit `PKT (500 GM)` for the same ingredient.
- Both values can be valid. A direct unit-text join or quantity comparison is invalid until the 500-gram conversion is governed.

# Findings Not To Present As Confirmed Data Errors

- Overdue open POs: valid procurement exceptions; a revised delivery date may exist outside the report.
- Closed PO received after expected date: a valid service exception; close-date semantics need confirmation.
- Negative-margin sales: arithmetic can be valid for promotions, discounts, or loss leaders.
- Negative closing stock: operationally serious, but can arise from timing, backdated movements, UOM, or count adjustments.
- Repeated recipe or recipe-consumption rows: the export may omit effective-date or event keys, so equality is not proof of duplicate business events.
- Negative variance or consumption states: sign conventions require business approval before calling them wrong.

# Recommended Presentation Sequence

1. State that structural parsing passed.
2. Show the stale Closing Stock row and explain the current-state blocker.
3. Show the June missing-cost row and the 47.4% period-wide coverage result.
4. Show the opening-valuation row as a narrower major limitation.
5. Close with PO identifier and UOM standardization as examples of why the layered model is necessary.
