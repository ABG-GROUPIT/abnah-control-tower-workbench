# Report Structure Blueprints

This folder is the portable, screenshot-free source for report layouts shown in the editable workspace.

## Source Policy

- Store derived schema labels and structural relationships only.
- Never store screenshots, local screenshot paths, report row values, or client data here.
- Keep one JSON file per captured report so another developer or AI agent can change a report without loading the full catalogue.
- Use stable report IDs from `schema-pack/generated/report_catalog.csv`.

## Blueprint Contract

Required report keys:

- `report_id`
- `schema_status`: `captured`, `partial`, `pending`, or `unavailable`
- `verification_status`: `needs_review`, `reviewed`, or `uat_verified`
- `layout_kind`: `flat`, `grouped_columns`, `grouped_rows`, `mixed`, or `freeform`
- `blocks`

Optional `data_points` preserve semantic fields independently of the visual layout. Each point can include `key`, `label`, `semantic_role`, `data_type`, `status`, and `notes`.

## Supported Blocks

### `flat_table`

Use one leaf node per exported column.

```json
{
  "id": "primary",
  "name": "Report table",
  "kind": "flat_table",
  "columns": [
    { "label": "Outlet Name", "key": "outlet_name" },
    { "label": "Business Date", "key": "business_date" }
  ]
}
```

### `column_tree`

Use nested `children` for merged or grouped column headers. Leaves become data points; parent nodes remain structural groups.

### `matrix`

Use `row_headers`, nested `value_columns`, and repeating `row_groups`. This covers DSR, pivot, period-versus-metric, outlet, and comparison layouts.

### `key_value`

Use for summary measures that appear above or beside a tabular report.

### `grid`

Use the explicit grid escape hatch when no higher-level block describes the report. Cells specify zero-based `row`, `column`, `rowSpan`, `columnSpan`, `text`, `kind`, and optional `fieldId`.

Every block compiles into the same runtime grid. The site can then rename cells, paste tabular labels, merge or unmerge ranges, add or delete rows and columns, resize columns, and add or remove complete tables.

## Intake Workflow

1. Inspect local evidence without copying it into this project.
2. Classify the report as flat, grouped columns, grouped rows/matrix, mixed, or freeform.
3. Record one blueprint and semantic data-point list.
4. Run `refresh_atlas.bat`.
5. Review the blank structure in the workspace.
6. Correct it in the editor, submit it for review, and publish a revision.

The generated runtime contract is `schema-pack/generated/workspace.json`. Do not edit that file manually.

## P1 Completion Baseline

P1 was reconciled against all usable local report-output evidence on 2026-07-15. Its portable baseline is:

- 90 catalogue entries: 85 active and 5 archived placeholders.
- 76 captured reports and 14 explicitly unavailable reports.
- 0 partial reports and 0 pending reports.
- 59 reviewed report blueprints across Sales Analysis, Settlements, Discounts & Offers, Tax Analysis, and Performance.
- 7 captured Misc blueprints are reviewed and 10 remain `needs_review`; this is a verification state, not an incomplete-schema state.

The nine active unavailable reports are one filter-only Discounts & Offers report and eight Misc reports for which no usable result table or export schema was present. Every unavailable entry carries its reason in a status override.

Dynamic report members such as dates, categories, sources, sections, meal periods, or order types are represented as named repeating groups. Sample member values are never copied into a blueprint.

See `p1_main/README.md` for the section ledger and transfer notes. `scripts/validate_workspace_data.py` locks this baseline so a later build cannot silently reintroduce legacy OCR `partial` states.

## P2 Batch-One Baseline

The first P2 evidence batch was reconciled on 2026-07-15:

- 155 catalogue reports remain in scope.
- 32 reports are captured, 3 are partial, and 120 remain pending.
- All 35 materialized reports are reviewed.
- Analytics is fully assessed: 9 captured and 1 partial.
- Audit is partly assessed: 23 captured, 2 partial, and 25 pending.
- Attendance and all later P2 sections remain pending until usable schema evidence is supplied.

The three partial reports have explicit evidence boundaries: Food Cost Report has an incomplete right-hand header continuation, Complimentary Report ends inside Item Name, and Report By Time lacks its lower sections. They must not be guessed complete.

See `p2_reports/README.md` for the report ledger and transfer notes. The P2 guard in `scripts/validate_workspace_data.py` makes every future discovery an intentional baseline update.
