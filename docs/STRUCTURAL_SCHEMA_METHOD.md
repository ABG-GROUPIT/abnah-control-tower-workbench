# Structural Schema Method

## Purpose

Convert many locally inspected screenshots or exported header lists into a consistent, editable, screenshot-free representation of what each report can expose.

The output is a blank structural table. It preserves header hierarchy and report shape, not sample values.

## Intake Decision

Use the least complex shape that preserves the report.

1. One header row with independent columns: `flat_table`.
2. Parent headers spanning child columns: `column_tree`.
3. Repeating metric rows grouped under section labels: `matrix`.
4. Summary labels plus a separate detail table: multiple blocks, usually `key_value` plus `flat_table` or `column_tree`.
5. Irregular merged cells that do not fit the above: `grid`.

Do not force a visually complex report into a flat field list. Do not use `grid` when a stable higher-level shape expresses it clearly.

## Evidence Reading Method

For each report, inspect local evidence in this order:

1. Main or header view: establish table count and left-to-right order.
2. Horizontal continuation: complete columns and merged parent spans.
3. Vertical continuation: detect repeating row groups, footer sections, and second tables.
4. Notes/context view: capture labels that explain grain or grouping.
5. Filters: record only filters that change report grain or schema; do not repeat common filters mechanically.

The evidence itself stays outside the project. A blueprint must remain understandable without knowing the screenshot filename.

## Exactness Rules

- Transcribe source labels exactly.
- Keep duplicate labels when they occur under different parent groups.
- Use stable machine keys to distinguish duplicates.
- Preserve visible header order.
- Preserve merged parent-child structure.
- Use blank cells for values.
- Record suspected OCR or product spelling issues in `structure_notes`.
- If a continuation is missing, mark the report `partial`.
- If the report returns no schema, mark it `unavailable` and leave a short reason.

## Complex Table Patterns

### Grouped Columns

Use nested column nodes. A parent becomes a merged `group` cell; each leaf becomes a `field` cell. Example patterns include Cashier, Super Categories DSR, Entp Day, and Shift.

### Grouped Rows

Use a matrix when a vertical section label spans several metric rows. Budget DSR is the reference pattern.

### Mixed Report

Represent each visually distinct table or summary region as a separate block. WhatsApp Message is the reference pattern. Never put two unrelated grids into one artificial table.

### Unusual Layout

Use `grid` with explicit zero-based coordinates and spans. Start with the smallest bounding rectangle. Validate that every span is in bounds and no cells overlap.

## Editable Runtime

The editor supports:

- direct cell text editing;
- rectangular selection;
- merge and unmerge;
- add/delete rows and columns;
- set cell role;
- resize columns;
- paste tab-separated cells;
- add, rename, reorder through selection, and remove complete tables;
- undo and redo during the current editing session.

After a complex structure is corrected in the browser, export its report JSON and reconcile the approved shape into the source blueprint. D1 preserves the revision, but the source file preserves portability.

## Batch Strategy for P2 and P4

Process one portal section at a time:

1. Inventory report names and stable IDs.
2. Fill all simple flat reports from text headers.
3. Flag complex candidates before encoding them.
4. Encode and review complex candidates individually.
5. Run the complete build and validator after every section.
6. Publish only reviewed reports.

This prevents one malformed grid from blocking a large 100-200 report batch and keeps review ownership clear.

## Definition of Done for One Report

- Correct stable report ID and navigation location.
- Exact complete headers or an explicit `partial` state.
- Correct table count, header hierarchy, row groups, and order.
- No sample values, image, or evidence path.
- Semantic points separated from visual structure where useful.
- Schema validation passes.
- A human reviewer has checked the blank rendering.
- Published revision exists only after review.
