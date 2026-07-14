# Experience System

## Product Character

This is an operational data workspace, not a marketing site. The interface is dense, quiet, and designed for repeated comparison across hundreds of reports.

## Navigation

- First level: Discovery, API validation, KPI lineage.
- Discovery hierarchy: page, section, report.
- Search and schema-status filters narrow the navigator.
- One selected report owns the main workspace at a time.

The report navigator is the primary discovery mechanism. A network graph is reserved for future approved lineage where relationships are meaningful.

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

## Future Lineage

The lineage surface uses fixed left-to-right lanes and one KPI selection. It must not render every report/model relationship at once. Candidate, selected, rejected, and deferred relationships require explicit records and labels.

## Responsive Behavior

Desktop prioritizes navigator plus editor. Smaller screens stack navigation and report workspace, keep tabs reachable, and allow wide schema tables to scroll within their tool surface. Text and controls must not overlap or change fixed table geometry.
