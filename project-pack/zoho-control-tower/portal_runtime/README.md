# Portal Runtime Pack

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
