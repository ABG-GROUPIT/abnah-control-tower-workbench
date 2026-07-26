# ABNAH Local CSV Audit Engine

This folder is the private local bridge between Restroworks CSV exports and the
ABNAH Schema Workspace. It checks complete CSV files on the approved local PC,
uses Ollama for semantic review, and produces a scrubbed packet that Codex can use
to update the Workbench. Raw rows never enter the packet.

## Complete Workflow

```text
named CSV drop
  -> deterministic schema and value audit
  -> local-only profiles, samples and normalized evidence
  -> local Ollama analyst
  -> independent local Ollama verifier
  -> privacy gate
  -> CODEX_PACKET.zip
  -> Codex validates packet and edits Workbench source blueprints
  -> refresh_atlas.bat and all Workbench checks
```

The deterministic engine is authoritative for exact header order, row width,
types, blank/null/zero/negative counts, duplicates, and encoded arithmetic rules.
The local LLM interprets those facts, compares months, identifies semantically
suspicious patterns, and proposes whether the schema, a variant, notes, or a local
contract needs review. It does not replace deterministic checks.

## 1. Prepare The CSV Drop

Create one folder anywhere on the local PC and place all selected exports below
it. Subfolders are allowed. Do not edit headers or combine months manually.

Use lowercase canonical names:

```text
enterprise_consumption__2026-03-01__2026-03-31__all.csv
enterprise_purchase_order__2026-03-01__2026-03-31__all.csv
purchase_detail__2026-03-01__2026-03-31__all.csv
enterprise_stock_return__2026-03-01__2026-03-31__all.csv
enterprise_wastage_normal__2026-03-01__2026-03-31__all.csv
gross_net_margin__2026-03-01__2026-03-31__all.csv
stock_in_stock_out__2026-03-01__2026-03-31__all.csv
enterprise_variance_normal__2026-03-01__2026-03-31__all.csv
enterprise_variance_master__2026-03-01__2026-03-31__all.csv
enterprise_reorder__snapshot__2026-03-31__all.csv
item_recipe__snapshot__2026-03-31__all.csv
```

For outlet-specific exports, replace `all` with the stable outlet code. Keep each
month as a separate file so schema drift and month-specific blank/zero behavior
remain visible.

The first production pilot should contain one populated month for each selected
report. After that passes, add four or five monthly exports using identical report
filters. Snapshot/master reports remain separate from transaction periods.

See `references/FIRST_BATCH_SCHEMA_REFERENCE.md` for the current extraction order
and exact grouped-header interpretation.

For the complete four-page production source set, exact filter modes and canonical
file names, use `references/FULL_CONTROL_TOWER_EXTRACTION_MANIFEST.md`.

## 2. Prepare The 5070 Ti PC

Install Ollama, copy this entire `local-auditor` folder to the machine, then
run once:

```bat
setup_5070_model.bat
```

This pulls `qwen3:14b`, the default analyst and verifier. The engine talks only to
`localhost`; a non-local Ollama URL is rejected.

## 3. Run Everything

From this folder:

```bat
run_full_pipeline.bat "D:\ABNAH_LOCAL\CSV_DROP"
```

The 5070 Ti default is equivalent to:

```powershell
python run_pipeline.py `
  --input "D:\ABNAH_LOCAL\CSV_DROP" `
  --model qwen3:14b `
  --num-ctx 32768
```

For the tested RTX 3050 6GB laptop path, run once:

```bat
setup_laptop_model.bat
```

Then run the full local audit with:

```bat
run_laptop_pipeline.bat "D:\ABNAH_LOCAL\CSV_DROP"
```

This uses `qwen2.5:7b-instruct` with an 8,192-token context and a five-minute model
keep-alive. It completed the 26-file, 20-contract analyst/verifier run locally. The
previous `llama3.1:8b` fallback fit the laptop but did not reliably follow value-vs-schema
category rules, so it is not recommended for final audit packets.

The laptop can always run the deterministic stage. The 5070 Ti remains preferable for
larger future batches and `qwen3:14b`, but it is not required for the current contract set.

Each analyst and verifier pass unloads the model by default to avoid retaining a
large prompt cache. Completed passes are stored under
`output/_local_llm_checkpoints/` using an evidence hash. Rerunning unchanged CSVs
and settings resumes those checkpoints; changed files, contracts, models or
context settings create a new checkpoint automatically.

`--skip-llm` exists only for parser engineering tests. A packet created that way
has status `deterministic_only` and is not the final Codex handoff.

## 4. Read The Result

Every run creates two deliberately separate areas:

```text
output/run_YYYYMMDD_HHMMSS/
  LOCAL_EVIDENCE_DO_NOT_UPLOAD/
    deterministic_audit/
    full_profiles_with_local_samples.json
    full_local_llm_reviews.json
  CODEX_PACKET/
  CODEX_PACKET.zip
  run_manifest.json
```

`LOCAL_EVIDENCE_DO_NOT_UPLOAD` may contain actual values and normalized local CSVs.
It stays on the approved machine.

`CODEX_PACKET.zip` contains only headers, semantic column positions, counts,
flags, deterministic findings, verifier-approved interpretations, and explicit
Workbench targets. It contains no screenshots, raw rows, normalized CSVs, or
customer values.

Only hand `CODEX_PACKET.zip` to Codex when `packet_manifest.json` says:

```json
{"status": "ready_for_codex"}
```

Rerun statuses `local_llm_failed`, `grounding_review_required`, and
`privacy_review_required`. A `deterministic_only` packet is useful for testing but
is incomplete.

## Review Full Reports Locally

Run the independent deterministic business review after the corrected contract
audit:

```bat
py -3 business_review.py --audit-run "D:\ABNAH_LOCAL\output\run_YYYYMMDD_HHMMSS" --as-of 2026-07-23
```

It adds:

- severity tiers: `critical`, `major`, `minor`, and `info`;
- interpretation states: confirmed issue, operational exception, or needs definition;
- cross-report controls for transfers, consumption/variance, bill/margin, PO/receipt, and recipe/UOM lineage;
- a local-only `local_review_packet.json` for the hosted browser viewer.

The hosted Schema Atlas contains report structure, coverage, issue density,
Codex semantic classifications, and redacted issue context. Full operational
rows remain in the local audit run.

Open the localhost-only reviewer with:

```bat
run_local_report_viewer.bat
```

To review another completed run:

```bat
run_local_report_viewer.bat "D:\ABNAH_LOCAL\output\run_YYYYMMDD_HHMMSS"
```

The reviewer binds to `127.0.0.1:8765`. It shows every normalized row, supports
report/export selection, search, pagination, severity/class/state filters, and
flagged-only mode. It highlights exact rows and fields from deterministic and
business-semantic checks. It has no upload or external network route. Source
blank/null cells are rendered as `blank`; numeric zero remains `0`. The private
packet download contains operational rows and must never be uploaded or committed.

The launcher must run on the same laptop as the browser, and its terminal must
remain open. `127.0.0.1` never connects to another laptop. Verify the running
service at:

```text
http://127.0.0.1:8765/health
```

If the browser reports `connection refused`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\diagnose_local_report_viewer.ps1
```

That error means no reviewer process is listening, the audit run is missing,
Python is unavailable, or the port is occupied. It does not mean that 8765 is
an insecure port. A different local port can be selected before launch with
`ABNAH_VIEWER_PORT`, but hosted deep links use 8765 by default.

## What Is Checked

- literal header sequence, duplicate labels, insertions, removals and renames;
- semantic row width, trailing export padding and shifted/malformed rows;
- declared and inferred types, parse failures and date behavior;
- blank, null, zero, positive and negative counts per field;
- all-null, mostly-null, all-zero, mostly-zero and constant fields;
- duplicate source rows and cross-file schema fingerprints;
- report-specific equations and reconciliation rules from `contracts/*.json`;
- local numeric ranges and per-file medians for semantic outlier review;
- naming/date discipline and unmatched reports that need a new contract;
- whether evidence implies a Workbench schema, variant, note, or catalog update.

After the verifier, a deterministic grounding gate removes unsupported findings,
rejects invalid evidence references, normalizes contradictory update actions, and
prevents value claims when an export is header-only. Every report must record this
gate before the packet can receive `ready_for_codex` status.

Zero and negative values are findings, not automatic errors. For returns,
adjustments, variances and credits they may be valid. The local LLM must interpret
them using report grain and field semantics, while the verifier rejects claims not
grounded in deterministic evidence.

Quantity-times-price rules include the complete uncertainty implied by exported
display precision. A row is flagged only when its amount falls outside both the
normal tolerance and that rounding envelope. Margin rules do not infer 100%
margin when exported cost is zero; zero cost is assessed separately as a coverage
state.

## Architecture

- `audit.py`: deterministic contract validator and local normalized output.
- `profiler.py`: exhaustive schema/value metrics and privacy-safe profiles.
- `llm_review.py`: two-pass localhost Ollama analyst/verifier.
- `packet_builder.py`: packet redaction, privacy checks and Workbench targets.
- `run_pipeline.py`: complete orchestration command.
- `local_report_viewer.py`: loopback-only full-row evidence reviewer.
- `issue_taxonomy.py`: shared severity and interpretation classifier.
- `business_review.py`: deterministic cross-report and business-semantic review.
- `contracts/*.json`: report-specific headers, positional semantics and rules.
- `tests/`: contract, profiling, alignment and privacy regression tests.

Most reports require a JSON contract, not a unique Python script. A Python adapter
is added only when an export cannot be represented as a stable column sequence.
Repeated child labels such as `Amt` are mapped by parent and position and are never
deduplicated by label alone.

## Add Or Revise A Contract

1. Copy the nearest contract and assign a stable `report_id`.
2. Add a narrow filename regex and canonical filename prefix.
3. Record the literal exported header in `expected_header`.
4. Map every row position once in `row_columns`.
5. Use `row_source_labels` when header cells do not align one-to-one with row cells.
6. Attach the stable Workbench report ID and source blueprint path.
7. Keep inferred formulas at `review` until populated exports validate them.
8. Add a regression test and run the full test suite.

Commands:

```powershell
python audit.py --list-contracts
python -m unittest discover -s tests -v
```

No local model may silently modify a contract or Workbench source. It proposes a
change in the packet; Codex reviews the evidence and performs the versioned edit.
