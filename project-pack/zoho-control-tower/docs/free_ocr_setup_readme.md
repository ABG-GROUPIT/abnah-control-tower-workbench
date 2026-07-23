# Free OCR Setup For POSist Screenshots

This project does not require a local LLM for the first POSist screenshot pass.

The preferred order is screenshot-first for this POSist workflow:

```text
screenshot -> OCR -> structured report chunks -> Codex model review
CSV/XLS/PDF export -> optional supporting evidence only
local LLM -> optional cleanup/classification only
```

## Current Free Stack

Minimum free stack:

| Layer | Tool | Why |
|---|---|---|
| Default OCR | RapidOCR ONNXRuntime | Free, local, light setup, good for clean UI screenshots. |
| Preprocessing | OpenCV | Improves cropped/low-contrast screenshots. |
| Optional OCR fallback | Tesseract OCR + `pytesseract` | Useful if RapidOCR misses simple UI text. |
| Optional export parsing | `pandas`, `openpyxl` | Reads CSV/XLS/XLSX exports if they exist, but screenshots are primary. |

## Check Status

From the project root:

```powershell
python scripts\check_free_ocr_tools.py
```

or:

```powershell
scripts\check_free_ocr_tools.bat
```

## Install Free OCR Tools

RapidOCR currently works on this laptop through Python 3.9. Python 3.13/3.14 can fail because available `rapidocr-onnxruntime` builds do not support those versions.

Use the helper script first:

```powershell
scripts\setup_free_ocr_env.bat
```

This prefers `py -3.9` and creates:

```text
.venv-ocr39/
```

Manual install, if needed:

```powershell
py -3.9 -m venv .venv-ocr39
.venv-ocr39\Scripts\python.exe -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-ocr.txt
```

Optional Tesseract fallback:

```powershell
winget install UB-Mannheim.TesseractOCR
```

Re-run:

```powershell
.venv-ocr39\Scripts\python.exe scripts\check_free_ocr_tools.py
```

For the full OCR PC workflow, see:

```text
docs/run_screenshot_extraction_on_ocr_pc.md
```

## Run Screenshot Extraction

After screenshots are dumped into:

```text
source_intake/posist_uat/_incoming_drop/posist_ss/
```

run:

```powershell
scripts\run_posist_screenshot_extraction.bat
```

This writes a run folder under:

```text
source_intake/posist_uat/ocr_runs/
```

To run without OCR for a structure-only dry run:

```powershell
python scripts\run_posist_screenshot_extraction.py --engine none
```

To use Tesseract instead of RapidOCR:

```powershell
python scripts\run_posist_screenshot_extraction.py --engine tesseract
```

Optional EasyOCR GPU path, only if the OCR PC has a working PyTorch/CUDA setup:

```powershell
python scripts\run_posist_screenshot_extraction.py --engine easyocr --gpu
```

## Local LLM Policy

Do not add a local LLM until it is actually needed.

Use a local LLM only if:

1. There are 100-200 screenshots.
2. OCR output is too noisy to classify manually.
3. We need cheap pre-classification into page, section, report, fields, and priority domain.

The local LLM should not decide schema changes. It should only produce intermediate suggestions that Codex can audit against screenshots, exports, and API docs.
