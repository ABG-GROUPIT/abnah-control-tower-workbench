from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 20 * 1024 * 1024

ALLOWED_IGNORED_FILES = {
    "local_data_auditor/input/.gitkeep",
    "local_data_auditor/input/README.md",
    "local_data_auditor/output/.gitkeep",
    "source_intake/posist_uat/_incoming_drop/.gitkeep",
    "source_intake/posist_uat/_incoming_drop/README.md",
    "source_intake/posist_uat/batches/.gitkeep",
    "source_intake/posist_uat/ocr_runs/.gitkeep",
}

PRIVATE_PREFIXES = (
    "local_data_auditor/input/",
    "local_data_auditor/output/",
    "source_intake/posist_uat/_incoming_drop/",
    "source_intake/posist_uat/batches/",
    "source_intake/posist_uat/_working_previews/",
    "source_intake/posist_uat/ocr_runs/",
)

SECRET_PATTERNS = {
    "GitHub token": re.compile(r"gh[oprsu]_[A-Za-z0-9_]{20,}"),
    "Sites token": re.compile(r"art_v1_[A-Za-z0-9_]{20,}"),
    "OpenAI key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "Populated database URL": re.compile(
        r"(?im)^DATABASE_URL[ \t]*=[ \t]*"
        r"(?!$|postgresql\+psycopg2://USER:PASSWORD)[^\r\n]+"
    ),
}

TEXT_EXTENSIONS = {
    ".bat",
    ".csv",
    ".env",
    ".example",
    ".html",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sql",
    ".txt",
    ".yaml",
    ".yml",
}


def repository_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(
        {
            line.strip().replace("\\", "/")
            for line in result.stdout.splitlines()
            if line.strip()
        }
    )


def main() -> None:
    violations: list[str] = []
    files = repository_files()

    for relative in files:
        path = ROOT / relative
        if not path.is_file():
            continue

        if relative not in ALLOWED_IGNORED_FILES and relative.startswith(PRIVATE_PREFIXES):
            violations.append(f"private intake/output file is publishable: {relative}")

        if path.stat().st_size > MAX_FILE_BYTES:
            violations.append(f"file exceeds 20 MB safety limit: {relative}")

        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {
            ".gitignore",
            ".gitattributes",
        }:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            violations.append(f"cannot inspect {relative}: {exc}")
            continue

        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                violations.append(f"{label} detected in {relative}")

    if violations:
        joined = "\n".join(f"- {item}" for item in violations)
        raise SystemExit(f"Repository safety check failed:\n{joined}")

    print(f"Repository safety check passed: {len(files)} publishable files inspected.")


if __name__ == "__main__":
    main()
