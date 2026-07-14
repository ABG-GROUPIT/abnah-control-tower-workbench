# Portable Schema Pack

This folder is the transferable machine-readable memory for ABNAH data discovery.

## Source

- `source/report_structures/`: one screenshot-free structural blueprint per explicitly captured report.
- `source/kpi_lineage/`: empty contract until KPIs and mappings are approved.
- `source/catalog/`: report, field, API, question, test, and mapping registries.
- `source/model_sql/`: current/proposed SQL model context.
- `source/reference_chunks/`: text-only report notes and headers.

## Generated

- `generated/workspace.json`: complete editable report baseline.
- `generated/workspace_report_catalog.csv`: fast report/schema index.
- `generated/kpi-lineage.json`: current KPI-lineage contract.
- `generated/atlas.json`: report, API, and model discovery catalog.
- `generated/quality_report.json`: catalog quality state.

Do not edit generated files manually.

## Privacy Rule

Do not add screenshots, image files, new screenshot paths, client records, report values, or secrets. A structural blueprint should be useful after the local evidence folder is gone.

## Rebuild

```powershell
refresh_atlas.bat
```

The manifest records contract versions, counts, entry points, and source hashes for transfer validation.
