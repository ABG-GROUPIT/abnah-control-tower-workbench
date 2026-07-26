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

After a complex structure is corrected in the browser, export its report JSON
and reconcile the approved shape into the source blueprint. Browser state keeps
the working copy; the source file and Git history preserve the transferable
approved revision.

## Batch Strategy for P2 and P4

Process one portal section at a time:

1. Inventory report names and stable IDs.
2. Fill all simple flat reports from text headers.
3. Flag complex candidates before encoding them.
4. Encode and review complex candidates individually.
5. Run the complete build and validator after every section.
6. Publish only reviewed reports.

This prevents one malformed grid from blocking a large 100-200 report batch and keeps review ownership clear.

## P1 Reconciliation Baseline

P1 no longer uses report-level completeness inferred from OCR confidence. All usable local report-output evidence has been transcribed into explicit blueprints, including horizontal continuations and non-flat report shapes.

The locked P1 baseline is 90 catalogue entries, 85 active reports, 76 captured reports, 14 unavailable reports, and zero `partial` or `pending` reports. Five unavailable entries are archived catalogue placeholders; the remaining nine active unavailable reports have explicit evidence reasons.

For future changes:

1. Update the report blueprint or status override.
2. Update the P1 completion baseline in `scripts/validate_workspace_data.py` only when discovery genuinely changes the catalogue.
3. Regenerate the workspace contract and run the full validator.
4. Review at least one flat and every newly introduced complex rendering before publishing.

Verification status is intentionally separate from schema completeness. A report may be structurally `captured` while still `needs_review`; it must not be relabelled `partial` for that reason.

## P2 Batch-One Baseline

The first P2 transcription pass covers all 10 Analytics reports and 25 of the 50 Audit reports. It produces 32 captured schemas and 3 explicitly partial schemas; the other 120 P2 catalogue entries remain pending.

The pass demonstrates the supported intake paths:

1. Plain pasted headers become `flat_table` blueprints.
2. Pasted pivot descriptions become grouped-row or grouped-column structures.
3. Locally inspected report views become explicit mixed or grid structures when merged headers, repeated groups, context rows, or multiple tables matter.
4. A document view can clarify table segmentation, but neither the document nor its rendered pages enter the project.

The complex reference reports are Forecast Comparison Report, Food Cost Report, KOT Tracking Report, Report By Time, Item Based Offer Report, day_part_daily_sales, Complimentary Detail Report Headwise, and BTS Itemwise Report. Their source blueprints should be consulted before encoding a structurally similar P2 or P4 report.

The P2 baseline is intentionally strict. When a later batch resolves a pending report or completes one of the three partial reports, update both `p2_reports/README.md` and `P2_BATCH_ONE_BASELINE` in the validator in the same change.

## Definition of Done for One Report

- Correct stable report ID and navigation location.
- Exact complete headers or an explicit `partial` state.
- Correct table count, header hierarchy, row groups, and order.
- No sample values, image, or evidence path.
- Semantic points separated from visual structure where useful.
- Schema validation passes.
- A human reviewer has checked the blank rendering.
- Published revision exists only after review.
