# Portable Schema Pack

This folder is the transferable machine-readable memory for ABNAH data discovery.

## Source

- `source/report_structures/`: one screenshot-free structural blueprint per structurally captured report.
- `source/kpi_lineage/`: empty contract until KPIs and mappings are approved.
- `source/catalog/`: report, field, API, question, test, and mapping registries.
- `source/model_sql/`: current/proposed SQL model context.
- `source/reference_chunks/`: text-only report notes and headers.

In this repository, `captured` means structurally transcribed from one or more governed evidence channels. It does not mean that a strict schema-only image is present in the private migration candidate. Current private image coverage is tracked separately: 64 of 94 historically evidenced groups are image-covered and 30 are image-pending. Among the 30 image-pending groups, 27 have verified text-schema cards totaling 530 fields and 3 remain text-pending. Text cards never count as screenshots.

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
