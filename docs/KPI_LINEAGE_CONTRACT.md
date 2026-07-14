# KPI Lineage Contract

## Current State

The contract is intentionally empty. No KPI has been approved, so the interface shows zero KPI definitions and zero published lineage maps.

## Purpose

After ABNAH finalizes KPIs, represent one KPI at a time from factual source report through transformations to the chart:

```text
source report -> RAW -> STD -> DIM/FACT -> SUM -> KPI -> chart
```

The lineage view is explanatory and read-only. Discovery and mapping decisions are edited in controlled source/workflow records, not by dragging nodes into implied relationships.

## Required KPI Definition

Before adding a KPI, capture:

- stable ID and business name;
- approved business definition;
- formula;
- output grain;
- owner;
- approval state.

## Required Node

Every node is scoped to one KPI and references an existing report, model object, KPI, or chart. It records kind, label, reference ID, lane order, and notes.

## Required Edge

Every edge records:

- source and target node IDs;
- transformation description;
- explicit join keys where applicable;
- decision state: candidate, selected, rejected, or deferred;
- rationale.

Similar field names do not establish a join. A visual connection must represent a reviewed edge record.

## Publication

A publication points to one KPI and version. The future UI should let a viewer select a KPI, inspect only its lineage, and compare candidate decisions without crowding every KPI into one graph.

## Extension Sequence

1. Approve KPI definitions in the business meeting.
2. Confirm source reports and API availability in UAT.
3. Confirm report and payload grain.
4. Select transformations and joins.
5. Reconcile output to source totals.
6. Publish one KPI lineage map.
7. Add chart reference only after the KPI output is accepted.
