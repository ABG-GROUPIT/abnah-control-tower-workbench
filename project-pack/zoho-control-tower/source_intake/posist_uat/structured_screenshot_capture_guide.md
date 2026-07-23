# Structured Screenshot Capture Guide

This guide is for ABNAH POSist UAT screenshots. It is designed for Codex schema discovery, not for the end product.

## Where To Dump Screenshots

Run this from the project root:

```powershell
python scripts\setup_posist_screenshot_structure.py
```

Then dump screenshots under:

```text
source_intake/posist_uat/_incoming_drop/posist_ss/
```

The folder structure follows:

```text
POSist page -> report section -> individual report -> screenshot slot
```

Current top-level pages:

1. `p1_main`
2. `p2_reports`
3. `p3_examples`
4. `p4_stock_admin`

`p4_stock_admin` is for the separate POSist Stock Administration area. Use it for BOH/raw-report screenshots such as Enterprise Reports, Transactional Reports, PO/SO Reports, Indent Reports, Aggregation Reports, Analytical Reports, Other Reports, Summary, Bill Passing, Catering, and item-master/detail screens.

## Screenshot Slots Per Report

Each report folder has these slots:

| Slot | Use |
|---|---|
| `01_filters` | Report title, selected filters, outlet/deployment, date range, generate/export buttons. |
| `02_headers` | First table view with column headers and visible grain. |
| `03_hscroll` | Left-to-right screenshots when a report table has horizontal scrolling. |
| `04_vscroll` | Top-to-bottom screenshots when a report has vertical scrolling or pagination. |
| `05_exports` | CSV, XLS, PDF, or downloaded report exports. |
| `06_notes` | Short notes about configuration, missing data, odd filters, API hints, or report behavior. |

## Capture Rules

1. Capture the section menu once per section and put it in `00_section_menu_screenshots`.
2. For each configured report, capture the filter panel before clicking `Generate Report`.
3. Capture table headers clearly. If columns are cut off, use horizontal scroll screenshots in order.
4. If rows continue below the screen, use vertical scroll screenshots in order.
5. If export is available, save it in `05_exports` as supporting evidence. Screenshots remain the primary intake source for this workflow.
6. If a report is not configured or not useful, do not spend time capturing every table. Mark it in `00_REPORT_STATUS.csv`.
7. Avoid credentials, tokens, customer personal data, and payment details where possible.

## Naming Convention

Use names like:

```text
hourly_sales_by_category__filters__part01.png
hourly_sales_by_category__table_left__part02.png
hourly_sales_by_category__table_right__part03.png
hourly_sales_by_category__export.csv
```

For scroll captures:

```text
report_slug__hscroll_01_left.png
report_slug__hscroll_02_middle.png
report_slug__hscroll_03_right.png
report_slug__vscroll_01_top.png
report_slug__vscroll_02_middle.png
report_slug__vscroll_03_bottom.png
```

## Manifest Fields

The scaffold creates:

```text
00_CAPTURE_MANIFEST.csv
00_REPORT_STATUS.csv
00_FOLDER_MAP.csv
```

Important fields to fill:

| Field | Meaning |
|---|---|
| `configured_in_uat` | `yes`, `no`, or `unknown`. |
| `capture_type` | `section_menu`, `filters`, `table_header`, `hscroll`, `vscroll`, `export`, `note`. |
| `scroll_axis` | `none`, `horizontal`, `vertical`, or `both`. |
| `visible_columns_or_metrics` | Key headers/metrics visible in the screenshot. |
| `api_endpoint_candidate` | Restroworks endpoint if known, such as `fetch_Inventory_data` or `bills`. |
| `priority_domain` | `inventory_consumption`, `vendor_procurement`, `sales_revenue`, `master_data`, `low_priority`. |

## How Codex Will Use This Later

The screenshot extraction runner produces these memory chunks:

| Artifact | Purpose |
|---|---|
| `screen_index.csv` | One row per screenshot/export. |
| `report_catalog.csv` | One row per report with filters, grain, schema, and usefulness. |
| `field_catalog.csv` | One row per extracted field/metric/filter. |
| `api_coverage_matrix.csv` | Report-to-API availability and endpoint mapping. |
| `model_impact_backlog.csv` | Required changes to `STD`, `DIM`, `FACT`, and `SUM` model layers. |
| `chunks/page_section_report/*.md` | Small report-level markdown chunks for Codex to reference later. |

Run it with:

```powershell
python scripts\run_posist_screenshot_extraction.py
```

For a Stock Administration-only pass from the desktop dump, run:

```powershell
scripts\run_desktop_stock_admin_ocr_test.bat
```

Output is written under:

```text
source_intake/posist_uat/ocr_runs/
```

## Free OCR And Local LLM Plan

Do not use paid OCR first.

Check the local free OCR setup with:

```powershell
python scripts\check_free_ocr_tools.py
```

Setup details are documented in:

```text
docs/free_ocr_setup_readme.md
```

OCR PC run guide:

```text
docs/run_screenshot_extraction_on_ocr_pc.md
```

Recommended free stack:

1. Use RapidOCR as the default local OCR engine.
2. Use Tesseract as an optional fallback.
3. Use EasyOCR with GPU only if your 5070 Ti PC already has a working PyTorch/CUDA setup.
4. Use a local LLM only after OCR, for cleanup and classification, not for raw extraction.
5. Keep Codex responsible for final schema reasoning and model adaptation.

The practical order is:

```text
Screenshot -> OCR text extraction -> structured chunks/catalogs -> Codex model mapping
CSV/XLS export -> optional support if available
```

Local LLM is optional, not mandatory. Use it only if OCR text is messy or if hundreds of screenshots need pre-classification before Codex review. A free local setup can use Ollama with a small model such as Qwen/Llama/Phi-class models for tasks like:

- normalizing OCR text,
- classifying screenshots into page/section/report,
- detecting likely table headers,
- suggesting priority domain.

Do not let the local LLM make final schema decisions. It should produce intermediate suggestions that Codex can audit against screenshots, exports, and API docs.

## Priority Rule

Do not process every POSist report equally.

First priority:

1. Inventory and consumption intelligence.
2. Vendor and procurement analytics.
3. Sales and revenue only where it supports consumption forecasting or validation.

Use the Restroworks API packet to check whether a report has a likely API-backed source before proposing model changes.
