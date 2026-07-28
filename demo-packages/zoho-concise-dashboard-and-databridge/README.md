# ABNAH Concise Dashboard and DataBridge Demo

This package is an isolated, time-boxed demonstration layer. It does not replace,
rename, or modify:

- the existing 38 Query Tables;
- either current Zoho dashboard;
- the GitHub Pages control-tower portal;
- any current raw or normalized table.

## What This Package Adds

| Area | Deliverable |
|---|---|
| Page 1 visual sample | Three concise Query Tables for action, menu impact, and estimated expiry |
| Page 2 visual sample | Three concise Query Tables for PO control, vendor control, and price movement |
| Filter correction | One explicit set of merged dashboard filters per page; no report-specific user filters |
| Wide-table correction | Six tabular views with only 7-8 visible business columns |
| Conditional formatting | Exact status columns and a compact color rulebook |
| DataBridge demonstration | Three weekly delta workbooks plus three cumulative refresh workbooks |

## Start Here

1. Open [dashboard-demo/ZOHO_CLICK_BY_CLICK.md](dashboard-demo/ZOHO_CLICK_BY_CLICK.md).
2. Create only the six Query Tables listed in
   [dashboard-demo/QUERY_MANIFEST.csv](dashboard-demo/QUERY_MANIFEST.csv).
3. Build the two new sample dashboard tabs exactly as documented.
4. Keep **Auto Add User Filters** off and **Show Report Specific User Filter**
   off.
5. For the ingestion demonstration, open
   [data-bridge-demo/README.md](data-bridge-demo/README.md).

## Architecture

```text
Existing raw and AUX inputs
        |
        +-- Existing standard/fact tables 05, 07, 22, 23, 24, 26
        |         |
        |         +-- Existing Queries 27-31 and 38 (untouched)
        |         |
        |         +-- D01-D06 concise demo tables (new, parallel)
        |
        +-- DataBridge live-drop workbook (separate ingestion demonstration)
```

The six demo Query Tables reuse validated lower-layer logic so their values
remain traceable. They do not become production dependencies and no lookup
relationship is required for this sample.

## Filter Contract

The filter helper columns are intentionally named identically within each page.
This lets Zoho manually merge the relevant columns into one dashboard control.

| Page | Shared helper columns |
|---|---|
| P1 | `filter_date`, `filter_outlet`, `filter_category`, `filter_severity` |
| P2 | `filter_date`, `filter_outlet`, `filter_vendor`, `filter_category` |

These helper columns remain in each Query Table but are hidden from the visible
tabular reports.

## Rollback

Delete only the six `D01`-`D06` Query Tables and the sample dashboards. No
existing object needs to be resaved or rebuilt.
