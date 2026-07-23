# Vendor Last 5 Purchase Price - Source Assessment

## Decision

`Vendor Last 5 Purchase Price` is useful as an optional vendor-item price
reconciliation source. It is not required in the active 14-table Control Tower
v2 import and does not replace `Vendor Report`, Purchase Order or Entry.

Keep it inactive until its exact CSV contract is added to the local audit
engine and a stable row key or export-overlap rule is approved.

## Captured Shape

Three local exports were assessed without adding operational rows to GitHub:

- 464 rows across the three files;
- 281 unique transaction-shaped rows after recognizing cross-file overlap;
- 228 distinct items;
- 40 distinct vendors;
- 17 named columns plus a trailing empty CSV field;
- 16 headers containing trailing spaces.

The named fields are:

```text
S.NO
Item Name
Item Code
Super Category Name
Category Name
Purchase Date
Vendor
Quantity
Unit
Unit Price
Sub Total
Discount
CGST Tax
SGST Tax
IGST Tax
Non GST Tax
Total
```

## Verified Behavior

- No blank item or vendor values were observed.
- No non-positive quantity or unit-price values were observed.
- No negative totals were observed.
- `Sub Total = Quantity x Unit Price` reconciled for all rows.
- One material total bridge difference of INR 12.86 recurred in overlapping
  files and requires source-owner interpretation.
- One INR 0.03 difference is consistent with rounding.
- Only one item was observed across multiple vendors.
- Six items appeared in multiple UOMs.
- Five items had multiple raw prices.
- The maximum observed unique purchase shapes per item was three, despite the
  report title referring to the last five purchases.
- Among 31 comparable item/vendor/UOM series, no actual unit-price change was
  observed in the captured sample.

## Supported Uses

After normalization and overlap control, the report can support:

- last observed paid unit price;
- observed vendor-item relationships;
- same-item, same-vendor and same-UOM price comparison;
- reconciliation against Entry receipt price;
- exception checks for UOM changes and total bridges.

## Unsupported Uses

The report does not establish:

- approved primary or alternate vendor mappings;
- vendor SLA, promised lead time or actual OTIF;
- pending purchase orders;
- receipt completeness;
- vendor returns;
- outlet-specific vendor authorization;
- a stable transaction-line identifier.

## Future Model Position

If activated, use:

```text
Vendor Last 5 Purchase Price CSV
-> RAWN_CT_vendor_last_purchase_price
-> STD_CT_Vendor_Item_Price
-> optional price-movement reconciliation
```

Do not make it the sole source for Page 2 price movement. The current active
model calculates price movement from accepted Purchase Receipt lines because
those rows retain outlet, period and receipt context.
