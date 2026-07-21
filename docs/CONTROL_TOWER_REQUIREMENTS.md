# Control Tower Requirements

## Status

ABNAH business requirements have been received and translated into a versioned, screenshot-free contract at `schema-pack/source/control_tower/control-tower-requirements.json`.

All 35 KPI definitions are `draft`. The business calculation intent is known, but no report/API source relationship is selected until the remaining schemas and ABNAH UAT payloads prove the required identifiers, grain, and coverage.

The supplied HTML is a presentation reference with synthetic values. It is not a data or formula authority. The requirements workbook is the current business-rule authority.

## Four Pages

| Page | Name | Decision purpose |
| --- | --- | --- |
| 1 | Risk Action Center | Tell operations and procurement what requires action now, why, where, by when, and by whom. |
| 2 | Procurement, Vendor & Capital Control | Show locked capital, pending and delayed POs, vendor delivery performance, returns, and normalized price movement. |
| 3 | Consumption Variance & Menu Profitability | Compare theoretical and actual ingredient consumption, value positive leakage, and relate recipe COGS to menu margin. |
| 4 | SCM Descriptive Explorer & Data Quality | Provide governed drilldowns, exports, trend, and traceable data-quality exceptions. |

Use **consumption**, not **yield**, throughout Page 3. A Restroworks report named `Yield Report` keeps its source name in discovery, but it is not evidence for Page 3 until its schema proves relevant.

## Core Formulas

```text
required_qty = forecast_menu_qty * normalized_recipe_qty_per_menu_unit

available_qty = current_stock_qty + valid_open_po_qty

shortage_qty = max(0, required_qty_with_safety - available_qty)

days_cover = available_qty / normalized_daily_consumption_qty

open_po_liability = remaining_qty_canonical * normalized_unit_price

po_fill_rate = processed_or_accepted_qty / ordered_qty

vendor_otif = on_time_and_in_full_closed_po_lines / eligible_closed_po_lines

theoretical_consumption_qty = sum(sold_menu_qty * normalized_recipe_qty_per_menu_unit)

actual_consumption_qty = opening + grn + transfer_in - transfer_out - returns - closing

consumption_variance_qty = actual_consumption_qty - theoretical_consumption_qty

consumption_leakage_value = max(0, consumption_variance_qty) * normalized_average_unit_cost

theoretical_cogs = sum(sold_menu_qty * normalized_recipe_qty_per_unit * normalized_average_ingredient_cost)

menu_gross_margin = net_sales - theoretical_cogs
```

When transfer data is unavailable, actual consumption may temporarily use `previous closing + entry - current closing`, but that output must display reduced source completeness. Month-to-date variance is provisional without a physical stock count; month-end stock count is the reliable checkpoint.

## Page 1 RAG

| Color | Meaning | Rule intent |
| --- | --- | --- |
| Purple | Active stockout with menu impact | Stock is zero/negative, forecast demand is positive, and at least one dependent menu item exists. |
| Red | High risk | Days cover is below lead time, shortage is positive, expiry exposure is high, or a critical PO vendor has OTIF below 95%. |
| Amber | Warning | Cover is within the lead-time safety band, a pending PO has an amber vendor, or expiry exposure is moderate. |
| Green | Healthy | Available quantity covers demand plus safety and no expiry/vendor issue exists. |
| Grey | No data or not applicable | Recipe, stock, outlet, active SKU, or active outlet evidence is missing. |

Thresholds beyond the explicit 95% OTIF requirement remain configurable until business sign-off.

## Guardrails

- UOM normalization is a publication gate for quantity, consumption, COGS, and price comparison.
- OTIF cannot use the current approximate vendor-item-date PO/receipt match. It requires defensible PO-line-to-GRN linkage.
- Expiry risk is exact only with batch or expiry evidence. FIFO plus shelf life must be labeled estimated.
- A weighted vendor criticality score remains deferred until business owners approve weights.
- Standing PO analytics remain separate and hidden unless standing and release identifiers exist.
- Physical ingredient variance cannot be allocated exactly to individual menu items from stock alone.
- High inventory value is descriptive, not automatically bad.
- Every data-quality tile must drill to the exact exception rows and unresolved identifiers.

## Publication Gates

1. Capture and compare exact source headers and grain.
2. Test CSV import structure and types.
3. Build synthetic rows with the same schema and no client data.
4. Reconcile RAW totals against controlled Restroworks exports.
5. Validate UOM, identity, dates, statuses, and PO-to-GRN linkage.
6. Implement KPI query tables as draft.
7. Reconcile each KPI against controlled examples and source totals.
8. Publish only after formula, owner, threshold, source coverage, and caveats are approved.
