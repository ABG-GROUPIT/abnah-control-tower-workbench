# AI Agent Handoff

## Objective

Maintain a screenshot-free, evidence-disciplined understanding of ABNAH's Restroworks report schemas and four-page Supply Chain Control Tower requirements. Extend it through targeted P2/P4 discovery, UAT API testing, model revision, and approved KPI lineage without forcing another team to repeat discovery.

## Non-Negotiable Rules

1. Raw screenshots stay outside this repository and outside hosting.
2. Never store a screenshot filename or local evidence path in a new report blueprint.
3. Store structural labels and relationships only; never copy report row values or client records.
4. Preserve source labels exactly, including suspected spelling errors. Put corrections in notes.
5. Do not claim API coverage until ABNAH UAT access has been tested.
6. Business-supplied KPI definitions may be stored as `draft`; do not create selected sources, joins, transformations, thresholds, or published mappings without evidence and approval.
7. Empty and unavailable reports remain explicit states; do not fabricate columns.
8. Archive unknown duplicate placeholders rather than deleting or guessing them.

## Read Order

1. `README.md`
2. `schema-pack/manifest.json`
3. `docs/STRUCTURAL_SCHEMA_METHOD.md`
4. `docs/CONTROL_TOWER_REQUIREMENTS.md`
5. `docs/REPORT_CAPTURE_PRIORITY.md`
6. `docs/MODEL_REVISION_PLAN.md`
7. `schema-pack/source/control_tower/control-tower-requirements.json`
8. `docs/DATA_CONTRACT.md`
9. `docs/LOCAL_AUDIT_PACKET_WORKFLOW.md` when a local CSV packet is supplied
10. `docs/SCHEMA_CAPTURE_IMPORT.md` when a local schema-capture README is supplied
11. `schema-pack/generated/workspace_report_catalog.csv`
12. The selected report file under `schema-pack/source/report_structures/`
13. Relevant text chunk under `schema-pack/source/reference_chunks/`
14. `docs/KPI_LINEAGE_CONTRACT.md` before source selection or publication

## Truth Model

There are two intentional stores:

- Source blueprints are the transferable baseline in version control.
- D1 is the working store for edits, workflow state, and revision history.

For the live site, use the latest D1 current document. For a clean rebuild or team transfer, use source blueprints plus an exported D1 backup. Site edits are not automatically promoted into source JSON.

## Finding One Report

1. Filter `schema-pack/generated/workspace_report_catalog.csv` by `report_name`, `page`, or `section`.
2. Use the stable `report_id`; labels can repeat across P1, P2, and P4.
3. Search `schema-pack/source/report_structures/` for that ID.
4. If no blueprint exists, inspect the matching text-only reference chunk.
5. Do not load all 319 report files when one report answers the task.

## Adding P2 or P4

1. Check `docs/REPORT_CAPTURE_PRIORITY.md`; do not expand the current queue from a similar report name alone.
2. Classify the layout: flat, grouped columns, grouped rows, mixed, or freeform.
3. For a batch README, run `scripts/import_schema_captures.py`; for one report, create one JSON blueprint under the matching page/section.
4. Record exact labels and blank structure only.
5. Add semantic data points separately when the visual structure does not fully express them.
6. Compare overlapping report variants and record their role: primary, fallback, reconciliation, validation, or deferred.
7. Run `refresh_atlas.bat`.
8. Review the generated grid and all validation output.
9. Save, submit for review, and publish in the workspace only after manual checking.

## Current P2/P4 Coverage

- P2: 73 captured, 3 partial, 79 pending. Category/Item has 17 of 18 captured; Sales has 24 of 41 captured.
- P4: 24 captured, 50 pending. Enterprise Reports has 15 of 15 captured.
- Consumption Report has four independent mode tables; do not merge their fields by label.
- Enterprise Consumption, Variance, Wastage, Consolidated Indent, and Stock In/Out use position-aware keys for repeated quantity, amount, and subtotal labels.
- The stable legacy IDs for Gross/Net Margin, Source Analysis Summary, and Daily Sales Revenue are intentionally retained even though their display names were corrected.

## Current P1 Misc Structural Coverage

The 17 explicit blueprints include representative examples of every supported shape:

- Flat: Void Bill Item Wise, CRM, Voucher, Online Orders Time Log, EDC, Reprint, Item Out of Stock, Item Recipe, Staff Meal, Removed Taxes/Charges.
- Grouped columns: Cashier, Super Categories DSR, Entp Day, Shift.
- Grouped rows/matrix: Budget DSR.
- Mixed summary and detail: WhatsApp Message.
- Sales and Reload is encoded from its observed export structure.

Eight reports with no usable result are marked `unavailable`; two unknown placeholders are archived.

## Required Checks

```powershell
py -3 scripts/build_workspace_data.py
py -3 scripts/validate_workspace_data.py
py -3 scripts/validate_control_tower.py
npm run typecheck
npm run lint
npm test
```

Also verify that no image file exists in the project and that generated workspace contracts contain no local path.

## Stop Conditions

Ask for evidence instead of proceeding when:

- a merged header could map to more than one child group;
- horizontal or vertical continuation is missing;
- a report has multiple tables but their boundary is unclear;
- an API path is documented but payload grain is unknown;
- a draft KPI lacks source fields at its required grain;
- UOM, PO-to-GRN, stock-count, recipe, or outlet identity cannot be reconciled;
- a formula, threshold, source selection, or business owner has not been approved for publication.
