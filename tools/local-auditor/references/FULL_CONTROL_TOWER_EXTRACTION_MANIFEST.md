# ABNAH Full Control Tower CSV Extraction Manifest

> Superseded for current extraction decisions. Read
> `docs/CONTROL_TOWER_SOURCE_FEASIBILITY_GATE.md`. There is no verified POSIST
> report named `Raw Material Item Detail`; Expiry is not enabled, and Enterprise
> ReOrder and Enterprise Stock Return are unavailable.

This is the production source checklist for all four approved Control Tower pages.
It deliberately separates a report screen from its required export variants. Raw
CSVs stay local and are processed only by `local_data_auditor`.

## Scope And Counts

- 19 production report screens.
- 2 reconciliation/control report screens.
- 21 distinct report screens in total.
- 1 historical ABNAH `Vendor Report` master contract outside the current UAT
  screen audit.
- 77 expected CSV exports for the five-period audit below when Standing Purchase
  Order is populated.
- 73 expected CSV exports when Standing Purchase Order is empty or unused.
- The current single outlet is derived from operational reports.

The empty `Enterprise Purchase Order` is not part of this list. Use `Purchase
Order Report`, which exposes PO status, ordered quantity, processed quantity,
remaining quantity, expected delivery, close/partial-receive date, vendor, item,
unit price and total item cost.

## Audit Periods

Use these exact five buckets for reports whose output has no row-level date or is
a period summary:

| Period | Start | End | Status |
|---|---|---|---|
| M01 | 2026-03-01 | 2026-03-31 | final month |
| M02 | 2026-04-01 | 2026-04-30 | final month |
| M03 | 2026-05-01 | 2026-05-31 | final month |
| M04 | 2026-06-01 | 2026-06-30 | final month |
| M05 | 2026-07-01 | 2026-07-21 | provisional MTD |

For reports containing a reliable row-level date, use one full-period export from
`2026-03-01` to `2026-07-21`, except where variants are listed below.

For final forecasting, re-export the two sales facts for at least 12 months if
the tenant has that history. Five months is sufficient for parser and structural
validation, but not for reliable annual seasonality.

## Global Filter Profile

Apply this profile unless a report-specific override is listed:

| Control | Required setting |
|---|---|
| Report Configuration | `FOH - in good co` |
| Brand | all ABNAH / `in good co` brands |
| Deployment | all ABNAH deployments |
| Outlet / Store / Kitchen | `Select All` |
| Vendor | `All` / `All Vendors` |
| Super Category | `Select All` |
| Category | `Select All` |
| Item | `Select All` |
| Consolidated across outlets | OFF |
| Category/vendor/section summary | OFF / `none` |
| Summary-only controls | OFF |
| Price For Report | `Average Price` |
| Export format | CSV |

Do not consolidate outlets. Outlet-level grain is required for risk, stock,
vendor and data-quality drilldowns. If a selector has no explicit `All`, leave it
blank only when the UI uses blank to mean all.

## Report Checklist

### Sales, Menu And Recipe

| # | Exact report | Required export and filter override | Files |
|---|---|---|---:|
| 01 | Gross/Net Margin Report | Full period. All sources, tabs, categories and items. Keep item/bill grain. If a bill-status selector exists, use settled/closed sales only. | 1 |
| 02 | Bill Item Detail Report | Full period. All tabs, item classifications and categories. Keep item/bill grain and do not summarize. | 1 |
| 03 | Item Recipe Report | Snapshot. All menu items and recipe items; do not filter to one item/category. | 1 |
| 04 | Recipe Consumption Report | Five monthly exports. `Select Operation = Billing`; `Recipe items Margin Summary Only = unchecked`; all deployments and stores. | 5 |

`Gross/Net Margin Report` is the primary sales and menu-profitability fact.
`Bill Item Detail Report` supplies item classification and timing detail. `Item
Recipe Report` supplies the menu-to-ingredient BOM.

### Inventory, Consumption And Data Quality

| # | Exact report | Required export and filter override | Files |
|---|---|---|---:|
| 06 | Enterprise Consumption | Five monthly exports. `ConsumptionColumn Only = OFF`; `Filter Items = none`; all super categories/categories; `Price For Report = Average Price`. | 5 |
| 07 | Enterprise Variance | Export both tabs for every month: `Variance Report` and `Master Variance Report`. Settings below. | 10 |
| 08 | Enterprise Wastage Report | Five monthly exports from `Wastage Report`, not `Master Wastage Report`; `Filter Items = none`; `Price For Report = Average Price`. | 5 |
| 09 | Enterprise Entry | One full-period CSV for each of the 12 confirmed transaction modes below; `Price For Report = Average Price`. | 12 |
| 10 | Closing Stock Report | Snapshot at 2026-03-31, 2026-04-30, 2026-05-31, 2026-06-30 and 2026-07-21. All stores/items; no summary or consolidation. | 5 |
| 11 | Enterprise Stock Re-Order | Unavailable; do not request or use. | 0 |
| 12 | Stock In Stock Out Report | Full period. All deployments/stores/items; `Price Filter = Transaction Price`; `Transaction Type = All` when available, otherwise blank/default all. | 1 |
| 13 | Expiry Report | Module not enabled; keep the KPI unavailable. | 0 |

Enterprise Variance settings:

| Tab | Setting |
|---|---|
| Variance Report | `Price For Report = Average Price`; `Filter Items = none`; `Consolidated Across Selected Outlets Data = OFF`; `Category Wise Summary = OFF`; `Show Only Kitchens Data = OFF`; omit no columns |
| Master Variance Report | `Price For Report = Average Price`; `Item Filter = All`; `Consumption Bifurcation = OFF`; `Stock In / Out Bifurcation = OFF`; `Show Only Closing Column = OFF`; leave `Select Fields For Actual Amt` empty/default |

Confirmed Enterprise Entry transaction modes, one CSV each:

1. `Stock Entry`
2. `Stock Sale`
3. `Physical Stock`
4. `Wastage`
5. `Stock Transfer From`
6. `Stock Transfer To`
7. `Processed Entry`
8. `Semi-Processed Entry`
9. `Stock Return (Wastage/Re-use)`
10. `Local Stock Return`
11. `Return from Receiver`
12. `Bulk Return`

### Procurement, Vendor And Replenishment

| # | Exact report | Required export and filter override | Files |
|---|---|---|---:|
| 14 | Purchase Order Report | Full period; all stores/vendors/items. Export each confirmed status separately: `Requested`, `Open`, `Closed`, `Unapproved`, `Rejected`, `settled prematurely`. Include any additional status shown below the captured list as another file. | 6+ |
| 15 | Standing Purchase Order Report | If populated/used, full period; all stores/vendors/items. Export `Requested`, `Open`, `Closed`, `settled prematurely` separately. | 4 |
| 16 | Purchase Detail | Use `Purchase Detail Report`, not `ABC Analysis Report`; full period; `PO Details = po_details`; `Summary By = none`; all stores/vendors/categories/items. | 1 |
| 17 | Enterprise Stock Return | Unavailable/header-only; do not publish vendor-return KPIs. | 0 |
| 18 | ERP Vendor Price | Full period; all deployments; `Status = All`; `Published = All`; `Vendor = All Vendors`. | 1 |
| 19 | Enterprise Consolidated Indent | Five monthly exports; `Date Filter = Request Date`; all super categories/categories. | 5 |

`Enterprise Purchase Order Report - item detail` is now populated and is the
current PO authority. `Enterprise Entry Report - Stock Entry` is the receipt
fact, although its PO key is sparse. Vendor return quantity, value and tax
remain unavailable while `Enterprise Stock Return` has no rows. `ERP Vendor
Price` is schema-capture evidence until its downloaded CSV contract is
validated.

### Reconciliation Controls

These do not replace the detailed facts, but they are required for a defensible
production reconciliation pass.

| # | Exact report | Required export and filter override | Files |
|---|---|---|---:|
| 20 | Enterprise Purchase Summary Report | Five monthly exports; `Select Date Type = Transaction Date`; all vendors; `Consolidated Across Selected Outlets Data = OFF`; `Vendor Wise Data = OFF`; `Vendor Wise Item Summary Data = OFF`. | 5 |
| 21 | Food Cost Report | Five monthly exports from `Item Wise cogs`; all deployments/kitchens/categories; `Price For Report = Average Price`; `Consumption = All`; no summary-only mode. | 5 |

The Food Cost output depends on a physical stock entry at the report end date.
Treat July MTD as provisional and record any month where the physical stock count
was not entered.

## Master Sources And Remaining Attributes

The historical `Vendor Report` supplies the following exact master fields after
local structural cleaning:

| Source | Available fields | Still unavailable |
|---|---|---|
| Vendor Report | Vendor name/code, description, contact/compliance fields, validity dates, state, address | Active status, lead time, SLA, vendor category, service geography, approved item/category mapping |

Do not publish an India outlet map for the current one-outlet implementation.
Vendor names observed in PO or Entry but absent from the cleaned Vendor Report
remain transaction-only coverage exceptions, not approved master records.

## File Naming

Use lowercase canonical names and preserve each mode/status/month as a separate
file:

```text
gross_net_margin__2026-03-01__2026-07-21__all.csv
recipe_consumption__billing__2026-03-01__2026-03-31__all.csv
enterprise_consumption__2026-03-01__2026-03-31__all.csv
enterprise_variance_normal__2026-03-01__2026-03-31__all.csv
enterprise_variance_master__2026-03-01__2026-03-31__all.csv
enterprise_entry__stock_entry__2026-03-01__2026-07-21__all.csv
purchase_order__open__2026-03-01__2026-07-21__all.csv
purchase_detail__po_details__2026-03-01__2026-07-21__all.csv
closing_stock__snapshot__2026-03-31__all.csv
enterprise_reorder__snapshot__2026-07-21__all.csv
expiry__as_of__2026-07-21__all.csv
```

Use the exact outlet code instead of `all` only when the UI cannot export all
outlets together. Never merge manually exported outlet files before auditing.

## Recommended Extraction Order

1. Finish all 12 `Enterprise Entry` modes.
2. Export `Purchase Order Report` by status, then `Purchase Detail` with
   `po_details`.
3. Export `ERP Vendor Price` and `Enterprise Consolidated Indent` only when
   their populated CSVs are available.
4. Export monthly `Enterprise Consumption`, both `Enterprise Variance` tabs and
   `Enterprise Wastage Report`.
5. Export Closing Stock and Stock In Stock Out. Do not request unavailable
   reorder, expiry or invented raw-material-master reports.
6. Export sales, bill item, recipe and recipe-consumption facts.
7. Finish the two reconciliation controls and the two non-report masters.

After the first populated file for a report passes locally, add the remaining
months/modes. Do not wait for all 77 files before testing the parser.
