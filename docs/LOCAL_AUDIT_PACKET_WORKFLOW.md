# Local Audit Packet Workflow

This is the controlled handoff from private Restroworks CSV values to the
screenshot-free ABNAH Schema Workspace.

## Boundary

The local audit PC may hold CSV rows, samples, normalized outputs and full Ollama
analysis. The Workbench repository may hold only schemas, field labels, structural
relationships, counts, data-quality summaries and reviewed decisions.

Only `CODEX_PACKET.zip` crosses that boundary. Never copy the sibling
`LOCAL_EVIDENCE_DO_NOT_UPLOAD` folder into this repository or a cloud model.

## Packet Gate

Validate before reading or applying a packet:

```powershell
py -3 scripts/validate_audit_packet.py "D:\secure\CODEX_PACKET.zip"
```

The validator requires:

- packet status `ready_for_codex`;
- explicit false flags for raw data, screenshots and normalized CSVs;
- the exact packet file allowlist;
- one deterministic post-LLM grounding result for every report;
- no local paths, image references, raw-evidence keys, currency values or obvious
  personal values;
- valid stable Workbench report IDs and source-only blueprint paths.

Use `--allow-incomplete` only while testing packet construction. It does not make
an incomplete packet suitable for schema reconciliation.

## Codex Read Order

1. `00_READ_ME_FIRST.md`
2. `packet_manifest.json`
3. `schema_changes.json`
4. `workbench_updates.json`
5. `value_health.json`
6. `llm_verified_reviews.json`
7. `field_profiles.csv`
8. `privacy_report.json`

Deterministic evidence outranks local-model interpretation. A verifier-approved
LLM statement is still a review aid, not proof of source behavior by itself.

## Update Decisions

| Packet evidence | Workbench action |
|---|---|
| Header insertion, removal, rename or reordered position | Review and edit the source blueprint structure |
| Same report with a genuinely different stable layout | Add a named variant/block, preserving report identity |
| Unmatched report with a known catalog entry | Create a source blueprint only after report identity and grain are reviewed |
| No stable catalog ID | Reconcile the catalog first; do not invent an ID |
| All-null, all-zero, negative or outlier values only | Add a reviewed data-quality note when useful; do not alter blank structure |
| Parser/contract mapping error | Fix the local contract, rerun, and discard the prior packet |
| Unsupported LLM interpretation | Reject it and retain deterministic evidence only |

Repeated labels such as `Amt` must remain attached to their parent measure and
source position. Do not deduplicate them by text. For a report whose header cells
do not align with row cells, preserve explicit blank positions in the blueprint.

## Apply And Regenerate

1. Locate the stable report ID in
   `schema-pack/generated/workspace_report_catalog.csv`.
2. Open the packet target under `schema-pack/source/report_structures/`.
3. Compare the existing blank grid with `semantic_columns` and observed header
   variants in the packet.
4. Edit source JSON only. Never edit `schema-pack/generated/` or `public/data/`.
5. Keep `verification_status` as `needs_review` until the rendered blank structure
   has been checked by a person.
6. Record value-only findings as notes without copying exact business values.
7. Run:

```powershell
refresh_atlas.bat
npm run data:validate
npm run typecheck
npm run lint
npm test
```

8. Review the report in Discovery, including merged cells and every variant.
9. Publish only after the structural change and its evidence have been reviewed.

## Transfer

Retain the packet ID in the schema note or change record, not its local filesystem
path. Transfer source blueprints, generated indexes, documentation and the normal
D1 backup. Raw audit evidence remains in the approved secure storage location.
