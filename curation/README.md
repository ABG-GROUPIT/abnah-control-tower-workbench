# Curation Registries

These two CSV files are the only manual decision inputs used by the atlas. Keep discovery facts in the report indexes, API packet and SQL sources. Keep human review outcomes here.

## `mapping_options.csv`

One row represents a possible or chosen source-to-model relationship.

- `source_id` and `target_id` must be stable atlas node IDs.
- `relationship_type` must be `report_maps_to_model` for a report source or `api_maps_to_model` for an API source.
- `target_id` must identify a model node.
- `status` must be `candidate`, `selected`, `rejected` or `deferred`.
- `decision_reason` explains why the option was chosen, rejected or deferred.
- A selected mapping still needs supporting UAT evidence and reconciliation tests.

## `validation_tests.csv`

One row represents a repeatable check against an API endpoint, report or mapping subject.

- `subject_id` must be a stable atlas node ID.
- Recommended `test_type` values are `availability`, `authentication`, `payload_fields`, `grain`, `filters`, `pagination` and `reconciliation`.
- `status` must be `planned`, `passed`, `partial`, `failed` or `blocked`.
- `evidence_ref` should point to a controlled sample, test output or meeting record without embedding credentials.

Run `refresh_atlas.bat` after editing either file. Do not edit generated catalogs directly.
