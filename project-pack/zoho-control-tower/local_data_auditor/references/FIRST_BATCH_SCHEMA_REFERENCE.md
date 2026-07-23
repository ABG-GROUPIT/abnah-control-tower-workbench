# First-Batch Schema Reference

> Historical capture reference. Enterprise ReOrder and Enterprise Stock Return
> are now confirmed unavailable/header-only for the current tenant. Do not ask
> for new exports unless ABNAH later enables or populates them.

## Decision

Use one shared deterministic audit engine and one semantic JSON contract per
report or report mode. This is custom parsing at the correct boundary: each
report has its own positional schema and rules, while CSV reading, diagnostics,
hashing, redaction and output remain common.

Repeated display labels are never deduplicated. Their meaning comes from the
nearest parent measure and the preserved source position. For example, the
Enterprise Consumption sequence:

```text
Purchase Qty | Amt | Consumption Qty | Amt | Closing Qty | Amt
```

is mapped as:

```text
purchase_qty | purchase_amt | consumption_qty | consumption_amt |
closing_qty | closing_amt
```

The `Amt` after `Consumption Qty` is consumption value. It is not an
`amount_yield` field and it is not a duplicate to discard.

## Exact Export Order

The populated Enterprise Consumption and both Enterprise Variance samples are
already available for engine validation. Export these next, in this order:

1. **Enterprise Purchase Order Report**: all PO statuses and all selected
   outlets; include both open and closed/partially received lines.
2. **Purchase Detail**: `PO Details = enabled`, no summary/ABC mode, item-level
   rows, all vendors and categories.
3. **Enterprise Stock Return** or the identical **Stock Entry Return Report**:
   all transaction statuses.
4. **Enterprise Wastage Report - Normal**: normal item-detail tab, not Master
   Wastage.
5. **Gross/Net Margin Report**: bill-item detail. Customer name and number are
   marked sensitive and are excluded from normalized output.
6. **Enterprise Stock Re-Order**: one full current snapshot with all items,
   including healthy rows.
7. **Item Recipe Report**: one full active recipe snapshot.
8. **Stock In Stock Out Report**: all movement rows and both directions.

After those pilot files pass, export four or five months as separate monthly
files for Enterprise Consumption, Enterprise PO, Purchase Detail, Stock Return,
Normal Wastage, Gross/Net Margin and Stock In/Out. Export Normal and Master
Variance separately at month end. Recipe and ReOrder are snapshot/master exports,
not monthly facts unless historical snapshots are intentionally required.

## Why These Reports

| Contract | Required ABNAH facts |
|---|---|
| Enterprise Consumption detail | Opening/closing quantity and value, inflow/outflow, consumption, wastage, reuse, returns, ideal and adjusted closing |
| Enterprise PO item detail | Vendor, PO status, ordered/processed/remaining quantity, expected/close dates, price, discounts, tax and liability |
| Purchase Detail with PO fields | Receipt/purchase transaction, PO linkage, invoice, vendor, item, quantity, UOM, price and tax |
| Enterprise Stock Return | Vendor/item return quantity and value, original entry reference and return date |
| Normal Wastage | Item-level stock wastage, billing wastage, consumption denominator and total wastage |
| Master Variance | Store/item physical count, variance, physical gain/loss and actual consumption at a reconcilable grain |
| Normal Variance | Enterprise item overview; useful for ranking, but physical coverage can be partial |
| Gross/Net Margin | Item sales, discounts, net/gross sales, purchase value and source margin percentages |
| Enterprise ReOrder | Available stock, reorder level and minimum-order level |
| Item Recipe | Menu-item-to-ingredient bridge, recipe quantity and recipe UOM |
| Stock In/Out | Transfer/movement direction, references, quantity and value |

Together these are the minimum detailed set for PO delay/fill rate, vendor return
risk, price movement, inventory capital, consumption variance, wastage, menu
impact and margin. Aggregate Food Cost, COGS, Purchase Summary, Daily Sales
Summary and Master Wastage reports can validate totals later, but they should not
replace these lower-grain facts.

## Contract-Specific Semantics

### Enterprise Consumption

Evidence: populated UAT CSV, 802 rows, plus grouped UAT interface schema.

Every quantity-like measure is paired positionally with its following `Amt`:

```text
opening, purchase, indent receive, indent dispatch,
internal indent receive, internal indent dispatch, stock in, consumption,
source yield wastage, stock out, stock out + consumption, wastage, reuse,
return, closing, physical gain/loss, ideal closing, physical-adjusted closing
```

Observed in the current sample:

- `stock_out_plus_consumption = stock_out + consumption` on all 802 rows.
- `physical_adjusted_closing = closing` on all 802 current rows, but this is an
  observation rather than a permanent rule; a future physical adjustment can
  legitimately make the fields differ.
- The observed ideal-closing quantity uses aggregate `stock_in`; purchase and
  indent columns are source breakouts and must not be added again.
- Physical gain/loss is not a simple closing-minus-ideal bridge in the current
  data. It is retained as a source measure and no formula is guessed.

### Enterprise Variance - Normal

Evidence: populated UAT CSV, 431 rows.

The CSV header has 40 cells, while populated rows have 42 cells. Two numeric
positions occur between `Return Amt` and the real `Closing Date`, and every
current row contains zero in both. They are retained as:

```text
unlabelled_qty_before_closing
unlabelled_amt_before_closing
```

A future non-zero value is a hard stop until Restroworks identifies the omitted
group label. The final empty export cell is padding and is trimmed.

Normal Variance is aggregated over the selected enterprise scope. Physical
quantity can cover only counted stores, while closing quantity covers the wider
selection. Therefore `variance = closing - physical` is not a valid row-level
hard rule here: it matched only 2 of 55 currently counted rows. Use this report
for enterprise ranking and use Master Variance for store-level reconciliation.

### Enterprise Variance - Master

Evidence: populated UAT CSV, 426 rows.

This is a separate contract and a different grain. Among 55 rows with a physical
count, `variance = closing - physical` matched all 55 within tolerance.
Physical-adjusted closing matched source closing on all 426 current rows, but it
is not forced to remain equal in future physical-adjustment periods. `NA`
physical values are valid nulls and are not converted to zero.

### Enterprise Wastage - Normal

Evidence: grouped UAT interface schema; populated normal export still required.

The four pairs are:

```text
stock_wastage_qty / stock_wastage_amt
consumption_qty / consumption_amt
billing_wastage_qty / billing_wastage_amt
total_wastage_qty / total_wastage_amt
```

Consumption is the comparison denominator, not another component to add into
total wastage. Percentage logic remains unsigned until populated rows prove the
source formula.

### PO, Purchase, Return, Margin, ReOrder, Recipe and Stock Movement

- Enterprise PO is populated and schema-validated; receipt linkage and status
  semantics remain production gates. Enterprise Stock Return remains
  header-only.
- Purchase Detail, Normal Wastage, Gross/Net Margin and Stock In/Out now have
  populated audited CSV evidence.
- Item Recipe uses the reviewed P1 eight-field visual schema. It is the required
  menu-item-to-ingredient bridge; Recipe Consumption is a different transactional
  report and is not a substitute.
- Enterprise ReOrder has a validated eight-field header, but the current export
  is header-only.

## Additional Source Gaps

These are required for the final dashboard but should not be invented inside the
parser:

- **Expiry Report or batch-expiry source** is not enabled. Keep expiry KPIs
  unavailable; receipt age without batch and shelf-life evidence is not expiry.
- **Item master** for base UOM, conversion factor, shelf life, storage type and
  active status.
- The historical **Vendor Report** supplies stable vendor name/code, validity,
  compliance context, state and address after structural cleaning. Active
  status, lead time, SLA, approved item/category mapping and service geography
  remain unavailable.
- The current implementation has one outlet. Derive its identity from
  operational reports and do not publish a multi-outlet map.
- **Standing PO Report** only if ABNAH actually uses standing POs and the source
  exposes standing-PO-to-release-PO keys.

## Evidence Register

No screenshots are copied into this auditor. Only derived schema definitions are
stored.

| Evidence key | Used for |
|---|---|
| P4 Stock Administration schema capture README | Literal P4 headers and report-mode names |
| P2 Reports schema capture README | Gross/Net Margin literal header |
| Populated Enterprise Consumption CSV | Position, row width and observed formulas |
| Populated Enterprise Variance CSV | Hidden pair, row width and aggregate physical-scope behavior |
| Populated Master Variance CSV | Store-level variance and null behavior |
| Historical Vendor Report and cleaning runbook | Exact 16-column vendor schema plus phone/address spillover repair rules |
| Header-only Enterprise PO, ReOrder and Stock Entry Return CSVs | Literal export headers and trailing blank behavior |
| P1 Schema Atlas Item Recipe record | Eight-field menu-to-ingredient schema |
| Dashboard Requirement 1.2 workbook | Required source fields and KPI coverage |
