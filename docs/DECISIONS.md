# Decisions

## D-001: Screenshots Stay Local

Raw screenshots and their paths are not part of the workspace contract or hosted application. Only derived schema structure is retained.

## D-002: Discovery Is a Report Workspace

Hundreds of reports are navigated through search and page/section hierarchy. A graph is not the primary discovery interface.

## D-003: One Universal Editable Grid

Flat, grouped-column, grouped-row, mixed, and freeform source descriptions compile into one cell/span model. Complex structures do not require one-off UI code.

## D-004: Portable Baseline Plus Durable Working Store

Version-controlled source blueprints are the durable, transferable authority.
GitHub Pages keeps in-progress edits in the current browser until a reviewer
exports and reconciles them. Supabase is reserved for the secured portal
session and URL handoff, not discovery documents.

## D-005: Controlled Publication

Edits are drafts, review is explicit, and only an in-review revision can be published. Published mode is read-only.

## D-006: No Hard Delete

Unknown or obsolete reports are archived. Discovery history remains recoverable.

## D-007: API Documentation Is Not UAT Evidence

Public endpoints remain candidates until ABNAH authentication, payload shape, grain, filters, and reconciliation are tested.

## D-008: KPI Definitions May Be Draft; Lineage Waits for Evidence

Business-supplied KPI definitions and formulas are recorded as draft. Source nodes, joins, transformations, and chart edges remain empty until report schemas, UAT payloads, reconciliation, and approval prove them.

## D-009: One KPI Per Lineage View

Future lineage is scoped to a selected KPI across fixed source-to-chart lanes. This supports business explanation without an unreadable all-system network.

## D-010: Backup Export, Controlled Restore

Users can export the current browser workspace. Bulk restore is kept out of the
UI until overwrite and authorization rules are designed.

## D-011: Consumption Terminology

Page 3 uses consumption, not yield. Source report names are preserved exactly, but `Yield Report` is not assumed to support consumption variance without schema evidence.

## D-012: Revise the Existing Model

Keep the useful 37-query layer convention and core facts. Replace synthetic outlet mappings, name joins, approximate PO/receipt joins, arbitrary low-stock rules, and missing UOM/movement logic. Do not create a separate P4 model.

## D-013: Hybrid Ingestion

Use validated Restroworks APIs where they provide complete grain and fields. Use controlled CSV or scheduled file ingestion for missing source domains. Public API documentation is candidate evidence, not ABNAH availability evidence.

## D-014: Detailed Facts, Aggregate Reconciliation

KPI calculations should use the most detailed stable facts. Summary and report-level aggregates are retained for reconciliation unless they provide a uniquely required grain.

## D-015: Zoho First, Custom Shell by Capability Test

Build and validate the data model, calculations, standard visuals, drilldowns, and exports in Zoho Analytics first. Use embedded or white-label Zoho inside a custom shell only when a documented test shows the native portal cannot meet the required action queue, RAG interaction, map, or presentation behavior.
