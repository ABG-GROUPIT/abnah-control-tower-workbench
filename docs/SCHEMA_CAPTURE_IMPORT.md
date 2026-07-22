# Schema Capture Import

This workflow converts local P2/P4 discovery notes into the portable, screenshot-free website baseline.

## Boundary

- Screenshots, raw CSV rows, local paths, customer values, and attachment names stay outside this repository.
- Only report labels, ordered fields, merged-header relationships, mode boundaries, row groups, and semantic notes are committed.
- Repeated generic headers such as `Amt`, `Qty`, and `Subtotal` must receive position-aware keys. Never deduplicate them by label alone.

## Import

```powershell
py -3 scripts/import_schema_captures.py `
  --p2 "<local-path-to-P2-capture-readme>" `
  --p4 "<local-path-to-P4-capture-readme>"
```

The importer preserves existing reviewed blueprints by default. Use `--overwrite-existing` only after comparing the replacement with the current file.

Plain exported header rows are converted automatically. Complex reviewed layouts are encoded in `custom_blueprints()` inside the importer so multi-mode and grouped reports remain reproducible without retaining their visual evidence.

## Rebuild And Review

```powershell
npm run data:refresh
npm run data:validate
npm run typecheck
npm run lint
npm test
```

Review these generated indexes before publishing:

- `schema-pack/generated/workspace_report_catalog.csv`
- `schema-pack/generated/workspace.json`
- `schema-pack/manifest.json`

For a newly captured report, confirm the stable report ID, display name, field count, table/mode count, positional keys, schema status, and source note. A populated blank structure proves only that the schema was observed; it does not prove row quality, API coverage, joins, or KPI suitability.

## Current Imported Checkpoint

- P2: 73 captured, 3 partial, 79 pending.
- P4: 24 captured, 50 pending.
- P4 Consumption Report: four separately modelled modes.
- Enterprise Consumption: position-aware quantity/amount pairs retained across the inventory lifecycle.
- Enterprise Purchase Order: schema known but UAT result empty; regular Purchase Order remains the planned authority.
