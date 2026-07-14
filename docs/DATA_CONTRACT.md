# Data Contracts

## Stable Identity

Report IDs are the primary key. Names may repeat across pages and sections.

Example:

```text
report:p1_main:06_misc:03_budget_dsr_report
```

Do not rename an ID when only display text changes.

## Source Blueprint

Each `report_structures/*.json` file contains:

- `report_id`
- `schema_status`: `captured`, `partial`, `pending`, `unavailable`
- `verification_status`: `needs_review`, `reviewed`, `uat_verified`
- `layout_kind`: `flat`, `grouped_columns`, `grouped_rows`, `mixed`, `freeform`
- `capture_method`
- optional `structure_notes`
- optional semantic `data_points`
- one or more structural `blocks`

Supported block kinds:

- `flat_table`: one leaf per exported column.
- `column_tree`: nested groups compile to merged header cells.
- `matrix`: repeating row groups plus one or more value-column trees.
- `key_value`: label/value summary region.
- `grid`: explicit rows, columns, spans, labels, and cell roles.

## Runtime Grid

Every structural block compiles into:

```ts
interface SchemaTable {
  id: string;
  name: string;
  rows: number;
  columns: number;
  columnWidths: number[];
  cells: SchemaCell[];
}
```

Each cell has zero-based `row` and `column`, positive `rowSpan` and `columnSpan`, exact `text`, and a kind: `group`, `field`, `label`, `context`, or `blank`.

Cells must remain within bounds and may not overlap. Blank coordinates are allowed; the editor materializes them when needed.

## Report Workspace Document

A document combines:

- report identity and classification;
- schema and verification statuses;
- semantic fields;
- one or more editable blank tables;
- API test records;
- notes;
- archive/custom flags;
- workflow and version metadata.

The source policy is fixed to schema-only storage.

## API Test Record

An API test distinguishes documented possibility from observed UAT behavior:

- endpoint ID, name, method, and path;
- test type;
- status: `not_tested`, `planned`, `passed`, `partial`, `failed`, `blocked`;
- result, error type, notes, and tested timestamp.

`passed` must describe the actual ABNAH UAT payload, filters, grain, and reconciliation outcome.

## KPI Lineage Contract

The empty lineage contract contains four collections:

- `kpis`: approved business definitions, formula, grain, and owner;
- `nodes`: one KPI-scoped reference per source/model/KPI/chart object;
- `edges`: transformations, join keys, rationale, and decision state;
- `publications`: immutable publication metadata.

No relationship is implied by lane position or similar names.

## Generated Files

- `schema-pack/generated/workspace.json`
- `schema-pack/generated/workspace_report_catalog.csv`
- `schema-pack/generated/kpi-lineage.json`
- browser copies under `public/data/`

Generated files are replaced by builders and must never be hand-edited.

## Contract Invariants

1. No image or local evidence path.
2. No row-level business values.
3. Exact observed labels; interpretations belong in notes.
4. Unique report, table, cell, field, API-test, note, node, and edge IDs within scope.
5. No overlapping grid cells.
6. Unknown availability remains unknown.
7. UAT verification and business approval are explicit state changes.
