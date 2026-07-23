# Zoho Control Tower v2 - Validation And Publication Gates

## Validation Principle

Every dashboard number must be traceable through:

```text
saved dashboard component
-> saved Zoho report
-> aggregate formula or Query Table field
-> fact or summary Query Table
-> standardized landing table
-> exact Restroworks-shaped source contract
```

Visual plausibility is not acceptance.

## Local Build Validation

Run:

```powershell
python -m generator.generate_all
python scripts/build_control_tower_v2_sql.py
python scripts/build_control_tower_truth_pack.py
python -m unittest discover -s tests -v
```

Expected:

- 21 validated report contracts
- 173 exact-schema source files
- 40,775 source report rows
- 35 generator reconciliation checks passing
- 21 exact source headers: 20 current UAT contracts plus historical Vendor Report
- 69 confirmed blank/zero-only fields mirrored and excluded downstream
- 2 header-only report contracts mirrored with zero rows
- 38 active Query Tables
- Maximum Query Table dependency level 3
- 12 truth/acceptance files
- 9 truth-pack checks passing
- All unit tests passing

Review:

```text
exports/control_tower_zoho/_RECONCILIATION_RESULTS.csv
exports/control_tower_zoho/truth/CONTROL_TOWER_ACCEPTANCE_CHECKS.csv
```

Stop the build if either file contains a non-PASS row.

## Import Validation

For every landing table:

1. Compare source and Zoho row counts.
2. Confirm no rejected rows.
3. Confirm the first and last source period.
4. Confirm three outlet codes.
5. Confirm identifier fields remain text.
6. Confirm null expected-delivery dates remain null.
7. Confirm negative and zero stock values were not removed.
8. Confirm decimal values were not parsed with a comma or currency symbol.

Do not fix source exceptions manually inside Zoho. Correct the controlled source
or standardization rule and reload it.

## Query Table Validation

### Level 1

| Check | Expected |
| --- | --- |
| Standardized sales quantity | 23,319 |
| Transfer From vs Transfer To | Equal at transaction/item total |
| Closing amount bridge | Quantity x average cost reconciles within rounding |
| Expiry scenario | Query 38 rows are positive, traceable and explicitly marked demo-only; exact batch expiry remains unavailable |
| PO missing expected date | Null remains visible, not converted to a date |

### Level 2

| Check | Expected |
| --- | --- |
| Actual consumption | Reproduces opening + receipts + in - out - return - closing |
| Theoretical COGS | Uses recipe quantities and item cost |
| PO/GRN link | Outlet + PO + item |
| Menu profitability | Net sales - theoretical COGS |
| Forecast ingredient demand | Menu forecast x canonical recipe quantity |

### Level 3

| Check | Expected |
| --- | --- |
| Consumption variance | Actual - theoretical |
| OTIF denominator | Eligible closed lines only |
| Menu sales at risk | Allocated across risky ingredients; no duplicate full menu revenue |
| Risky PO count | Distinct exact PO number |
| Data quality | One row per exception with drillable reference |
| Dependency depth | Never greater than 3 |

## Synthetic Overall Truth

These totals cover all three months and all three outlets. Use the matching CSV
rows for period- or outlet-filtered checks.

### Page 1

| Metric | Expected |
| --- | ---: |
| Outlets at risk | 3 |
| Risk item rows | 221 across three monthly checkpoints |
| Menu items at risk | 110 |
| Stockout risk value | INR 976,271.72 |
| Expiry risk value | INR 628,131.99; synthetic batch-linked demo estimate |
| Open risky PO count | 53 |
| Purple item rows | 38, including expired demo tranches |

### Page 2

| Metric | Expected |
| --- | ---: |
| Ordered gross purchase value | INR 4,732,795.81 |
| Received purchase value | INR 3,733,632.47 |
| Closing inventory value | INR 7,191,795.45 |
| Open PO liability | INR 511,128.17 |
| PO fill rate | 83.2529% |
| Vendor OTIF | 51.6704% |
| Vendor return rate | Unavailable |
| Observed wastage value | INR 6,747.33 |
| Expiry exposure | INR 628,131.99; synthetic batch-linked demo estimate |
| Wastage plus expiry demo scenario | INR 634,879.32 |

### Page 3

| Metric | Expected |
| --- | ---: |
| Net sales | INR 6,027,041.45 |
| Quantity sold | 23,319 |
| Theoretical COGS | INR 1,083,602.04 |
| Consumption leakage value | INR 59,388.51 |
| Menu gross margin | INR 4,943,439.41 |
| Menu gross margin % | 82.0210% |

### Page 4 Data Quality

| Exception | Expected |
| --- | ---: |
| Negative stock | 1 |
| Zero stock with demand | 2 |
| Sold item missing recipe | 0 |
| Operational item missing master | 0 |
| UOM mismatch without conversion | 0 |
| Open PO missing expected delivery | 3 |

Exact expiry and vendor-return metrics remain unavailable for actual ABNAH
data. The synthetic expiry scenario must remain labelled; synthetic OTIF
remains a formula test and is not an ABNAH actual-data result.

## Dashboard Acceptance Procedure

For each saved report:

1. Set period to `month_01` and outlet to `OUT001`.
2. Read the matching row in the relevant `PAGE*_Truth.csv`.
3. Compare every KPI.
4. Repeat for all nine outlet-month combinations.
5. Compare each all-outlet month.
6. Compare each all-period outlet.
7. Compare the overall row.
8. Open underlying data for at least one non-zero exception.
9. Export the report and confirm displayed and exported totals agree.

Use a currency tolerance of INR 0.05 and quantity tolerance of 0.001 unless a
source contract specifies a tighter rule.

## Ratio Validation

Ratios must be recalculated from their aggregate components.

Correct:

```text
sum(received_qty) / sum(ordered_qty)
sum(otif_success_flag) / sum(eligible_closed_line_flag)
sum(gross_margin_value) / sum(net_sales)
```

Incorrect:

```text
sum(row_fill_rate)
average(row_margin_percent) without weighting
OTIF success count / all PO lines
```

Zoho aggregate formula behavior:
https://www.zoho.com/analytics/help/analyze-data/aggregate-formula.html

## Filter Validation

Test the two dashboard-global filters:

- Source period
- Outlet

Then test page filters independently: region/new-matured, category, vendor,
PO status, risk type, severity, action owner, menu item, ingredient, UOM and
exception type.

For each global filter:

1. Apply one value.
2. Confirm every relevant component changes.
3. Confirm unrelated page-specific reports do not error.
4. Clear the filter.
5. Confirm the full synthetic truth returns.

Zoho dashboard filter guidance:
https://www.zoho.com/analytics/help/dashboard/filter.html

## Visual Validation

- No title contains yield.
- Purple, red, amber, green and grey mean the same thing on every page.
- Every expiry report says `Synthetic estimate - no POSIST batch/expiry
  source`; no actual-data view presents the scenario as truth.
- Page 4 high values are not automatically red.
- Table text is not clipped at the target presentation resolution.
- Counts display no decimals.
- INR values use one consistent scale.
- The map resolves every approved outlet.
- Every action row has owner and due band.
- Every data-quality tile drills to exact records.
- Report filters remain usable on all four tabs.

## Production Publication Gates

Do not publish the named KPI until its gate is satisfied:

| KPI area | Gate |
| --- | --- |
| Stockout risk | Approved forecast, recipe, UOM, stock and valid inbound coverage |
| Exact expiry risk | Keep unavailable until batch/expiry evidence is enabled; synthetic demo estimate remains non-production |
| OTIF | Exact PO-line/GRN link, expected date, closed-line rule and tolerance |
| Overdue PO | Populated expected date and normalized open status |
| Purchase price movement | Comparable UOM and approved price basis |
| Consumption variance | Physical stock checkpoint and complete movement coverage |
| Menu gross margin | Effective recipe date and approved ingredient cost basis |
| Working capital | Approved interpretation of inventory plus PO commitment |

## ABNAH PO Production Gate

The latest Enterprise Purchase Order export is populated and matches its
27-column contract. Validate it as follows:

- Reconcile every eligible PO line to Enterprise Entry/GRN evidence.
- Confirm open, partial and closed status semantics.
- Confirm expected-delivery coverage and the OTIF tolerance rule.
- Keep OTIF and overdue-PO components hidden or visibly draft until these checks
  pass.
- Treat Purchase Detail as sparse fallback evidence, not the PO authority.

The remaining limitation is linkage and business semantics, not an empty schema.

## Sign-Off Record

For each KPI record:

```text
KPI name
business owner
formula version
source reports/APIs
source completeness
threshold version
truth comparison result
known caveats
approval date
approver
publication status
```

Do not replace the truth files when ABNAH data arrives. Create a separate
controlled reconciliation result for the production load.
