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
