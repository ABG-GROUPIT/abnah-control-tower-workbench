# Data Dictionary

## Neon Schemas

`raw`: report-facing synthetic ABNAH-style raw tables.

`control`: loader tracking only.

No `analytics` schema is created in this build.

## Raw Tables

`raw.vendor_report`: synthetic vendor master with clean vendor names, single contact numbers, optional compliance fields, and about 70 vendors. Primary key: `row_id`.

`raw.menu_master`: sellable cafe menu items with flattened variants, realistic premium cafe pricing, 1/0 flags for `non_veg` and `has_variant`, and realistic missing descriptions/aliases/HSN values. Primary key: `row_id`.

`raw.brand_recipe_consumption`: ABNAH-style BOM export. The recipe/menu item fields are populated only on the first ingredient row of each recipe block; continuation rows leave `recipe_name`, `recipe_qty`, and `recipe_unit` blank. Primary key: `row_id`.

`raw.sales_report`: ABNAH-style daily outlet-item sales with positive quantity and positive net sale only. Loaded from outlet-wise monthly CSV files.

`raw.purchase_report`: PO-style procurement data with processed and remaining quantities driven by PO status. Loaded from outlet-wise monthly CSV files.

`raw.entry_report`: receipt/GRN-style entries derived from processed purchase quantities, with occasional returns. Loaded from outlet-wise monthly CSV files.

`raw.inventory_closing_report`: daily closing stock for key ingredients/materials. `store_stock_qty` maps to the observed stock column concept in the source report. Loaded from outlet-wise monthly CSV files.

`raw.indian_calendar_holidays`: configurable synthetic holiday/calendar markers for Jan-Mar 2026.

`raw.manual_calendar_events`: admin/manual event layer for business explanations of sales spikes.

`raw.competitor_pricing`: contextual competitor menu and price mapping by Delhi market area.

## Control Table

`control.etl_load_batch` records loaded months and row counts. Incremental month loaders check this table before loading.

`control.loaded_row_registry` stores `month_code`, `table_name`, and `row_id` for operational rows. This is how Month 2 and Month 3 rows can be deleted without adding `month_code` to raw reports.

## Synthetic Data Period

- `month_01`: 2026-01-01 to 2026-01-31
- `month_02`: 2026-02-01 to 2026-02-28
- `month_03`: 2026-03-01 to 2026-03-31
