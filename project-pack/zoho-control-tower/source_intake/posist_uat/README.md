# POSist UAT Codex Screenshot Intake

This folder is a working intake layer for Codex. It is not part of the final product and it is not a production POSist connector.

Use it when ABNAH POSist UAT screenshots, API documentation screenshots, report exports, or sample responses arrive.

## Structured Screenshot Folder

Use the structured folder when you are capturing POSist report menus and report schemas:

```powershell
python scripts\setup_posist_screenshot_structure.py
```

This creates:

```text
source_intake/posist_uat/_incoming_drop/posist_ss/
```

The structure follows:

```text
POSist page -> report section -> individual report -> screenshot slot
```

Read the detailed guide:

```text
source_intake/posist_uat/structured_screenshot_capture_guide.md
```

The first sample observations from `C:\Users\ARNAV\Downloads\CODEX` are summarized here:

```text
source_intake/posist_uat/codex_downloads_sample_observations.md
```

The Stock Administration sample from `C:\Users\ARNAV\Downloads\Stock Administration` is summarized here:

```text
source_intake/posist_uat/stock_administration_sample_observations.md
```

Use `p4_stock_admin` for the separate BOH/raw-report capture branch. This is the current first-priority screenshot route for ABNAH inventory/consumption and vendor/procurement discovery.

## Bulk CSV Header README Templates

When downloading many report exports is faster than filling every report folder manually, generate page-level staging READMEs:

```powershell
python scripts\generate_posist_schema_readme_templates.py --root "C:\Users\ARNAV\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS"
```

This creates:

```text
C:\Users\ARNAV\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS\p2_reports\00_SCHEMA_CAPTURE_README.md
C:\Users\ARNAV\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS\p4_stock_admin\00_SCHEMA_CAPTURE_README.md
```

Paste exact CSV header rows and short notes into these files. Later Codex should split the filled sections back into the report folders and build the durable schema index.

## Restroworks API Docs Packet

A first packet has been created from the public Restroworks API reference:

```text
source_intake/posist_uat/restroworks_api_docs_packet/
```

It contains:

- `README.md`: usefulness verdict and confirmation questions.
- `endpoint_inventory.csv`: endpoint-level inventory and ABNAH priority mapping.
- `model_mapping_seed.csv`: first-pass mapping from Restroworks API modes to current/candidate ABNAH model objects.

Use this packet as API evidence before reviewing screenshots. It shows that the public docs include high-value Stock endpoints for inventory transactions and indents, plus sales bill/invoice endpoints for later consumption and revenue modelling.

## Drop Folder

Put all incoming files here:

```text
source_intake/posist_uat/_incoming_drop/
```

Subfolders are allowed. For example:

```text
_incoming_drop/
  inventory/
  procurement/
  api_docs/
  random_unsorted/
```

Codex can still process it as long as the files are inside `_incoming_drop/`.

## Run The Intake Builder

From the project root:

```powershell
python scripts/prepare_posist_screenshot_intake.py
```

or:

```powershell
scripts\prepare_posist_screenshot_intake.bat
```

This creates a dated analysis batch under:

```text
source_intake/posist_uat/batches/YYYY-MM-DD/
```

The batch contains:

- `00_manifest.csv`
- `05_codex_analysis_outputs/intake_inventory.csv`
- `05_codex_analysis_outputs/screen_catalog_seed.csv`
- `05_codex_analysis_outputs/api_endpoint_catalog_seed.csv`
- `05_codex_analysis_outputs/api_field_catalog_seed.csv`
- `05_codex_analysis_outputs/posist_to_current_model_mapping_seed.csv`
- `05_codex_analysis_outputs/review_packets/packet_*.md`

## Manifest

The script creates or updates `00_manifest.csv`. You can fill details manually before or after running it.

Important fields to fill when possible:

- `posist_module`
- `screen_or_report_name`
- `menu_path_or_url`
- `outlet_filter`
- `date_filter`
- `visible_columns_or_metrics`
- `priority_domain`
- `notes`

If you do not have time to fill the manifest, still dump the screenshots. The script will infer a first-pass domain from filenames and folder names.

## Privacy

Actual dropped files and generated batches are ignored by git. Keep credentials, tokens, and customer-sensitive data out of screenshots where possible. Redact API secrets before dropping docs or samples.
