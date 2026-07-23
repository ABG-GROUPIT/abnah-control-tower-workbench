"""Check local free OCR tooling for POSist screenshot intake.

This script does not run OCR. It only reports whether the free OCR stack is
available on the current machine.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys


PYTHON_MODULES = [
    ("PIL", "Pillow image handling"),
    ("pytesseract", "Python wrapper for Tesseract"),
    ("cv2", "OpenCV image preprocessing"),
    ("rapidocr_onnxruntime", "RapidOCR fallback engine"),
    ("pandas", "CSV/XLS analysis support"),
    ("openpyxl", "XLSX export parsing"),
]


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def tesseract_status() -> tuple[bool, str]:
    exe = shutil.which("tesseract")
    if not exe:
        return False, "not found on PATH"
    try:
        result = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover - defensive check script
        return False, f"found at {exe}, but version check failed: {exc}"
    first_line = (result.stdout or result.stderr).splitlines()
    version = first_line[0] if first_line else "version unknown"
    return result.returncode == 0, f"{exe} ({version})"


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    print()

    tess_ok, tess_detail = tesseract_status()
    print(f"Tesseract binary: {'OK' if tess_ok else 'MISSING'} - {tess_detail}")
    print()

    module_results: list[tuple[str, bool, str]] = []
    for module, purpose in PYTHON_MODULES:
        ok = has_module(module)
        module_results.append((module, ok, purpose))
        print(f"{module}: {'OK' if ok else 'MISSING'} - {purpose}")

    print()
    rapidocr_ready = has_module("rapidocr_onnxruntime")
    tesseract_ready = tess_ok and has_module("PIL") and has_module("pytesseract")
    export_ready = has_module("pandas") and has_module("openpyxl")

    print(f"Default screenshot OCR ready (RapidOCR): {'YES' if rapidocr_ready else 'NO'}")
    print(f"Tesseract fallback ready: {'YES' if tesseract_ready else 'NO'}")
    print(f"CSV/XLS export parsing ready: {'YES' if export_ready else 'NO'}")

    if not rapidocr_ready:
        print()
        print("Minimum free screenshot OCR setup:")
        print("1. Install Python OCR packages:")
        print("   python -m pip install -r requirements-ocr.txt")
        print("2. Optional Tesseract fallback:")
        print("   winget install UB-Mannheim.TesseractOCR")

    return 0 if rapidocr_ready or tesseract_ready or export_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
