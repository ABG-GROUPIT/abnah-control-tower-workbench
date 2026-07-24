# Complete ABNAH Project Pack

This folder makes the ABG workbench repository a single-clone handoff for the
ABNAH Control Tower project.

## Start Here

1. Read `zoho-control-tower/FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/START_HERE.md`.
2. Follow `zoho-control-tower/WORK_LAPTOP_SETUP.md` for a new machine.
3. Use the numbered folders under
   `zoho-control-tower/FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/` for the final
   Zoho import, Query Table, dashboard, validation, and handoff workflow.
4. Return to the repository root and run `npm run data:refresh` whenever the
   canonical SQL or presentation contract changes.

## Included

- all synthetic three-outlet source data and final Zoho import CSVs;
- all 38 final Control Tower Query Tables and their build manifests;
- click-by-click Zoho import, lookup, formula, dashboard, Ask Zia, validation,
  and publication instructions;
- KPI/source matrices, truth packs, reconciliation outputs, fidelity registers,
  limitations, and presentation-safe issue documentation;
- the synthetic-data generators, local CSV auditor, schema contracts, tests,
  API packet, screenshot-intake tooling, and developer handoff material;
- the earlier model, dashboard, external-signal, and Ask Zia research retained
  for traceability.

The website application, editable schema catalogue, synchronized
presentation/model contracts, and this complete pack are all available from
the hosted [ABNAH Control Tower Workbench](https://abg-groupit.github.io/abnah-control-tower-workbench/).
Open its `Library` surface to search individual files or download the complete
pack as one archive.

## Deliberately Local Only

The following are not part of this pack:

- POSist/Restroworks screenshots;
- real operational CSV exports or full actual-data rows;
- local auditor runtime inputs and outputs;
- credentials, tokens, database files, and local environment values.

These exclusions preserve the project rules agreed during discovery. Their
parsers, contracts, empty intake folders, and operating instructions are
included so the workflow can be run locally.

## Integrity

`PROJECT_PACK_MANIFEST.csv` records the size and SHA-256 digest of every file
under `zoho-control-tower/`. Validate it from the repository root:

```powershell
py -3 scripts/validate_project_pack.py
```

After intentionally changing the bundled implementation, refresh the manifest:

```powershell
py -3 scripts/validate_project_pack.py --write-manifest
```
