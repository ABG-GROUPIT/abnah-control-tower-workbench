# Implementation Plan

## Completed Baseline

- Searchable report workspace replacing graph-first discovery.
- Universal editable grid with merge/unmerge, row/column editing, widths, table management, paste, undo, and redo.
- Editable data points, API tests, notes, and report metadata.
- Draft, review, publish, archive, and read-only Published view.
- D1 optimistic persistence and immutable revision history.
- Authenticated full workspace backup export.
- P1 Misc explicit structural blueprints: 17 captured, 8 unavailable, 2 archived unknown.
- Empty, versioned KPI-lineage contract.
- Screenshot-free source policy and validators.

## Next: P2 Schema Intake

1. Complete simple reports from exact text/CSV headers.
2. Identify grouped, matrix, mixed, and freeform exceptions.
3. Encode one portal section per batch.
4. Review complex blank structures individually.
5. Publish only completed sections.

## Next: P4 Stock Administration Intake

Prioritize reports supporting inventory, consumption, vendor, procurement, purchase order, receipt/entry, variance, wastage, food cost, and re-order analysis. Use the same structural method; do not create a second data model for P4.

## UAT API Phase

1. Test authentication and outlet access.
2. Capture endpoint parameters and pagination.
3. Compare payload fields and grain with report schemas.
4. Reconcile totals and date/outlet behavior.
5. Mark passed, partial, failed, or blocked with concrete evidence notes.
6. Select API-backed sources only after verification.

## KPI and Relational Mapping Phase

Start only after the ABNAH meeting confirms KPIs and workflow. For each KPI, document the definition and grain, compare possible sources, select relationships, record joins and transformations, reconcile output, then publish one lineage map.

## Later Hardening

- Controlled backup restore utility.
- Role separation between editor, reviewer, and publisher if required.
- Automated source-blueprint reconciliation from approved D1 publications.
- UAT payload schema packet import that explicitly strips values and secrets.
- Private production deployment and scheduled D1 export under ABNAH ownership.
