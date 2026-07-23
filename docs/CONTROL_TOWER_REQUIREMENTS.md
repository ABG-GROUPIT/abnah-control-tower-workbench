# Control Tower Requirements

## Status

ABNAH business requirements have been received and translated into a versioned, screenshot-free contract at `schema-pack/source/control_tower/control-tower-requirements.json`.

The 35 KPI definitions remain the business contract. Current source feasibility is 29 supported or transparently model-derived, one provisional (`PO Fill Rate`), one partial (`Observed Wastage Leakage`), and four unavailable (`Expiry Risk`, `Vendor OTIF`, `Lead-Time Deviation`, and `Vendor Return Rate`).

The supplied HTML is a presentation reference with synthetic values. It is not a data or formula authority. The requirements workbook is the current business-rule authority.

## Four Pages

| Page | Name | Decision purpose |
| --- | --- | --- |
| 1 | Risk Action Center | Tell operations and procurement what requires action now from projected shortage, menu impact, and open-PO evidence. |
| 2 | Procurement, Vendor & Capital Control | Show locked capital, pending and delayed POs, provisional fill, observed vendors, and normalized price movement. |
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
| Red | High projected shortage | Forecast requirement exceeds current stock plus valid open PO quantity. |
| Amber | Safety-stock pressure | Forecast requirement multiplied by the approved safety factor exceeds current stock plus valid open PO quantity. |
| Green | Covered | Available stock and valid inbound cover forecast demand plus safety. |
| Grey | No data or not applicable | Recipe, stock, outlet mapping, or item identity evidence is missing. |

Safety factors and forecast horizons remain configurable until business sign-off. OTIF is a formula demo only and is not part of active RAG until deterministic PO-to-receipt linkage exists.

## Guardrails

- UOM normalization is a publication gate for quantity, consumption, COGS, and price comparison.
- OTIF cannot use the current approximate vendor-item-date PO/receipt match. It requires defensible PO-line-to-GRN linkage.
- `Expiry Report` is not enabled for ABNAH. Expiry must display `Unavailable`, not zero or an unapproved estimate.
- `Enterprise Stock Return` and `Enterprise Stock Re-Order` are not populated sources. Vendor return rate is unavailable, and projected shortage must not be called a POSIST reorder breach.
- There is no captured POSIST report named `Raw Material Item Detail`. Derive the POC item reference from exact operational reports and leave unsupported master attributes null.
- ABNAH currently has one outlet in scope. Derive its identity from operational rows and do not publish a geographic outlet map.
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
