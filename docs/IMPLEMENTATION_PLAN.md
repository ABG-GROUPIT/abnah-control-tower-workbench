# Implementation Plan

## Completed Baseline

- Searchable report workspace replacing graph-first discovery.
- Universal editable grid with merge/unmerge, row/column editing, widths, table management, paste, undo, and redo.
- Editable data points, API tests, notes, and report metadata.
- Draft, review, publish, archive, and read-only Published view.
- Browser-local persistence and explicit workspace backup export.
- P1 Misc explicit structural blueprints: 17 captured, 8 unavailable, 2 archived unknown.
- Empty, versioned KPI-lineage contract.
- Screenshot-free source policy and validators.
- Versioned four-page control-tower requirements contract with 35 draft KPIs.
- Read-only control-tower site surface for page logic, source capture, API gaps, and model decisions.
- P2/P4 capture queue narrowed to reports that can support the agreed control-tower requirements.

## Next: Targeted Schema Intake

1. Ingest the P2 schemas already collected through Daily Sales Summary Report.
2. Capture Daily Sales Report Detailed and Gross Sale Wastage Report.
3. Inspect the P2 comparison headers listed in `REPORT_CAPTURE_PRIORITY.md`; materialize only unique structures.
4. Capture the P4 PO/GRN and inventory/consumption P0 groups.
5. Compare enterprise and operational variants before selecting any primary source.
6. Review complex blank structures individually and publish only completed sections.

## Next: P4 Stock Administration Intake

Use the exact groups in `REPORT_CAPTURE_PRIORITY.md`. Keep overlapping enterprise and operational report names until their fields and grain are compared. Use the same structural method and one shared model.

## UAT API Phase

1. Test authentication and outlet access.
2. Capture endpoint parameters and pagination.
3. Compare payload fields and grain with report schemas.
4. Reconcile totals and date/outlet behavior.
5. Mark passed, partial, failed, or blocked with concrete evidence notes.
6. Select API-backed sources only after verification.

## Model Revision Phase

Revise the existing 37-query model after the P0 schemas are available. Replace hardcoded outlets, name-based joins, approximate PO/receipt linkage, arbitrary low-stock flags, and missing UOM/movement logic. Add actual consumption, variance, wastage, risk, action, vendor-performance, and data-quality layers as described in `MODEL_REVISION_PLAN.md`.

## KPI and Relational Mapping Phase

Business definitions are now recorded as draft. For each KPI, compare possible sources, select relationships only after schema/UAT validation, record joins and transformations, reconcile output, obtain formula and threshold approval, then publish one lineage map.

## Later Hardening

- Controlled backup restore utility.
- Role separation between editor, reviewer, and publisher if required.
- Automated source-blueprint reconciliation from approved browser backups.
- UAT payload schema packet import that explicitly strips values and secrets.
- Optional Supabase-backed shared schema review after its authorization and
  overwrite contract is approved.
