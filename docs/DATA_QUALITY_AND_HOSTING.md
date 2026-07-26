# Data Quality And Hosting

## Purpose

The Data Quality surface unifies the hosted Control Tower evidence register and
the full local row reviewer without putting operational data in source control.

## Evidence Boundary

The repository contains:

- aggregate finding types, counts, severity, interpretation state, and treatment;
- passed, failed, and definition-gated cross-report controls;
- exact schemas and redacted bounded excerpts;
- no raw CSV/XLS files, screenshots, local paths, or full operational rows.

The local audit run contains:

- normalized operational rows;
- `business_review.json` with row-level classified observations;
- `public_business_review.json` with safe aggregates;
- `local_review_packet.json`, which contains full rows and must never be uploaded
  or committed.

Selecting the local packet on the hosted Data Quality page uses the browser File
API. JavaScript reads the file in the current browser tab; the application has no
upload endpoint for it.

## Classification Contract

Severity and interpretation are independent.

| Severity | Meaning |
|---|---|
| Critical | Blocks a dependent production KPI or is a high-impact exception |
| Major | Material coverage, logic, or operational issue |
| Minor | Bounded discrepancy or low-materiality exception |
| Info | Passed control or non-defect context |

| State | Meaning |
|---|---|
| Confirmed issue | Exported evidence directly proves the condition |
| Operational exception | The value may be valid but requires action |
| Needs business definition | The observation is real; treatment needs approval |

Do not classify every negative value as an error. Do not classify a valid
rounding residual as major. Use the shared implementation in
`tools/local-auditor/issue_taxonomy.py`.

## Local Review

From the synthetic-data repository:

```powershell
py -3 tools/local-auditor/business_review.py `
  --audit-run "D:\ABNAH_LOCAL\output\run_YYYYMMDD_HHMMSS" `
  --as-of 2026-07-23

py -3 tools/local-auditor/local_report_viewer.py `
  --audit-run "D:\ABNAH_LOCAL\output\run_YYYYMMDD_HHMMSS"
```

Open `http://127.0.0.1:8765/`. Download the private packet only when it will be
opened locally in the Data Quality page.

## Deployment

There is one frontend deployment:

- GitHub Pages: Atlas, project library, Data Quality surface, and `/portal/`.

The portal's OAuth and URL-only runtime API is the `abnah-portal` Supabase Edge
Function. It is backend infrastructure, not a second website.

Build and validate the Pages version:

```powershell
npm run data:validate
npm run typecheck
npm run build:pages
npm run preview:pages
```

GitHub Actions deploys `pages-dist/` from `main` through
`.github/workflows/pages.yml`. Never add the local review packet to that
directory.

## Update Sequence

1. Run the deterministic audit and business review locally.
2. Review high-impact observations in the localhost viewer.
3. Compile only `public_business_review.json` into the Control Tower evidence.
4. Run `refresh_atlas.bat`.
5. Run privacy validation, typecheck, the Pages production build, and UI checks.
6. Commit and deploy only after the deployable tree contains no raw rows.
