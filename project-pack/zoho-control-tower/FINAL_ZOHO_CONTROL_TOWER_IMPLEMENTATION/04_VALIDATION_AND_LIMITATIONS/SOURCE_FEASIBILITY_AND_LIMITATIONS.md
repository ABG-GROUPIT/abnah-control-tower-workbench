# ABNAH Control Tower Source Feasibility Gate

## Decision

There is no captured POSIST report named `Raw Material Item Detail`. That label
was an internal planning assumption and must not be requested from ABNAH or
shown as an available report.

The active model derives its item reference from exact, captured reports:

- `Closing Stock Report`
- `Enterprise Entry Report - Stock Entry`
- `Enterprise Purchase Order Report - item detail`
- `Item Recipe Report`

These reports support item identifiers, names, categories, UOM, observed cost,
stock, vendor and recipe relationships. They do not prove shelf life, reorder
level, standard order quantity, item criticality, active status, or an approved
primary/alternate-vendor relationship.

## Confirmed Unavailable Inputs

| Requested input | Current state | Model treatment |
| --- | --- | --- |
| Expiry Report | Module is not enabled | Exact production expiry remains unavailable; the synthetic demonstrator uses a visibly labelled scenario estimate only |
| Enterprise Stock Re-Order | Header-only/unavailable | No source reorder or minimum-order level is used |
| Enterprise Stock Return | Header-only/unavailable | Vendor return rate and vendor-return leakage remain unavailable |
| Outlet Master | No production export supplied | Keep operational outlet identity; use the three-row synthetic geography only for the demonstrator map |
| Raw Material Item Detail | Not a verified POSIST report | Remove the name and use the composite item reference above |
| Vendor Report | Historical ABNAH export and exact 16-column contract available | Use as the vendor identity master only after local structural repair; retain PO/Entry-only names as exceptions |

## Vendor Report Quality Gate

The exact source name is `Vendor Report`. It supports vendor name/code,
description, contact and compliance fields, validity dates, state and address.
The earlier ABNAH export also documented structural risks that must be repaired
locally before Zoho import:

- multiple phone-number cells shifting the columns that follow;
- long addresses continuing onto a second physical row;
- unquoted commas or overflow text creating too many cells;
- invalid or malformed GSTIN, PAN, FSSAI and email values.

The report does not prove default lead time, SLA, active-status semantics, or
approved vendor-item/category mapping. Those attributes remain null unless an
exact additional source is validated.

## Exact Surrounding Reports

If more evidence is available, request only these exact POSIST report names:

| Exact report name | Potential use | Current evidence state |
| --- | --- | --- |
| `Kitchen Wise Item Report` | Item-to-store and UOM context | Name catalogued; CSV schema not captured |
| `Default Cost Report` | Default item cost context | Name catalogued; CSV schema not captured |
| `Vendor Pricing Report` | Vendor-item price comparison | Name catalogued; CSV schema not captured |
| `ERP Vendor Price` | Vendor-item-UOM price mapping | Headers captured; downloaded CSV contract not validated |
| `Re-Order Level` | Possible alternative to Enterprise ReOrder | Name catalogued; CSV schema not captured |
| `Late Delivery Report` | Possible delivery-performance validation | Name catalogued; CSV schema not captured |
| `Bulk Return Report` | Item-level internal return quantity | Already captured; no vendor value linkage |

No field is assumed from these reports until a populated CSV is captured.

## KPI Feasibility

The 35 requested KPI definitions now fall into four groups:

| State | Count | Treatment |
| --- | ---: | --- |
| Supported or transparently model-derived | 29 | Build in the synthetic dashboard |
| Provisional business interpretation | 1 | PO Fill Rate from processed versus ordered quantity; label provisional |
| Partial | 1 | Show `Observed Wastage Value`, not full Financial Leakage |
| Unavailable | 4 | Expiry Risk, Vendor OTIF, Lead-Time Deviation and Vendor Return Rate |

Vendor OTIF and lead-time deviation can still be demonstrated as formula
prototypes on synthetic linked PO/GRN rows, but they are not publishable for
ABNAH actual data while Enterprise Entry contains PO number on only 2 of 562
audited rows.

## Visual Gates

- In the synthetic demonstrator, show expiry only as `Demo estimate - no POSIST
  batch/expiry source`. In an actual-data view, hide the metric until the
  module or equivalent evidence is available.
- Replace expiry-inclusive Financial Leakage with observed wastage value.
- The synthetic three-outlet map is allowed only with its scenario label.
  Replace it with approved outlet geography before production.
- Do not show approved alternate-vendor recommendations until an exact
  vendor-item approval mapping is supplied. `Vendor Report` alone is not that
  mapping.
- Show projected shortage and days cover from Closing Stock, demand, recipe and
  valid open PO fields. Do not label them `below reorder level`.
- Keep vendor return rate absent rather than displaying zero.
- Keep OTIF and lead-time visuals marked `formula demo / production blocked`
  until PO-to-GRN linkage is materially populated.

## Synthetic Build Gate

The source-shaped synthetic CSVs are complete and pass exact-header and
cross-report reconciliation tests. The active Zoho SQL pack deliberately does
not depend on:

- `AUX_Item_Master`
- `AUX_Vendor_Master`
- `Enterprise Stock Re-Order`
- `Enterprise Stock Return`

`AUX_Menu_Demand_Forecast` and `AUX_Theoretical_Consumption` are model outputs.
`AUX_Outlet_Master` and `AUX_Expiry_Estimate` are active only as visibly
synthetic demonstrator references. The latter is derived from closing stock,
theoretical demand and category shelf-life assumptions and cannot be presented
as POSIST batch truth.
