# CODEX Downloads Screenshot Sample Observations

Sample folder reviewed:

```text
C:\Users\ARNAV\Downloads\CODEX
```

Review date: 2026-07-13

This was a structure/design review only. The screenshots were not run through the OCR scraper.

## What The Sample Contains

The sample has 30 PNG screenshots inside:

```text
CODEX/
  Example Report Schema/
  Main page 1 Posist/
  Reports Page Posist/
```

Observed screenshot types:

| Type | Example | Use |
|---|---|---|
| POSist page/menu screenshot | Main report page with section list | Defines top-level page and section hierarchy. |
| Section expanded screenshot | Sales Reports, Audit Reports, Tax Analysis Reports | Defines report folders inside each section. |
| Report filter/schema screenshot | Hourly Sales By Category | Defines filters, grain, table headers, scroll behavior, and export options. |
| Horizontal-scroll table part | Tax Summary/report table continuation | Shows that wide reports need multiple ordered screenshots. |

## Structure Decision

Use this hierarchy:

```text
POSist page -> report section -> individual report -> screenshot slot
```

Two main POSist pages were observed:

1. `p1_main`
2. `p2_reports`

The current sample also includes:

3. `p3_examples`

Each report folder has slots for:

```text
01_filters
02_headers
03_hscroll
04_vscroll
05_exports
06_notes
```

## Important Capture Insight

Some reports expose hidden schema through scroll behavior. For example, the sample `Hourly Sales By Category` report uses an hourly time bucket in `OPEN TIME`, and other reports have wide table headers that require horizontal scrolling. These details affect the eventual data model grain, so screenshots must preserve:

- selected filters,
- date range,
- outlet/deployment,
- report title,
- table headers,
- scroll direction/order,
- export availability.

## Processing Rule

Do not process every report equally. First prioritize reports/API-backed data that improve:

1. Inventory and consumption intelligence.
2. Vendor and procurement analytics.
3. Sales and revenue only where it supports consumption forecasting, validation, or menu intelligence.

Before SQL changes, compare every high-value report against the Restroworks API docs packet:

```text
source_intake/posist_uat/restroworks_api_docs_packet/
```
