# ABNAH Schema Workspace

This repository is the portable discovery memory and editable schema workspace for ABNAH's Restroworks/POSist data assessment.

The current phase records what data exists, how each report is structurally arranged, which public API candidates may expose it, what has actually been tested, and the draft business requirements for ABNAH's four-page Supply Chain Control Tower. Draft formulas are stored separately from source lineage so that an approved calculation is never confused with a proven data connection.

## Hard Boundary

Raw screenshots remain local to the person collecting them.

This repository and the hosted workspace may contain only:

- derived report names, headers, merged-header relationships, row groups, and semantic notes;
- blank structural tables, never report row values;
- API documentation metadata and UAT test outcomes;
- reviewed mapping decisions after they are approved.

Do not add screenshots, screenshot paths, client records, credentials, tokens, or downloaded report values.

## Current Snapshot

- 319 reports catalogued across P1, P2, and Stock Administration/P4.
- 17 P1 Misc reports encoded as explicit editable structural blueprints.
- 8 P1 Misc reports marked unavailable because their screens returned no usable schema.
- 2 unknown P1 Misc placeholders archived instead of being guessed.
- 34 public Restroworks API candidates packeted; none are ABNAH UAT verified yet.
- 35 draft control-tower KPI definitions, 0 approved KPIs, and 0 published KPI lineage maps.
- P2 now has 73 captured schemas, 3 bounded partial schemas, and 79 pending reports.
- P4 now has 24 captured schemas and 50 pending reports, including all 15 Enterprise reports and four explicit Consumption Report modes.
- Four business pages recorded: Risk Action Center; Procurement, Vendor & Capital Control; Consumption Variance & Menu Profitability; SCM Descriptive Explorer & Data Quality.
- The current P2/P4 schema capture checkpoint is compiled into the website baseline; CSV value and structural-integrity validation remains pending.
- Inventory and consumption intelligence plus vendor and procurement remain phase-1 priorities.

## Product Surfaces

- `Discovery`: searchable report navigator, data points, editable blank structures, notes, report settings, and revision history.
- `API validation`: endpoint registry and per-report test records with passed, partial, failed, blocked, and not-tested states.
- `Control tower`: page requirements, draft KPI formulas, prioritized report capture, API gaps, and the model/delivery decision.
- `KPI lineage`: draft KPI selector with an intentionally empty source-to-chart canvas until schemas and UAT prove the mapping.
- `Workspace`: editable current revision.
- `Published`: read-only latest published revision or repository baseline.

## Start Here

Developer:

1. Read `docs/ARCHITECTURE.md`, `docs/CONTROL_TOWER_REQUIREMENTS.md`, and `docs/STRUCTURAL_SCHEMA_METHOD.md`.
2. Run `npm install`.
3. Run `refresh_atlas.bat` after source changes.
4. Run `npm run dev`.
5. Run `npm run typecheck`, `npm run lint`, `npm run data:validate`, and `npm test` before transfer.

AI agent:

1. Read `AGENT_HANDOFF.md`.
2. Read `schema-pack/manifest.json`.
3. Query `schema-pack/generated/workspace_report_catalog.csv` to narrow the report.
4. Read `docs/LOCAL_AUDIT_PACKET_WORKFLOW.md` before applying a CSV audit packet.
5. Read `docs/SCHEMA_CAPTURE_IMPORT.md` before importing another P2/P4 capture batch.
6. Read `docs/REPORT_CAPTURE_PRIORITY.md` before continuing P2 or P4 discovery.
7. Open only that report's blueprint or reference chunk.
8. Never infer a join, selected source, grain, or API capability from a similar label.

Business reviewer:

1. Use `Published` view.
2. Search for a report by business name or section.
3. Inspect blank table structure, known data points, API state, and notes.
4. Treat `not tested` and `candidate` as unknown, not as available.

## Folder Map

```text
ABNAH Schema Atlas/
  app/                         workspace UI and API routes
  db/                          D1 current-document and revision storage
  drizzle/                     database migration history
  docs/                        architecture, intake, operations, transfer
  scripts/                     builders and validators
  schema-pack/
    source/
      report_structures/       portable per-report schema blueprints
      control_tower/            draft business requirements and source plan
      kpi_lineage/             definitions derived from requirements; mappings still empty
      catalog/                 report, field, API, and decision inputs
      model_sql/               current/proposed model SQL context
      reference_chunks/        text-only report notes and headers
    generated/                 generated contracts and indexes
  public/data/                 browser-readable generated contracts
```

## Data Authorities

- Portable baseline: `schema-pack/source/` compiled into `schema-pack/generated/`.
- Hosted working state: D1 current documents and immutable revisions.
- Published presentation: latest D1 published revision, falling back to the generated baseline when no edited publication exists.

Editing in the site does not automatically rewrite source JSON. Export a backup before transfer and intentionally reconcile approved edits into source blueprints.

## Commands

```powershell
refresh_atlas.bat
py -3 scripts/import_schema_captures.py --p2 "<P2 README>" --p4 "<P4 README>"
npm run dev
npm run data:validate
npm run typecheck
npm run lint
npm test
```

Generated files under `schema-pack/generated/` and `public/data/` must not be edited manually.
