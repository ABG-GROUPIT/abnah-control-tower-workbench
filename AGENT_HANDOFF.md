# AI Agent Handoff

## Objective

Maintain a screenshot-free, evidence-disciplined understanding of ABNAH's Restroworks report schemas and four-page Supply Chain Control Tower requirements. Extend it through targeted P2/P4 discovery, UAT API testing, model revision, and approved KPI lineage without forcing another team to repeat discovery.

## Non-Negotiable Rules

1. Raw screenshots stay outside this repository and outside hosting.
2. Never store a screenshot filename or local evidence path in a new report blueprint.
3. Report blueprints store structural labels and relationships only. The
   Control Tower evidence contract may include one compiler-generated,
   non-sensitive numeric/date excerpt per deterministic finding type; never copy
   full rows, arbitrary values, or client records.
4. Preserve source labels exactly, including suspected spelling errors. Put corrections in notes.
5. Do not claim API coverage until ABNAH UAT access has been tested.
6. Preserve the current 38-table v2 model and 76-object presentation
   contract. New production thresholds or unavailable-source claims still
   require evidence and business approval.
7. Empty and unavailable reports remain explicit states; do not fabricate columns.
8. Archive unknown duplicate placeholders rather than deleting or guessing them.
9. Never commit a Zoho private permalink, OAuth token, refresh token, client
   secret, password, or operational embed response.
10. Treat ABNAH's supplied Control Tower HTML as authoritative for page
    structure, KPI/view naming, business intent, interaction hierarchy, and
    target visual treatment. Treat its hard-coded values as examples only.

## Read Order

1. `README.md`
2. `project-pack/README.md`
3. `schema-pack/generated/project-pack-index.json` to find any implementation,
   SQL, dataset, guide, test, or local tool without scanning the whole pack
4. `schema-pack/manifest.json`
5. `docs/STRUCTURAL_SCHEMA_METHOD.md`
6. `docs/CONTROL_TOWER_KPI_AND_CHART_LINEAGE_HANDBOOK.md`
7. `docs/PRESENTATION_SAFE_ACTUAL_DATA_ISSUES.md`
8. `schema-pack/source/control_tower/control-tower-presentation.json`
9. `schema-pack/source/model/control-tower-model.json`
10. `docs/CONTROL_TOWER_REQUIREMENTS.md`
11. `docs/REPORT_CAPTURE_PRIORITY.md`
12. `docs/MODEL_REVISION_PLAN.md`
13. `schema-pack/source/control_tower/control-tower-requirements.json`
14. `docs/DATA_CONTRACT.md`
15. `docs/LOCAL_AUDIT_PACKET_WORKFLOW.md` when a local CSV packet is supplied
16. `docs/DATA_QUALITY_AND_HOSTING.md` before changing severity, local evidence, or deployment
17. `docs/SCHEMA_CAPTURE_IMPORT.md` when a local schema-capture README is supplied
18. `schema-pack/generated/workspace_report_catalog.csv`
19. The selected report file under `schema-pack/source/report_structures/`
20. Relevant text chunk under `schema-pack/source/reference_chunks/`
21. `docs/KPI_LINEAGE_CONTRACT.md` before source selection or publication
22. `project-pack/zoho-control-tower/docs/ZOHO_CURRENT_WORKSPACE_MIGRATION.md`
    before changing the completed 38-table Zoho workspace
23. `project-pack/zoho-control-tower/docs/ABNAH_REFERENCE_TO_ZOHO_CAPABILITY_MATRIX.md`
    before changing the final report set
24. `project-pack/zoho-control-tower/docs/ZOHO_EMBEDDED_PORTAL_SETUP.md`
    before changing embeds, authentication or hosting
25. `project-pack/zoho-control-tower/docs/ZOHO_PORTAL_HOSTING_AUTH_HANDOFF.md`
    before changing the standalone portal, work-laptop handoff, OAuth boundary,
    GitHub Pages or SharePoint decision

## Truth Model

There are three intentional stores:

- Source blueprints are the transferable baseline in version control.
- GitHub Pages keeps working edits in browser-local storage. Approved,
  transferable state belongs in source blueprints and Git.
- Supabase is the only production backend. It is limited to Zoho OAuth state,
  encrypted portal sessions, and the versioned secured-view URL handoff.
- GitHub Pages uses browser-local persistence and backup export because it has
  no server-side database.
- GitHub Pages also publishes the validated project pack under
  `project-pack/zoho-control-tower/`; use the generated project-library index
  for direct access instead of recursively loading every file.

For the live Atlas, use the committed generated baseline plus any explicit
browser backup under review. For a clean rebuild or team transfer, use source
blueprints and Git; browser edits are not automatically promoted into source
JSON. The `/portal/` frontend is hosted only on GitHub Pages and calls the
Supabase function described in `docs/ZOHO_PORTAL_RUNTIME.md`.

The presentation architecture is generated differently: update the canonical
Query Tables or dashboard story register under
`project-pack/zoho-control-tower/`, then run `npm run data:refresh`. That
regenerates both handbooks and synchronizes the exact SQL and presentation
contract into this repository before validation.

Operational CSV rows remain a fourth, local-only evidence store. The hosted
Data Quality surface may read `local_review_packet.json` through a user-selected
file input, but the browser must not upload, persist, or commit that packet.
The transferable implementation for generating and reviewing that packet is in
`tools/local-auditor/`; never add its runtime `input/` or `output/` contents.

## Finding One Report

1. Filter `schema-pack/generated/workspace_report_catalog.csv` by `report_name`, `page`, or `section`.
2. Use the stable `report_id`; labels can repeat across P1, P2, and P4.
3. Search `schema-pack/source/report_structures/` for that ID.
4. If no blueprint exists, inspect the matching text-only reference chunk.
5. Do not load all 318 report files when one report answers the task.

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
- P4: 26 captured, 48 pending. Enterprise Reports has 15 of 15 captured; Bulk Return and Closing Stock are also captured from the first sanitized local CSV audit.
- The first local CSV checkpoint covers 26 exports across 20 contracts. Read `docs/REAL_CSV_AUDIT_CHECKPOINT.md` before revising report identities, formulas, or value-quality notes.
- The historical `Vendor Report` is a separate exact 16-column contract. Treat
  it as quality-gated evidence, run its local phone/address spillover repairs,
  and never substitute the invented name `Vendor Master`.
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
npm run build:pages
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
