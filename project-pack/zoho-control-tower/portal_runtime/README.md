# Portal Runtime Pack

This folder is a generated, secret-free mirror of the production portal
contract from the repository root.

- GitHub Pages is the only frontend host.
- Supabase is the only production backend.
- Supabase handles Zoho OAuth, workspace verification, opaque sessions, and
  allowlisted Query Table exports.
- The browser renders custom KPI, action and evidence surfaces from rows.
- Selected secured Zoho map/bar/line views render in hybrid visual slots;
  dashboard URLs remain external fallbacks.
- No POSist rows, screenshots, credentials, or runtime tokens belong here.

Start with `docs/ZOHO_PORTAL_RUNTIME.md`. Edit the repository source files, then
run `py -3 scripts/sync_portal_runtime_to_pack.py`; do not maintain these copies
independently.
