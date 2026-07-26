#!/usr/bin/env python3
"""Mirror the deployable GitHub Pages/Supabase portal contract into the pack."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "project-pack" / "zoho-control-tower"
DESTINATION = PACK_ROOT / "portal_runtime"

PORTAL_FILES = (
    ".github/workflows/pages.yml",
    "app/components/EmbeddedControlTowerPortal.tsx",
    "app/lib/supabase-portal-client.ts",
    "app/lib/zoho-portal-handoff.ts",
    "app/lib/zoho-portal-types.ts",
    "app/lib/zoho-report-embed-contract.ts",
    "config/supabase-portal.json",
    "config/zoho-portal.json",
    "config/zoho-secured-embed-handoff.example.json",
    "docs/ZOHO_PORTAL_RUNTIME.md",
    "github-pages/index.html",
    "github-pages/main.tsx",
    "supabase/.env.example",
    "supabase/config.toml",
    "supabase/functions/_shared/crypto.ts",
    "supabase/functions/_shared/zoho.ts",
    "supabase/functions/abnah-portal/index.ts",
    "supabase/migrations/20260727000100_abnah_portal.sql",
)

README = """# Portal Runtime Pack

This folder is a generated, secret-free mirror of the production portal
contract from the repository root.

- GitHub Pages is the only frontend host.
- Supabase is the only production backend.
- Supabase handles Zoho OAuth, workspace verification, opaque sessions, and
  the shared URL-only handoff.
- No POSist rows, screenshots, credentials, or runtime tokens belong here.

Start with `docs/ZOHO_PORTAL_RUNTIME.md`. Edit the repository source files, then
run `py -3 scripts/sync_portal_runtime_to_pack.py`; do not maintain these copies
independently.
"""


def main() -> None:
    pack_root = PACK_ROOT.resolve()
    destination = DESTINATION.resolve()
    if pack_root not in destination.parents:
        raise SystemExit(f"Unsafe portal-runtime destination: {destination}")

    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir(parents=True)

    copied = 0
    for relative_text in PORTAL_FILES:
        relative = Path(relative_text)
        source = ROOT / relative
        if not source.is_file():
            raise SystemExit(f"Portal runtime source is missing: {relative_text}")
        target = DESTINATION / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1

    (DESTINATION / "README.md").write_text(README, encoding="utf-8")
    print(f"Portal runtime mirrored into project pack: {copied + 1} files.")


if __name__ == "__main__":
    main()
