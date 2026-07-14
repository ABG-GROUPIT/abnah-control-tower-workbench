# KPI Lineage Source

This source remains intentionally empty until ABNAH approves KPI definitions and mapping decisions.

Each future lineage map is scoped to one KPI and follows this fixed order:

`source_report -> raw -> std -> dimension/fact -> summary -> kpi -> chart`

Do not create lineage records from semantic similarity alone. Add a KPI only after its business definition, grain, formula, owner, and approval state are known. Add edges only after join keys and transformations are reviewed.
