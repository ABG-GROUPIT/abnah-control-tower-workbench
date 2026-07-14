# Decisions

## D-001: Screenshots Stay Local

Raw screenshots and their paths are not part of the workspace contract or hosted application. Only derived schema structure is retained.

## D-002: Discovery Is a Report Workspace

Hundreds of reports are navigated through search and page/section hierarchy. A graph is not the primary discovery interface.

## D-003: One Universal Editable Grid

Flat, grouped-column, grouped-row, mixed, and freeform source descriptions compile into one cell/span model. Complex structures do not require one-off UI code.

## D-004: Portable Baseline Plus Durable Working Store

Version-controlled source blueprints provide transferability. D1 provides current edits and immutable revisions. Neither silently overwrites the other.

## D-005: Controlled Publication

Edits are drafts, review is explicit, and only an in-review revision can be published. Published mode is read-only.

## D-006: No Hard Delete

Unknown or obsolete reports are archived. Discovery history remains recoverable.

## D-007: API Documentation Is Not UAT Evidence

Public endpoints remain candidates until ABNAH authentication, payload shape, grain, filters, and reconciliation are tested.

## D-008: KPI Lineage Waits for Approval

The lineage contract and view exist as an empty architecture. No KPI, formula, join, or chart connection is fabricated before business approval.

## D-009: One KPI Per Lineage View

Future lineage is scoped to a selected KPI across fixed source-to-chart lanes. This supports business explanation without an unreadable all-system network.

## D-010: Backup Export, Controlled Restore

Authenticated users can export all current documents and revisions. Bulk restore is kept out of the UI until overwrite and authorization rules are designed.
