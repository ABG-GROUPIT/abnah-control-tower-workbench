# Update Workflow

## A. Add or Correct a Report Schema

1. Inspect the local screenshot or exported header text without moving it into this repository.
2. Locate the report ID in `schema-pack/generated/workspace_report_catalog.csv`.
3. Read `docs/STRUCTURAL_SCHEMA_METHOD.md` and choose a block shape.
4. Add or edit one JSON file under `schema-pack/source/report_structures/<page>/<section>/`.
5. Run `refresh_atlas.bat`.
6. Open the report in Discovery and review its blank structure.
7. Correct browser-side details if needed and save a draft.
8. Submit for review; publish only after another pass.
9. Reconcile the approved browser document back into the source blueprint before formal transfer.

## B. Text-Only Simple Report

For a normal export, only exact column titles and order are required. Use `flat_table`. A filter screenshot is unnecessary when filters are common and do not change grain or columns.

Use screenshots locally when you need to resolve merged headers, multiple tables, vertical row groups, conditional sections, or grain-changing filters.

## C. Mark No Data or Unknown

- `unavailable`: the report screen provides no usable schema in the current environment.
- `pending`: report exists but has not been inspected.
- `partial`: some columns or groups are known, but continuation/evidence is missing.
- archived: duplicate/unknown placeholder that should not appear in normal navigation.

Never treat unavailable as proof that the product never stores the data.

## D. Record an API Candidate

1. Add documented endpoint metadata without claiming ABNAH access.
2. Link it to a report only when its documented subject is relevant.
3. Keep status `not_tested` or `planned` until UAT.
4. In UAT, record authentication outcome, parameters, pagination, payload grain, outlet/date filters, IDs, and totals reconciliation.
5. Use `partial`, `failed`, or `blocked` with a concrete error type instead of softening the result.

## E. Capture a Meeting Decision

Use a `decision` note for business conclusions and an `issue` note for unresolved risks. Do not convert discussion into approved KPI or mapping records unless the owner and approval are explicit.

## F. Refresh and Verify

```powershell
refresh_atlas.bat
npm run data:validate
npm run typecheck
npm run lint
npm test
```

The refresh command rebuilds both the discovery catalog and structural workspace, then validates both.

## G. Back Up Before Transfer

Use the `Backup` action in the top bar while authenticated. It exports all D1 current documents and revision payloads as JSON. Store that export in the approved secure handoff location, not in this repository when it contains internal notes.

Source JSON plus the backup export is the complete transfer package. Source JSON alone omits browser-only revisions.
