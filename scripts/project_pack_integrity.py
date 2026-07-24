"""Cross-platform integrity helpers for the consolidated project pack."""

from __future__ import annotations

import hashlib
from pathlib import Path


TEXT_EXTENSIONS = {
    "",
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


def canonical_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def canonical_size_sha256(path: Path) -> tuple[int, str]:
    data = canonical_bytes(path)
    return len(data), hashlib.sha256(data).hexdigest()
