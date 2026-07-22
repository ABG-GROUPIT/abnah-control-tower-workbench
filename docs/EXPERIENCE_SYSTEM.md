# Experience System

## Product Character

This is an operational data workspace, not a marketing site. The interface is dense, quiet, and designed for repeated comparison across hundreds of reports.

## Navigation

- First level: Discovery, API validation, Control tower, Architecture.
- Discovery hierarchy: page, section, report.
- Search and schema-status filters narrow the navigator.
- One selected report owns the main workspace at a time.

The report navigator is the primary factual discovery mechanism. The Architecture surface visualizes the current feasible plan and is explicitly labeled as under validation; it does not claim reviewed production lineage.

## Report Workspace

Tabs divide distinct tasks:

- Data points: semantic field inventory.
- Table structure: exact blank visual shape.
- API and tests: endpoint availability and UAT outcome.
- Notes: source interpretation, engineering context, decisions, issues.
- Report settings: identity, classification, verification, archive.
- History: revision audit trail.

## Structural Editor

The table behaves like a focused schema spreadsheet. Stable dimensions prevent edits from shifting surrounding layout. Merged cells express hierarchy; cell roles distinguish groups, fields, context, and blank value regions.

The editor is for structure, not operational data entry.

## Workflow Feedback

The header always exposes workflow state, version, dirty state, persistence connection, and available actions. Conflicts and validation errors are explicit. Published view removes editing affordances.

## Architecture Graph

The graph provides two levels:

- Executive groups nodes by layer and business domain for presentation.
- Engineering expands every report, master, model table, KPI, and dashboard page.

Users can focus one control-tower page, search data points, pan, zoom, move nodes, select a node to trace upstream and downstream paths, inspect transformation logic and fallbacks, and open catalogued source schemas. Layer, state, source count, and the current validation gate are always visible.

The planned architecture contract and reviewed lineage contract remain separate. Candidate or feasible relationships belong in the architecture graph. Only evidence-backed, reviewed mappings can enter lineage publications.

## Responsive Behavior

Desktop prioritizes navigator plus editor or controls plus graph plus inspector. Smaller screens stack controls, retain a fixed-height movable canvas, then place the inspector below it. Wide schema tables continue to scroll within their tool surface. Text and controls must not overlap or change fixed table geometry.
