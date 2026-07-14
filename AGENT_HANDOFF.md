# AI Agent Handoff

## Objective

Maintain a screenshot-free, evidence-disciplined understanding of ABNAH's Restroworks report schemas. Extend it through P2, Stock Administration/P4, UAT API testing, and later approved KPI lineage without forcing another team to repeat discovery.

## Non-Negotiable Rules

1. Raw screenshots stay outside this repository and outside hosting.
2. Never store a screenshot filename or local evidence path in a new report blueprint.
3. Store structural labels and relationships only; never copy report row values or client records.
4. Preserve source labels exactly, including suspected spelling errors. Put corrections in notes.
5. Do not claim API coverage until ABNAH UAT access has been tested.
6. Do not create KPIs, joins, formulas, or selected mappings without explicit business approval.
7. Empty and unavailable reports remain explicit states; do not fabricate columns.
8. Archive unknown duplicate placeholders rather than deleting or guessing them.

## Read Order

1. `README.md`
2. `schema-pack/manifest.json`
3. `docs/STRUCTURAL_SCHEMA_METHOD.md`
4. `docs/DATA_CONTRACT.md`
5. `schema-pack/generated/workspace_report_catalog.csv`
6. The selected report file under `schema-pack/source/report_structures/`
7. Relevant text chunk under `schema-pack/source/reference_chunks/`
8. `docs/KPI_LINEAGE_CONTRACT.md` only when KPI approval work begins

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

1. Classify the layout: flat, grouped columns, grouped rows, mixed, or freeform.
2. Create one JSON blueprint under the matching page/section.
3. Record exact labels and blank structure only.
4. Add semantic data points separately when the visual structure does not fully express them.
5. Run `refresh_atlas.bat`.
6. Review the generated grid and all validation output.
7. Save, submit for review, and publish in the workspace only after manual checking.

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
- a KPI formula or business grain has not been approved.
