# Architecture

## System Boundary

The application is a schema discovery, control-tower requirements, and review workspace. It is not a report viewer and does not host raw screenshots or operational data.

```text
local screenshot or local CSV header inspection
                    |
                    | manual structural interpretation only
                    v
schema-pack/source/report_structures/*.json
                    |
                    | build_workspace_data.py
                    v
schema-pack/generated/workspace.json
                    |
          +---------+---------+
          |                   |
          v                   v
read-only baseline      editable web workspace
                              |
                              v
                 D1 current documents + revisions
                              |
                    draft -> review -> publish
                              |
                              v
                    read-only Published view
```

## Layers

### Source Layer

`schema-pack/source/report_structures/` contains one small blueprint per report. High-level block types describe common structures; an explicit grid is the escape hatch.

`schema-pack/source/control_tower/control-tower-requirements.json` is the authority for draft business definitions, page modules, capture priorities, API gaps, and model decisions.

`schema-pack/source/kpi_lineage/kpi-lineage.json` owns lineage state, nodes, edges, and publications. Generated draft KPI definitions are derived from the control-tower contract; the mapping collections remain empty until evidence supports them.

### Build Layer

`scripts/build_atlas_data.py` builds the report/API/model discovery catalog.

`scripts/build_workspace_data.py` overlays explicit structural blueprints on that catalog, compiles every shape into a universal editable grid, and emits workspace, control-tower, and lineage contracts.

`scripts/validate_workspace_data.py` checks workspace contract versions, IDs, dimensions, spans, overlap, and source policy. `scripts/validate_control_tower.py` cross-checks pages, draft KPIs, report candidates, API candidates, terminology, and empty mapping state.

### Application Layer

- `AtlasWorkspace`: navigation, surface switching, persistence orchestration, and backup export.
- `ReportNavigator`: report search, page/section navigation, schema filters, and custom report creation.
- `ReportWorkspacePanel`: per-report tabs and workflow controls.
- `SchemaGridEditor`: spreadsheet-like blank structural editing.
- `DataPointEditor`: semantic field metadata.
- `ApiTestEditor` and `ApiRegistry`: endpoint candidates and UAT outcomes.
- `NotesEditor`: engineering, source, decision, and issue notes.
- `ControlTowerWorkspace`: read-only business requirements, source plan, and delivery decision browser.
- `KpiLineageWorkspace`: draft KPI selector and read-only mapping canvas.

### Persistence Layer

D1 stores:

- one current document per report;
- every save or workflow transition as an immutable revision;
- actor, version, action, workflow state, and timestamp.

Writes use optimistic version checks. A stale editor receives HTTP `409` instead of overwriting a newer revision.

## Workflow

All modifications become `draft`. A draft can be submitted as `in_review`. Only an `in_review` current revision can be published or returned to draft. Published mode never edits data.

Generated baselines have version `0`. The first D1 save becomes version `1`.

## Security Boundary

- R2 is disabled; no image/object storage is configured.
- Hosted writes require `oai-authenticated-user-email` from the authenticated host.
- Localhost uses a local editor identity for development.
- Request bodies are capped at 2 MB.
- Documents are sanitized and unknown keys are removed.
- Limits: 50 tables, 500 rows, 500 columns, and 100,000 cells per report.
- The source policy is overwritten server-side and cannot be weakened by a client.

Deploy privately. Authentication at the hosting boundary is required for confidentiality; the application write check is not a substitute for private site access.

## Extension Points

P2 and P4 require new blueprint files, not new React components. A genuinely new structural shape should first be represented with `grid`; only add a compiler primitive after the pattern repeats and reduces real complexity.

KPI work uses a separate requirements contract and read-only single-KPI lineage view. Discovery documents remain factual even if definitions or mapping decisions change.
