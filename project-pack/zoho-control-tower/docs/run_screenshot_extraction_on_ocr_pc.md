# Run POSist Screenshot Extraction On OCR PC

Use this when the screenshots are ready and you want to process them locally on the 5070 Ti PC.

## 1. Copy The Folder

Copy this project folder to the OCR PC:

```text
C:\Users\ARNAV\OneDrive\Desktop\ABNAH actual demo\abnah-zoho-synthetic-demo
```

The important input folder is:

```text
source_intake/posist_uat/_incoming_drop/posist_ss/
```

For the laptop/Desktop workflow, use this simpler input folder:

```text
C:\Users\ARNAV\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS
```

For the first main-page-only test, fill:

```text
C:\Users\ARNAV\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS\p1_main
```

For the Stock Administration pass, fill:

```text
C:\Users\ARNAV\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS\p4_stock_admin
```

## 2. Install Free OCR Environment

From the project root on the OCR PC:

```powershell
scripts\setup_free_ocr_env.bat
```

This creates `.venv-ocr` and installs the free OCR packages from `requirements-ocr.txt`.

RapidOCR is the default engine. It does not require CUDA.

## 3. Run Extraction

From the project root:

```powershell
.venv-ocr\Scripts\python.exe scripts\run_posist_screenshot_extraction.py
```

For the first Desktop main-page test, run:

```powershell
scripts\run_desktop_main_page_ocr_test.bat
```

For the Stock Administration-only pass, run:

```powershell
scripts\run_desktop_stock_admin_ocr_test.bat
```

Output is created under:

```text
source_intake/posist_uat/ocr_runs/<run_id>/
```

## 4. Copy Back For Codex Review

Copy the generated run folder back to the laptop/project if needed.

The key files Codex will review are:

```text
report_catalog.csv
field_catalog.csv
api_coverage_matrix.csv
model_impact_backlog.csv
03_report_chunks/
```

## Optional Commands

Structure-only dry run:

```powershell
.venv-ocr\Scripts\python.exe scripts\run_posist_screenshot_extraction.py --engine none
```

Tesseract fallback, after installing Tesseract OCR:

```powershell
.venv-ocr\Scripts\python.exe scripts\run_posist_screenshot_extraction.py --engine tesseract
```

EasyOCR GPU path, only if PyTorch/CUDA is already working on the OCR PC:

```powershell
.venv-ocr\Scripts\python.exe scripts\run_posist_screenshot_extraction.py --engine easyocr --gpu
```

## What The Extractor Produces

| File/folder | Purpose |
|---|---|
| `screen_index.csv` | One row per screenshot/note with folder context. |
| `ocr_line_catalog.csv` | OCR lines grouped by screenshot/report. |
| `report_catalog.csv` | One row per report with fields, priority, and API candidates. |
| `field_catalog.csv` | Candidate table headers/metrics/filters. |
| `api_coverage_matrix.csv` | Heuristic mapping to Restroworks API candidates. |
| `model_impact_backlog.csv` | First-pass model adaptation tasks. |
| `03_report_chunks/` | Report-level markdown chunks for Codex. |

## Rule

Do not revise SQL from OCR alone. OCR output is evidence for Codex. SQL/model changes should happen only after we compare:

1. screenshots,
2. OCR chunks,
3. Restroworks/POSist API docs,
4. sample API responses when available.
