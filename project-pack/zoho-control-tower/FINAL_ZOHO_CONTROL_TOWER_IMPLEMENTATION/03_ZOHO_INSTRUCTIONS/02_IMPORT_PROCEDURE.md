# Zoho Control Tower v2 - Import Procedure

## Import Policy

Use the normalized landing files for model construction. Keep the exact-header
files as local fidelity evidence.

```text
Use in Zoho: exports/control_tower_zoho/normalized/RAWN_CT_*.csv
Keep local:  exports/control_tower_zoho/RAW_CT_*.csv
```

The normalized files preserve every validated source field and add:

- `source_period_code`
- `source_outlet_code`
- `source_outlet_name`
- `source_period_start`
- `source_period_end`

## Minimum First Import

The current Zoho workspace already contains these ten populated files with
Zoho's `-Copy` suffix. Keep those names; the SQL pack targets them directly.

| File | Zoho table |
| --- | --- |
| `RAWN_CT_vendor_report.csv` | `RAWN_CT_vendor_report-Copy` |
| `RAWN_CT_gross_net_margin.csv` | `RAWN_CT_gross_net_margin-Copy` |
| `RAWN_CT_item_recipe_report.csv` | `RAWN_CT_item_recipe_report-Copy` |
| `RAWN_CT_enterprise_variance_normal.csv` | `RAWN_CT_enterprise_variance_normal-Copy` |
| `RAWN_CT_closing_stock.csv` | `RAWN_CT_closing_stock-Copy` |
| `RAWN_CT_enterprise_purchase_order.csv` | `RAWN_CT_enterprise_purchase_order-Copy` |
| `RAWN_CT_enterprise_entry.csv` | `RAWN_CT_enterprise_entry-Copy` |
| `RAWN_CT_enterprise_transfer_from.csv` | `RAWN_CT_enterprise_transfer_from-Copy` |
| `RAWN_CT_enterprise_transfer_to.csv` | `RAWN_CT_enterprise_transfer_to-Copy` |
| `RAWN_CT_enterprise_wastage_normal.csv` | `RAWN_CT_enterprise_wastage_normal-Copy` |

`RAWN_CT_enterprise_stock_return.csv` is retained as an exact header contract,
but it has no rows in the audited UAT evidence or synthetic mirror. Do not make
it an active landing dependency or publish return-rate measures until a
populated export passes the local audit.

Import these four supporting model-output/reference tables:

| File | Zoho table |
| --- | --- |
| `AUX_Menu_Demand_Forecast.csv` | `AUX_Menu_Demand_Forecast-Copy` |
| `AUX_Theoretical_Consumption.csv` | `AUX_Theoretical_Consumption-Copy` |
| `AUX_Outlet_Master.csv` | `AUX_Outlet_Master-Copy` |
| `AUX_Expiry_Estimate.csv` | `AUX_Expiry_Estimate-Copy` |

The outlet and expiry AUX files are demonstrator references, not Restroworks
exports:

- `AUX_Outlet_Master` contains the same three synthetic outlet keys used by all
  12 existing files, plus demo geography and maturity attributes. It remains
  packaged as transferable reference evidence; current Query 37 derives outlet
  identity from Query 13 and embeds the same visibly synthetic map attributes,
  so Query 37 does not depend on this imported table.
- `AUX_Expiry_Estimate` derives one near-expiry FIFO tranche per qualifying
  period/outlet/item. It links to a synthetic receipt batch and GRN where a
  usable receipt exists; otherwise it uses an explicitly marked synthetic
  opening tranche. Quantity is bounded by Closing Stock and expected
  consumption is deducted before the assumed expiry date. It is not a complete
  batch ledger and must retain its `production_use_status` field.

If `AUX_Expiry_Estimate-Copy` was imported from an earlier package, replace its
data instead of appending. The corrected demonstrator file has 206 rows and 39
columns: 79 rows carry synthetic receipt/GRN/PO/vendor lineage and 127 are
explicitly labelled synthetic opening-stock fallback tranches. After replacing
the import, replace and save Query 38 from the current SQL package. Query 27 no
longer reads this AUX table. Replace Query 27 separately only if the workspace
still has the older combined-risk version or its SQL fails to parse. No other
Query Table needs to be re-saved for either correction.

The current Query 38 does not cast source columns. During import, verify Zoho
recognizes the date columns as dates and quantity, value, coordinate, day-count
and flag columns as numeric. The Query Table intentionally preserves those
imported types to avoid parser-specific cast failures.

Do not import `AUX_Item_Master` or `AUX_Vendor_Master`. Item identity remains
derived from operational landings and vendor identity remains anchored to the
quality-gated historical `Vendor Report`.

Before importing `RAWN_CT_vendor_report`, run the local cleaner and reject the
file if phone overflow, address continuation, extra cells, or malformed
compliance identifiers remain unresolved. The cleaned report supports vendor
identity and compliance context only; it does not supply lead time, SLA, or
approved vendor-item mapping.

## Optional Reconciliation Imports

Import these only when testing source agreement or a fallback:

- `RAWN_CT_bill_item_detail`
- `RAWN_CT_purchase_detail`
- `RAWN_CT_recipe_consumption`
- `RAWN_CT_enterprise_consumption_detail`
- `RAWN_CT_enterprise_opening`
- `RAWN_CT_enterprise_physical`
- `RAWN_CT_enterprise_reorder`
- `RAWN_CT_enterprise_variance_master`
- `RAWN_CT_bulk_return`
- `RAWN_CT_stock_in_stock_out`

Do not use the three `SCHEMA_CAPTURE_CT_*` files as production authorities.
Their UI schemas are captured, but their exact downloaded CSV contracts have not
been validated.

## Browser Import Steps

For each file:

1. Open the target Zoho Analytics workspace.
2. Click **Create**.
3. Click **New Table / Import Data**.
4. Select **Files & Feeds**.
5. Select **Local Drive**.
6. Choose the CSV file.
7. Set **Table Name** to the exact `-Copy` name shown above.
8. Confirm **First row contains column names** is enabled.
9. Set encoding to UTF-8 when prompted.
10. Set date format to `yyyy-MM-dd` for ISO date columns.
11. In the preview, verify all identifier fields are text.
12. Verify quantities, rates, percentages and amounts are numeric.
13. For import errors, choose **Don't import the data** during the controlled
    build. Do not convert malformed production values silently.
14. Click **Create**.
15. Open the imported table and record imported row count.

Zoho supports direct file imports up to the current file and row limits
documented here:
https://www.zoho.com/analytics/help/import-data/files-feeds.html

Use Databridge for larger or regularly refreshed local files:
https://www.zoho.com/analytics/help/import-data/csv.html

## Required Type Checks

### Text

- Outlet, item, menu, vendor, PO, PR, GRN, invoice and batch identifiers
- Status
- UOM
- Category and super-category
- Source period code

### Date

- Sales date
- PO date
- Expected delivery date
- Receipt/entry date
- Opening and closing date
- Transfer, wastage and return date
- Forecast date
- Expiry estimate date and as-of date

### Decimal

- All quantities
- Unit price, average price and rate
- Subtotal, discount, tax, total and margin values

Do not import item codes such as `ING001` as numbers. Do not import PO or invoice
identifiers in a type that drops leading zeroes.

## Row-Count Checkpoint

Use `_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv` to compare expected row counts
for the 14 active files. `_CONTROL_TOWER_IMPORT_MANIFEST.csv` is the complete
evidence inventory and contains files that must not be imported into v2.
For the current pack:

- Validated source report rows: 40,775
- Validated source contracts: 21
- Core landing tables used by SQL: 10
- Supporting model-output/reference tables: 4
- Synthetic outlet reference rows: 3
- Synthetic expiry scenario rows: 206
- Receipt/GRN-linked scenario rows: 79
- Explicit synthetic opening-tranche rows: 127

After each import, record:

```text
table name
source filename
source row count
Zoho imported row count
rejected row count
import timestamp
```

Do not build or revise the dependent Query Tables until all fourteen required
tables exist with exact
names and zero unexplained rejected rows.
