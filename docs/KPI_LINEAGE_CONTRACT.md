# KPI Lineage Contract

## Current State

The business requirements define 35 draft KPIs. They are derived into the generated lineage contract from `schema-pack/source/control_tower/control-tower-requirements.json`.

The lineage map itself remains intentionally empty: zero source nodes, zero edges, zero approved KPIs, and zero publications. A draft formula does not prove a source relationship.

## Purpose

After ABNAH finalizes KPIs, represent one KPI at a time from factual source report through transformations to the chart:

```text
source report -> RAW -> STD -> DIM/FACT -> SUM -> KPI -> chart
```

The lineage view is explanatory and read-only. Discovery and mapping decisions are edited in controlled source/workflow records, not by dragging nodes into implied relationships.

## Required KPI Definition

Before approving a KPI, capture:

- stable ID and business name;
- business definition and current approval state;
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

1. Record the business-supplied definition as draft.
2. Confirm source reports and API availability in UAT.
3. Confirm report and payload grain, identifiers, UOM, and completeness.
4. Compare candidates and select transformations and joins.
5. Reconcile output to source totals and controlled examples.
6. Approve definition, thresholds, owner, and caveats.
7. Publish one KPI lineage map.
8. Add chart reference only after the KPI output is accepted.
